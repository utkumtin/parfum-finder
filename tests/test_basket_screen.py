"""Tests for the basket screen: the matrix, the scenarios, and the key bindings.

The database is seeded through store's own writers rather than raw SQL, so a
test can only set up a state the scanner could actually produce. A fake runner
stands in for engine.run_site, so nothing here touches the network.
"""

import asyncio
import json
import sqlite3
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from textual.content import Content
from textual.widgets import DataTable, Static

from parfum_finder.basket import SiteScenario, SplitLeg, SplitPlan
from parfum_finder.engine import ProductCandidate, SearchHit, SiteResult, Variant
from parfum_finder.profiles import load_site_profile, sync_to_db
from parfum_finder.store import add_basket_item, connect, now_iso, record_snapshot
from parfum_finder.tui import basket_screen as basket_screen_module
from parfum_finder.tui.app import ParfumFinderApp
from parfum_finder.tui.basket_screen import (
    STALE_PRICE_STYLE,
    BasketScreen,
    format_age,
)
from parfum_finder.tui.search_screen import SearchScreen

# Keyword-tolerant: the search screen hands its runner a browser session and a
# listing filter too, and one runner is injected for both screens.
Runner = Callable[..., Awaitable[SiteResult]]

BRAND = "dior"
NAME = "sauvage"
CONC = "EDP"


def _write_profile(
    sites_dir: Path,
    site_id: str,
    name: str,
    *,
    threshold: int | None = None,
    shipping_cost: int = 0,
    notes: str | None = None,
    enabled: bool = True,
) -> None:
    sites_dir.mkdir(parents=True, exist_ok=True)
    shipping: dict[str, Any] = {
        "free_shipping_threshold_kurus": threshold,
        "shipping_cost_kurus": shipping_cost,
    }
    if notes is not None:
        shipping["notes"] = notes
    profile = {
        "schema_version": 1,
        "id": site_id,
        "name": name,
        "base_url": "https://example.com",
        "enabled": enabled,
        "platform": None,
        "strategy": "httpx",
        "extraction": "jsonld",
        "search": {
            "url_template": "{base_url}/search?q={query}",
            "result_item": ".card",
            "result_url": "a::attr(href)",
            "result_title": "a::text",
        },
        "variant_rules": {
            "size_from": "title",
            "size_pattern": r"(\d+) ?ml",
            "exclude_keywords": [],
            "max_size_ml": 30,
        },
        "shipping": shipping,
        "discovered_at": "2026-08-01T00:00:00Z",
        "needs_review": [],
    }
    (sites_dir / f"{site_id}.json").write_text(json.dumps(profile))


def _variant(ml_x10: int, price_kurus: int | None, *, in_stock: bool = True) -> Variant:
    return Variant(
        size_ml_x10=ml_x10,
        raw_title=f"Dior Sauvage EDP Dekant {ml_x10 / 10:g} ml",
        product_url=f"https://example.com/p?ml={ml_x10}",
        price_kurus=price_kurus,
        in_stock=in_stock,
    )


def _sync(sites_dir: Path, db_path: Path) -> None:
    conn = connect(db_path)
    try:
        profiles = [load_site_profile(p) for p in sorted(sites_dir.glob("*.json"))]
        sync_to_db(conn, profiles, synced_at=now_iso())
    finally:
        conn.close()


def _price(
    db_path: Path,
    site_id: str,
    variant: Variant,
    *,
    name: str = NAME,
    fetched_at: str | None = None,
) -> None:
    conn = connect(db_path)
    try:
        record_snapshot(
            conn,
            site_id=site_id,
            brand=BRAND,
            name=name,
            concentration=CONC,
            match_score=97,
            variant=variant,
            fetched_at=fetched_at,
        )
    finally:
        conn.close()


def _basket(db_path: Path, size_ml_x10: int, *, name: str = NAME, qty: int = 1) -> int:
    conn = connect(db_path)
    try:
        return add_basket_item(
            conn,
            brand=BRAND,
            name=name,
            concentration=CONC,
            size_ml_x10=size_ml_x10,
            qty=qty,
        )
    finally:
        conn.close()


