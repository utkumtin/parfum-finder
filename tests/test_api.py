"""Tests for parfum_finder.api: FastAPI TestClient, a fake SiteRunner, a
temp sqlite file.

The app's own profile loading (`create_app`'s lifespan) globs a real
`sites_dir` for `*.json` files, so tests that need a profile in
`app.state.parfum.profiles` write one to a tmp directory rather than
injecting it after startup -- the same path `sync_to_db` runs at boot takes.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketDisconnect

from parfum_finder.api.app import create_app
from parfum_finder.engine import (
    ProductCandidate,
    SearchHit,
    SiteResult,
    SiteRunner,
    Variant,
)
from parfum_finder.matcher import MAX_QUERIES, QUERY_SEPARATOR_PATTERN
from parfum_finder.store import STALE_PRICE_DAYS, now_iso
from parfum_finder.updater import DownloadProgress, UpdateDownload

_PROFILE_TEMPLATE: dict[str, Any] = {
    "schema_version": 1,
    "id": "site-a",
    "name": "Site A",
    "base_url": "https://example.com",
    "enabled": True,
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
    "discovered_at": "2026-08-01T00:00:00Z",
    "needs_review": [],
}


def _write_profile(sites_dir: Path, **overrides: Any) -> None:
    profile = {**_PROFILE_TEMPLATE, **overrides}
    (sites_dir / f"{profile['id']}.json").write_text(json.dumps(profile))


def _ok_result(
    site_id: str,
    *,
    score_title: str = "Dior Sauvage EDP Dekant",
    price_kurus: int = 25_000,
    size_ml_x10: int = 50,
) -> SiteResult:
    candidate = ProductCandidate(raw_title=score_title, url="https://example.com/p")
    variant = Variant(
        size_ml_x10=size_ml_x10,
        raw_title=f"{score_title} {size_ml_x10 / 10:g} ml",
        product_url="https://example.com/p",
        price_kurus=price_kurus,
        in_stock=True,
    )
    hit = SearchHit(candidate, (variant,))
    return SiteResult(site_id, "ok", (hit,), f"{site_id}: ok")


def _static_runner(results: dict[str, SiteResult]) -> SiteRunner:
    async def runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
        return results[profile["id"]]

    return runner


@pytest.fixture
def sites_dir(tmp_path: Path) -> Path:
    d = tmp_path / "sites"
    d.mkdir()
    return d


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "db.sqlite3"


def _client(
    sites_dir: Path, db_path: Path, runner: Any
) -> Iterator[tuple[TestClient, str]]:
    app = create_app(sites_dir=sites_dir, db_path=db_path, runner=runner)
    with TestClient(app) as client:
        yield client, app.state.parfum.auth_token


@pytest.fixture
def client(sites_dir: Path, db_path: Path) -> Iterator[tuple[TestClient, str]]:
    runner = _static_runner({"site-a": _ok_result("site-a")})
    yield from _client(sites_dir, db_path, runner)


def _auth(token: str) -> dict[str, str]:
    return {"X-Auth-Token": token}


# -- auth ---------------------------------------------------------------


def test_missing_token_is_rejected(client: tuple[TestClient, str]) -> None:
    c, _token = client
    response = c.get("/api/sites")
    assert response.status_code == 401


def test_wrong_token_is_rejected(client: tuple[TestClient, str]) -> None:
    c, _token = client
    response = c.get("/api/sites", headers=_auth("not-the-token"))
    assert response.status_code == 401


def test_an_explicit_token_is_the_one_that_works(
    sites_dir: Path, db_path: Path
) -> None:
    app = create_app(
        sites_dir=sites_dir,
        db_path=db_path,
        runner=_static_runner({}),
        auth_token="chosen-by-the-caller",
    )
    with TestClient(app) as c:
        assert (
            c.get("/api/sites", headers=_auth("chosen-by-the-caller")).status_code
            == 200
        )


def test_the_token_env_var_is_read_when_no_token_is_passed(
    sites_dir: Path, db_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The development path: uvicorn and the Vite dev server are two processes
    # that only share an environment.
    monkeypatch.setenv("PARFUM_FINDER_TOKEN", "from-the-environment")
    app = create_app(sites_dir=sites_dir, db_path=db_path, runner=_static_runner({}))
    with TestClient(app) as c:
        assert (
            c.get("/api/sites", headers=_auth("from-the-environment")).status_code
            == 200
        )


# -- static frontend -------------------------------------------------------


def test_no_ui_build_leaves_the_api_untouched(
    sites_dir: Path, db_path: Path, tmp_path: Path
) -> None:
    # A fresh checkout (and the Linux CI job) never runs `npm run build`, so
    # the directory this points at has no index.html: the mount must be
    # skipped rather than raising, and "/api/*" must not have been shadowed
    # by a "/" route that was never registered.
    app = create_app(
        sites_dir=sites_dir,
        db_path=db_path,
        runner=_static_runner({}),
        ui_dir=tmp_path / "no-such-ui-build",
        auth_token="the-token",
    )
    with TestClient(app) as c:
        assert c.get("/api/config", headers=_auth("the-token")).status_code == 200
        assert c.get("/").status_code == 404


def test_the_ui_build_is_served_with_the_token_injected(
    sites_dir: Path, db_path: Path, tmp_path: Path
) -> None:
    ui_dir = tmp_path / "ui"
    (ui_dir / "assets").mkdir(parents=True)
    (ui_dir / "index.html").write_text(
        "<html><head><title>t</title></head><body></body></html>"
    )
    (ui_dir / "assets" / "index.js").write_text("console.log('ui')")
    app = create_app(
        sites_dir=sites_dir,
        db_path=db_path,
        runner=_static_runner({}),
        ui_dir=ui_dir,
        auth_token="the-token",
    )
    with TestClient(app) as c:
        # "/api/*" still works with a mount registered: the mount must not
        # have shadowed it.
        assert c.get("/api/config", headers=_auth("the-token")).status_code == 200
        index = c.get("/")
        assert index.status_code == 200
        assert 'window.__PARFUM_TOKEN__="the-token";' in index.text
        assert c.get("/assets/index.js").status_code == 200


# -- config ---------------------------------------------------------------


def test_config_publishes_the_constants_a_client_would_otherwise_copy(
    client: tuple[TestClient, str],
) -> None:
    # Every value here has a Python definition the display layer must agree
    # with. A frontend hardcoding any of them is the drift this endpoint exists
    # to prevent, so the test asserts against the imported constants, not
    # against numbers typed here a second time.
    c, token = client
    response = c.get("/api/config", headers=_auth(token))
    assert response.status_code == 200
    assert response.json() == {
        "stale_price_days": STALE_PRICE_DAYS,
        "max_queries": MAX_QUERIES,
        "query_separator_pattern": QUERY_SEPARATOR_PATTERN,
    }


# -- sites ----------------------------------------------------------------


def test_list_sites_flags_a_stale_profile(sites_dir: Path, db_path: Path) -> None:
    _write_profile(sites_dir, id="site-a", discovered_at="2020-01-01T00:00:00Z")
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        response = c.get("/api/sites", headers=_auth(token))
        assert response.status_code == 200
        [site] = response.json()
        assert site["id"] == "site-a"
        assert site["needs_review"] is True


def test_list_sites_does_not_flag_a_fresh_profile(
    sites_dir: Path, db_path: Path
) -> None:
    _write_profile(sites_dir, id="site-a", discovered_at=now_iso())
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        [site] = c.get("/api/sites", headers=_auth(token)).json()
        assert site["needs_review"] is False


# -- search -----------------------------------------------------------------


def test_search_rejects_an_unparseable_query(client: tuple[TestClient, str]) -> None:
    c, token = client
    response = c.post("/api/search", json={"query": "###"}, headers=_auth(token))
    assert response.status_code == 422


def test_search_rejects_more_than_max_queries(client: tuple[TestClient, str]) -> None:
    c, token = client
    query = " - ".join(f"Brand{i} Perfume{i}" for i in range(11))
    response = c.post("/api/search", json={"query": query}, headers=_auth(token))
    assert response.status_code == 422


def test_search_names_the_perfume_behind_each_query_index(
    client: tuple[TestClient, str],
) -> None:
    # The scan events only ever carry query_index, so this list is the only
    # thing that lets a warning say which perfume it is about. A rejected part
    # shifts the indexes, which is why the index is sent rather than implied by
    # position in the typed line.
    c, token = client
    response = c.post(
        "/api/search",
        json={"query": "### - Dior Sauvage EDP - Creed Aventus"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    assert response.json()["searches"] == [
        {"index": 0, "text": "Dior Sauvage EDP"},
        {"index": 1, "text": "Creed Aventus"},
    ]


def test_search_streams_events_and_results_are_readable_after(
    sites_dir: Path, db_path: Path
) -> None:
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        started = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        )
        assert started.status_code == 200
        search_id = started.json()["search_id"]

        with c.websocket_connect(f"/api/search/{search_id}?token={token}") as ws:
            events = []
            while True:
                event = ws.receive_json()
                events.append(event)
                if event["type"] == "scan_finished":
                    break

        types = [e["type"] for e in events]
        assert "scan_started" in types
        assert "rows_ready" in types
        assert types[-1] == "scan_finished"

        results = c.get(f"/api/results/{search_id}", headers=_auth(token))
        assert results.status_code == 200
        body = results.json()
        assert body["finished"] is True
        rows = body["rows"]
        assert len(rows) == 1
        assert rows[0]["site_id"] == "site-a"
        assert rows[0]["display_title"] == "Dior Sauvage EDP Dekant 5 ml"
        assert rows[0]["price_per_ml_kurus"] == "5000"


def test_results_is_not_finished_before_the_stream_is_read(
    sites_dir: Path, db_path: Path
) -> None:
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        search_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]
        results = c.get(f"/api/results/{search_id}", headers=_auth(token))
        assert results.json() == {
            "rows": [],
            "hidden_out_of_stock": 0,
            "finished": False,
        }


def test_a_second_search_for_the_same_perfume_is_answered_from_cache(
    sites_dir: Path, db_path: Path
) -> None:
    """The plan's whole cache-first design: a perfume scanned once has a
    price on record, and a second search for it never touches the shops
    again -- run_scan yields CacheHit + RowsReady instead of asking `runner`.
    """
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        first_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]
        with c.websocket_connect(f"/api/search/{first_id}?token={token}") as ws:
            while ws.receive_json()["type"] != "scan_finished":
                pass

        second_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]
        with c.websocket_connect(f"/api/search/{second_id}?token={token}") as ws:
            events = []
            while True:
                event = ws.receive_json()
                events.append(event)
                if event["type"] == "scan_finished":
                    break

        assert "cache_hit" in [e["type"] for e in events]
        rows = c.get(f"/api/results/{second_id}", headers=_auth(token)).json()["rows"]
        assert len(rows) == 1
        assert rows[0]["site_id"] == "site-a"


def test_search_stream_refuses_a_second_connect(sites_dir: Path, db_path: Path) -> None:
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        search_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]

        with c.websocket_connect(f"/api/search/{search_id}?token={token}") as ws:
            while ws.receive_json()["type"] != "scan_finished":
                pass

        with pytest.raises(WebSocketDisconnect) as excinfo:
            with c.websocket_connect(f"/api/search/{search_id}?token={token}") as ws:
                ws.receive_json()
        assert excinfo.value.code == 4409


def test_search_stream_refuses_a_bad_token(sites_dir: Path, db_path: Path) -> None:
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        search_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]

        with pytest.raises(WebSocketDisconnect) as excinfo:
            with c.websocket_connect(f"/api/search/{search_id}?token=wrong") as ws:
                ws.receive_json()
        assert excinfo.value.code == 4401


def test_search_stream_refuses_an_unknown_search_id(
    client: tuple[TestClient, str],
) -> None:
    c, token = client
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with c.websocket_connect(f"/api/search/does-not-exist?token={token}") as ws:
            ws.receive_json()
    assert excinfo.value.code == 4404


def test_results_rejects_an_unknown_sort_key(sites_dir: Path, db_path: Path) -> None:
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        search_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]
        response = c.get(
            f"/api/results/{search_id}?sort=nonsense", headers=_auth(token)
        )
        assert response.status_code == 422


def test_results_404s_for_an_unknown_search_id(client: tuple[TestClient, str]) -> None:
    c, token = client
    response = c.get("/api/results/does-not-exist", headers=_auth(token))
    assert response.status_code == 404


# -- wishlist ---------------------------------------------------------------


def _wishlist_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "site_id": "site-a",
        "site_label": "Site A",
        "query_index": 0,
        "product": "Dior Sauvage EDP",
        "raw_title": "Dior Sauvage EDP 5 ml",
        "size_ml_x10": 50,
        "price_kurus": 25_000,
        "price_per_ml_kurus": "5000",
        "in_stock": True,
        "match_score": 95,
        "confident": True,
        "brand": "dior",
        "name": "sauvage",
        "concentration": "EDP",
        "product_url": "https://example.com/sauvage",
        "clone_of": "",
        "own_identity": True,
        "age_days": 0,
    }
    row.update(overrides)
    return row


def test_wishlist_crud_is_idempotent_and_preserves_saved_order(
    sites_dir: Path, db_path: Path
) -> None:
    first = _wishlist_row()
    updated = _wishlist_row(price_kurus=20_000, price_per_ml_kurus="4000")
    second = _wishlist_row(
        size_ml_x10=100,
        raw_title="Dior Sauvage EDP 10 ml",
        price_kurus=35_000,
        price_per_ml_kurus="3500",
    )
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        assert (
            c.put("/api/wishlist/items", headers=_auth(token), json=first).status_code
            == 204
        )
        assert (
            c.put("/api/wishlist/items", headers=_auth(token), json=second).status_code
            == 204
        )
        assert (
            c.put("/api/wishlist/items", headers=_auth(token), json=updated).status_code
            == 204
        )

        saved = c.get("/api/wishlist", headers=_auth(token)).json()["rows"]
        assert saved == [
            {**updated, "prices": {}},
            {**second, "prices": {}},
        ]

        identity = {
            key: first[key]
            for key in ("site_id", "brand", "name", "concentration", "size_ml_x10")
        }
        assert (
            c.request(
                "DELETE", "/api/wishlist/items", headers=_auth(token), json=identity
            ).status_code
            == 204
        )
        assert (
            c.request(
                "DELETE", "/api/wishlist/items", headers=_auth(token), json=identity
            ).status_code
            == 204
        )
        assert c.get("/api/wishlist", headers=_auth(token)).json()["rows"] == [
            {**second, "prices": {}}
        ]


def test_wishlist_returns_other_shops_prices_for_the_exact_saved_variation(
    sites_dir: Path, db_path: Path
) -> None:
    _write_profile(sites_dir, id="site-a", name="Site A")
    _write_profile(sites_dir, id="site-b", name="Site B")
    _write_profile(sites_dir, id="site-c", name="Site C")
    runner = _static_runner(
        {
            "site-a": _ok_result("site-a", price_kurus=25_000),
            "site-b": _ok_result("site-b", price_kurus=21_000),
            "site-c": _ok_result("site-c", price_kurus=39_000, size_ml_x10=100),
        }
    )
    for c, token in _client(sites_dir, db_path, runner):
        search_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]
        with c.websocket_connect(f"/api/search/{search_id}?token={token}") as ws:
            while ws.receive_json()["type"] != "scan_finished":
                pass

        result_rows = c.get(f"/api/results/{search_id}", headers=_auth(token)).json()[
            "rows"
        ]
        saved_row = next(row for row in result_rows if row["site_id"] == "site-a")
        assert (
            c.put(
                "/api/wishlist/items", headers=_auth(token), json=saved_row
            ).status_code
            == 204
        )

        wishlist_row = c.get("/api/wishlist", headers=_auth(token)).json()["rows"][0]
        assert wishlist_row["prices"] == {"site-a": 25_000, "site-b": 21_000}


def test_wishlist_refresh_scans_only_the_saved_perfume_and_updates_its_row(
    sites_dir: Path, db_path: Path
) -> None:
    _write_profile(sites_dir, id="site-a", name="Site A")
    runner = _static_runner({"site-a": _ok_result("site-a", price_kurus=31_000)})
    saved = _wishlist_row(age_days=30)
    identity = {
        key: saved[key]
        for key in ("site_id", "brand", "name", "concentration", "size_ml_x10")
    }

    for c, token in _client(sites_dir, db_path, runner):
        assert (
            c.put("/api/wishlist/items", headers=_auth(token), json=saved).status_code
            == 204
        )

        started = c.post("/api/wishlist/refresh", headers=_auth(token), json=identity)
        assert started.status_code == 200
        assert started.json()["searches"] == [{"index": 0, "text": "dior sauvage EDP"}]
        assert c.get("/api/searches/recent", headers=_auth(token)).json() == []

        search_id = started.json()["search_id"]
        with c.websocket_connect(f"/api/search/{search_id}?token={token}") as ws:
            while ws.receive_json()["type"] != "scan_finished":
                pass

        refreshed = c.get("/api/wishlist", headers=_auth(token)).json()["rows"][0]
        assert refreshed["price_kurus"] == 31_000
        assert refreshed["price_per_ml_kurus"] == "6200"
        assert refreshed["age_days"] == 0
        assert refreshed["prices"] == {"site-a": 31_000}


def test_wishlist_refresh_rejects_an_unknown_item(
    sites_dir: Path, db_path: Path
) -> None:
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        response = c.post(
            "/api/wishlist/refresh",
            headers=_auth(token),
            json={
                key: _wishlist_row()[key]
                for key in (
                    "site_id",
                    "brand",
                    "name",
                    "concentration",
                    "size_ml_x10",
                )
            },
        )
        assert response.status_code == 404


def test_wishlist_rejects_an_invalid_variant_size(
    sites_dir: Path, db_path: Path
) -> None:
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        response = c.put(
            "/api/wishlist/items",
            headers=_auth(token),
            json=_wishlist_row(size_ml_x10=0),
        )
        assert response.status_code == 422


def test_wishlist_survives_app_recreation(sites_dir: Path, db_path: Path) -> None:
    row = _wishlist_row()
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        assert (
            c.put("/api/wishlist/items", headers=_auth(token), json=row).status_code
            == 204
        )

    for c, token in _client(sites_dir, db_path, _static_runner({})):
        assert c.get("/api/wishlist", headers=_auth(token)).json()["rows"] == [
            {**row, "prices": {}}
        ]


# -- basket -----------------------------------------------------------------


def _scan_then_add(
    c: TestClient, token: str, *, confirmed: bool = False, confident: bool = True
) -> Any:
    return c.post(
        "/api/basket/items",
        headers=_auth(token),
        json={
            "brand": "dior",
            "name": "sauvage",
            "concentration": "EDP",
            "size_ml_x10": 50,
            "own_identity": True,
            "clone_of": "",
            "confident": confident,
            "confirmed": confirmed,
        },
    )


def _seed_priced_perfume(sites_dir: Path, db_path: Path) -> None:
    """Scan once so a perfume exists to add to the basket -- add_basket_item
    refuses a perfume nobody has priced yet, same as store.py's own rule."""
    _write_profile(sites_dir, id="site-a")
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        search_id = c.post(
            "/api/search",
            json={"query": "Dior Sauvage EDP"},
            headers=_auth(token),
        ).json()["search_id"]
        with c.websocket_connect(f"/api/search/{search_id}?token={token}") as ws:
            while ws.receive_json()["type"] != "scan_finished":
                pass


