"""Tests for the search screen: grouping, persistence, and the key bindings.

A fake runner stands in for engine.run_site everywhere -- these tests never
touch the network. Some fake runners are gated on an asyncio.Event so a test
can hold one site open while the others finish, which is the only way to check
what the screen shows while a scan is still running.
"""

import asyncio
import json
import logging
import sqlite3
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
from textual.content import Content
from textual.widgets import Button, DataTable, Input, ProgressBar, Static

from parfum_finder.engine import ProductCandidate, SearchHit, SiteResult, Variant
from parfum_finder.store import connect, record_snapshot
from parfum_finder.tui.app import ParfumFinderApp
from parfum_finder.tui.search_screen import ConfirmScreen

QUERY_TEXT = "Dior Sauvage EDP"


def _write_profile(
    sites_dir: Path,
    site_id: str,
    name: str,
    *,
    discovered_at: str = "2026-08-01T00:00:00Z",
    enabled: bool = True,
) -> None:
    sites_dir.mkdir(parents=True, exist_ok=True)
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
        "shipping": {"free_shipping_threshold_kurus": None, "shipping_cost_kurus": 0},
        "discovered_at": discovered_at,
        "needs_review": [],
    }
    (sites_dir / f"{site_id}.json").write_text(json.dumps(profile))


def _variant(
    ml_x10: int,
    price_kurus: int | None,
    *,
    in_stock: bool = True,
    title: str = "Dior Sauvage EDP Dekant",
    url: str = "https://example.com/p",
) -> Variant:
    return Variant(
        size_ml_x10=ml_x10,
        raw_title=f"{title} {ml_x10 / 10:g} ml",
        product_url=f"{url}?ml={ml_x10}",
        price_kurus=price_kurus,
        in_stock=in_stock,
    )


def _ok_result(site_id: str, *variants: Variant) -> SiteResult:
    candidate = ProductCandidate(
        raw_title="Dior Sauvage EDP Dekant", url="https://example.com/p"
    )
    hit = SearchHit(candidate, variants)
    return SiteResult(site_id, "ok", (hit,), f"{site_id}: ok")


# The screen hands its runner a browser session, a listing filter and a shared
# product cache as well. A fake that ignores them still has to accept them, and
# **_ is how these say they are not what is under test.
Runner = Callable[..., Awaitable[SiteResult]]


def _static_runner(results: dict[str, SiteResult]) -> Runner:
    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        return results[profile["id"]]

    return runner


def _app(sites_dir: Path, db_path: Path, runner: Runner) -> ParfumFinderApp:
    return ParfumFinderApp(sites_dir=sites_dir, db_path=db_path, runner=runner)


async def _submit_query(pilot: Any, text: str = QUERY_TEXT) -> None:
    query = pilot.app.screen.query_one("#query", Input)
    query.value = text
    query.focus()
    await pilot.pause()
    await pilot.press("enter")


def _rendered(widget: Static) -> str:
    """What the widget actually paints, with markup applied.

    `.content` is the raw string handed to update(), so an assertion on it
    cannot tell a key hint that reaches the screen from one that markup
    swallowed as a style tag on the way.
    """
    visual = widget.visual
    assert isinstance(visual, Content)
    return visual.plain


async def _wait_until(
    predicate: Callable[[], bool], pilot: Any, timeout_s: float = 3.0
) -> None:
    async def poll() -> None:
        while not predicate():
            await pilot.pause()

    await asyncio.wait_for(poll(), timeout_s)


async def _wait_for_table(pilot: Any, timeout_s: float = 3.0) -> Any:
    """Wait for the scan to end, which is the only time the table is filled.

    Counting finished scans is not enough anymore: the last site can be done
    while the rows are still being sorted into blocks, and a test that read the
    table there would see an empty one at random.
    """
    screen = pilot.app.screen
    # _total is what says a scan started at all, so this cannot fall through on
    # the moment before the worker has begun.
    await _wait_until(
        lambda: screen._total > 0 and not screen._scanning, pilot, timeout_s
    )
    return screen.query_one("#results", DataTable)