def _days_ago(days: int) -> str:
    stamp = datetime.now(UTC) - timedelta(days=days, hours=1)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def _static_runner(results: dict[str, SiteResult]) -> Runner:
    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        return results[profile["id"]]

    return runner


def _ok(site_id: str, *variants: Variant) -> SiteResult:
    candidate = ProductCandidate(
        raw_title="Dior Sauvage EDP Dekant", url="https://example.com/p"
    )
    return SiteResult(site_id, "ok", (SearchHit(candidate, variants),), None)


def _scenario(
    site_id: str,
    name: str,
    subtotal_kurus: int,
    shipping_kurus: int,
    *,
    covered: int,
    total_items: int,
) -> SiteScenario:
    return SiteScenario(
        site_id=site_id,
        name=name,
        subtotal_kurus=subtotal_kurus,
        shipping_kurus=shipping_kurus,
        total_kurus=subtotal_kurus + shipping_kurus,
        covered=covered,
        total_items=total_items,
        missing=(),
        free_shipping_gap_kurus=None,
        free_shipping_met=False,
        notes=None,
    )


def _leg(
    site_id: str, name: str, subtotal_kurus: int, shipping_kurus: int, *item_ids: int
) -> SplitLeg:
    scenario = _scenario(
        site_id,
        name,
        subtotal_kurus,
        shipping_kurus,
        covered=len(item_ids),
        total_items=len(item_ids),
    )
    return SplitLeg(scenario=scenario, item_ids=item_ids)


def _plan(*legs: SplitLeg, omitted_sites: tuple[str, ...] = ()) -> SplitPlan:
    total = sum(leg.scenario.total_kurus for leg in legs)
    return SplitPlan(legs=legs, total_kurus=total, omitted_sites=omitted_sites)


def _stub_optimize(monkeypatch: pytest.MonkeyPatch, plan: SplitPlan | None) -> None:
    """Fix what basket.optimize hands the screen instead of relying on the search.

    Patched on the screen's own module, since that is the name the screen calls
    -- basket_screen imported `optimize` by value, so patching basket.optimize
    would leave the screen still holding the original.
    """
    monkeypatch.setattr(
        basket_screen_module, "optimize", lambda items, prices, shipping: plan
    )


def _app(sites_dir: Path, db_path: Path, runner: Runner | None = None) -> Any:
    return ParfumFinderApp(
        sites_dir=sites_dir,
        db_path=db_path,
        runner=runner or _static_runner({}),
    )


async def _open_basket(pilot: Any) -> BasketScreen:
    """Push the basket and wait until its first read has landed."""
    app = pilot.app
    screen = BasketScreen(
        sites_dir=app.sites_dir, db_path=app.db_path, runner=app.runner
    )
    app.push_screen(screen)
    await _wait_until(
        lambda: bool(screen.query_one("#basket", DataTable).columns), pilot
    )
    return screen


async def _wait_until(
    predicate: Callable[[], bool], pilot: Any, timeout_s: float = 3.0
) -> None:
    async def poll() -> None:
        while not predicate():
            await pilot.pause()

    await asyncio.wait_for(poll(), timeout_s)


def _text(screen: BasketScreen, widget_id: str) -> str:
    # .visual, not .content: content is the raw string handed to update(),
    # so asserting on it cannot see markup eating part of the line before it
    # is painted. .visual is what the widget actually shows.
    visual = screen.query_one(f"#{widget_id}", Static).visual
    assert isinstance(visual, Content)
    return visual.plain


def _cells(screen: BasketScreen) -> list[list[str]]:
    table = screen.query_one("#basket", DataTable)
    return [[str(cell) for cell in table.get_row_at(i)] for i in range(table.row_count)]


def _qty(db_path: Path, basket_item_id: int) -> int | None:
    conn = connect(db_path)
    try:
        row: sqlite3.Row | None = conn.execute(
            "SELECT qty FROM basket_items WHERE basket_item_id = ?", (basket_item_id,)
        ).fetchone()
        return None if row is None else int(row[0])
    finally:
        conn.close()


# -- the matrix ------------------------------------------------------------