def test_add_basket_item_requires_confirmation_for_a_low_confidence_match(
    sites_dir: Path, db_path: Path
) -> None:
    _seed_priced_perfume(sites_dir, db_path)
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        refused = _scan_then_add(c, token, confirmed=False, confident=False)
        assert refused.status_code == 409
        accepted = _scan_then_add(c, token, confirmed=True, confident=False)
        assert accepted.status_code == 200


def test_add_basket_item_refuses_a_clone_with_no_identity_of_its_own(
    client: tuple[TestClient, str],
) -> None:
    c, token = client
    response = c.post(
        "/api/basket/items",
        headers=_auth(token),
        json={
            "brand": "armaf",
            "name": "club de nuit",
            "concentration": "EDP",
            "size_ml_x10": 50,
            "own_identity": False,
        },
    )
    assert response.status_code == 422


def test_basket_crud_and_report(sites_dir: Path, db_path: Path) -> None:
    _seed_priced_perfume(sites_dir, db_path)
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        added = _scan_then_add(c, token)
        assert added.status_code == 200
        item_id = added.json()["basket_item_id"]

        basket = c.get("/api/basket", headers=_auth(token)).json()
        assert len(basket["rows"]) == 1
        assert basket["rows"][0]["basket_item_id"] == item_id
        assert basket["rows"][0]["product_urls"] == {"site-a": "https://example.com/p"}
        assert basket["report"]["full"] or basket["report"]["partial"]

        patched = c.patch(
            f"/api/basket/items/{item_id}",
            headers=_auth(token),
            json={"qty": 3},
        )
        assert patched.status_code == 200
        assert patched.json()["qty"] == 3

        deleted = c.delete(f"/api/basket/items/{item_id}", headers=_auth(token))
        assert deleted.status_code == 204

        empty = c.get("/api/basket", headers=_auth(token)).json()
        assert empty["rows"] == []
        assert empty["best_combination"] is None


