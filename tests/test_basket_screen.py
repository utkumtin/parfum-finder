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

from textual.widgets import DataTable, Static

from parfum_finder.engine import ProductCandidate, SearchHit, SiteResult, Variant
from parfum_finder.profiles import load_site_profile, sync_to_db
from parfum_finder.store import add_basket_item, connect, now_iso, record_snapshot
from parfum_finder.tui.app import ParfumFinderApp
from parfum_finder.tui.basket_screen import BasketScreen, format_age
from parfum_finder.tui.search_screen import SearchScreen

Runner = Callable[[dict[str, Any], str], Awaitable[SiteResult]]

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
    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
        return results[profile["id"]]

    return runner


def _ok(site_id: str, *variants: Variant) -> SiteResult:
    candidate = ProductCandidate(
        raw_title="Dior Sauvage EDP Dekant", url="https://example.com/p"
    )
    return SiteResult(site_id, "ok", (SearchHit(candidate, variants),), None)


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
    return str(screen.query_one(f"#{widget_id}", Static).content)


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
        assert headers == ["Parfüm", "ml", "Ad", "Site A", "Site B", "Yaş"]
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
        assert "günden eski" in _text(screen, "basket-notices")
        # Coloured as well as counted. With a dozen lines the warning only says
        # that something is old; the red cell is what says which line.
        table = screen.query_one("#basket", DataTable)
        assert str(table.get_row_at(0)[-1].style) == "bold red"


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
        text = _text(screen, "scenarios")
        full, partial = text.split("── kısmi")
        assert "Site A   2/2" in full
        assert "Site B   1/2" in partial
        assert "eksik: dior sauvage EDP 10 ml" in partial
        assert "(kısmi)" in partial


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
        assert "Sepet boş" in _text(screen, "basket-notices")


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

    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
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

    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
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
