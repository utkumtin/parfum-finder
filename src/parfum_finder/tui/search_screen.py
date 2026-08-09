"""The search screen: a results table that fills in as each site finishes.

Columns: site, raw product title, size (ml), price, price per ml, stock, match
score. Results from a site land as soon as that site is done -- one task per
site, started together, none of them waiting on another. The screen never
waits for every site to finish before showing anything.

One line may ask for several perfumes, separated by " - ". They are scanned in
one pass, still one task per site, with that site's perfumes going one after
the other inside it: a site's requests are paced from one place, so starting a
shop's whole list at once would hand it the burst the pacing exists to prevent.

Matching and row-building are not redone here: both this screen's table and
the database go through store.snapshot_rows, so the two can never disagree
about which titles are this perfume.
"""

from __future__ import annotations

import asyncio
import sqlite3
import webbrowser
from collections.abc import Awaitable, MutableMapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Input, Static

from parfum_finder.engine import CacheKey, CandidateFilter, SiteResult, VariantsRead
from parfum_finder.fetch import Fetcher, browser_session
from parfum_finder.logging_setup import LOG_FILE_NAME, logger
from parfum_finder.matcher import (
    DEFAULT_THRESHOLD,
    MAX_QUERIES,
    PerfumeQuery,
    parse_query,
    split_queries,
    title_could_match,
)
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


class SiteRunner(Protocol):
    """What this screen needs of engine.run_site.

    A protocol rather than a plain callable alias because the scan hands the
    runner more than a query now: the browser session it owns, the filter that
    keeps a listing from being opened for nothing, and the product cache the
    perfumes of one scan share. A stand-in that cannot take them is a type
    error here instead of a surprise mid-scan.
    """

    def __call__(
        self,
        profile: dict[str, Any],
        query: str,
        *,
        fetcher: Fetcher = ...,
        keep_candidate: CandidateFilter | None = ...,
        variants_cache: MutableMapping[CacheKey, VariantsRead] | None = ...,
    ) -> Awaitable[SiteResult]: ...


# Clicking one of these headers sorts by it, the same three sorts the number
# keys offer. The other columns have no ordering worth offering. Counted from
# the size column, since a multi-perfume search puts one more column in front
# of it.
_SORT_BY_COLUMN = {0: "ml", 1: "price", 2: "per_ml"}

_BASE_COLUMNS = ("Site", "Ürün", "ml", "Fiyat", "₺/ml", "Stok", "%")

# One colour per site, so a long table reads as blocks instead of one wall of
# rows. Keyed by site_id and not by the label, because a stale profile gets a
# "N gün önce keşfedildi" badge glued to its label and would then miss its
# colour. A site that is not in here renders plain, which is the honest answer
# for a profile this palette has never seen.
#
# Soft and muted on purpose: these sit on textual-dark all scan long. The hex
# values are picked so that each one collapses to a different 256-colour index
# on terminals without truecolor, which is where near neighbours would blur
# into each other.
_SITE_STYLES = {
    "decantall": "#7fa8c9",
    "dekantdoktoru": "#8bbf8b",
    "dekantparfum": "#c8b26b",
    "luxurydekant": "#b294c4",
    "ruxangroup": "#d18f8f",
    "venco": "#5fb3b3",
}

# What a low match score is marked with. Only the site's own title and the
# score itself carry it: those two are the doubtful part. The price, size and
# stock of that listing were read correctly whatever the score says, and
# painting them made a whole row look untrustworthy over one weak title.
_LOW_CONFIDENCE_STYLE = "#cf9145"

# Where the sortable columns start, with and without the perfume column.
_FIRST_SORTABLE = _BASE_COLUMNS.index("ml")


def _listing_filter(query: PerfumeQuery) -> CandidateFilter:
    """Decide, from a search result's own title, whether to open its page."""

    def keep(raw_title: str | None) -> bool:
        return title_could_match(raw_title, query)

    return keep


@dataclass(frozen=True)
class _Search:
    """One perfume of a search, as typed and as parsed.

    The index is what groups the results table: three perfumes sorted into one
    ₺/ml list interleave into something nobody can read, so the typed order is
    the outer sort and the chosen column only orders each group.
    """

    index: int
    text: str
    query: PerfumeQuery


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
    query_index: int = 0
    query_label: str = ""
    clone_of: str = ""

    @property
    def price_per_ml_kurus(self) -> Decimal | None:
        # Decimal, not floor division: latest_prices computes this as a real
        # division too, and truncating to an int here would round two rows
        # that actually differ into a tie and quietly change the sort order.
        if self.price_kurus is None:
            return None
        return Decimal(self.price_kurus * 10) / Decimal(self.size_ml_x10)


