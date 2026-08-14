"""The search screen: a progress bar while scanning, one grouped table after.

A perfume that has been searched before is answered from the price history
instead of from the shops. Every scan already writes what it read, so the second
search for the same bottle has a price on record for every site that carried it,
and spending another round of requests to confirm it is the cost this avoids.
Those rows carry their reading's age in the "Güncellik" column and [r] is what
asks the shops again. A perfume with nothing on record is scanned as before, so
a first search never needs a keypress to produce prices.

Columns: the site's own title (as "Ürün"), site, size (ml), price, price per
ml, match score, freshness. Nothing lands in the table mid-scan. Sites finish
in whatever order they finish, and a table growing under a reader's eyes cannot
be read: the cheapest row so far keeps changing, and the row someone is looking
at keeps moving. So the scan shows a progress bar in the table's place and the
table fills in one go at the end, already grouped and ordered.

The error count next to the bar stays live. With the table empty and the
details in the log file, it is the only sign that a scan is going wrong while
it is still going.

One line may ask for several perfumes, separated by " - ". They are scanned in
one pass, still one task per site, with that site's perfumes going one after
the other inside it: a site's requests are paced from one place, so starting a
shop's whole list at once would hand it the burst the pacing exists to prevent.

The finished table is ordered in four layers: the order the perfumes were typed
in, then the product each row is actually about, then the site, then the size.
The first layer never appears on screen -- what was typed is what the person
already knows -- it only keeps the blocks in the order they asked for them.

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
from typing import TYPE_CHECKING, Any, Protocol

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Input, ProgressBar, Static

from parfum_finder.engine import CacheKey, CandidateFilter, SiteResult, VariantsRead
from parfum_finder.fetch import Fetcher, browser_session
from parfum_finder.logging_setup import LOG_FILE_NAME, logger
from parfum_finder.matcher import (
    DEFAULT_THRESHOLD,
    MAX_QUERIES,
    PerfumeQuery,
    parse_query,
    product_label,
    split_queries,
    title_could_match,
)
from parfum_finder.normalize import format_ml, format_price
from parfum_finder.profiles import load_site_profile, sync_to_db
from parfum_finder.sheets import (
    SheetsError,
    WishlistRow,
    find_header_columns,
    find_match,
    open_worksheet,
    read_sheet,
    write_result,
)
from parfum_finder.store import (
    DEFAULT_DB_PATH,
    CachedPrice,
    SnapshotRow,
    add_basket_item,
    basket_lines,
    cached_prices,
    connect,
    now_iso,
    price_history,
    snapshot_rows,
    write_snapshots,
)
from parfum_finder.tui.basket_screen import (
    STALE_PRICE_DAYS,
    STALE_PRICE_STYLE,
    BasketScreen,
    format_age,
    snapshot_age_days,
)
from parfum_finder.validate import (
    DEFAULT_SITES_DIR,
    STALE_PROFILE_DAYS,
    profile_age_days,
)

if TYPE_CHECKING:
    import gspread


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
# the size column.
_SORT_BY_COLUMN = {0: "ml", 1: "price", 2: "per_ml"}

# "Ürün" is the site's own title, untouched -- it is what makes a wrong match
# visible, and it is what tells apart two bottles a single search can turn up,
# such as "Layton" and "Layton Exclusif". The product a row is really about is
# still derived from it for grouping and sorting, it just no longer gets a
# column of its own next to this one.
#
# No "Stok" column: out-of-stock sizes are already hidden by default, so a
# column repeating that on every visible row added little. row.in_stock stays
# on _ResultRow, since the hide/show filter still needs it.
#
# "Güncellik" is last, after the sortable block, because _FIRST_SORTABLE and the
# header-click offsets are counted from "ml" and a column inserted before it
# would silently move what a header click sorts by. It reads the same as the
# basket's column of that name: a row served from storage says how old it is,
# and a row that was just scanned says "bugün".
_COLUMNS = ("Ürün", "Site", "ml", "Fiyat", "₺/ml", "%", "Güncellik")

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
    "splitcim": "#a3c46b",
    "venco": "#5fb3b3",
}

# What a low match score is marked with. Only the site's own title and the
# score itself carry it: those two are the doubtful part. The price, size and
# stock of that listing were read correctly whatever the score says, and
# painting them made a whole row look untrustworthy over one weak title.
_LOW_CONFIDENCE_STYLE = "#cf9145"

# A row already in the basket. This one paints the whole row, unlike the other
# two styles: what it says is not about one cell, it is that this size of this
# perfume is already picked and does not need deciding again. The site colour
# and the low-confidence orange give way underneath it, which is the cost of
# being able to see the picked rows while scrolling past the rest.
_IN_BASKET_STYLE = "#4fbf7a"

# Where the sortable columns start.
_FIRST_SORTABLE = _COLUMNS.index("ml")

# The sizes a decant buyer actually chooses between. Site blocks are ordered by
# the cheapest ₺/ml a site offers inside this band, so a shop whose smallest
# bottle is 10 ml cannot take the top of the list on the structural ₺/ml
# advantage a bigger bottle always has.
_BAND_MAX_ML_X10 = 30

# Where a site with nothing in the band goes: after every site that has one,
# ordered among themselves by their own cheapest ₺/ml. Comparing a 10 ml-only
# shop against the band would be comparing two different purchases.
_OUT_OF_BAND = 1

# And where a site whose every price failed to read goes: last, since there is
# no number to place it by at all.
_UNPRICED: tuple[int, Decimal] = (2, Decimal(0))


def _listing_filter(query: PerfumeQuery) -> CandidateFilter:
    """Decide, from a search result's own title, whether to open its page."""

    def keep(raw_title: str | None) -> bool:
        return title_could_match(raw_title, query)

    return keep