async def test_a_site_that_prices_nothing_still_gets_a_column_of_dashes(
    tmp_path: Path,
) -> None:
    """A site with no prices must be visibly empty, not invisibly absent.

    Sourcing the columns from the price rows would make the site disappear, and
    a site that vanished reads as "not part of this comparison" when what it
    actually means is "this shop has none of it".
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        headers = [
            str(c.label)
            for c in screen.query_one("#basket", DataTable).columns.values()
        ]
        assert headers == ["Parfüm", "ml", "Adet", "Site A", "Site B", "Güncellik"]
        assert _cells(screen)[0][3:5] == ["250.00 ₺", "—"]


async def test_a_disabled_site_is_not_a_column(tmp_path: Path) -> None:
    """A site nobody scans cannot be part of a comparison of today's prices."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B", enabled=False)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        headers = [
            str(c.label)
            for c in screen.query_one("#basket", DataTable).columns.values()
        ]
        assert "Site B" not in headers


async def test_an_out_of_stock_price_is_missing_rather_than_cheap(
    tmp_path: Path,
) -> None:
    """A sold-out listing must not win a comparison it cannot actually fill.

    It is the cheapest number on the row, so carrying it into the total would
    quietly recommend a site that would take the order and never ship it.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 10000, in_stock=False))
    _price(db, "site-b", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        assert _cells(screen)[0][3] == "—"
        scenarios = _text(screen, "scenarios")
        assert "Site A" not in scenarios
        assert "250.00 ₺" in scenarios


async def test_the_size_column_only_shows_a_price_for_its_own_size(
    tmp_path: Path,
) -> None:
    """Two sizes of one perfume are two rows with two prices, never one.

    The matrix joins on the tenths-of-a-ml integer for exactly this reason, and
    a 10 ml price leaking into the 5 ml row would double the basket's idea of
    what the small decant costs.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, 45000))
    _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        rows = _cells(screen)
        assert [(r[1], r[3]) for r in rows] == [
            ("5 ml", "250.00 ₺"),
            ("10 ml", "450.00 ₺"),
        ]


async def test_the_cell_shows_the_unit_price_while_the_total_counts_the_quantity(
    tmp_path: Path,
) -> None:
    """The matrix is a price list, the scenario is a bill.

    Multiplying the quantity into the cell would make one shop's single listing
    look like a different offer depending on how many the user happens to want.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50, qty=2)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        row = _cells(screen)[0]
        assert row[2] == "2"
        assert row[3] == "250.00 ₺"
        assert "500.00 ₺" in _text(screen, "scenarios")


# -- age -------------------------------------------------------------------


def test_format_age_reads_as_words_not_a_timestamp() -> None:
    """The age column exists to be glanced at, so it is phrased, not printed."""
    assert format_age(0) == "bugün"
    assert format_age(2) == "2 gün önce"
    assert format_age(21) == "3 hafta önce"
    assert format_age(None) == "—"


async def test_a_rows_age_is_its_stalest_cell(tmp_path: Path) -> None:
    """A row is only as fresh as the oldest price it is comparing.

    Reporting the newest would let one just-scanned column hide a column that
    has not been checked in weeks, which is precisely the state the refresh
    warning is supposed to catch.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000), fetched_at=now_iso())
    _price(db, "site-b", _variant(50, 26000), fetched_at=_days_ago(20))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        assert _cells(screen)[0][-1] == "2 hafta önce"
        notices = _text(screen, "basket-notices")
        assert "günden eski" in notices
        # And says which key fixes it. Content markup eats an unescaped [r].
        assert "[r]" in notices
        # Coloured as well as counted. With a dozen lines the warning only says
        # that something is old; the red cell is what says which line.
        table = screen.query_one("#basket", DataTable)
        assert str(table.get_row_at(0)[-1].style) == STALE_PRICE_STYLE


