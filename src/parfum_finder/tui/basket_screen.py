"""The basket screen: the shopping list, a scenario per site, and the best split.

The real decision is almost always between one full-coverage shop and splitting
the order, so those two blocks are what the screen opens on. Every other
scenario, including the partial ones, sits behind [t] and lands at the bottom
when it is opened. A partial site is tagged, e.g. "4/5 items", and never
compared directly against a full-coverage total. Each scenario shows how much
more is needed to unlock free shipping. The split-across-sites result is always
labeled as the best combination found, not the mathematically cheapest.
"""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Callable, Sequence
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
    Prices,
    SiteScenario,
    SplitLeg,
    SplitPlan,
    basket_inputs,
    build_basket_rows,
    compare_split_to_best_full,
    optimize,
    single_site_scenarios,
)
from parfum_finder.engine import SiteRunner
from parfum_finder.normalize import format_age, format_ml, format_price
from parfum_finder.profiles import load_site_profile
from parfum_finder.services.scan import (
    BasketPriceExcluded,
    BasketRefreshEvent,
    BasketRefreshStarted,
    BasketRowFinished,
    BasketWriteFailed,
    run_basket_refresh,
)
from parfum_finder.store import (
    DEFAULT_DB_PATH,
    STALE_PRICE_DAYS,
    BasketLine,
    BasketPrice,
    BasketSite,
    basket_lines,
    basket_prices,
    basket_sites,
    connect,
    remove_basket_item,
    set_basket_qty,
)
from parfum_finder.validate import DEFAULT_SITES_DIR
from parfum_finder.viewmodels import BasketRow

# One edit to the basket, handed to the worker that owns the write lock so the
# three key bindings do not each need their own copy of the connect/close dance.
_Change = Callable[[sqlite3.Connection], None]

# Soft dusty red for the stale age cell. Plain "red" shouts louder than an old
# price deserves, and it is an alarm colour the rest of the screen does not use.
# This hex is xterm colour 174 exactly, so a terminal without truecolor gets the
# same tone instead of a nearest guess.
STALE_PRICE_STYLE = "bold #d78787"

_EMPTY = "—"