async def test_no_rows_land_until_every_site_is_done(tmp_path: Path) -> None:
    """The table stays empty for the whole scan, and the bar carries the news.

    Rows arriving one site at a time made the table move under whoever was
    reading it: the cheapest row kept changing and the row under the cursor kept
    sliding. So a site finishing early is deliberately not shown, and the
    progress bar plus the live counter are what say the scan is going anywhere.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _write_profile(sites_dir, "site-c", "Site C")

    gate = asyncio.Event()

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        site_id = profile["id"]
        if site_id == "site-a":
            await gate.wait()
        return _ok_result(site_id, _variant(50, 25000))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen

        # site-b and site-c can finish; site-a is still parked on the gate.
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 0
        bar = screen.query_one("#progress", ProgressBar)
        assert bar.display
        assert (bar.progress, bar.total) == (2.0, 3.0)
        assert "2/3" in str(screen.query_one("#status", Static).content)

        gate.set()
        table = await _wait_for_table(pilot)
        assert table.row_count == 3
        # Site Başlığı is the site's raw title, untouched -- it is what makes a
        # wrong match visible, so nothing here may tidy it up.
        assert table.get_row_at(0)[2] == "Dior Sauvage EDP Dekant 5 ml"
        assert "3/3" in str(screen.query_one("#status", Static).content)
        # The bar has nothing left to say once the rows are there.
        assert not screen.query_one("#progress", ProgressBar).display


async def test_one_site_erroring_does_not_block_the_others(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        if profile["id"] == "site-a":
            raise RuntimeError("boom")
        return _ok_result("site-b", _variant(50, 25000))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    with caplog.at_level(logging.ERROR, logger="parfum_finder"):
        async with app.run_test() as pilot:
            await pilot.pause()
            await _submit_query(pilot)
            screen = app.screen
            await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

            table = screen.query_one("#results", DataTable)
            assert table.row_count == 1
            # The failure never reaches the screen. The count and the log file
            # name are all the user gets, the reason is in the file.
            assert screen._errors == 1  # type: ignore[attr-defined]
            assert str(screen.query_one("#notices", Static).content) == ""
            status = str(screen.query_one("#status", Static).content)
            assert "1 hata (parfum-finder.log)" in status

    logged = caplog.text
    assert "site-a" in logged
    assert "bağlantı hatası" in logged
    assert "boom" in logged


async def test_suspect_site_is_logged_and_contributes_no_rows(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    suspect = SiteResult(
        "site-a",
        "suspect",
        (),
        "site-a: the 'css' layer read no priced size from 3 hits",
    )
    runner = _static_runner({"site-a": suspect})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    with caplog.at_level(logging.ERROR, logger="parfum_finder"):
        async with app.run_test() as pilot:
            await pilot.pause()
            await _submit_query(pilot)
            screen = app.screen
            await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

            table = screen.query_one("#results", DataTable)
            assert table.row_count == 0
            assert str(screen.query_one("#notices", Static).content) == ""
            assert screen._errors == 1  # type: ignore[attr-defined]

    assert caplog.text.count("profil bozulmuş olabilir") == 1
    assert "the 'css' layer read no priced size from 3 hits" in caplog.text


async def test_empty_site_shows_the_no_match_notice_without_a_warning_mark(
    tmp_path: Path,
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    empty = SiteResult("site-a", "empty", (), "site-a: no decant matched 'x'")
    runner = _static_runner({"site-a": empty})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 0
        notices = str(screen.query_one("#notices", Static).content)
        # No warning mark: this is "not sold here", not a broken site, and
        # the two must never read the same way.
        assert notices == "site-a — eşleşme bulunamadı"
        assert screen._errors == 0  # type: ignore[attr-defined]


async def test_stale_profile_gets_the_age_badge_on_its_site_name(
    tmp_path: Path,
) -> None:
    sites_dir = tmp_path / "sites"
    # Comfortably past validate.STALE_PROFILE_DAYS (90) and fixed, so the
    # test can't start passing or failing depending on when it runs.
    _write_profile(sites_dir, "site-a", "Site A", discovered_at="2026-01-01T00:00:00Z")
    runner = _static_runner({"site-a": _ok_result("site-a", _variant(50, 100000))})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)

        table = await _wait_for_table(pilot)
        site_cell = str(table.get_row_at(0)[1])
        assert "⏳" in site_cell
        assert "gün önce keşfedildi" in site_cell


async def test_low_score_row_flags_the_match_percent_cell(tmp_path: Path) -> None:
    """Only the doubtful text is marked, not the whole line.

    A weak score says the site's title may not be this perfume. It says nothing
    about the price, size or stock that were read off that listing, so marking
    those too would put a warning on data that is fine.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    weak = Variant(
        size_ml_x10=50,
        raw_title="Dior Sauvage EDP Something Completely Different Dekant",
        product_url="https://example.com/weak",
        price_kurus=100000,
        in_stock=True,
    )
    candidate = ProductCandidate(raw_title=weak.raw_title, url="https://example.com/p")
    result = SiteResult("site-a", "ok", (SearchHit(candidate, (weak,)),), "site-a: ok")
    runner = _static_runner({"site-a": result})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)

        from rich.text import Text

        from parfum_finder.tui.search_screen import _LOW_CONFIDENCE_STYLE

        cells = table.get_row_at(0)
        percent_cell = cells[7]
        assert isinstance(percent_cell, Text)
        assert percent_cell.style == _LOW_CONFIDENCE_STYLE
        assert str(percent_cell) == "31"
        # The title is the other half of the doubt: it is what did not match.
        assert isinstance(cells[2], Text)
        assert cells[2].style == _LOW_CONFIDENCE_STYLE
        # The block heading stays plain: the doubt is already said twice, and a
        # third marking would make a whole row look wrong over one weak title.
        assert isinstance(cells[0], str)
        # ml, fiyat, ₺/ml and stok stay plain text, unmarked.
        assert all(isinstance(cell, str) for cell in cells[3:7])


async def test_site_colour_lands_on_the_site_cell_and_nowhere_else(
    tmp_path: Path,
) -> None:
    """The colour marks where one site's block ends and the next begins.

    It stays inside the Site cell so it can never meet the low-confidence
    marking in the same cell, which would leave two meanings fighting over one
    piece of text with no rule for which wins.
    """
    sites_dir = tmp_path / "sites"
    # A real site id, and stale enough to earn the age badge: the colour is
    # looked up by id, so a label the badge has rewritten must still get it.
    _write_profile(
        sites_dir, "decantall", "Decantall", discovered_at="2026-01-01T00:00:00Z"
    )
    runner = _static_runner(
        {"decantall": _ok_result("decantall", _variant(50, 100000))}
    )

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)

        from rich.text import Text

        from parfum_finder.tui.search_screen import _SITE_STYLES

        cells = table.get_row_at(0)
        assert isinstance(cells[1], Text)
        assert cells[1].style == _SITE_STYLES["decantall"]
        assert "gün önce keşfedildi" in str(cells[1])
        assert all(isinstance(cell, str) for cell in (cells[0], *cells[2:]))


def test_every_shipped_site_has_a_colour_that_survives_256_colours() -> None:
    """Two sites sharing a colour is worse than no colours at all.

    The palette is picked in truecolor, but Terminal.app and anything else
    without truecolor rounds every one of these to the nearest of 256 slots.
    Soft tones sit close together, so that rounding is exactly where two of
    them would land on the same colour, and nothing on a developer's screen
    would ever show it.
    """
    from rich.color import Color, ColorSystem

    from parfum_finder.tui.search_screen import _SITE_STYLES
    from parfum_finder.validate import DEFAULT_SITES_DIR

    shipped = {
        json.loads(path.read_text(encoding="utf-8"))["id"]
        for path in DEFAULT_SITES_DIR.glob("*.json")
    }
    assert shipped
    assert shipped <= set(_SITE_STYLES)

    downgraded = [
        Color.parse(style).downgrade(ColorSystem.EIGHT_BIT).number
        for style in _SITE_STYLES.values()
    ]
    assert len(set(downgraded)) == len(_SITE_STYLES)