def test_basket_survives_app_recreation(sites_dir: Path, db_path: Path) -> None:
    _seed_priced_perfume(sites_dir, db_path)
    for c, token in _client(sites_dir, db_path, _static_runner({})):
        assert _scan_then_add(c, token).status_code == 200

    for c, token in _client(sites_dir, db_path, _static_runner({})):
        rows = c.get("/api/basket", headers=_auth(token)).json()["rows"]
        assert len(rows) == 1
        assert rows[0]["qty"] == 1


def test_patch_unknown_basket_item_404s(client: tuple[TestClient, str]) -> None:
    c, token = client
    response = c.patch(
        "/api/basket/items/999999", headers=_auth(token), json={"qty": 2}
    )
    assert response.status_code == 404


def test_basket_refresh_streams_events(sites_dir: Path, db_path: Path) -> None:
    _seed_priced_perfume(sites_dir, db_path)
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        added = _scan_then_add(c, token)
        item_id = added.json()["basket_item_id"]
        assert item_id > 0

        started = c.post("/api/basket/refresh", headers=_auth(token))
        assert started.status_code == 200
        refresh_id = started.json()["refresh_id"]

        with c.websocket_connect(
            f"/api/basket/refresh/{refresh_id}?token={token}"
        ) as ws:
            events = []
            while True:
                event = ws.receive_json()
                events.append(event)
                if event["type"] == "refresh_finished":
                    break

        types = [e["type"] for e in events]
        assert types[0] == "refresh_started"
        assert types[-1] == "refresh_finished"