# Everything _render_scenarios needs, exactly as _render_all scored it.
_Scored = tuple[
    BasketReport,
    SplitPlan | None,
    list[BasketItem],
    Prices,
]


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
        ("t", "toggle_scenarios", "tüm senaryolar"),
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
        self._rows: list[BasketRow] = []
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
        # Off means the scenario area shows the cheapest full-coverage site and
        # the split plan only. That is the comparison the user is actually
        # making; the runner-up shops and the partial ones are reference, not
        # the decision, and burying the split under six near-identical blocks
        # is what made the screen hard to read.
        self._show_all_scenarios = False
        # What the last _render_all() scored, so toggling [t] can repaint from
        # it. optimize() is the expensive call on this screen and a keypress
        # that only changes how much of the answer is on screen has no business
        # asking for the answer again.
        self._scored: _Scored | None = None

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
        self._rows = build_basket_rows(lines, prices, self._excluded)
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

    # -- rendering ------------------------------------------------------------

    def _render_all(self) -> None:
        self._render_table()
        items, prices, shipping = basket_inputs(self._rows, self._sites)
        report = single_site_scenarios(items, prices, shipping)
        # optimize() is only worth asking on a basket that has rows: an empty
        # basket has nothing to split, and this also keeps an empty screen from
        # depending on optimize() at all.
        plan = optimize(items, prices, shipping) if self._rows else None
        self._scored = (report, plan, items, prices)
        self._render_notices(report)
        self._render_scenarios(report, plan, items, prices)
        self._update_status()

    def _render_table(self) -> None:
        table = self.query_one("#basket", DataTable)
        selected = self._selected_row()
        table.clear(columns=True)
        table.add_columns(
            "Parfüm", "ml", "Adet", *(site.name for site in self._sites), "Güncellik"
        )
        for row in self._rows:
            table.add_row(*self._cells(row))
        if selected is not None:
            ids = [r.line.basket_item_id for r in self._rows]
            if selected.line.basket_item_id in ids:
                table.move_cursor(row=ids.index(selected.line.basket_item_id))

    def _cells(self, row: BasketRow) -> tuple[object, ...]:
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
            cells.append(Text(age, style=STALE_PRICE_STYLE))
        else:
            cells.append(age)
        return tuple(cells)

    def _render_notices(self, report: BasketReport) -> None:
        notices = list(self._notices)
        if not self._rows:
            notices.append(r"Sepet boş. Arama ekranından \[a] ile ürün ekleyin.")
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
                    r"\[r] ile tazeleyin"
                )
        self.query_one("#basket-notices", Static).update("\n".join(notices))

    def _render_scenarios(
        self,
        report: BasketReport,
        plan: SplitPlan | None,
        items: Sequence[BasketItem],
        prices: Prices,
    ) -> None:
        # With no full-coverage site there is no cheapest-shop-versus-split
        # decision to open on, and the notice above the table sends the reader
        # to the partial scenarios by name. Collapsing them would point that
        # notice at nothing, so this case is always open.
        expanded = self._show_all_scenarios or not report.full
        # How many blocks the toggle governs. Zero means one full site and no
        # partials, so there is nothing to fold away and no hint to print.
        hideable = len(report.full[1:]) + len(report.partial) if report.full else 0
        lines: list[str] = []
        if report.full:
            shown = report.full if expanded else report.full[:1]
            lines.extend(_heading("TEK SİTE — TAM KAPSAMLI"))
            for scenario in shown:
                lines.extend(_scenario_block(scenario, "✓"))
        if plan is not None:
            lines.extend(_split_block(plan, report, items, prices))
        # Partials last: their totals are cheap for the wrong reason, and the
        # further they sit from the numbers they cannot be compared against,
        # the less often they get compared against them anyway.
        if expanded and report.partial:
            lines.extend(
                _heading("KISMİ — TAM KAPSAMLILARLA DOĞRUDAN KIYASLANAMAZ", mark="⚠ ")
            )
            for scenario in report.partial:
                lines.extend(_scenario_block(scenario, "⚠"))
        lines.extend(_toggle_hint(hideable, expanded=expanded))
        self.query_one("#scenarios", Static).update("\n".join(lines).strip("\n"))

    def _update_status(self) -> None:
        if self._refreshing:
            text = f"{self._scanned}/{self._scans} tarama tamam"
        else:
            text = f"Sepet ({len(self._rows)} ürün)"
        self.query_one("#basket-status", Static).update(text)

    def _selected_row(self) -> BasketRow | None:
        table = self.query_one("#basket", DataTable)
        index = table.cursor_row
        if not (0 <= index < len(self._rows)):
            return None
        return self._rows[index]

    # -- keys -----------------------------------------------------------------

    def action_toggle_scenarios(self) -> None:
        self._show_all_scenarios = not self._show_all_scenarios
        if self._scored is not None:
            self._render_scenarios(*self._scored)

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
        self._scans = 0
        self._update_status()
        try:
            async for event in run_basket_refresh(
                rows,
                profiles,
                runner=self.runner,
                db_path=self.db_path,
                write_lock=self._write_lock,
            ):
                self._apply_refresh_event(event)
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

    def _apply_refresh_event(self, event: BasketRefreshEvent) -> None:
        if isinstance(event, BasketRefreshStarted):
            self._scans = event.total
            self._update_status()
        elif isinstance(event, BasketPriceExcluded):
            self._excluded.add((event.site_id, event.basket_item_id))
            if event.notice is not None:
                self._note(event.notice)
        elif isinstance(event, BasketWriteFailed):
            self._note(event.notice)
        elif isinstance(event, BasketRowFinished):
            self._scanned += 1
            self._update_status()
        # BasketRefreshFinished carries nothing this screen paints.

    def _note(self, message: str) -> None:
        # A site that fails on every perfume in the basket would otherwise print
        # the same line once per row.
        if message not in self._notices:
            self._notices.append(message)


def _remove(basket_item_id: int) -> _Change:
    def change(conn: sqlite3.Connection) -> None:
        remove_basket_item(conn, basket_item_id=basket_item_id)

    return change