async def test_fresh_prices_raise_no_staleness_warning(tmp_path: Path) -> None:
    """The warning has to stay quiet when nothing is wrong, or it gets ignored."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        assert _cells(screen)[0][-1] == "bugün"
        assert "günden eski" not in _text(screen, "basket-notices")


# -- scenarios -------------------------------------------------------------


async def test_a_partial_site_is_grouped_apart_and_names_what_it_lacks(
    tmp_path: Path,
) -> None:
    """A partial total is cheaper for the wrong reason, so it is never mixed in.

    Site B here is cheaper only because it is not selling one of the items, and
    listing it alongside the full-coverage sites would read as the better buy.
    The warning rides on the heading rather than a separator line, so it is
    still attached to the group when the reader scrolls into the middle of it.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, 45000))
    _price(db, "site-b", _variant(50, 20000))
    _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        await pilot.press("t")
        text = _text(screen, "scenarios")
        full, partial = text.split("KISMİ — TAM KAPSAMLILARLA DOĞRUDAN KIYASLANAMAZ")
        assert "Site A   2/2" in full
        assert "Site B   1/2" in partial
        assert "eksik: dior sauvage EDP 10 ml" in partial
        assert "(kısmi)" in partial


async def test_the_partial_group_sits_below_the_split_block(tmp_path: Path) -> None:
    """The partials are reference material, and the split is a decision.

    Keeping the group that cannot be compared against anything between the two
    totals that can be compared is what made the old screen hard to read: the
    eye lands on a cheap partial total on its way from one real number to the
    other.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, 45000))
    _price(db, "site-b", _variant(50, 20000))
    _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        await pilot.press("t")
        text = _text(screen, "scenarios")
        assert text.index("EN İYİ BULUNAN KOMBİNASYON") < text.index("KISMİ —")


async def test_the_default_view_is_the_cheapest_full_site_against_the_split(
    tmp_path: Path,
) -> None:
    """Opening on every scenario at once buries the choice actually being made.

    In practice the decision is between the cheapest shop that can fill the
    whole list and splitting the order, so only those two are on screen at
    rest. The runner-up shops and the partials are still reachable, and the
    screen says how many of them it is holding back rather than pretending
    they do not exist.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _write_profile(sites_dir, "site-c", "Site C")
    _sync(sites_dir, db)
    # Site A is cheapest, Site B is a pricier full site, Site C is partial.
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, 45000))
    _price(db, "site-b", _variant(50, 26000))
    _price(db, "site-b", _variant(100, 46000))
    _price(db, "site-c", _variant(50, 20000))
    _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "Site A   2/2" in text
        assert "EN İYİ BULUNAN KOMBİNASYON" in text
        # Site C may still be named inside the split plan, which is one of the
        # two blocks that stay. What is folded away is its own scenario block.
        assert "Site B   2/2" not in text
        assert "Site C   1/2" not in text
        assert "KISMİ —" not in text
        assert "[t] 2 senaryo daha göster" in text


async def test_t_opens_the_remaining_scenarios_and_closes_them_again(
    tmp_path: Path,
) -> None:
    """The fold has to be reversible, or it is a feature that hides prices.

    A reader who opened the rest to check one number needs the compact view
    back without leaving and re-entering the screen.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-b", _variant(50, 26000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        assert "Site B" not in _text(screen, "scenarios")

        await pilot.press("t")
        opened = _text(screen, "scenarios")
        assert "Site B   1/1" in opened
        assert "[t] diğer senaryoları gizle" in opened

        await pilot.press("t")
        assert "Site B" not in _text(screen, "scenarios")


async def test_toggling_does_not_re_run_the_combination_search(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[t] changes how much of the answer is shown, not what the answer is.

    optimize() is the expensive call on this screen, so a keypress that only
    folds blocks open and shut must repaint from what was already scored.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-b", _variant(50, 26000))
    item_id = _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        calls = 0

        def _counted(items: Any, prices: Any, shipping: Any) -> SplitPlan:
            nonlocal calls
            calls += 1
            return _plan(_leg("site-a", "Site A", 25000, 0, item_id))

        monkeypatch.setattr(basket_screen_module, "optimize", _counted)
        await pilot.press("t")
        # The presses have to actually repaint, or "optimize was never called"
        # would also be true of a binding that does nothing at all.
        assert "Site B" in _text(screen, "scenarios")
        await pilot.press("t")
        assert "Site B" not in _text(screen, "scenarios")
        assert calls == 0


async def test_with_no_full_coverage_site_the_partials_are_open_from_the_start(
    tmp_path: Path,
) -> None:
    """The notice above the table sends the reader to the partial scenarios.

    Folding them away by default would point that notice at an empty screen,
    and there is no cheapest-full-site-versus-split decision left to keep the
    view compact for.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-b", _variant(100, 45000))
    _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "Hiçbir site listenin tamamını" in _text(screen, "basket-notices")
        assert "Site A   1/2" in text
        assert "Site B   1/2" in text
        assert "senaryo daha göster" not in text


