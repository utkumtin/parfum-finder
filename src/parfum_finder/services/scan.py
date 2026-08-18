"""Scan orchestration: cache-first read, per-site fan-out, one paced scan.

No Textual dependency here. A screen and, later, an HTTP/WS handler both
consume the same async event stream out of `run_scan`; only how each draws
an event differs. Cache-first ordering, the write lock, and one task per
site with its own perfumes run serially inside it are exactly what the TUI
did before this moved out of it -- see `run_scan`'s own docstring for the
two traps that still matter.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from parfum_finder.engine import (
    CacheKey,
    SiteResult,
    SiteRunner,
    SiteStatus,
    VariantsRead,
)
from parfum_finder.fetch import Fetcher, browser_session
from parfum_finder.logging_setup import logger
from parfum_finder.matcher import (
    DEFAULT_THRESHOLD,
    PerfumeQuery,
    listing_filter,
    product_label,
    search_spellings,
)
from parfum_finder.store import (
    CachedPrice,
    SnapshotRow,
    cached_prices,
    connect,
    snapshot_age_days,
    snapshot_rows,
    write_snapshots,
)
from parfum_finder.validate import STALE_PROFILE_DAYS, profile_age_days
from parfum_finder.viewmodels import BasketRow, ResultRow


@dataclass(frozen=True)
class Search:
    """One perfume of a search, as typed and as parsed.

    The index is the outermost sort key of the results table and the only
    part of the typed line that survives into it. Three perfumes sorted into
    one ₺/ml list interleave into something nobody can read, so the order
    they were asked for is what the blocks come out in. The blocks
    themselves are headed by the product each row is about, not by this.
    """

    index: int
    text: str
    query: PerfumeQuery


@dataclass(frozen=True)
class ScanStarted:
    """Once, before any request goes out.

    `total_perfumes` counts only what storage had nothing for -- the
    perfumes this scan is actually about to ask the shops for, not the
    typed count.
    """

    total_sites: int
    total_perfumes: int


@dataclass(frozen=True)
class SiteStarted:
    """One site's serial run of the to-be-scanned perfumes is starting."""

    site_id: str


@dataclass(frozen=True)
class CacheHit:
    """One perfume was answered from storage, not from the shops.

    `age_days` is the oldest reading among that perfume's cached rows, the
    same "a row is only as fresh as its stalest cell" rule the basket uses.
    """

    query_index: int
    age_days: int


@dataclass(frozen=True)
class RowsReady:
    """Priced rows one request added to the table, from cache or a site."""

    rows: tuple[ResultRow, ...]


@dataclass(frozen=True)
class SiteFinished:
    """One (site, perfume) request is done, whatever it ended in.

    `status` is the site's own verdict, or "error" standing in for a runner
    exception or a result this scan could not read at all -- both are
    logged, with their own detail, at the point they happen, so a consumer
    that only wants to count failures never has to branch on more than this
    field. `has_rows` says whether a `RowsReady` for this same request
    preceded it, which is what a "nothing found" notice is decided from.

    Always the last event of its (site, perfume) request: a `RowsReady` or
    a `WriteFailed` for the same request, if either happens, is put on the
    stream before this one.
    """

    site_id: str
    query_index: int
    status: SiteStatus
    detail: str | None
    has_rows: bool


@dataclass(frozen=True)
class WriteFailed:
    """A request already reported via `SiteFinished` could not be written to
    storage. The rows already reached the table; only the record is
    missing."""

    site_id: str
    query_index: int


@dataclass(frozen=True)
class ScanFinished:
    """The scan is over. `error_count` is every failure any event above
    reported, exactly what a status bar's "N hata" counts."""

    error_count: int


ScanEvent = (
    ScanStarted
    | SiteStarted
    | CacheHit
    | RowsReady
    | SiteFinished
    | WriteFailed
    | ScanFinished
)


def site_label(profile: dict[str, Any]) -> str:
    """A site's display name, with a badge when its profile is old enough
    to be worth re-discovering."""
    name = str(profile["name"])
    age = profile_age_days(str(profile["discovered_at"]))
    if age >= STALE_PROFILE_DAYS:
        return f"{name} ⏳ {age} gün önce keşfedildi"
    return name