async def test_sizes_go_up_inside_a_block_and_the_keys_still_reorder(
    tmp_path: Path,
) -> None:
    """The default is a readable block, not the cheapest ₺/ml at the top.

    Sizes ascending, every block the same way, so the eye can run down one
    column instead of re-reading each block's direction. The number keys are
    what turns the table back into a ranking, and they answer across sites, so
    they drop the site layer entirely.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    # 5 ml at 300 TL/ml, 10 ml at 200 TL/ml: per-ml ascending puts the 10 ml first,
    # size ascending puts the 5 ml first, price ascending puts the cheaper total first.
    small = _variant(50, 150000)  # 5 ml, 1500 TL -> 300 TL/ml
    big = _variant(100, 200000)  # 10 ml, 2000 TL -> 200 TL/ml
    runner = _static_runner({"site-a": _ok_result("site-a", small, big)})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)

        assert table.get_row_at(0)[3] == "5 ml"  # size ascending, default

        table.focus()
        await pilot.pause()
        await pilot.press("3")
        await pilot.pause()
        assert table.get_row_at(0)[3] == "10 ml"  # ₺/ml ascending

        await pilot.press("2")
        await pilot.pause()
        assert table.get_row_at(0)[3] == "5 ml"  # price ascending (1500 < 2000)

        await pilot.press("1")
        await pilot.pause()
        assert table.get_row_at(0)[3] == "5 ml"  # ml ascending


async def test_out_of_stock_rows_start_hidden_and_f_brings_them_back(
    tmp_path: Path,
) -> None:
    """A size nobody can buy must not be in the table by default.

    Its price is not an offer, and the table sorts by ₺/ml, so an out-of-stock
    row sitting at the top answers "what does this cost" with a number that is
    not for sale. It is still fetched and still stored, so [f] has to be able to
    put it back on screen rather than the row being dropped outright.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    in_stock = _variant(50, 100000, in_stock=True)
    out_of_stock = _variant(100, 200000, in_stock=False)
    runner = _static_runner({"site-a": _ok_result("site-a", in_stock, out_of_stock)})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 1
        status = _rendered(screen.query_one("#status", Static))
        assert "1 stoksuz" in status
        # Naming the key is the whole point of the counter: it says a row was
        # hidden and how to see it. Asserted on the rendered text because
        # content markup eats an unescaped [f] and leaves only the count.
        assert "[f]" in status

        table.focus()
        await pilot.pause()
        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 2

        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 1


async def test_enter_opens_the_selected_rows_own_product_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    first = _variant(50, 100000, url="https://example.com/five")
    second = _variant(100, 200000, url="https://example.com/ten")
    runner = _static_runner({"site-a": _ok_result("site-a", first, second)})

    opened: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url: opened.append(url))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        table.move_cursor(row=1)
        await pilot.pause()
        table.focus()
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        selected = screen._visible_rows[1]  # type: ignore[attr-defined]
        assert opened == [selected.product_url]
        assert selected.product_url == "https://example.com/ten?ml=100"


async def test_add_basket_asks_confirmation_for_low_score_and_writes_only_after_yes(
    tmp_path: Path,
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    # A title the brand/concentration checks pass but whose name is far enough
    # off to fall below matcher.DEFAULT_THRESHOLD.
    weak = Variant(
        size_ml_x10=50,
        raw_title="Dior Sauvage EDP Something Completely Different Dekant",
        product_url="https://example.com/weak",
        price_kurus=100000,
        in_stock=True,
    )
    candidate = ProductCandidate(raw_title=weak.raw_title, url="https://example.com/p")
    result = SiteResult("site-a", "ok", (SearchHit(candidate, (weak,)),), "site-a: ok")
    runner = _static_runner({"site-a": result})

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 1
        row = screen._visible_rows[0]  # type: ignore[attr-defined]
        assert not row.confident  # sanity: this is the low-score case under test

        table.focus()
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()

        conn = connect(db_path)
        try:
            assert conn.execute("SELECT * FROM basket_items").fetchall() == []
        finally:
            conn.close()

        await pilot.press("n")
        await pilot.pause()
        conn = connect(db_path)
        try:
            assert conn.execute("SELECT * FROM basket_items").fetchall() == []
        finally:
            conn.close()

        await pilot.press("a")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()

        conn = connect(db_path)
        try:
            basket = conn.execute("SELECT * FROM basket_items").fetchall()
        finally:
            conn.close()
        assert len(basket) == 1


async def test_add_basket_on_a_confident_row_writes_without_confirmation(
    tmp_path: Path,
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _ok_result("site-a", _variant(50, 100000))})

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        row = screen._visible_rows[0]  # type: ignore[attr-defined]
        assert row.confident

        table = screen.query_one("#results", DataTable)
        table.focus()
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()

        conn = connect(db_path)
        try:
            basket = conn.execute("SELECT * FROM basket_items").fetchall()
        finally:
            conn.close()
        assert len(basket) == 1


async def test_a_row_in_the_basket_is_painted_on_every_site_that_offers_it(
    tmp_path: Path,
) -> None:
    """The table has to say which sizes are already picked, and where.

    Without it the only way to know whether [a] was already pressed on a bottle
    is to open the basket and come back, and a scan of six shops for three
    perfumes is exactly where that gets forgotten and a size gets added twice.

    Every site's row for that size is painted, not just the one [a] was pressed
    on: the basket holds a bottle, not a shop, and the choice of where to buy it
    is the thing the basket screen makes afterwards. Painting only the source row
    would read as "buy it here", which is not what was decided.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    runner = _static_runner(
        {
            "site-a": _ok_result("site-a", _variant(50, 100000)),
            "site-b": _ok_result("site-b", _variant(50, 120000)),
        }
    )

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 2
        assert not any(
            _painted_in_basket(table.get_row_at(i)) for i in range(table.row_count)
        )

        table.focus()
        await pilot.pause()
        await pilot.press("a")
        await _wait_until(lambda: _painted_in_basket(table.get_row_at(0)), pilot)

        # Both rows, and every cell of them: a partly painted row reads as a
        # column saying something about itself rather than about the row.
        assert all(
            _painted_in_basket(table.get_row_at(i)) for i in range(table.row_count)
        )

        # And the paint comes off again. The basket screen leaves with
        # pop_screen, so nothing about the way back reports what changed in
        # there: a line removed with [d] has to un-paint its rows anyway, or the
        # table goes on claiming a bottle is picked after it was dropped.
        await pilot.press("s")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("escape")
        await _wait_until(lambda: not _painted_in_basket(table.get_row_at(0)), pilot)
        assert not any(
            _painted_in_basket(table.get_row_at(i)) for i in range(table.row_count)
        )


def _painted_in_basket(cells: list[object]) -> bool:
    from rich.text import Text

    from parfum_finder.tui.search_screen import _IN_BASKET_STYLE

    return all(
        isinstance(cell, Text) and cell.style == _IN_BASKET_STYLE for cell in cells
    )


async def test_prices_land_in_the_db_after_a_site_finishes(tmp_path: Path) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _ok_result("site-a", _variant(50, 100000))})

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT price_kurus, in_stock FROM price_snapshots"
        ).fetchall()
    finally:
        conn.close()
    assert [tuple(r) for r in rows] == [(100000, 1)]


async def test_the_screen_keys_work_right_after_a_search_without_refocusing(
    tmp_path: Path,
) -> None:
    """Submitting a query has to hand focus to the table.

    A focused Input swallows every printable key, so with focus left in the
    search box the footer would keep offering [f], [1], [a] and none of them
    would do anything. This test presses them the way a person would, with no
    focus call of its own, which is the only way that regression can fail a
    test.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    in_stock = _variant(50, 100000, in_stock=True)
    out_of_stock = _variant(100, 200000, in_stock=False)
    runner = _static_runner({"site-a": _ok_result("site-a", in_stock, out_of_stock)})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        table = await _wait_for_table(pilot)
        assert table.row_count == 1

        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 2

        await pilot.press("1")
        await pilot.pause()
        assert table.get_row_at(0)[3] == "5 ml"

        # Escape is the way back to the search box for the next query.
        await pilot.press("escape")
        await pilot.pause()
        assert screen.query_one("#query", Input).has_focus


