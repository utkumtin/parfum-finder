"""The search screen: a results table that fills in as each site finishes.

Columns: site, raw product title, size (ml), price, price per ml, stock, match
score. Results from a site land as soon as that site is done -- one worker per
site, started together, none of them waiting on another. The screen never
waits for every site to finish before showing anything.

Matching and row-building are not redone here: both this screen's table and
the database go through store.snapshot_rows, so the two can never disagree
about which titles are this perfume.
"""

from __future__ import annotations

import asyncio
import sqlite3
import webbrowser
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Footer, Input, Static

from parfum_finder.engine import SiteResult
from parfum_finder.matcher import DEFAULT_THRESHOLD, PerfumeQuery, parse_query
from parfum_finder.normalize import format_ml, format_price
from parfum_finder.profiles import load_site_profile, sync_to_db
from parfum_finder.store import (
    DEFAULT_DB_PATH,
    SnapshotRow,
    add_basket_item,
    connect,
    now_iso,
    price_history,
    snapshot_rows,
    write_snapshots,
)
from parfum_finder.tui.basket_screen import BasketScreen
from parfum_finder.validate import (
    DEFAULT_SITES_DIR,
    STALE_PROFILE_DAYS,
    profile_age_days,
)

SiteRunner = Callable[[dict[str, Any], str], Awaitable[SiteResult]]

# Clicking one of these headers sorts by it, the same three sorts the number
# keys offer. The other columns have no ordering worth offering.
_SORT_BY_COLUMN = {2: "ml", 3: "price", 4: "per_ml"}


@dataclass(frozen=True)
class _ResultRow:
    """One priced size, exactly as the table shows it and as a keypress needs it."""

    site_id: str
    site_label: str
    raw_title: str
    size_ml_x10: int
    price_kurus: int | None
    in_stock: bool | None
    match_score: int
    confident: bool
    brand: str
    name: str
    concentration: str
    product_url: str | None

    @property
    def price_per_ml_kurus(self) -> Decimal | None:
        # Decimal, not floor division: latest_prices computes this as a real
        # division too, and truncating to an int here would round two rows
        # that actually differ into a tie and quietly change the sort order.
        if self.price_kurus is None:
            return None
        return Decimal(self.price_kurus * 10) / Decimal(self.size_ml_x10)