def _cached_result_row(price: CachedPrice, label: str, search: Search) -> ResultRow:
    """Turn one stored price back into the row the table shows.

    Everything the table paints is either stored or derived from the stored
    title, with two exceptions. `clone_of` is empty and `own_identity` is
    True, which is the truth rather than a default standing in for one: a
    clone is filed under its own house and name, so it never comes back from
    a search for the perfume it imitates.
    """
    return ResultRow(
        site_id=price.site_id,
        site_label=label,
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


def _dedupe_snapshot_rows(rows: list[SnapshotRow]) -> list[SnapshotRow]:
    """Collapse listings a site's search page repeats into one.

    A search page can list the same bottle more than once -- an overlapping
    page, the same listing under two categories -- and nothing upstream of
    this filters that out. Storage would never show the duplicate anyway:
    `product_variants` is unique per (product, size), so a second listing for
    a size already seen overwrites the first instead of adding a row.
    Collapsing here, before either the table or storage sees these rows,
    keeps both agreeing with each other and keeps a write from recording the
    same size twice under one `fetched_at`. Last one in wins, matching what
    storage would do on its own: `write_snapshots` stamps a whole batch with
    one `fetched_at`, and `latest_prices` breaks that tie by `snapshot_id`,
    so whichever listing was read last is also the one storage would end up
    surfacing.
    """
    deduped: dict[tuple[str, str, str, str, int], SnapshotRow] = {}
    for row in rows:
        key = (
            row.site_id,
            row.brand,
            row.name,
            row.concentration,
            row.variant.size_ml_x10,
        )
        deduped[key] = row
    return list(deduped.values())


def _to_result_rows(
    label: str, search: Search, rows: list[SnapshotRow]
) -> list[ResultRow]:
    return [
        ResultRow(
            site_id=row.site_id,
            site_label=label,
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


def _read_cache(
    db_path: Path, searches: Sequence[Search], labels: dict[str, str]
) -> list[ResultRow]:
    """Rebuild the table's rows for every searched perfume already on record.

    Sites whose profile is gone or switched off are dropped rather than
    shown under their bare id: the label comes from the profile, and a row
    nobody can refresh is not an offer this scan should be making.
    """
    conn = connect(db_path)
    try:
        rows: list[ResultRow] = []
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


def _write_snapshot_rows(db_path: Path, rows: list[SnapshotRow]) -> None:
    conn = connect(db_path)
    try:
        write_snapshots(conn, rows)
    finally:
        conn.close()


def _about(site_id: str, search: Search, *, multi: bool) -> str:
    """Which perfume a log line is about, when more than one is in flight."""
    return f"{site_id} · {search.text}" if multi else site_id


async def run_scan(
    searches: Sequence[Search],
    profiles: Sequence[dict[str, Any]],
    *,
    runner: SiteRunner,
    db_path: Path,
    write_lock: asyncio.Lock,
    force: bool = False,
) -> AsyncIterator[ScanEvent]:
    """Show what storage already knows, then go to the shops for the rest.

    `force=True` skips the cache-first read entirely and scans every search
    -- what a refresh keypress means: cache or no cache, ask the shops
    again, so the table never ends up a mix of two different moments.

    **Cancellation.** This is a plain async generator, so a consumer that
    stops iterating (breaks its `async for`, or is itself cancelled while
    awaiting the next event) tears the scan down through the normal
    `asyncio.TaskGroup` / `browser_session` cleanup path -- there is no
    generation counter in here. A consumer serving more than one scan over
    its lifetime (a new search superseding an old one) is the one that has
    to notice it no longer wants an old scan's events; this function has no
    way to know that on its own.

    **Two traps, unchanged from the TUI this was extracted from:**

    1. `engine.run_sites()` is not used here on purpose: it returns nothing
       until every site is done, which makes live progress impossible. Each
       site instead runs its own perfumes serially, one task per site, so a
       site's requests stay paced from one place and a fast site's rows
       don't wait on a slow one.
    2. Every `store` call is blocking stdlib `sqlite3`, so each one runs in
       `asyncio.to_thread`, and every write goes through `write_lock` so two
       sites finishing together cannot collide on a locked database file.
    """
    enabled = [p for p in profiles if p.get("enabled", True)]
    labels = {str(p["id"]): site_label(p) for p in enabled}

    cache_rows_by_search: dict[int, list[ResultRow]] = {}
    if force:
        to_scan = list(searches)
    else:
        # Storage is asked before any shop is. A perfume that has been
        # searched before already has a price on record for every site that
        # carried it, and spending a full round of requests to find out it
        # is still 540 TL is the cost this exists to skip.
        try:
            cached = await asyncio.to_thread(_read_cache, db_path, searches, labels)
        except Exception:
            # Falling back to a live scan, which is what a first search does
            # anyway. An exception escaping here would kill the scan and
            # leave the caller with nothing at all, and a slow answer beats
            # none.
            logger.exception("kayıttaki fiyatlar okunamadı")
            cached = []
        for row in cached:
            cache_rows_by_search.setdefault(row.query_index, []).append(row)
        to_scan = [s for s in searches if s.index not in cache_rows_by_search]

    yield ScanStarted(total_sites=len(enabled), total_perfumes=len(to_scan))

    for search in searches:
        rows = cache_rows_by_search.get(search.index)
        if rows:
            yield CacheHit(
                query_index=search.index,
                age_days=max(row.age_days for row in rows),
            )
            yield RowsReady(rows=tuple(rows))

    if not to_scan or not enabled:
        yield ScanFinished(error_count=0)
        return

    multi = len(searches) > 1
    error_count = 0
    queue: asyncio.Queue[ScanEvent] = asyncio.Queue()
    # One product read per URL for the whole scan. Two perfumes searched at
    # one shop routinely list the same product, and a second read costs a
    # request and a rate-limit wait to learn what is already known.
    variants_cache: dict[CacheKey, VariantsRead] = {}

    async def scan_site(profile: dict[str, Any], fetcher: Fetcher) -> None:
        nonlocal error_count
        site_id = str(profile["id"])
        await queue.put(SiteStarted(site_id=site_id))
        for search in to_scan:
            try:
                # A shop that writes the house differently ("D&G" for Dolce &
                # Gabbana) answers the typed spelling with an empty results
                # page, and nothing downstream can recover from a page with no
                # products on it. So an empty answer is asked again with the
                # other spellings of that brand, and only an empty answer:
                # asking every spelling every time would multiply the requests
                # rate_limit_ms exists to hold down, against shops that are
                # small.
                for text in search_spellings(search.text):
                    result = await runner(
                        profile,
                        text,
                        fetcher=fetcher,
                        keep_candidate=listing_filter(search.query),
                        variants_cache=variants_cache,
                    )
                    if result.status != "empty":
                        break
            except Exception as e:
                result = SiteResult(site_id, "error", (), f"{type(e).__name__}: {e}")
            try:
                snap_rows = _dedupe_snapshot_rows(snapshot_rows(result, search.query))
            except Exception:
                logger.exception("%s — sonuç okunamadı", site_id)
                error_count += 1
                await queue.put(
                    SiteFinished(
                        site_id=site_id,
                        query_index=search.index,
                        status="error",
                        detail=None,
                        has_rows=False,
                    )
                )
                continue
            has_rows = bool(snap_rows)
            if has_rows:
                await queue.put(
                    RowsReady(
                        rows=tuple(_to_result_rows(labels[site_id], search, snap_rows))
                    )
                )
            if result.status in ("suspect", "error"):
                error_count += 1
                message = (
                    "profil bozulmuş olabilir"
                    if result.status == "suspect"
                    else "bağlantı hatası"
                )
                detail = (result.detail or "").removeprefix(f"{site_id}: ")
                logger.error(
                    "%s — %s: %s", _about(site_id, search, multi=multi), message, detail
                )
            if snap_rows:
                try:
                    async with write_lock:
                        await asyncio.to_thread(
                            _write_snapshot_rows, db_path, snap_rows
                        )
                except Exception:
                    logger.exception("%s — fiyatlar kaydedilemedi", site_id)
                    error_count += 1
                    await queue.put(
                        WriteFailed(site_id=site_id, query_index=search.index)
                    )
            await queue.put(
                SiteFinished(
                    site_id=site_id,
                    query_index=search.index,
                    status=result.status,
                    detail=result.detail,
                    has_rows=has_rows,
                )
            )

    async with browser_session() as fetcher:
        async with asyncio.TaskGroup() as group:
            for profile in enabled:
                group.create_task(
                    scan_site(profile, fetcher), name=f"scan:{profile['id']}"
                )
            remaining = len(enabled) * len(to_scan)
            done = 0
            while done < remaining:
                event = await queue.get()
                if isinstance(event, SiteFinished):
                    done += 1
                yield event

    yield ScanFinished(error_count=error_count)


# -- basket refresh -----------------------------------------------------


@dataclass(frozen=True)
class BasketRefreshStarted:
    total: int


@dataclass(frozen=True)
class BasketPriceExcluded:
    """One (site, row) pair the refresh could not price, whether the site
    broke or it said the decant is gone. `notice` is the warning text to
    show, or None for the silent case: an empty answer is positive evidence
    the shop stopped carrying it, not a failure."""

    site_id: str
    basket_item_id: int
    notice: str | None


@dataclass(frozen=True)
class BasketWriteFailed:
    site_id: str
    notice: str


@dataclass(frozen=True)
class BasketRowFinished:
    """One (site, row) refresh attempt is done, whatever it ended in.

    Always the last event of its unit: a `BasketPriceExcluded` or
    `BasketWriteFailed` for the same unit, if either happens, precedes it.
    """

    site_id: str
    basket_item_id: int


@dataclass(frozen=True)
class BasketRefreshFinished:
    pass


BasketRefreshEvent = (
    BasketRefreshStarted
    | BasketPriceExcluded
    | BasketWriteFailed
    | BasketRowFinished
    | BasketRefreshFinished
)


async def run_basket_refresh(
    rows: Sequence[BasketRow],
    profiles: Sequence[dict[str, Any]],
    *,
    runner: SiteRunner,
    db_path: Path,
    write_lock: asyncio.Lock,
) -> AsyncIterator[BasketRefreshEvent]:
    """Ask every enabled site for today's price of every basket row.

    One task per site, one after the other inside it: `runner` builds its
    own pacer per call, so firing a site's whole basket at once would put
    every rate-limit gap in parallel and hand a small shop the request burst
    this project exists not to send.

    `browser_session` wraps the whole refresh, same as `run_scan`. A site
    whose search page needs a real browser opens one lazily on its first row
    and keeps it for the rest of the refresh; without this, a refresh of N
    basket rows against such a site would launch and tear down N browsers
    instead of one -- a cost that grows with exactly the thing a refresh has
    no control over, how much is already in the basket.

    Policy, unchanged: a site that errors or comes back suspect excludes
    that (site, row) cell and shows a warning; a site that answers empty
    excludes it silently.
    """
    enabled = [p for p in profiles if p.get("enabled", True)]
    yield BasketRefreshStarted(total=len(enabled) * len(rows))
    if not enabled or not rows:
        yield BasketRefreshFinished()
        return

    queue: asyncio.Queue[BasketRefreshEvent] = asyncio.Queue()

    async def refresh_site(profile: dict[str, Any], fetcher: Fetcher) -> None:
        site_id = str(profile["id"])
        for row in rows:
            # Built from the stored identity parts instead of re-parsing a
            # sentence, because those parts are what the basket line is
            # keyed on and a round trip through the text parser could come
            # back split differently and file the refreshed price under
            # another perfume.
            query = PerfumeQuery(
                brand=row.line.brand,
                name=row.line.name,
                concentration=row.line.concentration,
            )
            # The size is left out of the search text on purpose. The shop
            # is asked for the perfume and answers with every size it
            # sells; the basket picks its own size back out of that by the
            # integer join.
            text = f"{row.line.brand} {row.line.name} {row.line.concentration}".strip()
            try:
                result = await runner(profile, text, fetcher=fetcher)
            except Exception as e:
                result = SiteResult(site_id, "error", (), f"{type(e).__name__}: {e}")
            if result.status in ("error", "suspect"):
                await queue.put(
                    BasketPriceExcluded(
                        site_id=site_id,
                        basket_item_id=row.line.basket_item_id,
                        notice=f"⚠ {site_id} tazelenemedi",
                    )
                )
            elif result.status == "empty":
                await queue.put(
                    BasketPriceExcluded(
                        site_id=site_id,
                        basket_item_id=row.line.basket_item_id,
                        notice=None,
                    )
                )
            else:
                snap_rows = _dedupe_snapshot_rows(snapshot_rows(result, query))
                try:
                    async with write_lock:
                        await asyncio.to_thread(
                            _write_snapshot_rows, db_path, snap_rows
                        )
                except Exception as e:
                    await queue.put(
                        BasketWriteFailed(
                            site_id=site_id,
                            notice=(
                                f"⚠ {site_id} — fiyatlar kaydedilemedi "
                                f"({type(e).__name__}: {e})"
                            ),
                        )
                    )
            await queue.put(
                BasketRowFinished(
                    site_id=site_id, basket_item_id=row.line.basket_item_id
                )
            )

    async with browser_session() as fetcher:
        async with asyncio.TaskGroup() as group:
            for profile in enabled:
                group.create_task(
                    refresh_site(profile, fetcher), name=f"refresh:{profile['id']}"
                )
            remaining = len(enabled) * len(rows)
            done = 0
            while done < remaining:
                event = await queue.get()
                if isinstance(event, BasketRowFinished):
                    done += 1
                yield event

    yield BasketRefreshFinished()
