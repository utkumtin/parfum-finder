"""The basket screen: the shopping list, a scenario per site, and the best split.

Sites that cover the whole list are shown separately from sites that only cover
part of it, and listed above them. A partial site is tagged, e.g. "4/5 items", and
never compared directly against a full-coverage total. Each scenario shows how much
more is needed to unlock free shipping. The split-across-sites result is always
labeled as the best combination found, not the mathematically cheapest.

TODO (M9): the split-across-sites block, its honesty label, and the comparison
line against the best full-coverage single site.
"""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from parfum_finder.basket import (
    BasketItem,
    BasketReport,
    ShippingConfig,
    SiteScenario,
    single_site_scenarios,
)
from parfum_finder.engine import SiteResult
from parfum_finder.matcher import PerfumeQuery
from parfum_finder.normalize import format_ml, format_price
from parfum_finder.profiles import load_site_profile
from parfum_finder.store import (
    DEFAULT_DB_PATH,
    BasketLine,
    BasketPrice,
    BasketSite,
    SnapshotRow,
    basket_lines,
    basket_prices,
    basket_sites,
    connect,
    remove_basket_item,
    set_basket_qty,
    snapshot_rows,
    write_snapshots,
)
from parfum_finder.validate import DEFAULT_SITES_DIR

SiteRunner = Callable[[dict[str, Any], str], Awaitable[SiteResult]]

# One edit to the basket, handed to the worker that owns the write lock so the
# three key bindings do not each need their own copy of the connect/close dance.
_Change = Callable[[sqlite3.Connection], None]

# A price older than this is called out at the top of the screen. It is not the
# profile staleness number: a profile that was described three months ago can
# still be reading the site correctly, while a two week old price is simply a
# price the shop has had plenty of time to change.
STALE_PRICE_DAYS = 14

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

_EMPTY = "—"


@dataclass(frozen=True)
class _BasketRow:
    """One basket line as the table shows it, with the keys a keypress needs."""

    line: BasketLine
    label: str
    # Unit price per site, only for the sites that can actually supply this line.
    prices: dict[str, int]
    age_days: int | None


def snapshot_age_days(fetched_at: str, now: datetime | None = None) -> int:
    """Whole days between a price snapshot and now.

    Only the one UTC format the database writes is accepted. Being lenient would
    let a row carrying a local time report an age that is quietly a few hours
    wrong, and the whole point of this number is that somebody trusts it enough
    to skip a refresh.
    """
    stamp = datetime.strptime(fetched_at, _TIMESTAMP_FORMAT).replace(tzinfo=UTC)
    return ((now or datetime.now(UTC)) - stamp).days


def format_age(age_days: int | None) -> str:
    """Turn a price age in days into the words the age column shows."""
    if age_days is None:
        return _EMPTY
    if age_days <= 0:
        return "bugün"
    if age_days < 7:
        return f"{age_days} gün önce"
    return f"{age_days // 7} hafta önce"