async def test_showing_the_hidden_rows_does_not_move_the_cursor_off_the_picked_row(
    tmp_path: Path,
) -> None:
    """The row under the cursor has to survive the table being rebuilt.

    Nothing rebuilds it mid-scan anymore, but [f] and the sort keys still do,
    and rebuilding sends the cursor back to the top. Without re-seeking, someone
    who pressed [f] to check what was hidden would then press [a] and add a
    different bottle than the one they were looking at. That is the exact
    mistake the raw-title column exists to prevent, so it cannot be allowed in
    through the back door.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    app = _app(
        sites_dir,
        tmp_path / "db.sqlite3",
        _static_runner(
            {
                "site-a": _ok_result(
                    "site-a",
                    # The out-of-stock 3 ml is hidden at first and sorts above
                    # both others, so bringing it back shifts every row down.
                    _variant(30, 60000, in_stock=False, url="https://a.example/three"),
                    _variant(50, 150000, url="https://a.example/five"),
                    _variant(100, 200000, url="https://a.example/ten"),
                )
            }
        ),
    )
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        table = await _wait_for_table(pilot)
        assert table.row_count == 2

        table.move_cursor(row=1)
        await pilot.pause()
        picked = screen._selected_row()  # type: ignore[attr-defined]
        assert picked is not None

        table.focus()
        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 3

        assert screen._selected_row() == picked  # type: ignore[attr-defined]


async def test_a_failed_write_is_counted_and_still_shows_the_sites_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A database that will not take the prices must not erase the site.

    The table needs nothing from sqlite, so a write failure that swallowed the
    rows would leave the footer counter stuck below the total with no reason
    given, which reads as "that site is still working" forever. The reason now
    lives in the log file, but the error count has to move, otherwise a site
    whose every write fails looks like a clean run.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _ok_result("site-a", _variant(50, 100000))})

    def explode(*args: Any, **kwargs: Any) -> int:
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr("parfum_finder.tui.search_screen.write_snapshots", explode)

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    with caplog.at_level(logging.ERROR, logger="parfum_finder"):
        async with app.run_test() as pilot:
            await pilot.pause()
            await _submit_query(pilot)
            screen = app.screen
            await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

            assert screen.query_one("#results", DataTable).row_count == 1
            await _wait_until(
                lambda: screen._errors == 1,  # type: ignore[attr-defined]
                pilot,
            )
            assert str(screen.query_one("#notices", Static).content) == ""

    assert "fiyatlar kaydedilemedi" in caplog.text
    assert "database is locked" in caplog.text


async def test_an_unreadable_result_is_counted_and_logged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A result the screen cannot read is a broken site, not a quiet skip.

    Nothing about it reaches the screen anymore, so the error count is the only
    hint that the list came back short.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _ok_result("site-a", _variant(50, 100000))})

    def explode(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("no url on that variant")

    monkeypatch.setattr("parfum_finder.tui.search_screen.snapshot_rows", explode)

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    with caplog.at_level(logging.ERROR, logger="parfum_finder"):
        async with app.run_test() as pilot:
            await pilot.pause()
            await _submit_query(pilot)
            screen = app.screen
            await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

            assert screen.query_one("#results", DataTable).row_count == 0
            assert screen._errors == 1  # type: ignore[attr-defined]
            assert str(screen.query_one("#notices", Static).content) == ""

    assert "sonuç okunamadı" in caplog.text
    assert "no url on that variant" in caplog.text


async def test_disabled_site_is_synced_but_not_scanned(tmp_path: Path) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A", enabled=False)

    calls: list[str] = []

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        calls.append(profile["id"])
        return _ok_result(profile["id"], _variant(50, 100000))

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        # Nothing enabled, so the scan is already "complete" at 0/0.
        await _wait_until(lambda: screen._total == 0, pilot)  # type: ignore[attr-defined]
        await pilot.pause()

    assert calls == []
    conn = connect(db_path)
    try:
        site_row = conn.execute(
            "SELECT enabled FROM sites WHERE site_id = 'site-a'"
        ).fetchone()
    finally:
        conn.close()
    assert site_row["enabled"] == 0


async def test_clone_row_shows_the_klon_marker_and_what_it_imitates(
    tmp_path: Path,
) -> None:
    """A clone sold instead of the searched perfume must not look like a real hit.

    matcher.match_title always hands a clone back with confident=False, so the
    percent cell already goes yellow. But without a marker on the title cell
    itself a cheap imitation would read as the cheapest real listing, and a
    person could buy the wrong bottle straight off the table.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    clone = Variant(
        size_ml_x10=50,
        raw_title="Armaf Club De Nuit Untold (Dior Sauvage EDP) Dekant",
        product_url="https://example.com/clone",
        price_kurus=50000,
        in_stock=True,
    )
    candidate = ProductCandidate(raw_title=clone.raw_title, url="https://example.com/p")
    result = SiteResult("site-a", "ok", (SearchHit(candidate, (clone,)),), "site-a: ok")
    runner = _static_runner({"site-a": result})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        table = await _wait_for_table(pilot)
        assert table.row_count == 1
        title_cell = str(table.get_row_at(0)[2])
        # The raw title survives untouched, since it is still what makes a wrong
        # match visible, with the marker appended rather than substituted in.
        assert clone.raw_title is not None
        assert clone.raw_title in title_cell
        assert "KLON ← Dior Sauvage EDP" in title_cell

        row = screen._visible_rows[0]  # type: ignore[attr-defined]
        assert row.clone_of == "Dior Sauvage EDP"