async def test_the_free_shipping_gap_is_the_number_the_decision_needs(
    tmp_path: Path,
) -> None:
    """ "Add one more and shipping is free" is the whole point of this screen."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", threshold=50000, shipping_cost=8900)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "250.00 ₺ + 89.00 ₺ kargo = 339.00 ₺" in text
        assert "ücretsiz kargoya 250.00 ₺ kaldı" in text


async def test_a_site_without_free_shipping_shows_no_gap_line(tmp_path: Path) -> None:
    """A threshold of NULL means there is no gap to close, at any subtotal.

    Printing one would send the user shopping toward a discount that does not
    exist on that shop.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", threshold=None, shipping_cost=8900)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 900000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "kaldı" not in text
        assert "eşiği aşıldı" not in text
        assert "89.00 ₺ kargo" in text


async def test_the_site_note_is_shown_next_to_its_scenario(tmp_path: Path) -> None:
    """A "3% off by bank transfer" note changes which total is really cheapest."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", notes="havale %3 indirim")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        assert "havale %3 indirim" in _text(screen, "scenarios")


# -- empty and error states -------------------------------------------------


async def test_an_empty_basket_says_how_to_fill_it(tmp_path: Path) -> None:
    """A blank screen with no explanation reads as a broken screen."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        notices = _text(screen, "basket-notices")
        assert "Sepet boş" in notices
        # The key is the how. Content markup eats an unescaped [a], which
        # turns the one useful sentence on an empty screen into a shrug.
        assert "[a]" in notices


async def test_an_item_no_site_sells_is_called_out_by_name(tmp_path: Path) -> None:
    """A row of nothing but dashes needs saying out loud, not leaving to be read."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, None))
    _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        notices = _text(screen, "basket-notices")
        assert '"dior sauvage EDP 10 ml" hiçbir sitede bulunamadı' in notices
        assert "Hiçbir site listenin tamamını karşılamıyor" in notices


# -- CRUD keys --------------------------------------------------------------


async def test_plus_and_minus_change_the_quantity(tmp_path: Path) -> None:
    """Quantity is what turns a price list into a bill, so it is editable here."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    item_id = _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("plus")
        await _wait_until(lambda: _qty(db, item_id) == 2, pilot)
        await pilot.press("minus")
        await _wait_until(lambda: _qty(db, item_id) == 1, pilot)


async def test_minus_at_one_is_a_no_op_rather_than_a_deletion(tmp_path: Path) -> None:
    """Removal has its own key, so "-" must never be a surprise delete.

    The quantity column also has a CHECK (qty > 0) behind it, so an unclamped
    decrement would take the whole screen down with a constraint error.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    item_id = _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("minus")
        await pilot.pause()
        await pilot.pause()
        assert _qty(db, item_id) == 1
        assert len(_cells(screen)) == 1


async def test_d_removes_the_selected_line(tmp_path: Path) -> None:
    """The list is edited here, not only on the search screen."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, 45000))
    first = _basket(db, 50)
    _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("d")
        await _wait_until(lambda: _qty(db, first) is None, pilot)
        await _wait_until(lambda: len(_cells(screen)) == 1, pilot)


# -- refresh ----------------------------------------------------------------