class ConfirmScreen(ModalScreen[bool]):
    """Asks before a low-confidence match is written to the basket."""

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }
    ConfirmScreen > Static {
        width: auto;
        max-width: 60;
        border: round $warning;
        padding: 1 2;
        background: $surface;
    }
    """

    BINDINGS = [
        ("y", "confirm", "evet"),
        ("n", "cancel", "hayır"),
        ("escape", "cancel", "iptal"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        yield Static(f"{self._message}\n\n[y] evet   [n] hayır")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class SearchScreen(Screen[None]):
    """The initial screen: search bar, streaming results table, notices, footer."""

    DEFAULT_CSS = """
    SearchScreen #notices {
        color: $warning;
        padding: 0 1;
    }
    SearchScreen #status {
        padding: 0 1;
        color: $text-muted;
    }
    SearchScreen #history-panel {
        width: 36;
        border-left: solid $panel;
        padding: 1;
        display: none;
    }
    """

    BINDINGS = [
        ("1", "sort('ml')", "ml"),
        ("2", "sort('price')", "fiyat"),
        ("3", "sort('per_ml')", "₺/ml"),
        ("f", "toggle_stock", "stok filtre"),
        ("h", "show_history", "fiyat geçmişi"),
        ("a", "add_basket", "sepete ekle"),
        ("s", "open_basket", "sepet"),
        ("escape", "focus_query", "ara"),
        ("q", "quit", "çık"),
        ("ctrl+c", "quit", "çık"),
    ]

    def __init__(
        self,
        *,
        sites_dir: Path = DEFAULT_SITES_DIR,
        db_path: Path = DEFAULT_DB_PATH,
        runner: SiteRunner,
    ) -> None:
        super().__init__()
        self.sites_dir = sites_dir
        self.db_path = db_path
        self.runner = runner
        self._profiles: list[dict[str, Any]] = []
        self._bootstrapped = asyncio.Event()
        self._rows: list[_ResultRow] = []
        self._visible_rows: list[_ResultRow] = []
        # One writer at a time. Every site worker opens its own connection and
        # store.connect() runs the schema script inside a write transaction, so
        # two sites landing together can collide on a locked database. Taking
        # turns costs a few milliseconds and is cheaper than losing a site's
        # prices to a lock error.
        self._write_lock = asyncio.Lock()
        self._notices: list[str] = []
        self._sort_key = "per_ml"
        self._hide_out_of_stock = False
        self._done = 0
        self._total = 0
        self._errors = 0
        self._generation = 0

    def compose(self) -> ComposeResult:
        yield Input(placeholder="örn. Dior Sauvage EDP", id="query")
        with Horizontal(id="body"):
            with Vertical(id="main-col"):
                yield DataTable(id="results", cursor_type="row")
                yield Static("", id="notices")
                yield Static("", id="status")
            yield Static("", id="history-panel")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results", DataTable)
        table.add_columns("Site", "Ürün", "ml", "Fiyat", "₺/ml", "Stok", "%")
        self._bootstrap()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # DataTable already binds "enter" to select the cursor's row and
        # posts this message; opening the browser hooks into that instead of
        # a second "enter" binding on the screen, which a focused table would
        # never let bubble up to anyway.
        event.stop()
        self.action_open_url()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        event.stop()
        key = _SORT_BY_COLUMN.get(event.column_index)
        if key is not None:
            self.action_sort(key)

    # -- setup: sites synced once, before any scan ever runs -----------------

    @work(exclusive=True, group="bootstrap")
    async def _bootstrap(self) -> None:
        profiles = await asyncio.to_thread(self._load_profiles)
        await asyncio.to_thread(self._sync_profiles, profiles)
        self._profiles = profiles
        self._bootstrapped.set()

    def _load_profiles(self) -> list[dict[str, Any]]:
        return [
            load_site_profile(path) for path in sorted(self.sites_dir.glob("*.json"))
        ]

    def _sync_profiles(self, profiles: list[dict[str, Any]]) -> None:
        # A fresh connection per call, opened and closed inside this one
        # thread: sqlite3 connections are tied to the thread that made them,
        # and the executor asyncio.to_thread hands work to is not guaranteed
        # to be the same thread on every call.
        conn = connect(self.db_path)
        try:
            sync_to_db(conn, profiles, synced_at=now_iso())
        finally:
            conn.close()

    # -- search: one worker per site, none waiting on another ----------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        # Focus moves to the table as the search starts. A focused Input eats
        # every printable key, so leaving it focused would make 1/2/3, f, h and
        # a do nothing while the footer still offers them, and there would be
        # no hint that the fix is to press tab first. Escape comes back here.
        self.query_one("#results", DataTable).focus()
        self._start_search(event.value)

    @work(exclusive=True, group="scan-setup")
    async def _start_search(self, text: str) -> None:
        try:
            query = parse_query(text)
        except ValueError as e:
            self._notices = [str(e)]
            self._set_notices()
            return
        await self._bootstrapped.wait()
        self._generation += 1
        generation = self._generation
        self._rows = []
        self._notices = []
        self._done = 0
        self._errors = 0
        self._total = sum(1 for p in self._profiles if p.get("enabled", True))
        self._refresh_table()
        self._set_notices()
        self._update_status()
        for profile in self._profiles:
            if not profile.get("enabled", True):
                continue
            self._scan_site(profile, text, query, generation)

    @work(exclusive=False, group="scan-site")
    async def _scan_site(
        self, profile: dict[str, Any], text: str, query: PerfumeQuery, generation: int
    ) -> None:
        try:
            result = await self.runner(profile, text)
        except Exception as e:
            result = SiteResult(
                str(profile["id"]), "error", (), f"{type(e).__name__}: {e}"
            )
        if generation != self._generation:
            return
        rows = snapshot_rows(result, query)
        # The screen is updated before the database is touched. The table needs
        # nothing from sqlite, so a write that fails must not be able to hide a
        # site that answered, or leave the footer counter stuck below the total
        # with no sign of why.
        self._apply_result(profile, result, rows)
        try:
            async with self._write_lock:
                await asyncio.to_thread(self._write_snapshots, rows)
        except Exception as e:
            if generation != self._generation:
                return
            self._notices.append(
                f"⚠ {result.site_id} — fiyatlar kaydedilemedi ({type(e).__name__}: {e})"
            )
            self._set_notices()

    def _write_snapshots(self, rows: list[SnapshotRow]) -> None:
        conn = connect(self.db_path)
        try:
            write_snapshots(conn, rows)
        finally:
            conn.close()

    def _apply_result(
        self, profile: dict[str, Any], result: SiteResult, rows: list[SnapshotRow]
    ) -> None:
        self._done += 1
        site_label = self._site_label(profile)
        if result.status in ("ok", "empty"):
            if rows:
                self._rows.extend(self._to_result_rows(site_label, rows))
            else:
                self._notices.append(f"{result.site_id} — eşleşme bulunamadı")
        elif result.status == "suspect":
            self._errors += 1
            self._notices.append(
                f"⚠ {result.site_id} — profil bozulmuş olabilir: {self._detail(result)}"
            )
        else:  # error
            self._errors += 1
            self._notices.append(
                f"⚠ {result.site_id} — bağlantı hatası ({self._detail(result)})"
            )
        self._refresh_table()
        self._set_notices()
        self._update_status()

    @staticmethod
    def _detail(result: SiteResult) -> str:
        # Every ExtractionFailed/exception message already opens with
        # "<site_id>: ", so it is stripped here rather than shown twice next
        # to the site id this notice line already names.
        detail = result.detail or ""
        return detail.removeprefix(f"{result.site_id}: ")

    def _site_label(self, profile: dict[str, Any]) -> str:
        name = str(profile["name"])
        age = profile_age_days(str(profile["discovered_at"]))
        if age >= STALE_PROFILE_DAYS:
            return f"{name} ⏳ {age} gün önce keşfedildi"
        return name

    @staticmethod
    def _to_result_rows(site_label: str, rows: list[SnapshotRow]) -> list[_ResultRow]:
        return [
            _ResultRow(
                site_id=row.site_id,
                site_label=site_label,
                raw_title=row.variant.raw_title or "",
                size_ml_x10=row.variant.size_ml_x10,
                price_kurus=row.variant.price_kurus,
                in_stock=row.variant.in_stock,
                match_score=row.match_score,
                confident=row.match_score >= DEFAULT_THRESHOLD,
                brand=row.brand,
                name=row.name,
                concentration=row.concentration,
                product_url=row.variant.product_url,
            )
            for row in rows
        ]

    # -- table: rebuilt on every change, small enough not to matter ----------

    def _refresh_table(self) -> None:
        table = self.query_one("#results", DataTable)
        # Whatever was under the cursor has to end up back under it. clear()
        # sends the cursor to the top, and a slow site landing mid-scan calls
        # this, so without re-seeking the row a person picked would move out
        # from under them and the next [a] would add a different perfume.
        selected = self._selected_row()
        visible = [
            r
            for r in self._rows
            if not (self._hide_out_of_stock and r.in_stock is False)
        ]
        visible.sort(key=self._sort_value)
        self._visible_rows = visible
        table.clear()
        for row in visible:
            table.add_row(*self._cells(row))
        if selected is not None and selected in visible:
            table.move_cursor(row=visible.index(selected))

    def _sort_value(self, row: _ResultRow) -> tuple[bool, Decimal]:
        if self._sort_key == "ml":
            return (False, Decimal(row.size_ml_x10))
        if self._sort_key == "price":
            return (row.price_kurus is None, Decimal(row.price_kurus or 0))
        return (
            row.price_per_ml_kurus is None,
            row.price_per_ml_kurus
            if row.price_per_ml_kurus is not None
            else Decimal(0),
        )

    @staticmethod
    def _cells(row: _ResultRow) -> tuple[object, ...]:
        ml = format_ml(Decimal(row.size_ml_x10) / Decimal(10))
        if row.price_kurus is None:
            price = "-"
        else:
            price = format_price(Decimal(row.price_kurus) / Decimal(100))
        if row.price_per_ml_kurus is None:
            per_ml = "-"
        else:
            per_ml = format_price(Decimal(row.price_per_ml_kurus) / Decimal(100))
        stock = "✓" if row.in_stock else ("✗" if row.in_stock is False else "?")
        cells: tuple[object, ...] = (
            row.site_label,
            row.raw_title,
            ml,
            price,
            per_ml,
            stock,
            str(row.match_score),
        )
        if not row.confident:
            return tuple(Text(str(cell), style="bold yellow") for cell in cells)
        return cells

    def _set_notices(self) -> None:
        self.query_one("#notices", Static).update("\n".join(self._notices))

    def _update_status(self) -> None:
        text = f"{self._done}/{self._total} site tamam"
        if self._errors:
            text += f" · {self._errors} hata"
        self.query_one("#status", Static).update(text)

    def _selected_row(self) -> _ResultRow | None:
        table = self.query_one("#results", DataTable)
        if not self._visible_rows:
            return None
        index = table.cursor_row
        if not (0 <= index < len(self._visible_rows)):
            return None
        return self._visible_rows[index]

    # -- keys ------------------------------------------------------------

    def action_sort(self, key: str) -> None:
        self._sort_key = key
        self._refresh_table()

    def action_toggle_stock(self) -> None:
        self._hide_out_of_stock = not self._hide_out_of_stock
        self._refresh_table()

    def action_open_url(self) -> None:
        row = self._selected_row()
        if row is None or row.product_url is None:
            return
        webbrowser.open(row.product_url)

    def action_add_basket(self) -> None:
        row = self._selected_row()
        if row is None:
            return
        self._add_to_basket(row)

    @work(exclusive=True, group="add-basket")
    async def _add_to_basket(self, row: _ResultRow) -> None:
        # push_screen(..., wait_for_dismiss=True) only works from inside a
        # worker, which is why the confirmation dialog and the write both
        # live in this @work method instead of directly in the action.
        if not row.confident:
            confirmed = await self.app.push_screen(
                ConfirmScreen(
                    f"{row.raw_title} düşük eşleşme skoruyla (%{row.match_score}) "
                    "sepete eklensin mi?"
                ),
                wait_for_dismiss=True,
            )
            if not confirmed:
                return
        await asyncio.to_thread(self._add_basket_item, row)

    def _add_basket_item(self, row: _ResultRow) -> None:
        conn = connect(self.db_path)
        try:
            add_basket_item(
                conn,
                brand=row.brand,
                name=row.name,
                concentration=row.concentration,
                size_ml_x10=row.size_ml_x10,
            )
        finally:
            conn.close()

    def action_show_history(self) -> None:
        panel = self.query_one("#history-panel", Static)
        if panel.display:
            panel.display = False
            return
        row = self._selected_row()
        if row is None:
            return
        self._load_history(row)

    @work(exclusive=True, group="history")
    async def _load_history(self, row: _ResultRow) -> None:
        rows = await asyncio.to_thread(self._read_history, row)
        panel = self.query_one("#history-panel", Static)
        if not rows:
            panel.update("fiyat geçmişi yok")
        else:
            lines = [
                f"{r['fetched_at']}  "
                f"{format_price(Decimal(r['price_kurus']) / Decimal(100))}"
                for r in rows
            ]
            panel.update("\n".join(lines))
        panel.display = True

    def _read_history(self, row: _ResultRow) -> list[sqlite3.Row]:
        conn = connect(self.db_path)
        try:
            return price_history(
                conn,
                site_id=row.site_id,
                brand=row.brand,
                name=row.name,
                concentration=row.concentration,
                size_ml_x10=row.size_ml_x10,
            )
        finally:
            conn.close()

    def action_open_basket(self) -> None:
        # Pushed, not switched. The scan behind it stays alive and its rows are
        # still there on the way back, so checking the basket does not cost a
        # second pass over every site.
        self.app.push_screen(
            BasketScreen(
                sites_dir=self.sites_dir, db_path=self.db_path, runner=self.runner
            )
        )

    def action_focus_query(self) -> None:
        self.query_one("#query", Input).focus()

    def action_quit(self) -> None:
        self.app.exit()