def test_basket_refresh_can_be_narrowed_to_one_line(
    sites_dir: Path, db_path: Path
) -> None:
    """Asking for one row's price must not re-scan the rest of the basket.

    The whole point of the per-row refresh is that a shop is asked about one
    perfume instead of every perfume someone happens to have saved, so a
    filter that quietly widened back to the full basket would be the feature
    failing while still looking like it worked.
    """
    _seed_priced_perfume(sites_dir, db_path)
    runner = _static_runner({"site-a": _ok_result("site-a")})
    for c, token in _client(sites_dir, db_path, runner):
        first = _scan_then_add(c, token).json()["basket_item_id"]
        second = c.post(
            "/api/basket/items",
            headers=_auth(token),
            json={
                "brand": "dior",
                "name": "sauvage",
                "concentration": "EDP",
                "size_ml_x10": 100,
                "own_identity": True,
                "clone_of": "",
                "confident": True,
                "confirmed": False,
            },
        ).json()["basket_item_id"]
        assert first != second

        started = c.post(
            "/api/basket/refresh",
            headers=_auth(token),
            json={"basket_item_id": second},
        )
        assert started.status_code == 200
        assert started.json()["total_rows"] == 1

        with c.websocket_connect(
            f"/api/basket/refresh/{started.json()['refresh_id']}?token={token}"
        ) as ws:
            touched = set()
            while True:
                event = ws.receive_json()
                if "basket_item_id" in event:
                    touched.add(event["basket_item_id"])
                if event["type"] == "refresh_finished":
                    break
        assert touched == {second}