async def test_refresh_writes_new_prices_and_counts_its_progress(
    tmp_path: Path,
) -> None:
    """Refresh is the most expensive thing the app does, so it reports itself.

    The count is scans, perfumes times sites, because that is the number of
    requests a small shop is about to receive.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000), fetched_at=_days_ago(30))
    _price(db, "site-b", _variant(50, 26000), fetched_at=_days_ago(30))
    _basket(db, 50)

    runner = _static_runner(
        {
            "site-a": _ok("site-a", _variant(50, 19000)),
            "site-b": _ok("site-b", _variant(50, 26000)),
        }
    )

    async with _app(sites_dir, db, runner).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("r")
        await _wait_until(lambda: _cells(screen)[0][3] == "190.00 ₺", pilot)
        assert _cells(screen)[0][-1] == "bugün"
        assert screen._scans == 2


async def test_a_site_that_breaks_during_refresh_is_unknown_not_expensive(
    tmp_path: Path,
) -> None:
    """A suspect site keeps serving its last good price, and that price is a lie.

    Nothing in the database marks the site as unreadable, so the exclusion is
    made here for as long as the screen is open. Leaving the old number in place
    would put a price nobody can currently verify into a total the user acts on.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-b", _variant(50, 26000))
    _basket(db, 50)

    runner = _static_runner(
        {
            "site-a": SiteResult("site-a", "suspect", (), "site-a: css layer read 0"),
            "site-b": _ok("site-b", _variant(50, 26000)),
        }
    )

    async with _app(sites_dir, db, runner).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("r")
        await _wait_until(lambda: _cells(screen)[0][3] == "—", pilot)
        assert "⚠ site-a tazelenemedi" in _text(screen, "basket-notices")
        assert "Site A" not in _text(screen, "scenarios")


async def test_a_shop_that_says_it_stopped_selling_it_loses_its_old_price(
    tmp_path: Path,
) -> None:
    """An empty answer is evidence of absence, so the stored price has to go.

    latest_prices keeps serving the last successful snapshot, so without this
    the screen would show a price for a decant the shop just said it no longer
    carries, and put it in a total the user acts on.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    runner = _static_runner({"site-a": SiteResult("site-a", "empty", (), None)})

    async with _app(sites_dir, db, runner).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("r")
        await _wait_until(lambda: _cells(screen)[0][3] == "—", pilot)
        # No failure notice: the shop answered perfectly well, it just does not
        # have it, and calling that a refresh error would train the user to
        # ignore the line that means something really broke.
        assert "tazelenemedi" not in _text(screen, "basket-notices")


async def test_an_empty_answer_for_one_line_leaves_the_other_lines_alone(
    tmp_path: Path,
) -> None:
    """A shop that dropped one decant is still telling the truth about the rest.

    The exclusion is keyed on the line as well as the site for this reason: a
    site-wide one would throw away four good prices because of a fifth.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _price(db, "site-a", _variant(100, 45000))
    _basket(db, 50)
    _basket(db, 100)

    scanned = 0

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        # Both lines are the same perfume, so they come in as the same query.
        # The 5 ml line is scanned first and only the 10 ml one comes back empty.
        nonlocal scanned
        scanned += 1
        if scanned == 1:
            return _ok("site-a", _variant(50, 19000))
        return SiteResult("site-a", "empty", (), None)

    async with _app(sites_dir, db, runner).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("r")
        await _wait_until(lambda: _cells(screen)[0][3] == "190.00 ₺", pilot)
        assert _cells(screen)[1][3] == "—"