async def test_add_basket_refuses_the_one_clone_that_has_no_name_of_its_own(
    tmp_path: Path,
) -> None:
    """A clone whose own title reads as one word cannot be added, and says so.

    This is the row that was never written to perfumes, because there was no
    house and no perfume to write it as. Without the refusal in front of it the
    add would reach add_basket_item, which raises on a perfume that is not on
    record, inside a worker where nothing is left to catch it: no basket line, no
    error on screen, nothing to say the keypress went nowhere.

    No dialog either. There is no question to ask when the answer cannot be yes.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    clone = Variant(
        size_ml_x10=50,
        raw_title="Untold (Dior Sauvage EDP) Dekant",
        product_url="https://example.com/clone",
        price_kurus=50000,
        in_stock=True,
    )
    candidate = ProductCandidate(raw_title=clone.raw_title, url="https://example.com/p")
    result = SiteResult("site-a", "ok", (SearchHit(candidate, (clone,)),), "site-a: ok")
    runner = _static_runner({"site-a": result})

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        table.focus()
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()

        assert len(pilot.app.screen_stack) == 2
        conn = connect(db_path)
        try:
            assert conn.execute("SELECT * FROM basket_items").fetchall() == []
        finally:
            conn.close()

        notices = str(screen.query_one("#notices", Static).content)
        assert "bir klon" in notices
        assert "eklenemez" in notices


async def test_add_basket_asks_before_a_clone_and_files_it_under_its_own_name(
    tmp_path: Path,
) -> None:
    """A clone goes into the basket as itself, and only after being named as one.

    Both halves matter. It is stored under "armaf club de nuit untold" and not
    under the Dior Sauvage that was searched for, because a basket line filed
    under the original would be priced from other sites' real Dior listings: the
    cheap clone goes in, the expensive original comes out.

    And the dialog has to say "klon" and name what it imitates. A clone is worth
    buying on purpose, but nobody who pressed [a] on a row they read as Sauvage
    should end up with an Armaf without being told which of the two it is.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    clone = Variant(
        size_ml_x10=50,
        raw_title="Armaf Club De Nuit Untold (Dior Sauvage EDP) Dekant",
        product_url="https://example.com/clone",
        price_kurus=50000,
        in_stock=True,
    )
    candidate = ProductCandidate(raw_title=clone.raw_title, url="https://example.com/p")
    result = SiteResult("site-a", "ok", (SearchHit(candidate, (clone,)),), "site-a: ok")
    runner = _static_runner({"site-a": result})

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        table.focus()
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()

        assert len(pilot.app.screen_stack) == 3
        question = str(pilot.app.screen.query_one(Static).content)
        assert "bir klon" in question
        assert "Dior Sauvage EDP" in question

        # Declined, and nothing was written.
        await pilot.press("n")
        await pilot.pause()
        conn = connect(db_path)
        try:
            assert conn.execute("SELECT * FROM basket_items").fetchall() == []
        finally:
            conn.close()

        await pilot.press("a")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(lambda: bool(screen._basket_keys), pilot)  # type: ignore[attr-defined]

        conn = connect(db_path)
        try:
            lines = conn.execute(
                "SELECT pf.brand, pf.name FROM basket_items b"
                " JOIN perfumes pf ON pf.perfume_id = b.perfume_id"
            ).fetchall()
        finally:
            conn.close()
        assert [tuple(line) for line in lines] == [("armaf", "club de nuit untold")]


async def test_history_panel_shows_deltas_the_price_range_and_the_out_of_stock_mark(
    tmp_path: Path,
) -> None:
    """The panel exists so today's price can be judged against its own past.

    A bare list of dates and prices makes a person do the subtraction and the
    ranking by eye. Without a signed delta per reading, the oldest reading
    correctly carrying none, a min/max summary, and a mark on readings taken
    while the size was out of stock, "900.00 ₺" is just a number with nothing
    to say whether it is a good one. The range deliberately skips readings
    taken out of stock: a price nobody could have paid must not be what
    today's price is judged cheap against.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    # The newest reading: out of stock, a fall from the reading before it, and
    # the cheapest of the three, so a range that wrongly counted it would say
    # so out loud.
    runner = _static_runner(
        {"site-a": _ok_result("site-a", _variant(50, 90000, in_stock=False))}
    )

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        # The one reading here is out of stock, which the table hides by
        # default. [f] shows it again, because the history panel deliberately
        # keeps counting readings the table leaves out.
        await pilot.press("f")
        await pilot.pause()
        row = screen._visible_rows[0]  # type: ignore[attr-defined]

        # Two older readings, dated well before any real clock could produce,
        # so ordering against the search's own "now" snapshot is never in doubt.
        conn = connect(db_path)
        try:
            oldest = Variant(
                size_ml_x10=row.size_ml_x10,
                raw_title="Dior Sauvage EDP Dekant",
                product_url="https://example.com/p",
                price_kurus=100000,
                in_stock=True,
            )
            record_snapshot(
                conn,
                site_id=row.site_id,
                brand=row.brand,
                name=row.name,
                concentration=row.concentration,
                match_score=row.match_score,
                variant=oldest,
                fetched_at="2000-01-01T00:00:00Z",
            )
            middle = Variant(
                size_ml_x10=row.size_ml_x10,
                raw_title="Dior Sauvage EDP Dekant",
                product_url="https://example.com/p",
                price_kurus=125000,
                in_stock=True,
            )
            record_snapshot(
                conn,
                site_id=row.site_id,
                brand=row.brand,
                name=row.name,
                concentration=row.concentration,
                match_score=row.match_score,
                variant=middle,
                fetched_at="2000-01-02T00:00:00Z",
            )
        finally:
            conn.close()

        table = screen.query_one("#results", DataTable)
        table.focus()
        await pilot.pause()
        await pilot.press("h")
        await pilot.pause()

        panel = screen.query_one("#history-panel", Static)
        text = str(panel.content)

        # Rise from the oldest reading to the middle one.
        assert "▲ +250.00" in text
        # Fall from the middle reading to the newest (today's) one.
        assert "▼ -350.00" in text
        # The oldest reading has nothing before it, so its line carries no
        # direction marker at all.
        oldest_line = next(line for line in text.splitlines() if "2000-01-01" in line)
        assert "▲" not in oldest_line
        assert "▼" not in oldest_line
        # Today's reading was taken while the size was out of stock.
        assert "stokta yoktu" in text
        # The 900.00 reading is the cheapest of the three but was out of
        # stock, so the range floor stays at the cheapest price actually on
        # offer and the line says how many readings it covers.
        assert "min 1,000.00 ₺ · max 1,250.00 ₺ · 2/3 okuma stoktaydı" in text
        # Headed with what the history is of, so a panel left open after the
        # cursor moves is never mistaken for another row's history.
        assert row.site_label in text
        assert row.raw_title in text


async def test_the_low_confidence_dialog_can_be_answered_with_the_keyboard_alone(
    tmp_path: Path,
) -> None:
    """The confirm dialog has to look and behave like something answerable.

    Its keys always worked, but the dialog used to be a line of text naming
    them, with nothing focusable in it. Arrows and enter, which is what anyone
    reaches for first, did nothing at all and the dialog read as frozen with
    escape the only way out. Buttons make the two answers real: one holds
    focus, tab moves between them and enter presses the focused one.

    "Hayır" holds the focus at open, so a reflexive enter on a dialog nobody
    read cancels instead of putting a doubtful bottle in the basket.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    # Dior Eau Sauvage against a search for Dior Sauvage: a real match, scored
    # below the threshold, which is exactly what the dialog exists to ask about.
    title = "Dior Eau Sauvage EDP"
    variant = _variant(50, 100000, title=title)
    candidate = ProductCandidate(raw_title=title, url="https://example.com/p")
    result = SiteResult("site-a", "ok", (SearchHit(candidate, (variant,)),), "ok")
    runner = _static_runner({"site-a": result})

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]
        assert not screen._visible_rows[0].confident  # type: ignore[attr-defined]

        screen.query_one("#results", DataTable).focus()
        await pilot.pause()
        await pilot.press("a")
        await _wait_until(lambda: isinstance(app.screen, ConfirmScreen), pilot)

        # Enter on the dialog as opened cancels: nothing reaches the basket.
        assert app.focused is not None and app.focused.id == "no"
        await pilot.press("enter")
        await _wait_until(lambda: not isinstance(app.screen, ConfirmScreen), pilot)
        assert _basket_count(db_path) == 0

        # Tab to "evet" and press it, the same way with no key shortcut used.
        await pilot.press("a")
        await _wait_until(lambda: isinstance(app.screen, ConfirmScreen), pilot)
        await pilot.press("tab")
        await pilot.pause()
        assert app.focused is not None and app.focused.id == "yes"
        await pilot.press("enter")
        await _wait_until(lambda: not isinstance(app.screen, ConfirmScreen), pilot)
        await _wait_until(lambda: _basket_count(db_path) == 1, pilot)


