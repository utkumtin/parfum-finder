"""Tests for the search screen: streaming, persistence, and the key bindings.

A fake runner stands in for engine.run_site everywhere -- these tests never
touch the network. Some fake runners are gated on an asyncio.Event so a test
can force sites to finish out of order, which is the one thing a test that
only checks the final table can never catch.
"""

import asyncio
import json
import sqlite3
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
from textual.widgets import DataTable, Input, Static

from parfum_finder.engine import ProductCandidate, SearchHit, SiteResult, Variant
from parfum_finder.store import connect
from parfum_finder.tui.app import ParfumFinderApp

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


Runner = Callable[[dict[str, Any], str], Awaitable[SiteResult]]


def _static_runner(results: dict[str, SiteResult]) -> Runner:
    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
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


async def _wait_until(
    predicate: Callable[[], bool], pilot: Any, timeout_s: float = 3.0
) -> None:
    async def poll() -> None:
        while not predicate():
            await pilot.pause()

    await asyncio.wait_for(poll(), timeout_s)


async def test_streaming_lands_out_of_order_rows_before_pending_site_resolves(
    tmp_path: Path,
) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")
    _write_profile(sites_dir, "site-c", "Site C")

    gate = asyncio.Event()

    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
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
        assert screen._done == 2  # type: ignore[attr-defined]

        status = screen.query_one("#status", Static)
        assert "2/3" in str(status.content)

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 2
        # Ürün is the site's raw title, untouched -- it is what makes a wrong
        # match visible, so nothing here may tidy it up.
        assert table.get_row_at(0)[1] == "Dior Sauvage EDP Dekant 5 ml"

        gate.set()
        await _wait_until(lambda: screen._done == 3, pilot)  # type: ignore[attr-defined]
        assert table.row_count == 3
        assert "3/3" in str(screen.query_one("#status", Static).content)


async def test_one_site_erroring_does_not_block_the_others(tmp_path: Path) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")

    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
        if profile["id"] == "site-a":
            raise RuntimeError("boom")
        return _ok_result("site-b", _variant(50, 25000))

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 1
        assert screen._errors == 1  # type: ignore[attr-defined]
        notices = str(screen.query_one("#notices", Static).content)
        assert "⚠ site-a" in notices
        assert "bağlantı hatası" in notices


async def test_suspect_site_shows_notice_and_contributes_no_rows(
    tmp_path: Path,
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
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 0
        notices = str(screen.query_one("#notices", Static).content)
        assert notices == (
            "⚠ site-a — profil bozulmuş olabilir: "
            "the 'css' layer read no priced size from 3 hits"
        )
        assert screen._errors == 1  # type: ignore[attr-defined]


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
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        site_cell = str(table.get_row_at(0)[0])
        assert "⏳" in site_cell
        assert "gün önce keşfedildi" in site_cell


async def test_low_score_row_flags_the_match_percent_cell(tmp_path: Path) -> None:
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
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        from rich.text import Text

        percent_cell = screen.query_one("#results", DataTable).get_row_at(0)[6]
        assert isinstance(percent_cell, Text)
        assert percent_cell.style == "bold yellow"
        assert str(percent_cell) == "31"


async def test_default_sort_is_price_per_ml_ascending_and_keys_reorder(
    tmp_path: Path,
) -> None:
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
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.get_row_at(0)[2] == "10 ml"  # cheaper per ml first, default sort

        table.focus()
        await pilot.pause()
        await pilot.press("1")
        await pilot.pause()
        assert table.get_row_at(0)[2] == "5 ml"  # ml ascending

        await pilot.press("2")
        await pilot.pause()
        assert table.get_row_at(0)[2] == "5 ml"  # price ascending (1500 < 2000)

        await pilot.press("3")
        await pilot.pause()
        assert table.get_row_at(0)[2] == "10 ml"  # back to ₺/ml ascending


async def test_f_toggles_hiding_out_of_stock_rows(tmp_path: Path) -> None:
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
        assert table.row_count == 2

        table.focus()
        await pilot.pause()
        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 1

        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 2


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
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        assert table.row_count == 2

        await pilot.press("f")
        await pilot.pause()
        assert table.row_count == 1

        await pilot.press("1")
        await pilot.pause()
        assert table.get_row_at(0)[2] == "5 ml"

        # Escape is the way back to the search box for the next query.
        await pilot.press("escape")
        await pilot.pause()
        assert screen.query_one("#query", Input).has_focus


async def test_a_late_site_landing_does_not_move_the_cursor_off_the_picked_row(
    tmp_path: Path,
) -> None:
    """The row under the cursor has to survive a slower site arriving.

    Rebuilding the table sends the cursor back to the top, so without
    re-seeking, a person who picked a row mid-scan would press [a] and add a
    different perfume than the one they were looking at. That is the exact
    mistake the raw-title column exists to prevent, so it cannot be allowed in
    through the back door.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    _write_profile(sites_dir, "site-b", "Site B")

    gate = asyncio.Event()

    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
        if profile["id"] == "site-b":
            await gate.wait()
            return _ok_result("site-b", _variant(30, 60000, url="https://b.example/p"))
        return _ok_result(
            "site-a",
            _variant(50, 150000, url="https://a.example/five"),
            _variant(100, 200000, url="https://a.example/ten"),
        )

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        table = screen.query_one("#results", DataTable)
        table.move_cursor(row=1)
        await pilot.pause()
        picked = screen._selected_row()  # type: ignore[attr-defined]
        assert picked is not None

        gate.set()
        await _wait_until(lambda: screen._done == 2, pilot)  # type: ignore[attr-defined]
        assert table.row_count == 3

        assert screen._selected_row() == picked  # type: ignore[attr-defined]


async def test_a_failed_write_is_reported_and_still_shows_the_sites_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A database that will not take the prices must not erase the site.

    The table needs nothing from sqlite, so a write failure that swallowed the
    rows would leave the footer counter stuck below the total with no reason
    given, which reads as "that site is still working" forever.
    """
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A")
    runner = _static_runner({"site-a": _ok_result("site-a", _variant(50, 100000))})

    def explode(*args: Any, **kwargs: Any) -> int:
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr("parfum_finder.tui.search_screen.write_snapshots", explode)

    app = _app(sites_dir, tmp_path / "db.sqlite3", runner)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _submit_query(pilot)
        screen = app.screen
        await _wait_until(lambda: screen._done == 1, pilot)  # type: ignore[attr-defined]

        assert screen.query_one("#results", DataTable).row_count == 1
        await _wait_until(
            lambda: (
                "kaydedilemedi" in str(screen.query_one("#notices", Static).content)
            ),
            pilot,
        )
        notices = str(screen.query_one("#notices", Static).content)
        assert "⚠ site-a — fiyatlar kaydedilemedi" in notices
        assert "database is locked" in notices


async def test_disabled_site_is_synced_but_not_scanned(tmp_path: Path) -> None:
    sites_dir = tmp_path / "sites"
    _write_profile(sites_dir, "site-a", "Site A", enabled=False)

    calls: list[str] = []

    async def runner(profile: dict[str, Any], query: str) -> SiteResult:
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