def test_basket_refresh_404s_for_an_unknown_line(
    client: tuple[TestClient, str],
) -> None:
    c, token = client
    response = c.post(
        "/api/basket/refresh", headers=_auth(token), json={"basket_item_id": 999999}
    )
    assert response.status_code == 404


# -- updates --------------------------------------------------------------


class _RecordingStream:
    """Just enough of an httpx streaming response to be downloaded from."""

    headers: dict[str, str] = {"Content-Length": "2"}

    def raise_for_status(self) -> None:
        return None

    def iter_bytes(self) -> Iterator[bytes]:
        yield b"MZ"

    def __enter__(self) -> _RecordingStream:
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None


class _RecordingClient:
    def __init__(self, asked: list[str]) -> None:
        self._asked = asked

    def __enter__(self) -> _RecordingClient:
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None

    def stream(self, _method: str, url: str) -> _RecordingStream:
        self._asked.append(url)
        return _RecordingStream()


def _update_client(
    sites_dir: Path,
    db_path: Path,
    info: dict[str, Any],
    download: UpdateDownload | None = None,
    request_quit: Any = None,
) -> Iterator[tuple[TestClient, str]]:
    app = create_app(
        sites_dir=sites_dir,
        db_path=db_path,
        runner=_static_runner({}),
        update_checker=lambda: info,
        update_download=download,
        request_quit=request_quit,
    )
    with TestClient(app) as c:
        yield c, app.state.parfum.auth_token