async def test_the_low_confidence_dialog_shows_the_keys_it_answers_to(
    tmp_path: Path,
) -> None:
    """The key hints have to survive to the screen, not just exist in source.

    The labels were written with the keys in them from the start, but Textual
    reads square brackets as content markup, so "Evet [y]" rendered as "Evet "
    and the only clue the dialog answers to y and n was gone. Nothing else on
    the dialog names those keys, so a user who does not tab has no way to learn
    them. This asserts on what the button actually renders, so the same markup
    swallow gets caught if it happens to any other label here.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    title = "Dior Eau Sauvage EDP"
    candidate = ProductCandidate(raw_title=title, url="https://example.com/p")
    result = SiteResult(
        "site-a",
        "ok",
        (SearchHit(candidate, (_variant(50, 100000, title=title),)),),
        "ok",
    )
    runner = _static_runner({"site-a": result})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        screen.query_one("#results", DataTable).focus()
        await pilot.pause()
        await pilot.press("a")
        await _wait_until(lambda: isinstance(app.screen, ConfirmScreen), pilot)

        # Button parses its label into Content, so .plain is the text that
        # actually reaches the screen, markup already applied.
        labels = {
            button.id: Content.from_text(button.label).plain
            for button in app.screen.query(Button)
        }
        assert labels == {"yes": "Evet [y]", "no": "Hayır [n]"}


def _basket_count(db_path: Path) -> int:
    conn = connect(db_path)
    try:
        return int(conn.execute("SELECT count(*) FROM basket_items").fetchone()[0])
    finally:
        conn.close()


TWO_PERFUMES = "Dior Sauvage EDP - Chanel Bleu EDP"


def _named_result(site_id: str, title: str, *variants: Variant) -> SiteResult:
    candidate = ProductCandidate(raw_title=title, url="https://example.com/p")
    return SiteResult(
        site_id, "ok", (SearchHit(candidate, variants),), f"{site_id}: ok"
    )


def _per_query_runner() -> tuple[Runner, list[tuple[str, str]]]:
    """Answer each perfume with a row of its own, and record every scan asked for."""
    asked: list[tuple[str, str]] = []

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        site_id = str(profile["id"])
        asked.append((site_id, query))
        # The candidate title is what the matcher judges, so a fake answering a
        # second perfume has to name it there too, not only on the variant.
        if "chanel" in query.casefold():
            title = "Chanel Bleu EDP Dekant"
            return _named_result(site_id, title, _variant(50, 20000, title=title))
        title = "Dior Sauvage EDP Dekant"
        return _named_result(site_id, title, _variant(50, 25000, title=title))

    return runner, asked


async def test_one_line_of_two_perfumes_scans_every_site_for_both(
    tmp_path: Path,
) -> None:
    # The point of the separator. Two perfumes and two shops is four scans, and
    # the results of all four belong on one screen where they can be compared.
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    runner, asked = _per_query_runner()

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, TWO_PERFUMES)
        screen = app.screen
        await _wait_until(lambda: screen._done == 4, pilot)  # type: ignore[attr-defined]

        assert sorted(asked) == [
            ("site-a", "Chanel Bleu EDP"),
            ("site-a", "Dior Sauvage EDP"),
            ("site-b", "Chanel Bleu EDP"),
            ("site-b", "Dior Sauvage EDP"),
        ]
        table = screen.query_one("#results", DataTable)
        assert table.row_count == 4
        # Which bottle a row is about, read off the site's own title rather than
        # copied back out of the search box.
        assert str(screen.query_one("#status", Static).content).startswith("4/4")
        assert table.get_row_at(0)[0] == "Dior Sauvage EDP"


async def test_a_single_perfume_still_gets_the_matched_product_column(
    tmp_path: Path,
) -> None:
    """One query is not one product, so the column cannot be hidden for it.

    It used to appear only on multi-perfume searches, on the grounds that it
    would otherwise repeat the search text down the screen. It no longer holds
    the search text: a search for "Parfums de Marly Layton" comes back with
    Layton and Layton Exclusif, two bottles at two prices, and this column is
    what says which is which.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner, _ = _per_query_runner()

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)

        assert table.get_row_at(0)[0] == "Dior Sauvage EDP"
        assert table.get_row_at(0)[1] == "Site A"