class BasketScreen(Screen[None]):
    """The basket: the list on top, one scenario per site underneath."""

    DEFAULT_CSS = """
    BasketScreen #basket-notices {
        color: $warning;
        padding: 0 1;
    }
    BasketScreen #scenarios {
        padding: 0 1;
    }
    BasketScreen #basket-status {
        padding: 0 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("d", "remove", "çıkar"),
        ("plus", "increment", "adet +"),
        ("minus", "decrement", "adet -"),
        ("r", "refresh_prices", "tazele"),
        ("escape", "back", "geri"),
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
        self._rows: list[_BasketRow] = []
        self._sites: list[BasketSite] = []
        self._notices: list[str] = []
        # (site, basket line) pairs this session's refresh could not price,
        # whether the site broke or answered that it does not sell that decant.
        # Either way the database still holds the last good snapshot and
        # latest_prices keeps serving it, so counting it would put a number
        # nobody can currently stand behind into a total the user is about to
        # act on. Nothing on disk records this, so the exclusion lasts only as
        # long as the screen is open.
        #
        # Per line rather than per site, because a shop that stopped carrying
        # one decant is still telling the truth about the other four.
        self._excluded: set[tuple[str, int]] = set()
        # One writer at a time, same reason as on the search screen: every
        # refresh worker opens its own connection and two landing together can
        # collide on a locked database.
        self._write_lock = asyncio.Lock()
        self._refreshing = False
        self._scanned = 0
        self._scans = 0

    def compose(self) -> ComposeResult:
        yield DataTable(id="basket", cursor_type="row")
        yield Static("", id="basket-notices")
        yield Static("", id="scenarios")
        yield Static("", id="basket-status")
        yield Footer()

    def on_mount(self) -> None:
        self._reload()

    # -- reading: the whole basket is small, so it is re-read wholesale -------

    @work(exclusive=True, group="basket-load")
    async def _reload(self) -> None:
        lines, prices, sites = await asyncio.to_thread(self._read)
        self._sites = sites
        self._rows = self._build_rows(lines, prices)
        self._render_all()

    def _read(self) -> tuple[list[BasketLine], list[BasketPrice], list[BasketSite]]:
        # A fresh connection inside this one thread: sqlite3 connections belong
        # to the thread that opened them and to_thread does not promise the same
        # thread twice.
        conn = connect(self.db_path)
        try:
            return basket_lines(conn), basket_prices(conn), basket_sites(conn)
        finally:
            conn.close()

    def _build_rows(
        self, lines: list[BasketLine], prices: list[BasketPrice]
    ) -> list[_BasketRow]:
        by_item: dict[int, dict[str, BasketPrice]] = {}
        for price in prices:
            # Out of stock is missing, not cheap. So is a site this session
            # could not price. Both are dropped here rather than carried into
            # the totals as a real offer.
            if (
                not price.in_stock
                or (price.site_id, price.basket_item_id) in self._excluded
            ):
                continue
            by_item.setdefault(price.basket_item_id, {})[price.site_id] = price
        rows: list[_BasketRow] = []
        for line in lines:
            found = by_item.get(line.basket_item_id, {})
            # The oldest reading on the row, not the newest. A row is only as
            # fresh as its stalest cell, and showing the newest would hide a
            # column that has not been checked in a month behind one that was
            # scanned an hour ago.
            ages = [snapshot_age_days(p.fetched_at) for p in found.values()]
            rows.append(
                _BasketRow(
                    line=line,
                    label=_label(line),
                    prices={site_id: p.price_kurus for site_id, p in found.items()},
                    age_days=max(ages) if ages else None,
                )
            )
        return rows

    # -- rendering ------------------------------------------------------------

    def _render_all(self) -> None:
        self._render_table()
        report = self._report()
        self._render_notices(report)
        self._render_scenarios(report)
        self._update_status()

    def _render_table(self) -> None:
        table = self.query_one("#basket", DataTable)
        selected = self._selected_row()
        table.clear(columns=True)
        table.add_columns(
            "Parfüm", "ml", "Ad", *(site.name for site in self._sites), "Yaş"
        )
        for row in self._rows:
            table.add_row(*self._cells(row))
        if selected is not None:
            ids = [r.line.basket_item_id for r in self._rows]
            if selected.line.basket_item_id in ids:
                table.move_cursor(row=ids.index(selected.line.basket_item_id))

    def _cells(self, row: _BasketRow) -> tuple[object, ...]:
        ml = format_ml(Decimal(row.line.size_ml_x10) / Decimal(10))
        # The unit price, not the line total. The quantity has its own column,
        # and multiplying it in here would make two rows of the same perfume
        # look like two different offers from the same shop.
        cells: list[object] = [
            f"{row.line.brand} {row.line.name} {row.line.concentration}".strip(),
            ml,
            str(row.line.qty),
        ]
        for site in self._sites:
            price = row.prices.get(site.site_id)
            cells.append(
                _EMPTY if price is None else format_price(Decimal(price) / Decimal(100))
            )
        age = format_age(row.age_days)
        # The stale rows are coloured, not just counted in the warning above the
        # table. With a dozen lines the warning says some price is old, and this
        # is what says which one.
        if row.age_days is not None and row.age_days >= STALE_PRICE_DAYS:
            cells.append(Text(age, style="bold red"))
        else:
            cells.append(age)
        return tuple(cells)

    def _report(self) -> BasketReport:
        items = [
            BasketItem(
                item_id=row.line.basket_item_id, label=row.label, qty=row.line.qty
            )
            for row in self._rows
        ]
        prices: dict[tuple[int, str], int | None] = {
            (row.line.basket_item_id, site_id): price
            for row in self._rows
            for site_id, price in row.prices.items()
        }
        shipping = [
            ShippingConfig(
                site_id=site.site_id,
                name=site.name,
                free_shipping_threshold_kurus=site.free_shipping_threshold_kurus,
                shipping_cost_kurus=site.shipping_cost_kurus,
                notes=site.notes,
            )
            for site in self._sites
        ]
        return single_site_scenarios(items, prices, shipping)

    def _render_notices(self, report: BasketReport) -> None:
        notices = list(self._notices)
        if not self._rows:
            notices.append("Sepet boş. Arama ekranından [a] ile ürün ekleyin.")
        else:
            for label in report.unavailable:
                notices.append(f'⚠ "{label}" hiçbir sitede bulunamadı')
            if not report.full:
                notices.append(
                    "⚠ Hiçbir site listenin tamamını karşılamıyor — aşağıdaki "
                    "kısmi senaryolara bakın"
                )
            if any(
                row.age_days is not None and row.age_days >= STALE_PRICE_DAYS
                for row in self._rows
            ):
                notices.append(
                    f"⚠ Bazı fiyatlar {STALE_PRICE_DAYS} günden eski — "
                    "[r] ile tazeleyin"
                )
        self.query_one("#basket-notices", Static).update("\n".join(notices))

    def _render_scenarios(self, report: BasketReport) -> None:
        lines: list[str] = []
        if report.full:
            lines.append("TEK SİTE SENARYOLARI — tam kapsamlı")
            lines.append("")
            for scenario in report.full:
                lines.extend(_scenario_block(scenario, "✓"))
        if report.partial:
            lines.append("── kısmi (tam kapsamlılarla doğrudan kıyaslanamaz) ──")
            lines.append("")
            for scenario in report.partial:
                lines.extend(_scenario_block(scenario, "⚠"))
        self.query_one("#scenarios", Static).update("\n".join(lines).rstrip())

    def _update_status(self) -> None:
        if self._refreshing:
            text = f"{self._scanned}/{self._scans} tarama tamam"
        else:
            text = f"Sepet ({len(self._rows)} ürün)"
        self.query_one("#basket-status", Static).update(text)

    def _selected_row(self) -> _BasketRow | None:
        table = self.query_one("#basket", DataTable)
        index = table.cursor_row
        if not (0 <= index < len(self._rows)):
            return None
        return self._rows[index]

    # -- keys -----------------------------------------------------------------

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_remove(self) -> None:
        row = self._selected_row()
        if row is not None:
            self._write_then_reload(_remove(row.line.basket_item_id))

    def action_increment(self) -> None:
        row = self._selected_row()
        if row is not None:
            self._write_then_reload(_set_qty(row.line.basket_item_id, row.line.qty + 1))

    def action_decrement(self) -> None:
        row = self._selected_row()
        # store.set_basket_qty clamps at 1, so this is a no-op on a single
        # bottle rather than a removal. Taking the last one out has its own key,
        # and a "-" that silently deleted the row would be a surprise.
        if row is not None:
            self._write_then_reload(_set_qty(row.line.basket_item_id, row.line.qty - 1))

    @work(exclusive=False, group="basket-write")
    async def _write_then_reload(self, change: _Change) -> None:
        async with self._write_lock:
            await asyncio.to_thread(self._apply, change)
        self._reload()

    def _apply(self, change: _Change) -> None:
        conn = connect(self.db_path)
        try:
            change(conn)
        finally:
            conn.close()

    # -- refresh: parallel across sites, serial within one --------------------

    def action_refresh_prices(self) -> None:
        if not self._refreshing and self._rows:
            self._refresh_prices()

    @work(exclusive=True, group="basket-refresh")
    async def _refresh_prices(self) -> None:
        profiles = await asyncio.to_thread(self._load_profiles)
        rows = list(self._rows)
        self._refreshing = True
        self._notices = []
        self._excluded = set()
        self._scanned = 0
        self._scans = len(profiles) * len(rows)
        self._update_status()
        try:
            # One task per site, and inside each task the perfumes go one after
            # the other. run_site builds its own pacer per call, so firing a
            # site's whole basket at once would put every rate_limit_ms gap in
            # parallel with the others and hand a small shop the request burst
            # this project exists not to send.
            async with asyncio.TaskGroup() as group:
                for profile in profiles:
                    group.create_task(self._refresh_site(profile, rows))
        finally:
            # Cleared even when a task blew up. The refresh key is gated on this
            # flag, and leaving it set would make [r] dead for as long as the
            # screen stays open, with nothing on screen saying why.
            self._refreshing = False
        self._reload()

    def _load_profiles(self) -> list[dict[str, Any]]:
        profiles = [
            load_site_profile(path) for path in sorted(self.sites_dir.glob("*.json"))
        ]
        return [p for p in profiles if p.get("enabled", True)]

    async def _refresh_site(
        self, profile: dict[str, Any], rows: list[_BasketRow]
    ) -> None:
        site_id = str(profile["id"])
        for row in rows:
            # Built from the stored identity parts instead of re-parsing a
            # sentence, because those parts are what the basket line is keyed on
            # and a round trip through the text parser could come back split
            # differently and file the refreshed price under another perfume.
            query = PerfumeQuery(
                brand=row.line.brand,
                name=row.line.name,
                concentration=row.line.concentration,
            )
            # The size is left out of the search text on purpose. The shop is
            # asked for the perfume and answers with every size it sells; the
            # basket picks its own size back out of that by the integer join.
            text = f"{row.line.brand} {row.line.name} {row.line.concentration}".strip()
            try:
                result = await self.runner(profile, text)
            except Exception as e:
                result = SiteResult(site_id, "error", (), f"{type(e).__name__}: {e}")
            if result.status in ("error", "suspect"):
                self._excluded.add((site_id, row.line.basket_item_id))
                self._note(f"⚠ {site_id} tazelenemedi")
            elif result.status == "empty":
                # The shop answered and does not have it. No notice, because
                # that is not a failure, but the old price still has to go:
                # leaving it would show a number for a decant the shop just
                # said it no longer sells. That is worse than the broken case,
                # since here there is positive evidence it is gone.
                self._excluded.add((site_id, row.line.basket_item_id))
            else:
                await self._store(site_id, snapshot_rows(result, query))
            self._scanned += 1
            self._update_status()

    async def _store(self, site_id: str, rows: list[SnapshotRow]) -> None:
        try:
            async with self._write_lock:
                await asyncio.to_thread(self._write, rows)
        except Exception as e:
            self._note(
                f"⚠ {site_id} — fiyatlar kaydedilemedi ({type(e).__name__}: {e})"
            )

    def _write(self, rows: list[SnapshotRow]) -> None:
        conn = connect(self.db_path)
        try:
            write_snapshots(conn, rows)
        finally:
            conn.close()

    def _note(self, message: str) -> None:
        # A site that fails on every perfume in the basket would otherwise print
        # the same line once per row.
        if message not in self._notices:
            self._notices.append(message)


def _label(line: BasketLine) -> str:
    """Name one basket line the way a missing-item warning has to read it."""
    perfume = f"{line.brand} {line.name} {line.concentration}".strip()
    return f"{perfume} {format_ml(Decimal(line.size_ml_x10) / Decimal(10))}"


def _remove(basket_item_id: int) -> _Change:
    def change(conn: sqlite3.Connection) -> None:
        remove_basket_item(conn, basket_item_id=basket_item_id)

    return change


def _set_qty(basket_item_id: int, qty: int) -> _Change:
    def change(conn: sqlite3.Connection) -> None:
        set_basket_qty(conn, basket_item_id=basket_item_id, qty=qty)

    return change


def _scenario_block(scenario: SiteScenario, mark: str) -> list[str]:
    """The two or three lines one site's scenario takes up on screen."""
    subtotal = format_price(Decimal(scenario.subtotal_kurus) / Decimal(100))
    shipping = format_price(Decimal(scenario.shipping_kurus) / Decimal(100))
    total = format_price(Decimal(scenario.total_kurus) / Decimal(100))
    head = (
        f"{mark} {scenario.name}   {scenario.covered}/{scenario.total_items}   "
        f"{subtotal} + {shipping} kargo = {total}"
    )
    if not scenario.is_full:
        head += "   (kısmi)"
    lines = [head]
    if scenario.missing:
        lines.append(f"    eksik: {', '.join(scenario.missing)}")
    if scenario.free_shipping_met:
        lines.append("    ücretsiz kargo eşiği aşıldı")
    elif scenario.free_shipping_gap_kurus is not None:
        gap = format_price(Decimal(scenario.free_shipping_gap_kurus) / Decimal(100))
        lines.append(f"    ücretsiz kargoya {gap} kaldı")
    if scenario.notes:
        lines.append(f"    {scenario.notes}")
    lines.append("")
    return lines