async def test_one_site_is_scanned_one_perfume_at_a_time(tmp_path: Path) -> None:
    """The pacing lives inside a single run_site call, so overlapping them loses it.

    Two perfumes fired at one shop at once would put both rate_limit_ms gaps in
    parallel and send the request burst this project exists not to send. Across
    two different shops overlapping is fine and is what keeps refresh quick.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _sync(sites_dir, db)
    for ml in (50, 100):
        _price(db, "site-a", _variant(ml, 25000))
        _price(db, "site-b", _variant(ml, 26000))
        _basket(db, ml)

    in_flight: dict[str, int] = {}
    peak_per_site = 0
    peak_overall = 0

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        nonlocal peak_per_site, peak_overall
        site_id = str(profile["id"])
        in_flight[site_id] = in_flight.get(site_id, 0) + 1
        peak_per_site = max(peak_per_site, in_flight[site_id])
        peak_overall = max(peak_overall, sum(in_flight.values()))
        await asyncio.sleep(0.02)
        in_flight[site_id] -= 1
        return _ok(site_id, _variant(50, 19000), _variant(100, 33000))

    async with _app(sites_dir, db, runner).run_test() as pilot:
        screen = await _open_basket(pilot)
        screen.query_one("#basket", DataTable).focus()
        await pilot.press("r")
        await _wait_until(
            lambda: not screen._refreshing and screen._scanned == 4, pilot
        )

    assert peak_per_site == 1
    assert peak_overall == 2


# -- navigation -------------------------------------------------------------


async def test_s_opens_the_basket_and_escape_comes_back_to_the_results(
    tmp_path: Path,
) -> None:
    """The basket is pushed over the search screen, so the scan survives the trip.

    Switching screens instead would throw away a finished scan and make checking
    the basket cost a second pass over every site.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)

    async with _app(sites_dir, db).run_test() as pilot:
        search = pilot.app.screen
        assert isinstance(search, SearchScreen)
        search.query_one("#results", DataTable).focus()
        await pilot.press("s")
        await _wait_until(lambda: isinstance(pilot.app.screen, BasketScreen), pilot)
        await pilot.press("escape")
        await _wait_until(lambda: pilot.app.screen is search, pilot)


# -- best combination --------------------------------------------------------


async def test_the_split_block_carries_its_heuristic_label_verbatim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The block must never be mistaken for a mathematically proven answer.

    optimize() enumerates a bounded subset search, not every possible split, so
    the screen has to keep saying "found", not "best possible", every time it
    shows this block. The caveat also has to stay actionable: it tells the
    reader to look at the other scenarios, which is the only thing they can
    actually do about the search being a heuristic.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    item_id = _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        _stub_optimize(monkeypatch, _plan(_leg("site-a", "Site A", 25000, 0, item_id)))
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "EN İYİ BULUNAN KOMBİNASYON" in text
        assert (
            "Aramanın bulduğu en ucuz dağılım; daha ucuzu olabilir, "
            "aşağıdaki seçeneklere de bakın." in text
        )


async def test_a_cheaper_split_is_marked_daha_ucuz_with_the_real_difference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The whole point of the block is telling the user how much splitting saves.

    A vague "cheaper" would not be actionable; the number has to be the exact
    gap between the split and the best single site so it can be weighed against
    the hassle of ordering from two shops.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", shipping_cost=0)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 15000))
    _price(db, "site-a", _variant(100, 15000))
    item1 = _basket(db, 50)
    item2 = _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        plan = _plan(
            _leg("site-b", "Site B", 10000, 0, item1),
            _leg("site-c", "Site C", 15000, 0, item2),
        )
        _stub_optimize(monkeypatch, plan)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        # site-a is the only full-coverage site: 15000 + 15000 = 300.00 ₺.
        # The split totals 25000 = 250.00 ₺, a 50.00 ₺ saving.
        assert "GENEL TOPLAM 250.00 ₺" in text
        assert "ⓘ En iyi tam kapsamlı tek site (Site A) 300.00 ₺" in text
        assert "→ bölmek 50.00 ₺ DAHA UCUZ" in text


async def test_a_pricier_split_is_marked_daha_pahali_not_dressed_up_as_advice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A split that costs more must read as a warning, never as a suggestion.

    The heuristic can lose to the best single site. Showing the block without
    an equally visible "more expensive" label would let a worse total slip by
    looking like the recommended combination just because it is on screen.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", shipping_cost=0)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 15000))
    _price(db, "site-a", _variant(100, 15000))
    item1 = _basket(db, 50)
    item2 = _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        plan = _plan(
            _leg("site-b", "Site B", 20000, 0, item1),
            _leg("site-c", "Site C", 15000, 0, item2),
        )
        _stub_optimize(monkeypatch, plan)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        # site-a totals 300.00 ₺, the split totals 35000 = 350.00 ₺.
        assert "→ bölmek 50.00 ₺ DAHA PAHALI" in text
        assert "DAHA UCUZ" not in text


