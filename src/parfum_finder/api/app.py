"""The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.

No business logic lives here. Every handler either reads or writes through
`store.py` (always inside `asyncio.to_thread`, since `sqlite3` is blocking) or
drives a Faz 1 service (`run_scan`, `run_basket_refresh`, `basket.py`) and
turns what comes back into JSON through `serialize.py`.

`create_app()` is a factory rather than a single module-level app so a test
can hand it a fake `SiteRunner` and a tmp-path database, the same way
`tests/test_scan_service.py` already does for the service layer underneath
it. `parfum_finder.api:app`, the module-level instance `uvicorn` points at,
is just `create_app()` called with every default.

Security: `127.0.0.1` only (the caller picks the port when it runs uvicorn),
plus a random token generated once per process. HTTP endpoints read it from
the `X-Auth-Token` header; the WebSocket routes read it from a `token` query
parameter instead, because browsers cannot set a header on a WebSocket
handshake at all.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import secrets
import sqlite3
from collections.abc import AsyncGenerator, AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, cast
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from parfum_finder import paths, ranking
from parfum_finder.api.serialize import (
    encode_basket_refresh_event,
    encode_basket_report,
    encode_basket_row,
    encode_result_row,
    encode_scan_event,
    encode_split_plan,
)
from parfum_finder.api.sessions import BasketRefreshSession, ScanSession
from parfum_finder.basket import (
    basket_inputs,
    build_basket_rows,
    optimize,
    single_site_scenarios,
)
from parfum_finder.engine import SiteRunner, run_site
from parfum_finder.matcher import (
    MAX_QUERIES,
    QUERY_SEPARATOR_PATTERN,
    parse_query,
    split_queries,
)
from parfum_finder.profiles import load_site_profile, sync_to_db
from parfum_finder.services.scan import (
    BasketRefreshEvent,
    RowsReady,
    ScanEvent,
    Search,
    run_basket_refresh,
    run_scan,
)
from parfum_finder.store import (
    DEFAULT_DB_PATH,
    STALE_PRICE_DAYS,
    BasketLine,
    BasketPrice,
    BasketSite,
    add_basket_item,
    basket_lines,
    basket_prices,
    basket_sites,
    connect,
    now_iso,
    recent_searches,
    record_search,
    remove_basket_item,
    remove_wishlist_item,
    save_wishlist_item,
    set_basket_qty,
    wishlist_rows,
)
from parfum_finder.updater import UpdateDownload, check_for_update
from parfum_finder.validate import (
    DEFAULT_SITES_DIR,
    STALE_PROFILE_DAYS,
    profile_age_days,
)
from parfum_finder.viewmodels import BasketRow

# The three sorts the results table offers. `None` means the grouped default,
# same as the TUI's own header-click behaviour.
_SORT_KEYS = ("ml", "price", "per_ml")

# How many past query lines the search screen offers. Short on purpose: the
# list sits under an empty input, and a long one turns the first screen into
# something to read instead of somewhere to type.
RECENT_SEARCHES = 5

_token_header = APIKeyHeader(name="X-Auth-Token", auto_error=False)

_TOKEN_ENV_VAR = "PARFUM_FINDER_TOKEN"


# Request/response models live at module scope, not inside create_app(): with
# `from __future__ import annotations` in effect, FastAPI resolves a route's
# annotations through the function's module globals, and a model class local
# to create_app() is invisible there -- the parameter silently falls back to
# being read as a query parameter instead of a request body.


class SearchRequest(BaseModel):
    query: str
    # Mirrors the TUI's [r]: every perfume goes to the shops regardless of
    # what is already cached, instead of a table mixing two moments.
    force: bool = False


class AcceptedSearch(BaseModel):
    index: int
    text: str


class SearchStartResponse(BaseModel):
    search_id: str
    rejected: list[str]
    # What each query_index in the event stream is about. Every scan event
    # names its perfume by index only, and a client that could not resolve one
    # would have to warn about "the second perfume" instead of about the
    # perfume, which is a warning nobody acts on.
    searches: list[AcceptedSearch]


class BasketAddRequest(BaseModel):
    brand: str
    name: str
    concentration: str
    size_ml_x10: int = Field(gt=0)
    qty: int = Field(default=1, gt=0)
    # These four mirror the ResultRow the client already has from
    # /api/results; the confirm rule they gate is enforced here too, so a
    # client cannot bypass it by simply not showing the modal.
    own_identity: bool = True
    clone_of: str = ""
    confident: bool = True
    confirmed: bool = False


class BasketQtyRequest(BaseModel):
    qty: int = Field(ge=1)


class WishlistIdentityRequest(BaseModel):
    site_id: str
    brand: str
    name: str
    concentration: str
    size_ml_x10: int = Field(gt=0)


class WishlistItemRequest(WishlistIdentityRequest):
    site_label: str
    query_index: int
    product: str
    raw_title: str
    price_kurus: int | None
    price_per_ml_kurus: str | None
    in_stock: bool | None
    match_score: int
    confident: bool
    product_url: str | None
    clone_of: str
    own_identity: bool
    age_days: int


class RefreshRequest(BaseModel):
    # Which basket line to re-price, or every line when it is left out. One
    # row is the same walk over the enabled sites with a shorter list of rows,
    # so nothing downstream has to know a refresh was narrowed.
    basket_item_id: int | None = None


class RefreshStartResponse(BaseModel):
    refresh_id: str
    total_rows: int


@dataclass
class _AppState:
    sites_dir: Path
    db_path: Path
    runner: SiteRunner
    auth_token: str
    write_lock: asyncio.Lock
    update_checker: Callable[[], dict[str, Any]]
    update_download: UpdateDownload
    # Kurulum devredildikten sonra pencereyi kapatmanın tek yolu. GUI dışında
    # (testlerde, uvicorn'la elle çalıştırıldığında) kapatılacak pencere yok.
    request_quit: Callable[[], None] | None = None
    profiles: list[dict[str, Any]] = field(default_factory=list)
    scan_sessions: dict[str, ScanSession] = field(default_factory=dict)
    refresh_sessions: dict[str, BasketRefreshSession] = field(default_factory=dict)


def _load_profiles(sites_dir: Path) -> list[dict[str, Any]]:
    return [load_site_profile(path) for path in sorted(sites_dir.glob("*.json"))]


def _sync_profiles(db_path: Path, profiles: list[dict[str, Any]]) -> None:
    conn = connect(db_path)
    try:
        sync_to_db(conn, profiles, synced_at=now_iso())
    finally:
        conn.close()


def create_app(
    *,
    sites_dir: Path = DEFAULT_SITES_DIR,
    db_path: Path = DEFAULT_DB_PATH,
    runner: SiteRunner = run_site,
    auth_token: str | None = None,
    ui_dir: Path | None = None,
    update_checker: Callable[[], dict[str, Any]] = check_for_update,
    update_download: UpdateDownload | None = None,
    request_quit: Callable[[], None] | None = None,
) -> FastAPI:
    resolved_ui_dir = ui_dir if ui_dir is not None else paths.ui_dir()
    state = _AppState(
        sites_dir=sites_dir,
        db_path=db_path,
        runner=runner,
        # A fresh random token per process is what ships: the window gets it
        # injected and nothing else can guess it. The override exists for
        # development, where the Vite dev server is a separate process that
        # has no way to be handed a token nobody printed.
        auth_token=(
            auth_token or os.environ.get(_TOKEN_ENV_VAR) or secrets.token_urlsafe(32)
        ),
        write_lock=asyncio.Lock(),
        update_checker=update_checker,
        update_download=(
            update_download if update_download is not None else UpdateDownload()
        ),
        request_quit=request_quit,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Only cli.py called this before; a GUI backend bypasses cli.main()
        # entirely, so nothing else here would ever read a .env file.
        load_dotenv()
        profiles = await asyncio.to_thread(_load_profiles, state.sites_dir)
        await asyncio.to_thread(_sync_profiles, state.db_path, profiles)
        state.profiles = profiles
        yield

    app = FastAPI(lifespan=lifespan)
    app.state.parfum = state

    def require_token(
        request: Request, token: Annotated[str | None, Depends(_token_header)]
    ) -> None:
        app_state: _AppState = request.app.state.parfum
        if token != app_state.auth_token:
            raise HTTPException(status_code=401, detail="invalid or missing token")

    auth = Depends(require_token)

    def get_state(request: Request) -> _AppState:
        return request.app.state.parfum

    # -- config ------------------------------------------------------------

    @app.get("/api/config", dependencies=[auth])
    async def get_config() -> dict[str, Any]:
        """The domain constants a client has to agree with us on.

        Sent rather than duplicated: a stale badge drawn against a threshold
        the display layer keeps its own copy of is a badge that stops meaning
        what the storage layer means the day one of the two changes.
        """
        return {
            "stale_price_days": STALE_PRICE_DAYS,
            "max_queries": MAX_QUERIES,
            # A regular expression source, not a literal separator: the same
            # spacing rule that keeps "Jean-Paul Gaultier" one perfume.
            "query_separator_pattern": QUERY_SEPARATOR_PATTERN,
        }

    # -- sites -------------------------------------------------------------

    @app.get("/api/sites", dependencies=[auth])
    async def list_sites(request: Request) -> list[dict[str, Any]]:
        app_state = get_state(request)
        return [_site_summary(p) for p in app_state.profiles]

    # -- search --------------------------------------------------------------

    @app.post("/api/search", dependencies=[auth])
    async def start_search(
        body: SearchRequest, request: Request
    ) -> SearchStartResponse:
        app_state = get_state(request)
        parts = split_queries(body.query)
        if len(parts) > MAX_QUERIES:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"en fazla {MAX_QUERIES} parfüm aranabilir, {len(parts)} bulundu"
                ),
            )
        searches: list[Search] = []
        rejected: list[str] = []
        for part in parts:
            try:
                query = parse_query(part)
            except ValueError as e:
                # One bad piece does not cancel the others, same as the TUI:
                # someone who typed three perfumes and mistyped one still gets
                # the two that parsed.
                rejected.append(str(e))
                continue
            searches.append(Search(index=len(searches), text=part, query=query))
        if not searches:
            raise HTTPException(
                status_code=422,
                detail="; ".join(rejected) or "a search needs a perfume to look for",
            )
        search_id = uuid4().hex
        app_state.scan_sessions[search_id] = ScanSession(
            id=search_id, searches=searches, rejected=rejected, force=body.force
        )
        # The whole line as typed, so replaying it reproduces the multi-perfume
        # query. A history that cannot be written is a convenience nobody gets,
        # not a reason to refuse a scan someone is waiting on.
        with contextlib.suppress(sqlite3.Error):
            await asyncio.to_thread(_record_search, app_state.db_path, body.query)
        return SearchStartResponse(
            search_id=search_id,
            rejected=rejected,
            searches=[AcceptedSearch(index=s.index, text=s.text) for s in searches],
        )

    @app.get("/api/searches/recent", dependencies=[auth])
    async def list_recent_searches(request: Request) -> list[dict[str, str]]:
        app_state = get_state(request)
        return await asyncio.to_thread(_recent_searches, app_state.db_path)

    @app.websocket("/api/search/{search_id}")
    async def stream_search(websocket: WebSocket, search_id: str) -> None:
        app_state: _AppState = websocket.app.state.parfum
        if websocket.query_params.get("token") != app_state.auth_token:
            await websocket.close(code=4401)
            return
        session = app_state.scan_sessions.get(search_id)
        if session is None:
            await websocket.close(code=4404)
            return
        if session.started:
            # A scan already ran (or is running) for this id. Re-driving
            # run_scan a second time would write every price snapshot twice.
            await websocket.close(code=4409)
            return
        session.started = True
        await websocket.accept()
        try:
            async with contextlib.aclosing(
                cast(
                    "AsyncGenerator[ScanEvent, None]",
                    run_scan(
                        session.searches,
                        app_state.profiles,
                        runner=app_state.runner,
                        db_path=app_state.db_path,
                        write_lock=app_state.write_lock,
                        force=session.force,
                    ),
                )
            ) as events:
                async for event in events:
                    if isinstance(event, RowsReady):
                        session.rows.extend(event.rows)
                    await websocket.send_json(encode_scan_event(event))
        except WebSocketDisconnect:
            # A closed tab or a page navigating away mid-scan. aclosing() above
            # is what tears run_scan's TaskGroup and browser_session down
            # cleanly; there is nothing left to send.
            pass
        finally:
            # Set whether the scan ran to completion or was cut short: either
            # way no further RowsReady is coming, and /api/results has to be
            # able to tell "this is the whole answer" from "this is what
            # arrived before the socket died".
            session.finished = True

    @app.get("/api/results/{search_id}", dependencies=[auth])
    async def get_results(
        search_id: str, request: Request, sort: str | None = None
    ) -> dict[str, Any]:
        if sort is not None and sort not in _SORT_KEYS:
            raise HTTPException(
                status_code=422, detail=f"sort must be one of {list(_SORT_KEYS)}"
            )
        app_state = get_state(request)
        session = app_state.scan_sessions.get(search_id)
        if session is None:
            raise HTTPException(status_code=404, detail="unknown search_id")
        # Out-of-stock sizes are hidden by default, same as the TUI's table:
        # a size nobody can buy is not an offer.
        visible = [r for r in session.rows if r.in_stock is not False]
        if sort is None:
            # Ranked over every row before the stock filter narrows it, so
            # showing or hiding out-of-stock sizes can never reshuffle which
            # site a block leads with.
            ranks = ranking.site_ranks(session.rows)
            visible.sort(key=lambda row: ranking.grouped_value(row, ranks))
        else:
            visible.sort(key=lambda row: ranking.sorted_value(row, sort))
        return {
            "rows": [encode_result_row(r) for r in visible],
            "hidden_out_of_stock": len(session.rows) - len(visible),
            # False for as long as the WS is streaming (or hasn't connected
            # yet): the rows above are what has arrived so far, not the
            # scan's whole answer, until this flips.
            "finished": session.finished,
        }

    # -- wishlist --------------------------------------------------------

    @app.get("/api/wishlist", dependencies=[auth])
    async def get_wishlist(request: Request) -> dict[str, Any]:
        app_state = get_state(request)
        rows = await asyncio.to_thread(_read_wishlist, app_state.db_path)
        return {"rows": rows}

    @app.put("/api/wishlist/items", dependencies=[auth])
    async def put_wishlist_item(
        request: Request, body: WishlistItemRequest
    ) -> Response:
        app_state = get_state(request)
        await asyncio.to_thread(_save_wishlist_item, app_state.db_path, body)
        return Response(status_code=204)

    @app.delete("/api/wishlist/items", dependencies=[auth])
    async def delete_wishlist_item(
        request: Request, body: WishlistIdentityRequest
    ) -> Response:
        app_state = get_state(request)
        await asyncio.to_thread(_remove_wishlist_item, app_state.db_path, body)
        return Response(status_code=204)

    # -- basket ----------------------------------------------------------

    @app.post("/api/basket/items", dependencies=[auth])
    async def add_item(request: Request, body: BasketAddRequest) -> dict[str, Any]:
        if not body.own_identity:
            # Nothing to add it as: store.add_basket_item has no row for a
            # clone whose own title was too short to name a house and a
            # perfume, because write_snapshots never wrote one for it either.
            raise HTTPException(
                status_code=422,
                detail="bu klonun kendi adı okunamadı, sepete eklenemez",
            )
        if (body.clone_of or not body.confident) and not body.confirmed:
            raise HTTPException(
                status_code=409,
                detail="düşük skorlu eşleşme veya klon; confirmed=true ile onaylayın",
            )
        app_state = get_state(request)
        try:
            item_id = await asyncio.to_thread(_add_basket_item, app_state.db_path, body)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        return {"basket_item_id": item_id}

    @app.patch("/api/basket/items/{item_id}", dependencies=[auth])
    async def set_qty(
        item_id: int, body: BasketQtyRequest, request: Request
    ) -> dict[str, Any]:
        app_state = get_state(request)
        try:
            qty = await asyncio.to_thread(
                _set_basket_qty, app_state.db_path, item_id, body.qty
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return {"basket_item_id": item_id, "qty": qty}

    @app.delete("/api/basket/items/{item_id}", dependencies=[auth])
    async def delete_item(item_id: int, request: Request) -> Response:
        app_state = get_state(request)
        removed = await asyncio.to_thread(
            _remove_basket_item, app_state.db_path, item_id
        )
        if not removed:
            raise HTTPException(status_code=404, detail="no such basket item")
        return Response(status_code=204)

    @app.get("/api/basket", dependencies=[auth])
    async def get_basket(request: Request) -> dict[str, Any]:
        app_state = get_state(request)
        lines, prices, sites = await asyncio.to_thread(_read_basket, app_state.db_path)
        rows = build_basket_rows(lines, prices)
        report, plan = await asyncio.to_thread(_score_basket, rows, sites)
        return {
            "rows": [encode_basket_row(r) for r in rows],
            "report": encode_basket_report(report),
            "best_combination": (
                encode_split_plan(plan, report) if plan is not None else None
            ),
        }

    @app.post("/api/basket/refresh", dependencies=[auth])
    async def start_basket_refresh(
        request: Request, body: RefreshRequest | None = None
    ) -> RefreshStartResponse:
        app_state = get_state(request)
        lines, prices, _sites = await asyncio.to_thread(_read_basket, app_state.db_path)
        rows = build_basket_rows(lines, prices)
        if body is not None and body.basket_item_id is not None:
            rows = [r for r in rows if r.line.basket_item_id == body.basket_item_id]
            if not rows:
                raise HTTPException(status_code=404, detail="no such basket item")
        refresh_id = uuid4().hex
        app_state.refresh_sessions[refresh_id] = BasketRefreshSession(
            id=refresh_id, rows=rows
        )
        return RefreshStartResponse(refresh_id=refresh_id, total_rows=len(rows))

    @app.websocket("/api/basket/refresh/{refresh_id}")
    async def stream_basket_refresh(websocket: WebSocket, refresh_id: str) -> None:
        app_state: _AppState = websocket.app.state.parfum
        if websocket.query_params.get("token") != app_state.auth_token:
            await websocket.close(code=4401)
            return
        session = app_state.refresh_sessions.get(refresh_id)
        if session is None:
            await websocket.close(code=4404)
            return
        if session.started:
            await websocket.close(code=4409)
            return
        session.started = True
        enabled_profiles = [p for p in app_state.profiles if p.get("enabled", True)]
        await websocket.accept()
        try:
            async with contextlib.aclosing(
                cast(
                    "AsyncGenerator[BasketRefreshEvent, None]",
                    run_basket_refresh(
                        session.rows,
                        enabled_profiles,
                        runner=app_state.runner,
                        db_path=app_state.db_path,
                        write_lock=app_state.write_lock,
                    ),
                )
            ) as events:
                async for event in events:
                    await websocket.send_json(encode_basket_refresh_event(event))
        except WebSocketDisconnect:
            pass

    # -- updates -----------------------------------------------------------
    #
    # İndirme adresi istemciden değil, buradaki kontrolden gelir: pencerede
    # açılan sayfanın gösterdiği bir URL'yi indirip çalıştırmak, kurulum
    # dosyasının nereden geldiği sorusunu sayfaya devretmek olurdu.

    @app.get("/api/update", dependencies=[auth])
    async def check_update(request: Request) -> dict[str, Any]:
        app_state = get_state(request)
        return await asyncio.to_thread(app_state.update_checker)

    @app.post("/api/update/download", dependencies=[auth])
    async def start_update_download(request: Request) -> dict[str, Any]:
        app_state = get_state(request)
        info = await asyncio.to_thread(app_state.update_checker)
        download_url = info.get("download_url")
        if not info.get("update_available") or not download_url:
            raise HTTPException(status_code=409, detail="indirilecek bir sürüm yok")
        started = app_state.update_download.start(str(download_url))
        if started is None:
            raise HTTPException(status_code=409, detail="indirme zaten sürüyor")
        return started.as_dict()

    @app.get("/api/update/progress", dependencies=[auth])
    async def update_progress(request: Request) -> dict[str, Any]:
        return get_state(request).update_download.progress().as_dict()

    @app.post("/api/update/install", dependencies=[auth])
    async def install_update(request: Request) -> dict[str, Any]:
        app_state = get_state(request)
        if not app_state.update_download.install():
            raise HTTPException(status_code=409, detail="kurulum dosyası hazır değil")
        # Pencere hemen değil, bu yanıt istemciye ulaştıktan sonra kapanır:
        # aynı çağrı içinde kapatmak, kullanıcıya kurulumun başladığını
        # söyleyen yanıtı yolda öldürürdü.
        if app_state.request_quit is not None:
            asyncio.get_running_loop().call_later(1.0, app_state.request_quit)
        return {"installing": True}

    # -- static frontend ---------------------------------------------------
    #
    # Registered last: a mount at "/" would otherwise shadow every "/api/*"
    # route declared above it, since Starlette resolves routes in
    # registration order. Skipped entirely when there is no build to serve
    # (a fresh checkout, or the Linux CI job, never runs `npm run build`).
    index_path = resolved_ui_dir / "index.html"
    if index_path.is_file():
        assets_dir = resolved_ui_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="ui-assets")

        # The packaged app has no window chrome to type a token into, so the
        # token has to already be on the page: pywebview loads "/" and the
        # React app's first API call happens before any script we could
        # inject afterwards would run, ruling out an `evaluate_js` approach.
        raw_html = index_path.read_text(encoding="utf-8")
        token_script = (
            f"<script>window.__PARFUM_TOKEN__={json.dumps(state.auth_token)};</script>"
        )
        indexed_html = raw_html.replace("<head>", f"<head>\n    {token_script}", 1)

        @app.get("/", include_in_schema=False)
        async def index() -> HTMLResponse:
            return HTMLResponse(indexed_html)

    return app


def _site_summary(profile: dict[str, Any]) -> dict[str, Any]:
    discovered_at = str(profile["discovered_at"])
    age = profile_age_days(discovered_at)
    return {
        "id": profile["id"],
        "name": profile["name"],
        "enabled": bool(profile.get("enabled", True)),
        "needs_review": age >= STALE_PROFILE_DAYS,
        "discovered_at": discovered_at,
    }


def _record_search(db_path: Path, query_text: str) -> None:
    conn = connect(db_path)
    try:
        record_search(conn, query_text, now_iso())
    finally:
        conn.close()


def _recent_searches(db_path: Path) -> list[dict[str, str]]:
    conn = connect(db_path)
    try:
        return [
            {"text": text, "searched_at": searched_at}
            for text, searched_at in recent_searches(conn, limit=RECENT_SEARCHES)
        ]
    finally:
        conn.close()


def _add_basket_item(db_path: Path, body: BasketAddRequest) -> int:
    conn = connect(db_path)
    try:
        return add_basket_item(
            conn,
            brand=body.brand,
            name=body.name,
            concentration=body.concentration,
            size_ml_x10=body.size_ml_x10,
            qty=body.qty,
        )
    finally:
        conn.close()


def _set_basket_qty(db_path: Path, item_id: int, qty: int) -> int:
    conn = connect(db_path)
    try:
        return set_basket_qty(conn, basket_item_id=item_id, qty=qty)
    finally:
        conn.close()


def _remove_basket_item(db_path: Path, item_id: int) -> bool:
    conn = connect(db_path)
    try:
        return remove_basket_item(conn, basket_item_id=item_id)
    finally:
        conn.close()


def _save_wishlist_item(db_path: Path, body: WishlistItemRequest) -> None:
    conn = connect(db_path)
    try:
        save_wishlist_item(
            conn,
            site_id=body.site_id,
            brand=body.brand,
            name=body.name,
            concentration=body.concentration,
            size_ml_x10=body.size_ml_x10,
            row_json=body.model_dump_json(),
        )
    finally:
        conn.close()


def _read_wishlist(db_path: Path) -> list[dict[str, Any]]:
    conn = connect(db_path)
    try:
        return [json.loads(row) for row in wishlist_rows(conn)]
    finally:
        conn.close()


def _remove_wishlist_item(db_path: Path, body: WishlistIdentityRequest) -> None:
    conn = connect(db_path)
    try:
        remove_wishlist_item(
            conn,
            site_id=body.site_id,
            brand=body.brand,
            name=body.name,
            concentration=body.concentration,
            size_ml_x10=body.size_ml_x10,
        )
    finally:
        conn.close()


def _read_basket(
    db_path: Path,
) -> tuple[list[BasketLine], list[BasketPrice], list[BasketSite]]:
    conn = connect(db_path)
    try:
        return basket_lines(conn), basket_prices(conn), basket_sites(conn)
    finally:
        conn.close()


def _score_basket(rows: list[BasketRow], sites: list[BasketSite]) -> tuple[Any, Any]:
    items, prices, shipping = basket_inputs(rows, sites)
    report = single_site_scenarios(items, prices, shipping)
    # optimize() is only worth asking on a basket that has rows, same guard
    # the basket screen uses -- an empty basket has nothing to split.
    plan = optimize(items, prices, shipping) if rows else None
    return report, plan
