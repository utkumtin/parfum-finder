"""Tests for parfum_finder.services.scan: the event stream a fake SiteRunner
drives, with no Textual and no network in it.

A fake runner stands in for engine.run_site throughout, keyed by site_id so
each test can script a different site's answer. The database is a real
tmp_path sqlite file, seeded through store's own writers, so a cache-hit test
can only set up a state a real scan could actually have produced.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from parfum_finder.basket import build_basket_rows
from parfum_finder.engine import (
    ProductCandidate,
    SearchHit,
    SiteResult,
    SiteRunner,
    Variant,
)
from parfum_finder.matcher import PerfumeQuery
from parfum_finder.profiles import sync_to_db
from parfum_finder.services.scan import (
    BasketPriceExcluded,
    BasketRefreshFinished,
    BasketRefreshStarted,
    BasketRowFinished,
    BasketWriteFailed,
    RowsReady,
    ScanFinished,
    Search,
    SiteFinished,
    run_basket_refresh,
    run_scan,
)
from parfum_finder.store import (
    BasketLine,
    BasketPrice,
    connect,
    now_iso,
    record_snapshot,
)


def _profile(
    site_id: str, name: str = "Site", *, enabled: bool = True
) -> dict[str, Any]:
    return {
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
        "discovered_at": now_iso(),
        "needs_review": [],
    }


def _search(index: int, text: str = "Dior Sauvage EDP") -> Search:
    return Search(
        index=index, text=text, query=PerfumeQuery(brand="dior", name="sauvage")
    )


def _variant(price_kurus: int | None = 25000) -> Variant:
    return Variant(
        size_ml_x10=50,
        raw_title="Dior Sauvage EDP Dekant 5 ml",
        product_url="https://example.com/p",
        price_kurus=price_kurus,
        in_stock=True,
    )


def _ok_result(site_id: str) -> SiteResult:
    candidate = ProductCandidate(
        raw_title="Dior Sauvage EDP Dekant", url="https://example.com/p"
    )
    hit = SearchHit(candidate, (_variant(),))
    return SiteResult(site_id, "ok", (hit,), f"{site_id}: ok")


def _static_runner(results: dict[str, SiteResult]) -> SiteRunner:
    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        return results[profile["id"]]

    return runner


async def _collect(gen: Any) -> list[Any]:
    return [event async for event in gen]


async def test_run_scan_reports_a_plain_single_site_scan(tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite3"
    profiles = [_profile("site-a", "Site A")]
    runner = _static_runner({"site-a": _ok_result("site-a")})
    conn = connect(db_path)
    try:
        sync_to_db(conn, profiles, synced_at=now_iso())
    finally:
        conn.close()

    events = await _collect(
        run_scan(
            [_search(0)],
            profiles,
            runner=runner,
            db_path=db_path,
            write_lock=asyncio.Lock(),
        )
    )

    assert [type(e).__name__ for e in events] == [
        "ScanStarted",
        "SiteStarted",
        "RowsReady",
        "SiteFinished",
        "ScanFinished",
    ]
    started, _site_started, rows_ready, finished, scan_finished = events
    assert (started.total_sites, started.total_perfumes) == (1, 1)
    assert rows_ready.rows[0].site_id == "site-a"
    assert (finished.site_id, finished.status, finished.has_rows) == (
        "site-a",
        "ok",
        True,
    )
    assert scan_finished.error_count == 0


async def test_run_scan_skips_the_shops_for_a_cached_perfume(tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite3"
    profiles = [_profile("site-a", "Site A")]
    conn = connect(db_path)
    try:
        sync_to_db(conn, profiles, synced_at=now_iso())
        record_snapshot(
            conn,
            site_id="site-a",
            brand="dior",
            name="sauvage",
            concentration="",
            match_score=97,
            variant=_variant(),
        )
    finally:
        conn.close()

    calls: list[str] = []

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        calls.append(profile["id"])
        return _ok_result(profile["id"])

    events = await _collect(
        run_scan(
            [_search(0)],
            profiles,
            runner=runner,
            db_path=db_path,
            write_lock=asyncio.Lock(),
        )
    )

    assert calls == []  # the cache answered it, nobody went to the shop
    assert [type(e).__name__ for e in events] == [
        "ScanStarted",
        "CacheHit",
        "RowsReady",
        "ScanFinished",
    ]
    started, cache_hit, rows_ready, _finished = events
    assert started.total_perfumes == 0
    assert cache_hit.query_index == 0
    assert rows_ready.rows[0].site_id == "site-a"


async def test_a_site_listing_the_same_size_twice_yields_one_row(
    tmp_path: Path,
) -> None:
    """A search page that lists the same bottle under two listings (an
    overlapping page, the same product under two categories) must not turn
    into two rows for one size: `product_variants` is unique per size on
    write, and the live table has to agree with what a reload of the same
    search will show once that write lands.
    """
    db_path = tmp_path / "db.sqlite3"
    profiles = [_profile("site-a", "Site A")]
    conn = connect(db_path)
    try:
        sync_to_db(conn, profiles, synced_at=now_iso())
    finally:
        conn.close()

    def _hit(price_kurus: int, url: str) -> SearchHit:
        candidate = ProductCandidate(raw_title="Dior Sauvage EDP Dekant", url=url)
        variant = Variant(
            size_ml_x10=50,
            raw_title="Dior Sauvage EDP Dekant 5 ml",
            product_url=url,
            price_kurus=price_kurus,
            in_stock=True,
        )
        return SearchHit(candidate, (variant,))

    result = SiteResult(
        "site-a",
        "ok",
        (_hit(25000, "https://example.com/p1"), _hit(27000, "https://example.com/p2")),
        "site-a: ok",
    )
    runner = _static_runner({"site-a": result})

    events = await _collect(
        run_scan(
            [_search(0)],
            profiles,
            runner=runner,
            db_path=db_path,
            write_lock=asyncio.Lock(),
        )
    )

    rows_ready = next(e for e in events if isinstance(e, RowsReady))
    assert len(rows_ready.rows) == 1
    # The later listing on the page is the one storage will also end up
    # showing, since `write_snapshots` stamps every row in the batch with
    # one timestamp and breaks the tie by write order.
    assert rows_ready.rows[0].price_kurus == 27000

    # The write side has to agree, or a duplicate listing costs a wasted row
    # in the price history every time this perfume is scanned.
    conn = connect(db_path)
    try:
        written = conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0]
    finally:
        conn.close()
    assert written == 1


async def test_run_scan_force_bypasses_the_cache(tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite3"
    profiles = [_profile("site-a", "Site A")]
    conn = connect(db_path)
    try:
        sync_to_db(conn, profiles, synced_at=now_iso())
        record_snapshot(
            conn,
            site_id="site-a",
            brand="dior",
            name="sauvage",
            concentration="",
            match_score=97,
            variant=_variant(),
        )
    finally:
        conn.close()

    calls: list[str] = []

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        calls.append(profile["id"])
        return _ok_result(profile["id"])

    events = await _collect(
        run_scan(
            [_search(0)],
            profiles,
            runner=runner,
            db_path=db_path,
            write_lock=asyncio.Lock(),
            force=True,
        )
    )

    assert calls == ["site-a"]
    assert "CacheHit" not in [type(e).__name__ for e in events]


async def test_a_runner_exception_is_reported_as_a_site_finished_error(
    tmp_path: Path,
) -> None:
    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        raise RuntimeError("boom")

    events = await _collect(
        run_scan(
            [_search(0)],
            [_profile("site-a", "Site A")],
            runner=runner,
            db_path=tmp_path / "db.sqlite3",
            write_lock=asyncio.Lock(),
        )
    )

    finished = next(e for e in events if isinstance(e, SiteFinished))
    assert finished.status == "error"
    assert finished.detail is not None and "boom" in finished.detail
    assert finished.has_rows is False
    scan_finished = next(e for e in events if isinstance(e, ScanFinished))
    assert scan_finished.error_count == 1


async def test_a_write_failure_still_reports_the_rows_and_counts_as_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("database is locked")

    monkeypatch.setattr("parfum_finder.services.scan.write_snapshots", explode)

    events = await _collect(
        run_scan(
            [_search(0)],
            [_profile("site-a", "Site A")],
            runner=_static_runner({"site-a": _ok_result("site-a")}),
            db_path=tmp_path / "db.sqlite3",
            write_lock=asyncio.Lock(),
        )
    )

    assert "WriteFailed" in [type(e).__name__ for e in events]
    assert any(isinstance(e, RowsReady) for e in events)  # rows still reached it
    scan_finished = next(e for e in events if isinstance(e, ScanFinished))
    assert scan_finished.error_count == 1


async def test_a_disabled_site_is_never_asked(tmp_path: Path) -> None:
    calls: list[str] = []

    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        calls.append(profile["id"])
        return _ok_result(profile["id"])

    events = await _collect(
        run_scan(
            [_search(0)],
            [_profile("site-a", "Site A", enabled=False)],
            runner=runner,
            db_path=tmp_path / "db.sqlite3",
            write_lock=asyncio.Lock(),
        )
    )

    assert calls == []
    assert [type(e).__name__ for e in events] == ["ScanStarted", "ScanFinished"]


# -- run_basket_refresh -------------------------------------------------


def _basket_row(basket_item_id: int = 1) -> Any:
    line = BasketLine(
        basket_item_id=basket_item_id,
        perfume_id=1,
        brand="dior",
        name="sauvage",
        concentration="EDP",
        size_ml_x10=50,
        qty=1,
        added_at=now_iso(),
    )
    return build_basket_rows(
        [line], [BasketPrice(basket_item_id, "site-a", 25000, True, now_iso())]
    )[0]


async def test_run_basket_refresh_excludes_a_suspect_site_with_a_notice(
    tmp_path: Path,
) -> None:
    suspect = SiteResult("site-a", "suspect", (), "site-a: broken")
    events = await _collect(
        run_basket_refresh(
            [_basket_row()],
            [_profile("site-a", "Site A")],
            runner=_static_runner({"site-a": suspect}),
            db_path=tmp_path / "db.sqlite3",
            write_lock=asyncio.Lock(),
        )
    )

    excluded = next(e for e in events if isinstance(e, BasketPriceExcluded))
    assert excluded.notice is not None and "tazelenemedi" in excluded.notice
    assert isinstance(events[-1], BasketRefreshFinished)
    assert isinstance(events[0], BasketRefreshStarted)
    assert any(isinstance(e, BasketRowFinished) for e in events)


async def test_run_basket_refresh_excludes_an_empty_answer_silently(
    tmp_path: Path,
) -> None:
    empty = SiteResult("site-a", "empty", (), None)
    events = await _collect(
        run_basket_refresh(
            [_basket_row()],
            [_profile("site-a", "Site A")],
            runner=_static_runner({"site-a": empty}),
            db_path=tmp_path / "db.sqlite3",
            write_lock=asyncio.Lock(),
        )
    )

    excluded = next(e for e in events if isinstance(e, BasketPriceExcluded))
    assert excluded.notice is None


async def test_run_basket_refresh_write_failure_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("database is locked")

    monkeypatch.setattr("parfum_finder.services.scan.write_snapshots", explode)

    events = await _collect(
        run_basket_refresh(
            [_basket_row()],
            [_profile("site-a", "Site A")],
            runner=_static_runner({"site-a": _ok_result("site-a")}),
            db_path=tmp_path / "db.sqlite3",
            write_lock=asyncio.Lock(),
        )
    )

    failed = next(e for e in events if isinstance(e, BasketWriteFailed))
    assert "database is locked" in failed.notice