async def test_one_shop_is_asked_for_its_perfumes_one_at_a_time(
    tmp_path: Path,
) -> None:
    # The constraint the whole scan shape exists for: a site's requests are paced
    # from one place per scan, so two of a shop's perfumes running side by side
    # would put both rate-limit gaps in parallel and hand it the burst the pacing
    # is there to prevent. Shops still run against each other in parallel.
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    inflight: dict[str, int] = {}
    overlapped: list[str] = []
    both_started = asyncio.Event()

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        site_id = str(profile["id"])
        inflight[site_id] = inflight.get(site_id, 0) + 1
        if inflight[site_id] > 1:
            overlapped.append(site_id)
        if len(inflight) == 2:
            both_started.set()
        # Held until both shops are in flight, so a scan that ran the sites one
        # after the other would fail here instead of passing quietly.
        await asyncio.wait_for(both_started.wait(), 3.0)
        inflight[site_id] -= 1
        return _ok_result(site_id, _variant(50, 25000))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, TWO_PERFUMES)
        screen = app.screen
        await _wait_until(lambda: screen._done == 4, pilot)  # type: ignore[attr-defined]

    assert overlapped == []


async def test_a_mistyped_perfume_does_not_cancel_the_ones_that_parsed(
    tmp_path: Path,
) -> None:
    # Three typed, one of them naming only a brand. Someone who mistyped one
    # wants the two that were right, and a line saying which one was not.
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner, asked = _per_query_runner()

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, "Dior Sauvage EDP - Chanel - Chanel Bleu EDP")
        screen = app.screen
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

        assert [query for _, query in asked] == ["Dior Sauvage EDP", "Chanel Bleu EDP"]
        assert "names only a brand" in str(screen.query_one("#notices", Static).content)


async def test_unparseable_query_mid_scan_takes_the_bar_down_with_it(
    tmp_path: Path,
) -> None:
    """A brand-only search sent while a scan runs must not freeze the screen.

    The second search cancels the first worker before it can lower the scanning
    flag, and then returns without starting anything. Nobody is left to end the
    scan, so the bar and the counter used to sit there for good.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")

    gate = asyncio.Event()

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        await gate.wait()
        return _ok_result(str(profile["id"]), _variant(50, 25000))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._scanning, pilot)  # type: ignore[attr-defined]

        await _submit_query(pilot, "Chanel")
        await _wait_until(lambda: not screen._scanning, pilot)  # type: ignore[attr-defined]

        assert not screen.query_one("#progress", ProgressBar).display
        assert str(screen.query_one("#status", Static).content) == ""
        assert "names only a brand" in str(screen.query_one("#notices", Static).content)

        # The abandoned scan's rows must not land either, whenever it unblocks.
        gate.set()
        await pilot.pause()
        await pilot.pause()
        assert screen.query_one("#results", DataTable).row_count == 0


async def test_more_perfumes_than_the_limit_sends_no_requests_at_all(
    tmp_path: Path,
) -> None:
    # Refused, not trimmed. Eleven perfumes across six shops is a long scan
    # against small businesses, and a search that quietly answered the first ten
    # would not say which one it dropped.
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner, asked = _per_query_runner()
    line = " - ".join(f"Marka{n} Parfum{n}" for n in range(11))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, line)
        await pilot.pause()

        assert asked == []
        notices = str(app.screen.query_one("#notices", Static).content)
        assert "en fazla 10 parfüm" in notices
        assert "11 var" in notices


async def test_the_table_stays_grouped_by_perfume_whatever_the_sort_is(
    tmp_path: Path,
) -> None:
    # Sorted by ₺/ml across both perfumes, the cheaper Chanel row would come
    # first and the table would alternate between two different bottles, which
    # is not a comparison of anything.
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner, _ = _per_query_runner()

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, TWO_PERFUMES)
        screen = app.screen
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert [table.get_row_at(i)[0] for i in range(2)] == [
            "Dior Sauvage EDP",
            "Chanel Bleu EDP",
        ]


async def test_add_basket_adds_the_perfume_the_cursor_is_actually_on(
    tmp_path: Path,
) -> None:
    # The keys read the row under the cursor out of the visible list, and a
    # multi-perfume search both groups that list and shifts every column one to
    # the right. Landing on the second group and adding the first group's bottle
    # is the mistake worth a test.
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner, _ = _per_query_runner()

    db_path = tmp_path / "db.sqlite3"
    app = _app(sites_dir, db_path, runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, TWO_PERFUMES)
        screen = app.screen
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        table.focus()
        await pilot.pause()
        await pilot.press("down")
        await pilot.pause()
        assert screen._selected_row().product == "Chanel Bleu EDP"  # type: ignore[attr-defined]
        await pilot.press("a")
        await pilot.pause()

        conn = connect(db_path)
        try:
            basket = conn.execute(
                "SELECT p.brand, p.name FROM basket_items b "
                "JOIN perfumes p ON p.perfume_id = b.perfume_id"
            ).fetchall()
        finally:
            conn.close()
        assert [tuple(row) for row in basket] == [("chanel", "bleu")]


async def test_theme_is_pinned_regardless_of_the_environment(tmp_path: Path) -> None:
    """The whole UI is tuned for one palette, so nothing outside may pick another.

    $TEXTUAL_THEME feeds the reactive's default, which is what the pre-mount
    assignment here stands in for. If someone ever moves the theme back to a
    class attribute it silently stops overriding, and this is what catches it.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    app = _app(sites_dir, tmp_path / "db.sqlite3", _static_runner({}))
    app.theme = "textual-light"

    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.theme == "textual-dark"


async def test_command_palette_offers_no_theme_switch(tmp_path: Path) -> None:
    """Closing the palette door is the other half of pinning the theme."""
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    app = _app(sites_dir, tmp_path / "db.sqlite3", _static_runner({}))

    async with app.run_test() as pilot:
        await pilot.pause()
        titles = [command.title for command in app.get_system_commands(app.screen)]

    assert "Theme" not in titles
    # The rest of the palette has to survive the filter.
    assert "Quit" in titles
    assert "Screenshot" in titles