async def test_the_comparison_is_the_best_full_site_never_a_cheaper_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A partial site's total is cheap for the wrong reason: it skipped a line.

    Comparing the split against it instead of the best full-coverage site would
    make an honest split look worse than a total that never bought the whole
    basket to begin with.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", shipping_cost=0)
    _write_profile(sites_dir, "site-b", "Site B", shipping_cost=0)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 15000))
    _price(db, "site-a", _variant(100, 15000))
    _price(db, "site-b", _variant(50, 5000))
    item1 = _basket(db, 50)
    item2 = _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        plan = _plan(
            _leg("site-b", "Site B", 5000, 0, item1),
            _leg("site-a", "Site A", 15000, 0, item2),
        )
        _stub_optimize(monkeypatch, plan)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "ⓘ En iyi tam kapsamlı tek site (Site A) 300.00 ₺" in text
        assert "En iyi tam kapsamlı tek site (Site B)" not in text


async def test_no_full_coverage_site_says_comparison_is_impossible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A comparison against nothing would look like a number, not an absence.

    When every single site is partial there is no honest baseline to measure
    the split against, so the screen has to say that plainly instead of
    silently dropping the comparison line.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A", shipping_cost=0)
    _write_profile(sites_dir, "site-b", "Site B", shipping_cost=0)
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 15000))
    _price(db, "site-b", _variant(100, 15000))
    item1 = _basket(db, 50)
    item2 = _basket(db, 100)

    async with _app(sites_dir, db).run_test() as pilot:
        plan = _plan(
            _leg("site-a", "Site A", 15000, 0, item1),
            _leg("site-b", "Site B", 15000, 0, item2),
        )
        _stub_optimize(monkeypatch, plan)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "ⓘ Tam kapsamlı tek site yok — karşılaştırma yapılamıyor" in text
        assert "DAHA UCUZ" not in text
        assert "DAHA PAHALI" not in text


async def test_optimize_returning_none_hides_the_block_entirely(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """None means no combination of sites can fill the basket at all.

    Showing an empty or partial block in that case would imply a combination
    exists when the actual answer is that nothing does.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        _stub_optimize(monkeypatch, None)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "EN İYİ BULUNAN KOMBİNASYON" not in text


async def test_an_empty_basket_never_calls_optimize_or_shows_the_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nothing to buy means nothing to split, so the block has no reason to show."""
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)

    def _boom(items: Any, prices: Any, shipping: Any) -> None:
        raise AssertionError("optimize should not be called on an empty basket")

    async with _app(sites_dir, db).run_test() as pilot:
        monkeypatch.setattr(basket_screen_module, "optimize", _boom)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "EN İYİ BULUNAN KOMBİNASYON" not in text


async def test_a_one_leg_plan_is_marked_single_site_not_a_split(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A one-leg plan is the best single site restated, and must read that way.

    Printing it with the same phrasing as a real multi-site split would suggest
    an order needs to be divided when it does not.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    item_id = _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        _stub_optimize(monkeypatch, _plan(_leg("site-a", "Site A", 25000, 0, item_id)))
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "Site A  (tek site — bölünmüyor)" in text


async def test_omitted_sites_are_named_in_their_own_notice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A truncated search has to say so, or a narrowed answer reads as complete.

    optimize() only enumerates MAX_ENUMERATED_SITES candidates; past that it
    silently drops the rest unless the screen names exactly which ones.
    """
    sites_dir, db = tmp_path / "sites", tmp_path / "db.sqlite"
    _write_profile(sites_dir, "site-a", "Site A")
    _sync(sites_dir, db)
    _price(db, "site-a", _variant(50, 25000))
    item_id = _basket(db, 50)

    async with _app(sites_dir, db).run_test() as pilot:
        plan = _plan(
            _leg("site-a", "Site A", 25000, 0, item_id),
            omitted_sites=("site-x", "site-y"),
        )
        _stub_optimize(monkeypatch, plan)
        screen = await _open_basket(pilot)
        text = _text(screen, "scenarios")
        assert "ⓘ 2 site kombinasyon aramasına dahil edilmedi: site-x, site-y" in text