def _set_qty(basket_item_id: int, qty: int) -> _Change:
    def change(conn: sqlite3.Connection) -> None:
        set_basket_qty(conn, basket_item_id=basket_item_id, qty=qty)

    return change


def _heading(text: str, *, mark: str = "") -> list[str]:
    """A block title plus the blank line that keeps it off the block above it.

    The three blocks used to run together as one wall of numbers. Bold plus a
    gap is what separates them, so every heading goes through here rather than
    each caller remembering to pad its own.
    """
    return ["", f"[bold]{mark}{text}[/bold]", ""]


def _toggle_hint(hideable: int, *, expanded: bool) -> list[str]:
    """The one line that says the screen is holding something back, or is not."""
    if hideable == 0:
        return []
    if expanded:
        return ["", r"\[t] diğer senaryoları gizle"]
    return ["", rf"\[t] {hideable} senaryo daha göster"]


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


def _leg_block(
    leg: SplitLeg,
    items: Sequence[BasketItem],
    prices: Prices,
    *,
    is_split: bool,
) -> list[str]:
    """One site's share of a split: its assigned items, then its own subtotal.

    A single-leg plan is a single-site scenario restated, not a split, so it is
    marked plainly instead of being dressed up as a recommendation to divide
    the order across sites when there is nothing being divided.
    """
    tag = "" if is_split else "  (tek site — bölünmüyor)"
    lines = [f"  {leg.scenario.name}{tag}"]
    by_id = {item.item_id: item for item in items}
    for item_id in leg.item_ids:
        price = prices.get((item_id, leg.scenario.site_id))
        price_str = (
            _EMPTY if price is None else format_price(Decimal(price) / Decimal(100))
        )
        lines.append(f"    {by_id[item_id].label}   {price_str}")
    subtotal = format_price(Decimal(leg.scenario.subtotal_kurus) / Decimal(100))
    shipping = format_price(Decimal(leg.scenario.shipping_kurus) / Decimal(100))
    lines.append(f"    {subtotal} + {shipping} kargo")
    return lines


def _split_block(
    plan: SplitPlan,
    report: BasketReport,
    items: Sequence[BasketItem],
    prices: Prices,
) -> list[str]:
    """The best-combination block: its legs, grand total, and its honesty checks."""
    # The caveat is worded as advice, not as a disclaimer. "matematiksel optimal
    # degildir" was true but told the reader nothing they could act on; what they
    # actually need to know is that the other scenarios are still worth a look.
    lines = [
        *_heading("EN İYİ BULUNAN KOMBİNASYON"),
        "Aramanın bulduğu en ucuz dağılım; daha ucuzu olabilir, "
        "aşağıdaki seçeneklere de bakın.",
        "",
    ]
    is_split = len(plan.legs) > 1
    for leg in plan.legs:
        lines.extend(_leg_block(leg, items, prices, is_split=is_split))
    total = format_price(Decimal(plan.total_kurus) / Decimal(100))
    lines.append(f"GENEL TOPLAM {total}")
    verdict = compare_split_to_best_full(plan, report)
    if verdict.best_full is not None and verdict.diff_kurus is not None:
        best_total = format_price(Decimal(verdict.best_full.total_kurus) / Decimal(100))
        lines.append(
            f"ⓘ En iyi tam kapsamlı tek site ({verdict.best_full.name}) {best_total}"
        )
        if verdict.diff_kurus < 0:
            cheaper = format_price(Decimal(-verdict.diff_kurus) / Decimal(100))
            lines.append(f"→ bölmek {cheaper} DAHA UCUZ")
        elif verdict.diff_kurus > 0:
            costlier = format_price(Decimal(verdict.diff_kurus) / Decimal(100))
            lines.append(f"→ bölmek {costlier} DAHA PAHALI")
        else:
            lines.append("→ bölmek bir fark yaratmıyor")
    else:
        lines.append("ⓘ Tam kapsamlı tek site yok — karşılaştırma yapılamıyor")
    if plan.omitted_sites:
        names = ", ".join(plan.omitted_sites)
        lines.append(
            f"ⓘ {len(plan.omitted_sites)} site kombinasyon aramasına dahil "
            f"edilmedi: {names}"
        )
    lines.append("")
    return lines