_NO_UPDATE: dict[str, Any] = {
    "current_version": "0.1.0",
    "latest_version": None,
    "update_available": False,
    "notes": "",
    "release_url": "",
    "download_url": None,
}

_AN_UPDATE: dict[str, Any] = {
    "current_version": "0.1.0",
    "latest_version": "0.2.0",
    "update_available": True,
    "notes": "- yeni",
    "release_url": "https://example.invalid/r",
    "download_url": "https://example.invalid/setup.exe",
}


def test_update_check_passes_the_release_through(
    sites_dir: Path, db_path: Path
) -> None:
    c, token = next(_update_client(sites_dir, db_path, _AN_UPDATE))
    response = c.get("/api/update", headers=_auth(token))

    assert response.status_code == 200
    assert response.json() == _AN_UPDATE


def test_download_starts_from_the_server_side_check(
    sites_dir: Path, db_path: Path
) -> None:
    """The URL the installer comes from is decided here, not by the page.

    A client-supplied download URL would move the question of where the
    executable came from into the window, which is the one place in this app
    that renders text written somewhere else.
    """
    asked: list[str] = []

    def client_factory(**_kwargs: Any) -> Any:
        return _RecordingClient(asked)

    download = UpdateDownload(
        dest_dir=db_path.parent / "download",
        client_factory=client_factory,
        spawn=lambda _path: None,
    )
    c, token = next(_update_client(sites_dir, db_path, _AN_UPDATE, download=download))
    response = c.post("/api/update/download", headers=_auth(token))

    assert response.status_code == 200
    assert response.json()["state"] == "downloading"
    for _ in range(200):
        if asked:
            break
        time.sleep(0.02)
    assert asked == ["https://example.invalid/setup.exe"]