@dataclass(frozen=True)
class _Search:
    """One perfume of a search, as typed and as parsed.

    The index is the outermost sort key of the results table and the only part
    of the typed line that survives into it. Three perfumes sorted into one ₺/ml
    list interleave into something nobody can read, so the order they were asked
    for is what the blocks come out in. The blocks themselves are headed by the
    product each row is about, not by this.
    """

    index: int
    text: str
    query: PerfumeQuery


@dataclass(frozen=True)
class _ResultRow:
    """One priced size, exactly as the table shows it and as a keypress needs it.

    `product` is what the site's own title reduces to, and it is both the block
    heading and the second sort layer. It is not the search text: a search for
    "Parfums de Marly Layton" also finds "Layton Exclusif", and those two are
    different bottles that must not share a block.

    `age_days` is how old the reading behind the row is. It defaults to 0, which
    is what a row this scan just fetched is, so only the rows repainted from
    storage have to fill it in.
    """

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
    product: str = ""
    clone_of: str = ""
    own_identity: bool = True
    age_days: int = 0

    @property
    def price_per_ml_kurus(self) -> Decimal | None:
        # Decimal, not floor division: latest_prices computes this as a real
        # division too, and truncating to an int here would round two rows
        # that actually differ into a tie and quietly change the sort order.
        if self.price_kurus is None:
            return None
        return Decimal(self.price_kurus * 10) / Decimal(self.size_ml_x10)