class ConfirmScreen(ModalScreen[bool]):
    """Asks before a low-confidence match is written to the basket.

    The two answers are real buttons, not a line of text naming two keys. The
    keys always worked, but a dialog that only prints "[y] evet [n] hayır" looks
    like something to move a cursor through, so pressing arrows and enter did
    nothing and the dialog read as frozen. Buttons take focus, tab moves between
    them and enter presses the focused one, which is what anyone tries first.
    The y and n keys stay, for anyone who already knows them.

    "Hayır" holds the focus at open, so a reflexive enter on a dialog nobody
    read cancels rather than putting a doubtful bottle in the basket.
    """

    AUTO_FOCUS = "#no"

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }
    ConfirmScreen > Vertical {
        width: auto;
        max-width: 60;
        height: auto;
        border: round $warning;
        padding: 1 2;
        background: $surface;
    }
    ConfirmScreen #buttons {
        width: auto;
        height: auto;
        padding-top: 1;
    }
    ConfirmScreen Button {
        margin-right: 2;
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
        with Vertical():
            yield Static(self._message)
            with Horizontal(id="buttons"):
                # Brackets are escaped because Textual reads them as content
                # markup, so an unescaped [y] is stripped out as a style tag
                # and the key hint never reaches the screen.
                yield Button(r"Evet \[y]", variant="warning", id="yes")
                yield Button(r"Hayır \[n]", variant="primary", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss(event.button.id == "yes")

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
        width: 44;
        border-left: solid $panel;
        padding: 1;
        display: none;
    }
    """

    BINDINGS = [
        ("1", "sort('ml')", "ml"),
        ("2", "sort('price')", "fiyat"),
        ("3", "sort('per_ml')", "₺/ml"),
        ("f", "toggle_stock", "stoksuzları göster"),
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
        # What the current results are about. Empty until the first search, and
        # what decides whether the table needs a perfume column at all.
        self._searches: list[_Search] = []
        self._limit_notice = ""
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
        # Hidden from the start. A size that cannot be bought is not an offer,
        # and leaving them in put the cheapest unbuyable price at the top of a
        # table sorted by ₺/ml, which is the one number people read first. They
        # are still fetched and still stored, [f] brings them back on screen,
        # and the price history panel goes on counting them.
        self._hide_out_of_stock = True
        self._hidden_count = 0
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
        self.query_one("#results", DataTable).add_columns(*self._columns())
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
        # Counted from the first sortable column, which a multi-perfume search
        # pushes one to the right.
        offset = _FIRST_SORTABLE + (1 if self._multi else 0)
        key = _SORT_BY_COLUMN.get(event.column_index - offset)
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

    def on_input_changed(self, event: Input.Changed) -> None:
        # Counted while it is being typed, not on submit. A pasted list is the
        # way this limit gets hit, and finding out only after pressing enter is
        # finding out after the wait.
        count = len(split_queries(event.value))
        self._limit_notice = (
            f"en fazla {MAX_QUERIES} parfüm aranabilir, bu satırda {count} var"
            if count > MAX_QUERIES
            else ""
        )
        self._set_notices()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        if self._limit_notice:
            # Refused rather than trimmed to the first ten. Which ones were
            # dropped is not something a status line makes obvious, and a scan
            # that quietly answered a shorter question is worse than no scan.
            return
        # Focus moves to the table as the search starts. A focused Input eats
        # every printable key, so leaving it focused would make 1/2/3, f, h and
        # a do nothing while the footer still offers them, and there would be
        # no hint that the fix is to press tab first. Escape comes back here.
        self.query_one("#results", DataTable).focus()
        self._start_search(event.value)

    @work(exclusive=True, group="scan-setup")
    async def _start_search(self, text: str) -> None:
        searches: list[_Search] = []
        rejected: list[str] = []
        for part in split_queries(text):
            try:
                query = parse_query(part)
            except ValueError as e:
                # One unparseable piece does not cancel the others. Someone who
                # typed three perfumes and mistyped one wants the two that were
                # right, and the line below says which one was not.
                rejected.append(str(e))
                continue
            searches.append(_Search(index=len(searches), text=part, query=query))
        if not searches:
            self._notices = rejected or ["a search needs a perfume to look for"]
            self._set_notices()
            return
        await self._bootstrapped.wait()
        self._generation += 1
        generation = self._generation
        self._searches = searches
        self._rows = []
        self._notices = rejected
        self._done = 0
        self._errors = 0
        profiles = [p for p in self._profiles if p.get("enabled", True)]
        self._total = len(searches) * len(profiles)
        self._reset_table()
        self._set_notices()
        self._update_status()
        # One product read per URL for the whole scan. Two perfumes searched at
        # one shop routinely list the same product, and the second read costs a
        # request and a rate-limit wait to learn what is already known.
        cache: dict[CacheKey, VariantsRead] = {}
        # The browser, if any site needs one, is started once and kept for the
        # whole scan instead of per page. Nothing is launched when no profile
        # asks for playwright.
        async with browser_session() as fetcher:
            async with asyncio.TaskGroup() as group:
                for profile in profiles:
                    group.create_task(
                        self._scan_site(profile, searches, generation, fetcher, cache),
                        name=f"scan:{profile['id']}",
                    )

    async def _scan_site(
        self,
        profile: dict[str, Any],
        searches: list[_Search],
        generation: int,
        fetcher: Fetcher,
        cache: dict[CacheKey, VariantsRead],
    ) -> None:
        """Scan one site for every perfume of this search, one at a time.

        Serial inside the site, and one of these per site. A site's requests are
        paced from one place per call, so running its perfumes side by side would
        put every gap in parallel and hand a small shop the burst the pacing
        exists to prevent.

        Nothing raises out of here. These run in a TaskGroup, where one escaping
        exception cancels every other site, which is the opposite of what a
        results table filling in site by site is for.
        """
        for search in searches:
            # Checked before each perfume, not once at the top. A search that has
            # been replaced would otherwise go on spending requests on every
            # remaining perfume before noticing.
            if generation != self._generation:
                return
            try:
                result = await self.runner(
                    profile,
                    search.text,
                    fetcher=fetcher,
                    keep_candidate=_listing_filter(search.query),
                    variants_cache=cache,
                )
            except Exception as e:
                result = SiteResult(
                    str(profile["id"]), "error", (), f"{type(e).__name__}: {e}"
                )
            if generation != self._generation:
                return
            try:
                rows = snapshot_rows(result, search.query)
            except Exception:
                logger.exception("%s — sonuç okunamadı", profile["id"])
                self._errors += 1
                self._done += 1
                self._update_status()
                continue
            # The screen is updated before the database is touched. The table
            # needs nothing from sqlite, so a write that fails must not be able
            # to hide a site that answered, or leave the footer counter stuck
            # below the total with no sign of why.
            self._apply_result(profile, search, result, rows)
            try:
                async with self._write_lock:
                    await asyncio.to_thread(self._write_snapshots, rows)
            except Exception:
                if generation != self._generation:
                    return
                logger.exception("%s — fiyatlar kaydedilemedi", result.site_id)
                self._errors += 1
                self._update_status()

    def _write_snapshots(self, rows: list[SnapshotRow]) -> None:
        conn = connect(self.db_path)
        try:
            write_snapshots(conn, rows)
        finally:
            conn.close()

    def _apply_result(
        self,
        profile: dict[str, Any],
        search: _Search,
        result: SiteResult,
        rows: list[SnapshotRow],
    ) -> None:
        self._done += 1
        site_label = self._site_label(profile)
        # Which perfume a line is about, when there is more than one in flight.
        # "site-a — eşleşme bulunamadı" three times over says nothing about which
        # of the three searches it failed.
        about = f"{result.site_id} · {search.text}" if self._multi else result.site_id
        if result.status in ("ok", "empty"):
            if rows:
                self._rows.extend(self._to_result_rows(site_label, search, rows))
            else:
                self._note(f"{about} — eşleşme bulunamadı")
        elif result.status == "suspect":
            self._errors += 1
            logger.error(
                "%s — profil bozulmuş olabilir: %s", about, self._detail(result)
            )
        else:  # error
            self._errors += 1
            logger.error("%s — bağlantı hatası: %s", about, self._detail(result))
        self._refresh_table()
        self._set_notices()
        self._update_status()

    def _note(self, message: str) -> None:
        # A site that fails on every perfume of a search would otherwise print
        # the same line once per perfume, and ten of those bury the sites that
        # did answer.
        if message not in self._notices:
            self._notices.append(message)
        self._set_notices()

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
    def _to_result_rows(
        site_label: str, search: _Search, rows: list[SnapshotRow]
    ) -> list[_ResultRow]:
        return [
            _ResultRow(
                site_id=row.site_id,
                site_label=site_label,
                query_index=search.index,
                query_label=search.text,
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
                clone_of=row.clone_of,
            )
            for row in rows
        ]

    # -- table: rebuilt on every change, small enough not to matter ----------

    def _reset_table(self) -> None:
        """Empty the table and give it the columns this search needs.

        The perfume column only exists when there is more than one perfume to
        tell apart. On the ordinary single search it would repeat the same words
        down the screen and take the width from the product titles, which are
        what a person actually reads.
        """
        table = self.query_one("#results", DataTable)
        table.clear(columns=True)
        table.add_columns(*self._columns())
        self._visible_rows = []
        self._hidden_count = 0

    def _columns(self) -> tuple[str, ...]:
        if self._multi:
            return ("Parfüm", *_BASE_COLUMNS)
        return _BASE_COLUMNS

    @property
    def _multi(self) -> bool:
        return len(self._searches) > 1

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
        # Counted, so the status line can say why a site that answered left no
        # rows behind. Without it a search where everything is out of stock
        # looks identical to one where nothing matched.
        self._hidden_count = len(self._rows) - len(visible)
        visible.sort(key=self._sort_value)
        self._visible_rows = visible
        table.clear()
        for row in visible:
            table.add_row(*self._cells(row))
        if selected is not None and selected in visible:
            table.move_cursor(row=visible.index(selected))

    def _sort_value(self, row: _ResultRow) -> tuple[int, bool, Decimal]:
        # The perfume comes first, always. Sorting three perfumes into one ₺/ml
        # list interleaves them, and a table where consecutive rows are different
        # bottles cannot be read as a comparison of anything.
        return (row.query_index, *self._within_query(row))

    def _within_query(self, row: _ResultRow) -> tuple[bool, Decimal]:
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

    def _cells(self, row: _ResultRow) -> tuple[object, ...]:
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
        title = row.raw_title
        if row.clone_of:
            title = f"{title}  KLON ← {row.clone_of}"
        site_style = _SITE_STYLES.get(row.site_id)
        site: object = (
            Text(row.site_label, style=site_style)
            if site_style is not None
            else row.site_label
        )
        score = str(row.match_score)
        return (
            # The perfume column is left plain even on a weak match: it repeats
            # what was typed, and the doubt is about the site's title, not it.
            *((row.query_label,) if self._multi else ()),
            site,
            title if row.confident else Text(title, style=_LOW_CONFIDENCE_STYLE),
            ml,
            price,
            per_ml,
            stock,
            score if row.confident else Text(score, style=_LOW_CONFIDENCE_STYLE),
        )

    def _set_notices(self) -> None:
        lines = [self._limit_notice] if self._limit_notice else []
        lines += self._notices
        self.query_one("#notices", Static).update("\n".join(lines))

    def _update_status(self) -> None:
        # "tarama", not "site": with several perfumes the total is one scan per
        # site per perfume, and calling that a site count says a scan of six
        # shops did eighteen of them.
        text = f"{self._done}/{self._total} tarama tamam"
        if self._errors:
            # The count is the only thing on screen about a failing site now, so
            # it says where the detail went.
            text += f" · {self._errors} hata ({LOG_FILE_NAME})"
        if self._hidden_count:
            text += rf" · {self._hidden_count} stoksuz sonuç gizlendi (\[f] göster)"
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
        self._update_status()

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
        if row.clone_of:
            self._notices = [
                f"⚠ {row.raw_title} bir klon, aradığınız parfüm değil "
                f"({row.clone_of}) — sepete eklenmedi."
            ]
            self._set_notices()
            return
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
        panel.update(self._history_text(row, rows))
        panel.display = True

    @staticmethod
    def _history_text(row: _ResultRow, rows: list[sqlite3.Row]) -> str:
        # Named up front: a panel left open while the cursor moves to another
        # row would otherwise show the old site/title's history under a new
        # selection with nothing to say it is stale.
        lines = [row.site_label, row.raw_title]
        if not rows:
            lines.append("")
            lines.append("fiyat geçmişi yok")
            return "\n".join(lines)
        lines.append("")
        prices = [
            Decimal(r["price_kurus"]) / Decimal(100)
            if r["price_kurus"] is not None
            else None
            for r in rows
        ]
        for i, r in enumerate(rows):
            price = prices[i]
            price_text = format_price(price) if price is not None else "-"
            # rows are newest first, so the reading before this one (older) is
            # the next entry. The last row in the list has none before it.
            older = prices[i + 1] if i + 1 < len(prices) else None
            if i == len(rows) - 1:
                delta = ""
            elif price is None or older is None:
                delta = "?"
            else:
                diff = price - older
                if diff > 0:
                    delta = f"▲ +{format_price(diff)}"
                elif diff < 0:
                    delta = f"▼ {format_price(diff)}"
                else:
                    delta = "="
            line = f"{r['fetched_at'][:10]}  {price_text}  {delta}"
            # A price read while the size was out of stock is not one anyone
            # could actually pay, so it is marked rather than shown as plain.
            if not r["in_stock"]:
                line += "  (stokta yoktu)"
            lines.append(line)
        # Out-of-stock readings are left out of the range for the same reason
        # their own line is marked: nobody could have paid that price, and a
        # range built on one would answer "is today cheap" against a number
        # that was never on offer.
        buyable = [
            price
            for price, r in zip(prices, rows, strict=True)
            if price is not None and r["in_stock"]
        ]
        if buyable:
            lines.append("")
            lines.append(
                f"min {format_price(min(buyable))} · max {format_price(max(buyable))} "
                f"· {len(buyable)}/{len(rows)} okuma stoktaydı"
            )
        return "\n".join(lines)

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