def test_download_is_refused_when_there_is_nothing_to_download(
    sites_dir: Path, db_path: Path
) -> None:
    c, token = next(_update_client(sites_dir, db_path, _NO_UPDATE))
    assert c.post("/api/update/download", headers=_auth(token)).status_code == 409


def test_install_closes_the_window_only_after_it_has_answered(
    sites_dir: Path, db_path: Path
) -> None:
    """The window has to stay up long enough to deliver this response.

    Closing inside the handler would kill the reply that tells the dialog the
    installer is running, leaving the last thing on screen a failed request.
    """
    quits: list[bool] = []
    download = UpdateDownload(spawn=lambda _path: None)
    c, token = next(
        _update_client(
            sites_dir,
            db_path,
            _AN_UPDATE,
            download=download,
            request_quit=lambda: quits.append(True),
        )
    )
    # Nothing downloaded yet: no spawn, no quit, and a status the dialog can
    # tell apart from a network failure.
    assert c.post("/api/update/install", headers=_auth(token)).status_code == 409
    assert quits == []


def test_install_reports_handoff_failure_without_closing_the_window(
    sites_dir: Path, db_path: Path
) -> None:
    class FailedHandoff(UpdateDownload):
        def install(self) -> bool:
            return False

        def progress(self) -> DownloadProgress:
            return DownloadProgress(
                state="error", message="güncelleme yardımcısı başlatılamadı"
            )

    quits: list[bool] = []
    c, token = next(
        _update_client(
            sites_dir,
            db_path,
            _AN_UPDATE,
            download=FailedHandoff(),
            request_quit=lambda: quits.append(True),
        )
    )

    response = c.post("/api/update/install", headers=_auth(token))

    assert response.status_code == 409
    assert response.json()["detail"] == "güncelleme yardımcısı başlatılamadı"
    assert quits == []