def _cached_result_row(
    price: CachedPrice, site_label: str, search: _Search
) -> _ResultRow:
    """Turn one stored price back into the row the table shows.

    Everything the table paints is either stored or derived from the stored
    title, with two exceptions. `clone_of` is empty and `own_identity` is True,
    which is the truth rather than a default standing in for one: a clone is
    filed under its own house and name, so it never comes back from a search for
    the perfume it imitates.
    """
    return _ResultRow(
        site_id=price.site_id,
        site_label=site_label,
        query_index=search.index,
        product=product_label(price.raw_title) or price.raw_title,
        raw_title=price.raw_title,
        size_ml_x10=price.size_ml_x10,
        price_kurus=price.price_kurus,
        in_stock=price.in_stock,
        match_score=price.match_score,
        confident=price.match_score >= DEFAULT_THRESHOLD,
        brand=price.brand,
        name=price.name,
        concentration=price.concentration,
        product_url=price.product_url,
        age_days=snapshot_age_days(price.fetched_at),
    )


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
    SearchScreen #progress {
        padding: 0 1;
        display: none;
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
        ("r", "refresh", "tazele"),
        ("h", "show_history", "fiyat geçmişi"),
        ("a", "add_basket", "sepete ekle"),
        ("w", "write_sheet", "sheet'e yaz"),
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
        sheets_credentials: Path | None = None,
        sheets_spreadsheet: str | None = None,
        sheets_worksheet: str | None = None,
    ) -> None:
        super().__init__()
        self.sites_dir = sites_dir
        self.db_path = db_path
        self.runner = runner
        self.sheets_credentials = sheets_credentials
        self.sheets_spreadsheet = sheets_spreadsheet
        self.sheets_worksheet = sheets_worksheet
        self._profiles: list[dict[str, Any]] = []
        self._bootstrapped = asyncio.Event()
        # What the current results are about. Empty until the first search, and
        # what decides whether the table needs a perfume column at all.
        self._searches: list[_Search] = []
        self._limit_notice = ""
        self._rows: list[_ResultRow] = []
        self._visible_rows: list[_ResultRow] = []
        # Which perfume/size pairs are in the basket, by the same four fields the
        # basket itself is keyed on. Site is not among them on purpose: a basket
        # line is a bottle to buy, not a shop to buy it from, so every site's row
        # for that size is marked and picking between them is still open.
        self._basket_keys: set[tuple[str, str, str, int]] = set()
        # One writer at a time. Every site worker opens its own connection and
        # store.connect() runs the schema script inside a write transaction, so
        # two sites landing together can collide on a locked database. Taking
        # turns costs a few milliseconds and is cheaper than losing a site's
        # prices to a lock error.
        self._write_lock = asyncio.Lock()
        self._notices: list[str] = []
        # None is the grouped default: product blocks, sites inside them ordered
        # by what they charge in the small-bottle band, sizes ascending. The
        # number keys replace the site and size layers with one column of their
        # own; the product blocks survive either way, since a table alternating
        # between two different bottles compares nothing.
        self._sort_key: str | None = None
        # Hidden from the start, and there is no key left to bring them back:
        # a size that cannot be bought is not an offer, and leaving them in put
        # the cheapest unbuyable price at the top of a table sorted by ₺/ml,
        # which is the one number people read first. They are still fetched
        # and still stored, and the price history panel goes on counting them.
        self._hide_out_of_stock = True
        self._hidden_count = 0
        self._done = 0
        self._total = 0
        self._errors = 0
        self._generation = 0
        self._scanning = False

    def compose(self) -> ComposeResult:
        yield Input(placeholder="örn. Dior Sauvage EDP", id="query")
        with Horizontal(id="body"):
            with Vertical(id="main-col"):
                yield DataTable(id="results", cursor_type="row")
                # Sits where the rows will be, and only while there are none.
                # The status line stays next to it rather than being replaced by
                # it: the bar says how far along the scan is, the status line
                # says whether it is going well.
                yield ProgressBar(id="progress", show_eta=False)
                yield Static("", id="notices")
                yield Static("", id="status")
            yield Static("", id="history-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#results", DataTable).add_columns(*self._columns())
        self._bootstrap()
        # Read once at mount: the basket outlives the app, so a search run after
        # a restart still has to come up with its picked rows painted.
        self._reload_basket()

    def on_screen_resume(self) -> None:
        # Coming back from the basket, where lines can be removed and quantities
        # changed. Hooked here and not on the push_screen callback because the
        # basket leaves with pop_screen, which never runs that callback, and the
        # rows would stay painted for a bottle no longer in the basket.
        self._reload_basket()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # DataTable already binds "enter" to select the cursor's row and
        # posts this message; opening the browser hooks into that instead of
        # a second "enter" binding on the screen, which a focused table would
        # never let bubble up to anyway.
        event.stop()
        self.action_open_url()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        event.stop()
        key = _SORT_BY_COLUMN.get(event.column_index - _FIRST_SORTABLE)
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
            self._end_empty_search(rejected)
            return
        await self._bootstrapped.wait()
        # Storage is asked before any shop is. A perfume that has been searched
        # before already has a price on record for every site that carried it,
        # and spending a full round of requests to find out it is still 540 TL is
        # the cost this exists to skip. [r] is what asks the shops again.
        try:
            cached = await asyncio.to_thread(self._read_cache, searches)
        except Exception:
            # Falling back to a live scan, which is what this screen did before
            # there was a record to read. An exception escaping here would kill
            # the worker and leave the user with no table at all, and a slow
            # answer beats none.
            logger.exception("kayıttaki fiyatlar okunamadı")
            cached = []
        answered = {row.query_index for row in cached}
        # Per perfume, not per search line. Two perfumes typed together where one
        # has been seen before and the other has not should cost one perfume's
        # worth of requests, not two.
        to_scan = [s for s in searches if s.index not in answered]
        await self._scan(searches, rejected, cached, to_scan)

    def action_refresh(self) -> None:
        # Nothing to refresh before the first search, and a second [r] mid-scan
        # would cancel the scan it was meant to be waiting for.
        if self._searches and not self._scanning:
            self._refresh_prices()

    @work(exclusive=True, group="scan-setup")
    async def _refresh_prices(self) -> None:
        searches = list(self._searches)
        await self._bootstrapped.wait()
        # Every perfume goes to the shops, cache or no cache: [r] means "ask
        # again", and refreshing only the rows that happened to be old would
        # leave the table a mix of two different moments.
        await self._scan(searches, [], [], searches)

    def _end_empty_search(self, rejected: list[str]) -> None:
        """Close out a submit that named no perfume anyone could look for."""
        # This worker already cancelled whatever scan was running, and it is
        # not starting one of its own, so nobody else is left to lower the
        # flag. Ending the scan here is what keeps a frozen bar and a stuck
        # counter off the screen. The generation bump goes with it, so the
        # late rows of the cancelled scan do not pile into _rows.
        self._generation += 1
        self._scanning = False
        self._done = 0
        self._total = 0
        self._errors = 0
        self._notices = rejected or ["a search needs a perfume to look for"]
        self._set_notices()
        self._update_status()

    async def _scan(
        self,
        searches: list[_Search],
        rejected: list[str],
        cached: list[_ResultRow],
        to_scan: list[_Search],
    ) -> None:
        """Show what storage already knows, then go to the shops for the rest.

        `cached` is already-built rows and `to_scan` is the perfumes storage had
        nothing for, so a run where the two are swapped in full is either a pure
        cache hit (nothing scanned) or a plain scan (nothing cached). Both are
        this one path, so the table is assembled the same way whichever it was.
        """
        self._generation += 1
        generation = self._generation
        self._searches = searches
        self._rows = list(cached)
        self._notices = rejected + self._cache_notices(searches, cached)
        self._done = 0
        self._errors = 0
        profiles = [p for p in self._profiles if p.get("enabled", True)]
        self._total = len(to_scan) * len(profiles)
        self._scanning = bool(to_scan)
        self._reset_table()
        self._set_notices()
        self._update_status()
        if to_scan:
            # One product read per URL for the whole scan. Two perfumes searched
            # at one shop routinely list the same product, and the second read
            # costs a request and a rate-limit wait to learn what is already
            # known.
            cache: dict[CacheKey, VariantsRead] = {}
            # The browser, if any site needs one, is started once and kept for
            # the whole scan instead of per page. Nothing is launched when no
            # profile asks for playwright.
            async with browser_session() as fetcher:
                async with asyncio.TaskGroup() as group:
                    for profile in profiles:
                        group.create_task(
                            self._scan_site(
                                profile, to_scan, generation, fetcher, cache
                            ),
                            name=f"scan:{profile['id']}",
                        )
        # The one place the table is filled. A newer search may have started
        # while this one was finishing, and painting these rows over its empty
        # table would put the answer to the old question under the new one.
        if generation != self._generation:
            return
        self._scanning = False
        self._refresh_table()
        self._update_status()

    def _cache_notices(
        self, searches: list[_Search], cached: list[_ResultRow]
    ) -> list[str]:
        """Say which perfumes came off the record instead of off the shops.

        Without this the table looks like a scan that finished impossibly fast,
        and the one thing a reader has to know about these rows is that pressing
        [r] is what turns them into today's prices.
        """
        answered = {row.query_index for row in cached}
        if not answered:
            return []
        if len(searches) == 1:
            return [r"kayıttan geldi — \[r] ile tazeleyin"]
        return [
            rf"{s.text} — kayıttan geldi, \[r] ile tazeleyin"
            for s in searches
            if s.index in answered
        ]

    def _read_cache(self, searches: list[_Search]) -> list[_ResultRow]:
        """Rebuild the table's rows for every searched perfume already on record.

        Sites whose profile is gone or switched off are dropped rather than shown
        under their bare id: the label comes from the profile, and a row nobody
        can refresh is not an offer this screen should be making.
        """
        labels = {
            str(profile["id"]): self._site_label(profile)
            for profile in self._profiles
            if profile.get("enabled", True)
        }
        conn = connect(self.db_path)
        try:
            rows: list[_ResultRow] = []
            for search in searches:
                for price in cached_prices(
                    conn,
                    brand=search.query.brand,
                    name=search.query.name,
                    concentration=search.query.concentration,
                ):
                    label = labels.get(price.site_id)
                    if label is None:
                        continue
                    rows.append(_cached_result_row(price, label, search))
            return rows
        finally:
            conn.close()

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
        # No table refresh here on purpose. Rows are collected all through the
        # scan and painted once at the end, so nothing moves under a reader.
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
                # The raw title stands in when there is nothing left to derive a
                # product name from. An empty block heading would be worse than
                # a messy one: it names nothing and merges every such row into
                # one block.
                product=product_label(row.variant.raw_title or "")
                or (row.variant.raw_title or ""),
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
                own_identity=row.own_identity,
            )
            for row in rows
        ]

    # -- table: rebuilt on every change, small enough not to matter ----------

    def _reset_table(self) -> None:
        """Empty the table for a new scan.

        The columns are the same every time now, so they are added once at mount
        and only the rows are cleared here.
        """
        table = self.query_one("#results", DataTable)
        table.clear()
        self._visible_rows = []
        self._hidden_count = 0

    def _columns(self) -> tuple[str, ...]:
        return _COLUMNS

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
        if self._sort_key is None:
            # Built from every row, not the visible ones, so that hiding and
            # showing the out-of-stock sizes cannot reshuffle the site blocks
            # under someone who was reading them.
            ranks = self._site_ranks()
            visible.sort(key=lambda row: self._grouped_value(row, ranks))
        else:
            visible.sort(key=self._sorted_value)
        self._visible_rows = visible
        table.clear()
        for row in visible:
            table.add_row(*self._cells(row))
        if selected is not None and selected in visible:
            table.move_cursor(row=visible.index(selected))
        # Last, not before: one of the notices is about what the filter above
        # just hid, so it can only be written once _visible_rows is what the
        # table actually holds.
        self._set_notices()

    def _site_ranks(self) -> dict[tuple[int, str, str], tuple[int, Decimal]]:
        """What each site charges for the product a block is about.

        One entry per site per product block, not per site: a shop that is
        cheapest on one bottle is not automatically cheapest on the next, and
        ranking it once for the whole scan would let its bargain on one perfume
        carry it to the top of a block where it is the dearest.

        Only rows whose price could be read count. A size with no price says
        nothing about what a shop charges, and letting it in would make the
        block order depend on which rows happen to be on screen.
        """
        band: dict[tuple[int, str, str], Decimal] = {}
        overall: dict[tuple[int, str, str], Decimal] = {}
        for row in self._rows:
            per_ml = row.price_per_ml_kurus
            if per_ml is None:
                continue
            key = (row.query_index, row.product, row.site_id)
            overall[key] = min(overall.get(key, per_ml), per_ml)
            if row.size_ml_x10 <= _BAND_MAX_ML_X10:
                band[key] = min(band.get(key, per_ml), per_ml)
        return {
            key: (0, band[key]) if key in band else (_OUT_OF_BAND, cheapest)
            for key, cheapest in overall.items()
        }

    def _grouped_value(
        self, row: _ResultRow, ranks: dict[tuple[int, str, str], tuple[int, Decimal]]
    ) -> tuple[int, str, int, Decimal, str, Decimal]:
        """The default order: typed order, product, site, size.

        The typed order comes first and is never shown. Sorting several perfumes
        into one ₺/ml list interleaves them, and a table where consecutive rows
        are different bottles cannot be read as a comparison of anything.

        Sizes go up inside a site's block, every block the same way, so the eye
        can move down a column instead of re-reading each one.
        """
        band, cheapest = ranks.get(
            (row.query_index, row.product, row.site_id), _UNPRICED
        )
        return (
            row.query_index,
            row.product,
            band,
            cheapest,
            row.site_label,
            Decimal(row.size_ml_x10),
        )

    def _sorted_value(self, row: _ResultRow) -> tuple[int, str, bool, Decimal]:
        """The order once a column has been picked: the site layer drops out.

        Asking for the cheapest ₺/ml and getting an answer still cut into site
        blocks is not an answer. The product blocks stay, for the same reason
        they always do.
        """
        return (row.query_index, row.product, *self._within_query(row))

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
        age = format_age(row.age_days)
        stale = row.age_days >= STALE_PRICE_DAYS
        # The stale marking outranks both row styles, unlike every other cell.
        # What it says is not decoration, it is that the number next to it is old
        # enough that the shop has had time to change it, and a row painted green
        # for being in the basket is exactly the row somebody is about to act on.
        age_cell: object = Text(age, style=STALE_PRICE_STYLE) if stale else age
        if self._basket_key(row) in self._basket_keys:
            return (
                *(
                    Text(cell, style=_IN_BASKET_STYLE)
                    for cell in (
                        title,
                        row.site_label,
                        ml,
                        price,
                        per_ml,
                        score,
                    )
                ),
                age_cell if stale else Text(age, style=_IN_BASKET_STYLE),
            )
        return (
            title if row.confident else Text(title, style=_LOW_CONFIDENCE_STYLE),
            site,
            ml,
            price,
            per_ml,
            score if row.confident else Text(score, style=_LOW_CONFIDENCE_STYLE),
            age_cell,
        )

    def _set_notices(self) -> None:
        lines = [self._limit_notice] if self._limit_notice else []
        lines += self._notices
        # Same warning the basket prints, for the same reason: the age column
        # says which row is old, and this is what makes sure nobody has to look
        # for it. A freshly scanned table never has a row old enough to trip it.
        if any(row.age_days >= STALE_PRICE_DAYS for row in self._rows):
            lines.append(
                f"⚠ Bazı fiyatlar {STALE_PRICE_DAYS} günden eski — "
                r"\[r] ile tazeleyin"
            )
        if self._rows and not self._visible_rows:
            # Rows were found and the stock filter hid every one of them, which
            # on screen looks exactly like a search that matched nothing. It
            # matters most on a table repainted from the record, where no site
            # was asked and so no "eşleşme bulunamadı" line was ever printed:
            # the answer is "everything is sold out", not "nobody sells it".
            lines.append(
                r"⚠ Bulunan bedenlerin tümü stok dışı — \[r] ile yeniden bakın"
            )
        self.query_one("#notices", Static).update("\n".join(lines))

    def _update_status(self) -> None:
        # "tarama", not "site": with several perfumes the total is one scan per
        # site per perfume, and calling that a site count says a scan of six
        # shops did eighteen of them.
        bar = self.query_one("#progress", ProgressBar)
        if self._total == 0:
            # Nothing has been scanned, so there is no progress to report. The
            # app looks like this on startup too, and now it does so by rule
            # rather than because nothing happened to call this yet.
            self.query_one("#status", Static).update("")
            bar.display = False
            return
        text = f"{self._done}/{self._total} tarama tamam"
        if self._errors:
            # The count is the only thing on screen about a failing site now, so
            # it says where the detail went.
            text += f" · {self._errors} hata ({LOG_FILE_NAME})"
        # _hidden_count stays tracked as infrastructure but is no longer shown
        # in the status line.
        self.query_one("#status", Static).update(text)
        # Driven from here rather than from its own call sites: every place the
        # counters move already calls this, and a bar updated from only some of
        # them would stall partway through a scan that is still running.
        bar.display = self._scanning
        if self._scanning:
            bar.update(total=self._total, progress=self._done)

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

    # Not on BINDINGS anymore, so no key reaches this. Left in place, along
    # with _hide_out_of_stock, as the plumbing a future key or setting could
    # still call.
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

    def action_write_sheet(self) -> None:
        row = self._selected_row()
        if row is None:
            return
        self._write_to_sheet(row)

    @work(exclusive=True, group="add-basket")
    async def _add_to_basket(self, row: _ResultRow) -> None:
        # push_screen(..., wait_for_dismiss=True) only works from inside a
        # worker, which is why the confirmation dialog and the write both
        # live in this @work method instead of directly in the action.
        if not row.own_identity:
            # Nothing to add it as. The title outside the parentheses was too
            # short to name a house and a perfume, so this bottle was never
            # stored, and the basket only ever holds perfumes that were.
            self._notices = [
                f"⚠ {row.raw_title} bir klon ve kendi adı okunamadı "
                f"({row.clone_of}) — sepete eklenemez."
            ]
            self._set_notices()
            return
        if row.clone_of:
            # Asked, not refused. A clone can be worth buying on purpose, and it
            # goes into the basket as itself rather than as the perfume it
            # imitates, so the only thing left to do is make sure whoever pressed
            # [a] knows which of the two they are buying.
            confirmed = await self.app.push_screen(
                ConfirmScreen(
                    f"{row.raw_title} bir klon, {row.clone_of} değil. "
                    "Kendi adıyla sepete eklensin mi?"
                ),
                wait_for_dismiss=True,
            )
            if not confirmed:
                return
        elif not row.confident:
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
        # Re-read rather than adding the key by hand: the write can bump an
        # existing line instead of making one, and the table has to end up
        # showing what the basket holds, not what this keypress meant to do.
        self._basket_keys = await asyncio.to_thread(self._read_basket_keys)
        self._refresh_table()

    @staticmethod
    def _basket_key(row: _ResultRow) -> tuple[str, str, str, int]:
        return (row.brand, row.name, row.concentration, row.size_ml_x10)

    @work(exclusive=True, group="basket-keys")
    async def _reload_basket(self) -> None:
        self._basket_keys = await asyncio.to_thread(self._read_basket_keys)
        self._refresh_table()

    def _read_basket_keys(self) -> set[tuple[str, str, str, int]]:
        conn = connect(self.db_path)
        try:
            return {
                (line.brand, line.name, line.concentration, line.size_ml_x10)
                for line in basket_lines(conn)
            }
        finally:
            conn.close()

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

    @work(exclusive=True, group="write-sheet")
    async def _write_to_sheet(self, row: _ResultRow) -> None:
        # Same reasoning as _add_to_basket: the confirmation dialog needs to
        # be awaited from inside a worker, so the whole flow lives here.
        sheets_configured = bool(
            self.sheets_credentials
            and self.sheets_spreadsheet
            and self.sheets_worksheet
        )
        if not sheets_configured:
            self._notices = [
                "⚠ Sheet entegrasyonu ayarlanmamış "
                "(--sheet-credentials/--sheet-id/--sheet-worksheet)."
            ]
            self._set_notices()
            return
        if row.price_kurus is None:
            self._notices = [f"⚠ {row.raw_title} için fiyat yok — sheet'e yazılamaz."]
            self._set_notices()
            return
        if row.age_days >= STALE_PRICE_DAYS:
            confirmed = await self.app.push_screen(
                ConfirmScreen(
                    f"{row.raw_title} fiyatı {format_age(row.age_days)} alındı. "
                    "Yine de sheet'e yazılsın mı?"
                ),
                wait_for_dismiss=True,
            )
            if not confirmed:
                return

        query = PerfumeQuery(
            brand=row.brand, name=row.name, concentration=row.concentration
        )
        try:
            ws, wishlist_rows, price_col, where_col = await asyncio.to_thread(
                self._read_wishlist
            )
        except SheetsError as exc:
            self._notices = [f"⚠ {exc}"]
            self._set_notices()
            return

        found = find_match(wishlist_rows, query)
        if found is None:
            self._notices = [
                f"⚠ {row.brand} {row.name} istek listenizde bulunamadı "
                "— sheet'e manuel ekleyin."
            ]
            self._set_notices()
            return
        matched_row, match = found
        if not match.confident:
            confirmed = await self.app.push_screen(
                ConfirmScreen(
                    f"'{matched_row.brand} {matched_row.model}' sheet satırı "
                    f"düşük eşleşme skoruyla (%{match.score}) bulundu. "
                    f"{row.raw_title} için buraya yazılsın mı?"
                ),
                wait_for_dismiss=True,
            )
            if not confirmed:
                return

        price_text = (
            f"{format_price(Decimal(row.price_kurus) / Decimal(100))} "
            f"({format_ml(Decimal(row.size_ml_x10) / Decimal(10))})"
        )
        try:
            await asyncio.to_thread(
                write_result,
                ws,
                matched_row.row_index,
                price_col,
                where_col,
                price_text,
                row.site_label,
                row.product_url,
            )
        except SheetsError as exc:
            self._notices = [f"⚠ {exc}"]
            self._set_notices()
            return

        self._notices = [
            f"✓ {matched_row.brand} {matched_row.model} → {price_text} "
            f"— {row.site_label} sheet'e yazıldı."
        ]
        self._set_notices()

    def _read_wishlist(
        self,
    ) -> tuple[gspread.Worksheet, list[WishlistRow], int, int]:
        # One blocking call: open the tab, read it in a single request, and
        # resolve the header columns up front, so a missing header is
        # reported before the match/confirm flow instead of after it.
        credentials = self.sheets_credentials
        spreadsheet = self.sheets_spreadsheet
        worksheet_name = self.sheets_worksheet
        assert credentials and spreadsheet and worksheet_name
        ws = open_worksheet(credentials, spreadsheet, worksheet_name)
        header_row, wishlist_rows = read_sheet(ws)
        price_col, where_col = find_header_columns(header_row)
        return ws, wishlist_rows, price_col, where_col

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