def _two_products(site_id: str) -> SiteResult:
    """One site answering with two different bottles for one query.

    Real behaviour, not a contrivance: a search for Layton comes back with
    Layton Exclusif alongside it, at 77%, and the two are different perfumes at
    very different prices.
    """
    hits = []
    for title, price in (
        ("Parfums de Marly Layton", 30000),
        ("Parfums de Marly Layton Exclusif", 90000),
    ):
        candidate = ProductCandidate(
            raw_title=title, url=f"https://example.com/{price}"
        )
        hits.append(SearchHit(candidate, (_variant(30, price, title=title),)))
    return SiteResult(site_id, "ok", tuple(hits), f"{site_id}: ok")


async def test_site_blocks_are_ordered_by_what_the_small_bottles_cost(
    tmp_path: Path,
) -> None:
    """A shop that only sells big bottles cannot win on ₺/ml alone.

    ₺/ml always falls as the bottle grows, so ranking sites on their best ₺/ml
    would hand the top of every block to whoever sells the largest decant. The
    band is what a decant buyer is actually choosing between, and a site with
    nothing in it is not cheaper, it is answering a different question.
    """
    sites_dir = tmp_path / "sites"
    for site_id, name in (
        ("site-a", "Site A"),
        ("site-b", "Site B"),
        ("site-c", "Site C"),
    ):
        _write_profile(sites_dir, site_id, name)

    title = "Dior Sauvage EDP Dekant"
    runner = _static_runner(
        {
            # 3 ml at 200 ₺/ml.
            "site-a": _named_result("site-a", title, _variant(30, 60000, title=title)),
            # 3 ml at 100 ₺/ml: the cheapest small bottle in the scan.
            "site-b": _named_result("site-b", title, _variant(30, 30000, title=title)),
            # Nothing under 10 ml, at 50 ₺/ml: the cheapest ₺/ml in the scan, and
            # still last, because nobody comparing 3 ml decants can buy it.
            "site-c": _named_result("site-c", title, _variant(100, 50000, title=title)),
        }
    )

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)

        assert [str(table.get_row_at(i)[1]) for i in range(3)] == [
            "Site B",
            "Site A",
            "Site C",
        ]


async def test_showing_the_hidden_rows_does_not_reshuffle_the_site_blocks(
    tmp_path: Path,
) -> None:
    """Block order is a property of the scan, not of what is on screen.

    Computed from the visible rows, [f] would reorder the whole table under
    someone who pressed it to check one thing, and pressing it again would give
    a third order. So the ranking reads every row whose price was readable,
    including the ones [f] is hiding.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")

    title = "Dior Sauvage EDP Dekant"
    runner = _static_runner(
        {
            # Its cheapest small bottle is out of stock, so with [f] off the only
            # site-a row on screen is a 5 ml -- outside the band entirely.
            "site-a": _named_result(
                "site-a",
                title,
                _variant(30, 30000, in_stock=False, title=title),
                _variant(50, 100000, title=title),
            ),
            "site-b": _named_result("site-b", title, _variant(30, 45000, title=title)),
        }
    )

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)

        hidden = [str(table.get_row_at(i)[1]) for i in range(table.row_count)]
        assert hidden == ["Site A", "Site B"]

        table.focus()
        await pilot.press("f")
        await pilot.pause()
        shown = [str(table.get_row_at(i)[1]) for i in range(table.row_count)]
        assert shown == ["Site A", "Site A", "Site B"]


async def test_one_query_finding_two_bottles_gets_two_blocks(tmp_path: Path) -> None:
    """Layton and Layton Exclusif are two perfumes, whatever was typed.

    Grouping on the search text would drop both into one block, where the
    Exclusif's higher price would read as this shop being expensive for Layton.
    The heading comes off each site's own title for exactly that reason.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _two_products("site-a")})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, "Parfums de Marly Layton")
        table = await _wait_for_table(pilot)

        assert [str(table.get_row_at(i)[0]) for i in range(2)] == [
            "Parfums De Marly Layton",
            "Parfums De Marly Layton Exclusif",
        ]
        # The Exclusif really is the 77% row the split exists for.
        assert str(table.get_row_at(1)[7]) == "77"


async def test_picking_a_column_keeps_the_product_blocks(tmp_path: Path) -> None:
    """Sorting drops the site layer, never the product layer.

    Sorted across products the cheapest Layton and the cheapest Exclusif would
    alternate down the screen, and a column of ₺/ml where consecutive rows are
    different bottles ranks nothing.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _two_products("site-a")})

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot, "Parfums de Marly Layton")
        table = await _wait_for_table(pilot)

        table.focus()
        await pilot.press("3")
        await pilot.pause()
        # The Exclusif is three times the price, so a table sorted by ₺/ml with
        # no product layer would put the Layton row first and leave it there.
        assert [str(table.get_row_at(i)[0]) for i in range(2)] == [
            "Parfums De Marly Layton",
            "Parfums De Marly Layton Exclusif",
        ]


async def test_a_second_search_replaces_the_first_and_not_its_columns(
    tmp_path: Path,
) -> None:
    """Searching again has to leave one table, with one set of headings.

    The columns are added once, at mount, now that they no longer depend on how
    many perfumes were typed. A second search that added them again would leave
    sixteen headings and shift every cell the keys read by eight.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")

    title = "Dior Sauvage EDP Dekant"
    other = "Chanel Bleu EDP Dekant"

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        if "chanel" in query.casefold():
            return _named_result("site-a", other, _variant(30, 20000, title=other))
        return _named_result("site-a", title, _variant(30, 60000, title=title))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        table = await _wait_for_table(pilot)
        assert table.row_count == 1
        assert len(table.columns) == 8

        await _submit_query(pilot, "Chanel Bleu EDP")
        # Waited on by content, not by the scanning flag: one fake site finishes
        # inside a single frame, so the flag can go up and down between polls.
        screen: Any = app.screen
        await _wait_until(
            lambda: (
                bool(screen._visible_rows)
                and screen._visible_rows[0].product == "Chanel Bleu EDP"
            ),
            pilot,
        )

        # The first search's row is gone, not sitting above the second's.
        assert table.row_count == 1
        assert table.get_row_at(0)[0] == "Chanel Bleu EDP"
        assert len(table.columns) == 8
