"""Async orchestration: parallel across sites, serial within a site, fault-isolated.

Built on asyncio.TaskGroup. Each site gets its own semaphore, a delay between
requests, and retries with backoff. If one site fails, the others keep going.

Results are never silently empty. If a site looks broken, for example zero results
on a page that clearly has products, a price that won't parse, or a variant selector
that only yielded one price, it gets marked "suspect" instead of "no matches."
Suspect results are excluded from basket totals as unknown, not treated as simply
expensive.

`search_site` is the single-site half of that: it drives one site end to end from
its profile alone. Run a query, read the result list, open each hit, and read its
sizes with whichever extraction layer the profile names.

That layer is used and no other. Falling through to a lower rung at runtime would
paper over exactly the profile rot this project treats as a first-class failure: a
site whose top layer quietly stopped answering would keep returning plausible rows
from a weaker layer, and nobody would learn the profile needs rewriting. Trying the
rungs in order is discovery's job, and reporting that a lower rung could take over
is `validate`'s.

A site the profile cannot express may add a `hooks/<id>.py` and take over one of
three named points. That file is meant to stay rare and to stay small: every hook
written is a sign the profile schema fell short, so the first question a new one
raises is whether the schema should have covered it.

`run_sites` is the other half: it starts every site at once and lets each one walk
its own pages in order.

Pacing is worth the care because the targets are small businesses, not
infrastructure, and a POST endpoint rung multiplies every visit: even paced, such
a site issues one request per size option a product page names instead of one per
product, so its runs are the longest and the ones a shop would notice first.
"""

from __future__ import annotations

import asyncio
import json
import random
import re
import time
from collections.abc import Awaitable, Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Literal, Protocol
from urllib.parse import quote, urljoin

from selectolax.parser import HTMLParser, Node

from parfum_finder.extract import (
    EXTRACTION_LAYERS,
    RawVariant,
    extract_css_variants,
    extract_embedded_variants,
    extract_endpoint_variants,
    extract_jsonld_variants,
    select_all,
    select_field,
)
from parfum_finder.fetch import (
    Fetcher,
    FetchResult,
    FormData,
    Headers,
    Method,
    PlaywrightNotInstalled,
    Strategy,
    fetch,
)
from parfum_finder.normalize import casefold_tr, parse_size_ml
from parfum_finder.probe import _PRODUCT_MARKUP_SELECTOR, _VARIANT_CONTROL_SELECTOR
from parfum_finder.profiles import DEFAULT_HOOKS_DIR, SiteHooks, load_site_hooks

# How many times one request may be sent before the failure is the caller's.
# Three is two recoveries: enough for a dropped connection or a shop catching its
# breath, few enough that a site which is properly down costs seconds, not minutes.
MAX_ATTEMPTS = 3

# What decides whether a search result is worth a request of its own, judged on
# the title the results page already gave. The caller supplies it, so the matcher
# stays outside the engine and one notion of "is this that perfume" keeps living
# in one place.
CandidateFilter = Callable[[str | None], bool]

# Site id and product URL. The site id is in the key so one cache can be shared
# by a whole scan without two shops reading each other's pages.
CacheKey = tuple[str, str]

# The wait before the first retry, doubled for the next one. Deliberately not
# rate_limit_ms: normal spacing is politeness between requests that worked, this
# is backing off from one that was refused, and a profile setting the first to
# zero must not turn a 429 into three requests in a row.
RETRY_BACKOFF_MS = 1000

# Statuses worth sending the same request for a second time. 429 is the shop
# asking directly; the 5xx ones are it having a bad moment. A 403 or a 404 is an
# answer, and repeating the request cannot change it.
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})

# The longest pause a shop may ask for and still be waited out. A refusal can
# name its own delay, and honouring it is the polite thing right up until the
# number is larger than the run has any business sitting through: a shop asking
# for an hour has said no, and holding a scan open to ask it again is neither
# useful to the person waiting nor kinder to the shop. Past this it is handed back
# as the answer, and the extraction layer already knows how to call a page it
# cannot read suspect.
MAX_RETRY_AFTER_S = 30.0

# How much a request may be held back beyond its site's own spacing, in
# milliseconds. Added to a wait, never subtracted from one: rate_limit_ms is the
# floor a shop is owed, and jitter allowed to shorten it would quietly spend what
# the profile set aside. What it buys is a run that does not arrive on a
# metronome, which is the part of looking like a person that fixed spacing alone
# cannot do.
JITTER_MS = (50.0, 200.0)

# How much product-shaped markup a search page has to carry before a run with no
# results off it is read as a dead selector rather than an honest "not sold here".
#
# The number is measured, not chosen: it is the smallest count any of the six
# captured search fixtures produces, from a page listing four products. The
# selector being counted is probe's, and probe warns it is a relative figure
# meant for comparing strategies on one page, not an absolute verdict. Using it
# absolutely is why the floor is taken from real pages instead of picked. A shop
# page's own chrome, the category links in its header and footer, lands well
# under this, which is what keeps a genuine no-results page from wearing the
# badge. Getting that wrong is worse than missing a break, because a badge that
# cries wolf on every unstocked perfume is one nobody reads.
PRODUCT_MARKUP_FLOOR = 8

# The shop saying, in its own markup, that this search found nothing. That is a
# direct answer and it outranks the count above, which is only a guess.
#
# It has to, because the guess was measured on shop pages that turned out not to
# be representative. Two of the six sites run their catalog through the header:
# a mega-menu listing every category, a sidebar widget of recent products, a grid
# of category tiles. None of it is a search result, all of it is product-shaped,
# and it lands at 138 and 426 nodes on a page whose own body class says
# search-no-results. Both shops therefore wore the broken-profile badge on every
# perfume they simply do not stock, which is exactly the cry-wolf failure the
# floor was picked to avoid.
#
# WordPress writes the body class on any search that matched nothing, and
# WooCommerce adds its own notice, so one entry covers both spellings a
# WooCommerce shop may use. Other platforms say it their own way and are not
# covered here: they keep falling through to the count, which is where they were
# before. A missing entry costs a false badge, never a missed break.
_NO_RESULTS_SELECTOR = ", ".join(
    (
        "body.search-no-results",
        ".woocommerce-no-products-found",
    )
)

# Bound at module level so tests can replace it and assert on the delays that were
# asked for. Sleeping for real would make the suite pay the pacing it is checking,
# and asserting on elapsed wall clock instead measures how busy the machine is.
_sleep = asyncio.sleep

# Bound for the same reason, and it matters more here: a test that rolls real
# dice cannot say what the code decided, only what it happened to draw.
_jitter = random.uniform


def _jitter_s() -> float:
    """A small random addition to a wait, in seconds."""
    low, high = JITTER_MS
    return _jitter(low, high) / 1000


class ExtractionFailed(RuntimeError):
    """A page answered but gave up nothing, where something was expected.

    This is the "suspect" condition of the error-isolation table, raised at the
    moment it is detected rather than folded into an empty result list. A site
    that returns nothing and a site whose selectors died look identical from the
    outside, and treating the second as the first is how a missing site gets read
    as "that perfume isn't sold there".

    The message names the page and the layer, because the next thing anyone does
    with this is open that page and check that one selector.
    """


@dataclass(frozen=True)
class PageEvidence:
    """What a product page said about its own sizes, kept instead of the page.

    Both answers are read off the markup once, while the page is in hand, and the
    page is then let go. Keeping the markup instead would hold every product a
    scan opened in memory for as long as the scan runs, so that two questions
    whose answers cannot change could be asked again off the same bytes.

    `offers_sizes` is whether this page had a size list for the layer to fail at,
    which is what separates a profile that went blind from a catalog that sells
    this perfume in one piece. A page nothing can be read off answers True, since
    the check it feeds has to fail loudly by default.

    `control_options` is how many sizes the page's own picker offered, or None
    when there was no page to count on or the profile names no picker. None means
    there is nothing to say, not that the page offered none.
    """

    offers_sizes: bool
    control_options: int | None


# One product read: the raw size rows, and what the page they came off showed.
VariantsRead = tuple[tuple[RawVariant, ...], PageEvidence]


@dataclass(frozen=True)
class ProductCandidate:
    """One hit on a search results page, before its product page is opened.

    `raw_title` is the listing's own wording, kept verbatim: it is what makes a
    wrong match visible to a person reading the results table, so nothing here
    tidies it up.
    """

    raw_title: str | None
    url: str


@dataclass(frozen=True)
class Variant:
    """One decant size of one product, in the units the database stores.

    Tenths of a millilitre and kuruş, both as integers, because both are compared
    and joined on: a basket matches sizes across sites by this number, and a free
    shipping threshold is a comparison that binary floats lose at the boundary.

    `price_kurus` may be None. A size that is sold out often shows no price at
    all, and dropping it would erase the difference between "this shop never sells
    that size" and "that size is out of stock right now", which is exactly what
    the stock column is for.
    """

    size_ml_x10: int
    raw_title: str | None
    product_url: str | None
    price_kurus: int | None
    in_stock: bool | None


@dataclass(frozen=True)
class SearchHit:
    """A candidate together with the decant sizes its product page offers."""

    candidate: ProductCandidate
    variants: tuple[Variant, ...]


SiteStatus = Literal["ok", "empty", "suspect", "error"]


@dataclass(frozen=True)
class SiteResult:
    """What one site had to say about one query, and how much to trust it.

    Four states, and the whole point of the type is the difference between the
    middle two:

    `ok` — hits came back. `empty` — the site answered fine and genuinely has
    nothing, either no search results at all or nothing but full bottles and
    testers. `suspect` — the site answered and the profile could not read it,
    so what it has is unknown. `error` — the request or the profile blew up
    before an answer existed.

    `empty` and `suspect` both carry no rows, and collapsing them is the bug
    this milestone exists to make impossible: one means "not sold here" and the
    other means "we stopped being able to see it". Downstream they part ways
    too, a suspect site is left out of basket totals as unknown rather than
    counted as expensive.

    `detail` is the line a person reads. It is filled in for every status
    including `ok`, because a result that says what it saw is how someone
    notices a site quietly returning one row where it used to return ten.
    """

    site_id: str
    status: SiteStatus
    hits: tuple[SearchHit, ...]
    detail: str | None


@dataclass
class SitePace:
    """One site's pacing state, for as long as whoever holds it says.

    The gate and the stamp are one object because the wait has to be decided
    while holding the gate. Sharing a bare timestamp instead would put the
    decision outside any shared lock, and two callers reading the same stamp both
    conclude the wait is over and send together.

    Held by the caller so it can outlive one request and one query. A scan asks
    each shop about several perfumes, and state that resets between them lets the
    first request of every perfume leave with no gap in front of it, which is a
    burst of exactly the shape the spacing exists to prevent.
    """

    gate: asyncio.Semaphore = field(default_factory=lambda: asyncio.Semaphore(1))
    last_finished: float | None = None


def _retry_after_s(result: FetchResult) -> float | None:
    """How long the shop asked to be left alone, or None if it did not say.

    A refusal may name its own delay, in seconds or as a date, and both spellings
    are in use. Reading it is how a retry becomes the thing the shop asked for
    rather than a guess that happens to land near it.

    Read off any status worth retrying, not only a 429. A 503 carrying the header
    is a shop saying when it will be back, and there is no reason to honour that
    from one status and guess at it from another.

    Anything unparseable answers None and falls back to the ordinary backoff. A
    header nobody can read is not a reason to stop retrying; it is only a reason
    not to trust it.

    A date already in the past comes back as zero rather than negative, since a
    shop saying "after a moment that has passed" is saying to go ahead.
    """
    raw = result.headers.get("retry-after")
    if raw is None:
        return None
    raw = raw.strip()
    try:
        return max(0.0, float(int(raw)))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return max(0.0, (when - datetime.now(UTC)).total_seconds())


def _paced_fetcher(
    profile: dict[str, Any], fetcher: Fetcher, pace: SitePace
) -> Fetcher:
    """Wrap a fetcher so one site's requests go out one at a time, spaced apart.

    The state is `pace`, and it belongs to the caller rather than to this
    closure. Two sites running side by side get one each and never wait on each
    other, which is the whole point of starting them together; a module-level
    gate would quietly turn the run serial and nothing would look wrong except
    the clock. A caller handing the same one back across several queries is what
    keeps a shop from being asked about the next perfume the instant the last one
    finished.

    The semaphore is the seriality guarantee rather than a throughput knob: the
    flow through one site is already sequential, but a hook is free to fire
    requests of its own, and this is what keeps such a site from becoming the
    burst the pacing exists to prevent.

    Everything happens while holding it, the waiting included. Deciding outside
    the gate lets two callers both look at the same last-finished stamp, both
    conclude the wait is over, and send together.

    Spacing is measured from when the previous request finished, not when it
    started, so a slow page is not followed immediately by the next one. The
    first request against a shop waits for nothing, since there is nothing to be
    polite about yet.

    A wait that happens carries a little jitter on top, so a run does not arrive
    on a metronome. It is only ever added, and only to a wait there already was:
    a profile asking for no spacing gets none, which is what keeps the setting
    meaning what it says.

    Retries cover the transient half only. A refused connection, a timeout, a 429
    or a 5xx get another go after a backoff; a missing playwright install, an
    unknown strategy or a POST a strategy cannot do are settings that will fail
    the same way every time, and repeating them just delays the error message.
    A status this gives up on is handed back as it is, unraised: reading what a
    503 page contains is the extraction layer's business, and it already knows
    how to call an unreadable page suspect.

    A refusal naming its own delay is waited out for exactly that, with no
    jitter added: the number came from the shop, and padding it would be
    answering a request with something else. That covers any retryable status
    carrying the header, a 503 as much as a 429. One longer than
    MAX_RETRY_AFTER_S ends the retries instead, since a shop asking for that much
    has said no.
    """
    rate_limit_s = int(profile.get("rate_limit_ms", 800)) / 1000

    async def attempt(
        url: str,
        strategy: Strategy,
        *,
        method: Method,
        data: FormData | None,
        headers: Headers | None,
        timeout_s: int,
    ) -> FetchResult:
        if pace.last_finished is not None:
            waited = time.monotonic() - pace.last_finished
            if waited < rate_limit_s:
                await _sleep(rate_limit_s - waited + _jitter_s())
        try:
            return await fetcher(
                url,
                strategy,
                method=method,
                data=data,
                headers=headers,
                timeout_s=timeout_s,
            )
        finally:
            pace.last_finished = time.monotonic()

    async def paced(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        async with pace.gate:
            for attempts_made in range(MAX_ATTEMPTS - 1):
                try:
                    result = await attempt(
                        url,
                        strategy,
                        method=method,
                        data=data,
                        headers=headers,
                        timeout_s=timeout_s,
                    )
                except (PlaywrightNotInstalled, NotImplementedError, ValueError):
                    raise
                except Exception:
                    pass
                else:
                    if result.status_code not in RETRY_STATUS:
                        return result
                    asked = _retry_after_s(result)
                    if asked is not None:
                        if asked > MAX_RETRY_AFTER_S:
                            return result
                        await _sleep(asked)
                        continue
                # The guess, for a shop that refused without saying how long.
                # Jittered like the spacing is, and for the same reason.
                await _sleep(RETRY_BACKOFF_MS * 2**attempts_made / 1000 + _jitter_s())
            # The last attempt is unguarded on purpose: whatever it gives is the
            # answer, so a caller sees the real exception rather than one this
            # wrapper reworded.
            return await attempt(
                url,
                strategy,
                method=method,
                data=data,
                headers=headers,
                timeout_s=timeout_s,
            )

    return paced


class SiteRunner(Protocol):
    """What a caller needs of run_site, as a type callers can stand a fake in for.

    A protocol rather than a plain callable alias because a scan hands the
    runner more than a query: the browser session it owns, the filter that
    keeps a listing from being opened for nothing, and the product cache the
    perfumes of one scan share. A stand-in that cannot take them is a type
    error at the call site instead of a surprise mid-scan.
    """

    def __call__(
        self,
        profile: dict[str, Any],
        query: str,
        *,
        fetcher: Fetcher = ...,
        keep_candidate: CandidateFilter | None = ...,
        variants_cache: MutableMapping[CacheKey, VariantsRead] | None = ...,
        pacers: MutableMapping[str, SitePace] | None = ...,
    ) -> Awaitable[SiteResult]: ...


async def run_site(
    profile: dict[str, Any],
    query: str,
    *,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
    fetcher: Fetcher = fetch,
    keep_candidate: CandidateFilter | None = None,
    variants_cache: MutableMapping[CacheKey, VariantsRead] | None = None,
    pacers: MutableMapping[str, SitePace] | None = None,
) -> SiteResult:
    """Run one site and classify what came back instead of raising.

    It is also where the pacing goes on. The fetcher handed down is wrapped so
    this site's requests leave one at a time, `rate_limit_ms` apart, with a
    bounded backoff retry on the transient ones. `search_site` stays unpaced
    because offline validation drives it against saved fixtures, where sleeping
    between reads off a disk buys nobody anything.

    This is `search_site` with the failures turned into data. Callers that run
    many sites at once want one site's breakage to be a row in the report, not
    an exception that has to be caught at every call site, and the TUI needs the
    reason in a form it can print next to the site's name.

    `search_site` keeps raising, because the tools that drive one site on
    purpose, validate above all, want the traceback and the exact message. This
    wrapper is for the run loop.

    Anything that is not `ExtractionFailed` is an `error`: a timeout, a profile
    field that does not exist, a hook that returned the wrong type. They differ
    in cause but not in what can be done with them, which is nothing but tell
    the user this site is out of this comparison and why.

    `keep_candidate` is passed down to `search_site` and counted on the way, so
    the `ok` detail can say how many listings were skipped. A filter that
    narrows the scan silently is the same failure as a broken selector: the
    table looks complete either way.

    `variants_cache` is shared across calls by whoever runs several perfumes
    against one site, so a product listed under two of them is read once. It is
    keyed by site as well as URL, so one dict can be handed to every site of a
    scan without two shops ever reading each other's pages.

    `pacers` is the same idea for politeness. Passing none gives this call a
    pacer of its own, which spaces the requests within it and nothing further;
    handing the same dict back for the next perfume is what makes the spacing
    hold across a whole scan instead of restarting at every query, where the
    first request of each one leaves with no gap in front of it.
    """
    # Only the id is read outside the boundary, because it is what a report row
    # is addressed by: a profile without one is not a site this can speak about,
    # so there is no honest SiteResult to hand back for it. Everything else,
    # setting up the pacing included, happens inside. A profile whose
    # rate_limit_ms is not a number would otherwise raise on the way in, before
    # the try, and take every other site in the TaskGroup down with it.
    site_id = str(profile["id"])
    skipped = 0

    def counted(raw_title: str | None) -> bool:
        nonlocal skipped
        assert keep_candidate is not None
        keep = keep_candidate(raw_title)
        if not keep:
            skipped += 1
        return keep

    pace = pacers.setdefault(site_id, SitePace()) if pacers is not None else SitePace()
    try:
        paced = _paced_fetcher(profile, fetcher, pace)
        hits = await search_site(
            profile,
            query,
            hooks_dir=hooks_dir,
            fetcher=paced,
            keep_candidate=counted if keep_candidate is not None else None,
            variants_cache=variants_cache,
        )
    except ExtractionFailed as e:
        return SiteResult(site_id, "suspect", (), str(e))
    except Exception as e:
        # Broad on purpose. This is the fault isolation boundary, so an
        # unforeseen failure has to end up in the report rather than take the
        # other sites down with it. The type is named because a bare timeout
        # message and a bare KeyError read the same and mean opposite things.
        # No site id in front of it, the result already carries one.
        return SiteResult(site_id, "error", (), f"{type(e).__name__}: {e}")
    filtered = f", {skipped} listing(s) skipped by title" if skipped else ""
    if not hits:
        return SiteResult(
            site_id, "empty", (), f"{site_id}: no decant matched {query!r}{filtered}"
        )
    sizes = sum(len(hit.variants) for hit in hits)
    return SiteResult(
        site_id,
        "ok",
        hits,
        f"{site_id}: {len(hits)} product(s), {sizes} decant size(s){filtered}",
    )


async def run_sites(
    profiles: Sequence[dict[str, Any]],
    query: str,
    *,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
    fetcher: Fetcher = fetch,
    keep_candidate: CandidateFilter | None = None,
    variants_cache: MutableMapping[CacheKey, VariantsRead] | None = None,
    pacers: MutableMapping[str, SitePace] | None = None,
) -> tuple[SiteResult, ...]:
    """Run every site against one query, all at once, and report each separately.

    Parallel across sites, serial inside one. The sites are unrelated shops, so
    nothing is gained by waiting for one before starting the next, and the run
    takes as long as the slowest site rather than the sum of all of them. Inside
    a site the pages stay in order: a shop's search page has to be read before
    its product pages can be opened, and firing a small business's whole product
    list at once is exactly what this project does not do.

    Fault isolation comes from `run_site`, which turns a site's failure into a
    `SiteResult` rather than an exception. That is what makes a TaskGroup the
    right tool here despite its all-or-nothing reputation: no task raises, so
    nothing ever cancels its siblings, and the group is used for the guarantee
    that no task outlives this call. A site that blows up shows up as an `error`
    row next to the sites that answered.

    Results come back in profile order, not finish order, so the same set of
    sites always reads the same way regardless of which shop happened to be
    slow. The TUI's streaming table wants the opposite and will need its own
    channel; ordering here is for callers that want the whole comparison.

    `keep_candidate` and `variants_cache` are handed to every site untouched. The
    cache is one dict for the whole call and safe to pass again on the next one,
    which is what lets a caller scanning several perfumes read a shared product
    page once.
    """
    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(
                run_site(
                    profile,
                    query,
                    hooks_dir=hooks_dir,
                    fetcher=fetcher,
                    keep_candidate=keep_candidate,
                    variants_cache=variants_cache,
                    pacers=pacers,
                ),
                name=f"site:{profile['id']}",
            )
            for profile in profiles
        ]
    return tuple(task.result() for task in tasks)


async def search_site(
    profile: dict[str, Any],
    query: str,
    *,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
    fetcher: Fetcher = fetch,
    keep_candidate: CandidateFilter | None = None,
    variants_cache: MutableMapping[CacheKey, VariantsRead] | None = None,
) -> tuple[SearchHit, ...]:
    """Run one query against one site and read every hit's sizes.

    Everything site-specific comes from `profile`: the search URL shape, which
    fetch strategy each page needs, the selectors that pick result rows out of
    the listing, and which extraction layer the product pages answer on.

    A site whose shape the profile cannot express may put a `hooks/<id>.py` next
    to it and take over one of three points: the query before it is sent, the
    candidate list after the results page is read, or the variant extraction. The
    rest of the flow, and the whole profile, still apply either way. A site with
    no hook file behaves exactly as before, which is every site so far.

    `fetcher` is what actually gets the bytes, the real network by default. It is
    a parameter so that offline profile validation can serve this site's saved
    fixtures through this very function, rather than validating a second flow
    that only resembles the one production runs.

    Each hit's sizes come back already read in millilitres and filtered down to
    the decants, per the profile's variant rules. Pairing a hit with the perfume
    that was actually asked for still needs the matcher, which reads these rows
    rather than being folded in here.

    A hit that ends up with no decant sizes is dropped, not fatal. Search results
    mix decants with plain full bottles, and one shop's catalog is known to be
    roughly four fifths of the latter: a full bottle has no size table worth
    reading, and letting one of those end the site would throw away the decants
    listed next to it.

    Raises ExtractionFailed only when the search returned hits, at least one of
    the pages opened had a size list to read at all, and the extraction layer
    read not one price from any of them, measured before the decant filter runs.
    A page that gave up sizeless rows counts as having had one, since the layer
    demonstrably found the list and lost only the prices off it. An
    empty result list off a page with nothing product-shaped on it is not an
    error, because a shop may genuinely not stock the perfume, and neither is a
    page of nothing but full bottles. But a page full of results where every
    product page reads as empty is a broken profile until proven otherwise: that
    is the difference between "not sold here" and "we stopped being able to see
    it", which is what a silent empty result destroys.

    The size-list clause is what keeps that reading honest, and it is not
    hypothetical: one shop's catalog is roughly four fifths full bottles, so a
    perfume it sells only as one puts a single sizeless product page in front of
    this check and nothing else. Reading that as a break blames the profile for a
    page that never had sizes on it. `_page_offers_sizes` is what draws the line,
    on the shop's markup rather than the profile's selectors, because evidence
    taken from the profile cannot tell a full bottle from a profile gone blind.

    Raises for the same reason one step earlier when the search page itself came
    back with no rows while plainly listing products, per `_check_empty_search`.

    Also raises when a profile names a `variant_control` and the page's size
    picker offers more options than the layer produced rows. That is the same
    failure one notch quieter: the site still answers, the table still fills,
    and a few sizes are simply missing from the comparison.

    `keep_candidate` judges a listing on the title the results page already gave
    and decides whether its product page is worth opening. That is where a scan
    spends its time: one request per candidate, `rate_limit_ms` apart, over a
    catalog that is mostly full bottles. Whether a product really is the searched
    perfume is still decided afterwards, on the product page, by the matcher the
    caller runs. This only decides where the requests go.

    One candidate is opened even when the filter keeps none of them. Without it a
    shop whose product pages stopped parsing would come back `empty` on every
    search where no title looked promising, which is exactly the
    `empty`-versus-`suspect` collapse the checks below exist to prevent. That one
    request is what still separates "not sold here" from "we stopped being able
    to read it".

    The trade left standing: `variant_control` is only checked on pages that were
    opened, so a size picker growing behind a skipped listing goes unnoticed
    until that perfume is the one being searched for.

    `variants_cache` memoizes product reads by site and URL. It belongs to the
    caller so it can span several perfumes against the same shop; passing none
    reads every page fresh.
    """
    hooks = load_site_hooks(str(profile["id"]), hooks_dir)
    if hooks.before_search is not None:
        rewritten = hooks.before_search(profile, query)
        if not isinstance(rewritten, str):
            # Coercing instead would search the site for the word "None" when a
            # hook forgets its return, get an empty results page, and report that
            # as the perfume not being sold here.
            raise ValueError(
                f"{profile['id']}: before_search returned "
                f"{type(rewritten).__name__}, not the query string to send"
            )
        query = rewritten
    result = await _fetch_page(
        profile, _search_url(profile, query), role="search", fetcher=fetcher
    )
    candidates = _read_candidates(profile, result.html, result.url)
    if hooks.after_search is not None:
        candidates = tuple(hooks.after_search(profile, candidates, result.html))
    if not candidates:
        _check_empty_search(profile, result)

    opened = _candidates_to_open(candidates, keep_candidate)
    rules = profile["variant_rules"]
    hits: list[SearchHit] = []
    extracted_a_price = False
    opened_a_page_with_sizes = False
    for candidate in opened:
        rows, evidence = await _read_variants(
            profile, candidate, hooks, fetcher, variants_cache
        )
        _check_variant_control(profile, candidate, rows, evidence)
        # Rows without prices are the loudest evidence of all: the layer read the
        # size list and lost only the price, so the page plainly had one and no
        # amount of missing markup argues otherwise.
        opened_a_page_with_sizes |= bool(rows) or evidence.offers_sizes
        rows = tuple(_with_candidate_identity(row, candidate) for row in rows)
        extracted_a_price |= any(row.price is not None for row in rows)
        variants = apply_variant_rules(rows, rules)
        if variants:
            hits.append(SearchHit(candidate=candidate, variants=variants))
    if opened and opened_a_page_with_sizes and not extracted_a_price:
        # Name what actually read the pages. A hook that took the job over is the
        # thing to open, and blaming the profile's layer for it sends whoever
        # reads this to the wrong file.
        source = (
            f"the parse_variants hook of {profile['id']}"
            if hooks.parse_variants is not None
            else f"the {profile['extraction']!r} layer"
        )
        raise ExtractionFailed(
            f"{profile['id']}: {source} read no priced size from any of the "
            f"{len(opened)} search result(s) it opened, starting with "
            f"{opened[0].url}"
        )
    return tuple(hits)


def _candidates_to_open(
    candidates: tuple[ProductCandidate, ...], keep_candidate: CandidateFilter | None
) -> tuple[ProductCandidate, ...]:
    """Narrow the search results down to the pages worth a request.

    The first one survives a filter that keeps nothing, and it is not a
    consolation prize: it is what keeps the price-extraction check above running
    on a real page. Kept out, a shop whose product pages went unreadable would
    report `empty` for every search whose listings looked unpromising, and
    "nobody here sells this" is the one thing a broken profile must never be able
    to say.
    """
    if keep_candidate is None or not candidates:
        return candidates
    kept = tuple(
        candidate for candidate in candidates if keep_candidate(candidate.raw_title)
    )
    return kept or candidates[:1]


def _check_empty_search(profile: dict[str, Any], result: FetchResult) -> None:
    """Fail when a search yielded no rows off a page that plainly lists products.

    The first line of the fail-loud table, and the one that costs the most when
    it is missing: a shop whose search selectors died answers 200 with a full
    page of perfumes, this reads nothing off it, and the shop drops out of the
    comparison looking exactly like a shop that does not stock the perfume. The
    cheapest site then wins on a table with a silent hole in it.

    Two separate reasons to be suspicious, and the first needs no guessing. If
    the row selector matched nodes but not one of them gave up a link, the rows
    are there and the link selector underneath them is dead. Rows going missing
    one at a time is not the same thing and stays allowed: one captured shop
    really does list five cards where only one is a product link.

    The second reason is the guess, and it is only reached when the page does not
    already answer the question itself. A shop that writes "this search found
    nothing" into its markup is telling us the row count is right, and no amount
    of product-shaped chrome around that sentence changes it: `_NO_RESULTS_SELECTOR`
    ends the check there.

    Failing that, nothing matched at all, so there is no evidence from the profile
    itself, only from the page: enough product-shaped markup on it and a run that
    read nothing is a broken selector rather than an answer. A page that is
    genuinely empty of products fails this and is correctly reported as empty.

    Only reached when the search produced nothing, so the reparse costs the
    normal path nothing.
    """
    root = HTMLParser(result.html).root
    if root is None:
        raise ExtractionFailed(
            f"{profile['id']}: {result.url} parsed to no markup "
            f"({len(result.html.encode())} byte body)"
        )
    selector = str(profile["search"]["result_item"])
    rows = len(root.css(selector))
    if rows:
        raise ExtractionFailed(
            f"{profile['id']}: {result.url} has {rows} result row(s) "
            f"({selector!r}) but none of them carried a link "
            f"({profile['search']['result_url']!r}), so every hit was dropped"
        )
    if root.css(_NO_RESULTS_SELECTOR):
        return
    cards = len(root.css(_PRODUCT_MARKUP_SELECTOR))
    if cards >= PRODUCT_MARKUP_FLOOR:
        raise ExtractionFailed(
            f"{profile['id']}: {selector!r} matched nothing on {result.url}, "
            f"but the page carries {cards} product-shaped node(s), so it is "
            f"listing something this profile can no longer see"
        )


def _check_variant_control(
    profile: dict[str, Any],
    candidate: ProductCandidate,
    rows: Sequence[RawVariant],
    evidence: PageEvidence,
) -> None:
    """Fail when the page's size picker offers more sizes than the layer read.

    The silent failure one notch quieter than an empty result: a product page
    with six sizes whose blob only carries two still produces rows, still fills
    the table, and still looks fine. Four sizes are just gone from the
    comparison, and the ₺/ml the shop is judged on is the ₺/ml of whichever two
    survived. One shop shipped exactly this during the discovery round.

    Counting rows, not prices. A size that is sold out often carries no price at
    all, so comparing prices against options would flag every shop with anything
    out of stock and teach whoever reads the badge to ignore it.

    A page whose picker matches nothing is not checked. That is a plain full
    bottle, which has no size table to be missing anything from, and those sit
    next to the decants in every catalog seen so far.

    Options that read as empty do not count either: a picker's first entry is
    usually a "choose a size" placeholder with no value behind it.

    The counting itself happened when the page was read, so a product listed under
    two of a scan's perfumes is checked both times off one reading of it.
    """
    options = evidence.control_options
    if options is None or options <= len(rows):
        return
    raise ExtractionFailed(
        f"{profile['id']}: {candidate.url} offers {options} sizes "
        f"({profile.get('variant_control')!r}) but the {profile['extraction']!r} "
        f"layer read {len(rows)}, so the sizes it missed would be priced by nobody"
    )


def _root(html: str | None) -> Node | None:
    """Parse a page once, or say there is no page to parse.

    Both ways of having no markup answer the same here, because everything
    downstream treats them the same: either no page was opened, or one was and it
    parsed to nothing.
    """
    return HTMLParser(html).root if html is not None else None


def _page_evidence(profile: dict[str, Any], root: Node | None) -> PageEvidence:
    """Read both facts a product page can offer about its sizes, in one pass.

    The only place a PageEvidence is built, so the two questions are always
    answered off the same reading of the same page and cannot drift apart. Every
    path that produces a product read comes through here, the ones that give up
    early included: a POST body with no options to post and a page carrying no
    size picker are different facts, and answering one with the other is exactly
    the confusion this exists to prevent.

    A page nothing can be read off answers `offers_sizes` True and counts no
    options. That is the fail-loud default, since nothing here is able to clear a
    profile: a layer that read no price off a page nobody can judge still has to
    answer for it.
    """
    if root is None:
        return PageEvidence(offers_sizes=True, control_options=None)
    selector = profile.get("variant_control")
    options = (
        len([value for value in select_all(root, str(selector)) if value.strip()])
        if selector
        else None
    )
    return PageEvidence(
        offers_sizes=_page_offers_sizes(profile, root),
        control_options=options,
    )


def _page_offers_sizes(profile: dict[str, Any], root: Node) -> bool:
    """Whether this product page had a size list for the layer to fail at.

    The question the site-level "read no priced size" check needs answered, and
    the reason it can tell a profile that went blind from a catalog that simply
    sells this perfume in one piece. Only a page that offers sizes is evidence
    against the profile; a page with none was never going to produce a row.

    Two ways to answer no. A page the shop marks sold out is one: its sizes are
    listed but unbuyable, and several shops stop writing the markup that prices
    them, which is a stock fact about one perfume rather than anything about the
    profile. A page with no size-picker markup at all is the second: a plain full
    bottle. Everything else answers yes.

    Only ever asked about a page that parsed. A page there is no markup for at all
    is the caller's case to answer, and it answers yes there for the same reason:
    the check this feeds has to fail loudly when nothing can clear a profile.

    The picker is looked for in the shop's own markup and never through the
    profile's selectors. A profile whose blob key was renamed also reads zero
    sizes off its own selector, so answering with it would excuse precisely the
    break this exists to catch.
    """
    if _page_says_sold_out(profile, root):
        return False
    return bool(root.css(_VARIANT_CONTROL_SELECTOR))


def _page_says_sold_out(profile: dict[str, Any], root: Node) -> bool:
    """Whether the page carries the shop's own out-of-stock marker.

    Named by the profile, usually through its platform template, because there is
    no markup every shop shares for this the way there is for a size picker: one
    writes a "notify me when it's back" button where the add-to-cart button was,
    another leaves the button and adds a notice beside it. A profile that names
    nothing keeps the old behavior, where a sold-out page is indistinguishable
    from a broken one.
    """
    selector = profile.get("out_of_stock")
    return bool(selector) and bool(root.css(str(selector)))


def _with_candidate_identity(
    row: RawVariant, candidate: ProductCandidate
) -> RawVariant:
    """Give a size the listing's title and URL when the page gave it none,
    and make sure whatever URL it does have is one a browser can open on its own.

    A site that lists every size as its own product names each one; a site with
    one page per product and a size table names none of them, and every size
    there really does share the page's title and URL. Leaving those empty would
    show blank rows in the results table and give the browse-this-one key nothing
    to open.

    A row's own URL, when it has one, still might be site-relative -- some
    endpoints and markup tables hand back "/urun/..." rather than a full link,
    since that is all the page itself needs. `candidate.url` is always absolute
    (it was already resolved against the page that was fetched), so resolving
    the row's URL against it turns a relative path into one that opens correctly
    outside the app, e.g. when written into the wishlist sheet.
    """
    url = urljoin(candidate.url, row.url) if row.url is not None else candidate.url
    if row.title is not None and url == row.url:
        return row
    return replace(
        row,
        title=row.title if row.title is not None else candidate.raw_title,
        url=url,
    )


def apply_variant_rules(
    rows: Sequence[RawVariant], rules: Mapping[str, Any]
) -> tuple[Variant, ...]:
    """Turn raw size rows into decant variants, dropping what is not a decant.

    Three things happen here, all driven by the profile's `variant_rules`:

    The size is read out of whichever text the site puts it in (`size_from`) with
    the site's own pattern, because the labels are not tidy: "2,7 ml - metal
    sprey", "30mldekant", "1 ML" and "10 ml " are all real. A row whose size
    cannot be read is dropped, since a size is what makes a price comparable at
    all and a price per unknown volume is worse than no row.

    Rows naming something that is not a decant are dropped by keyword, matched
    against both the title and the size label because the giveaway sits in
    different places on different sites: one shop writes "Full Şişe" in the title
    while another writes "30mldekant" in the size. Matching is casefolded rather
    than lowercased so that the Turkish dotted capital in a word like "Şişe"
    compares the way a reader expects.

    Sizes at or above `max_size_ml` are dropped too, whatever they call
    themselves. That threshold is the profile's, so a shop selling an unusual
    range can move it.

    A price that comes out to exactly 0 kuruş is read as no price, not a free
    perfume. At least one platform prints "0,00 TL" in every price field of a
    size that is out of stock rather than leaving the field out, so the raw
    value cannot be told apart from a genuine free item by its shape alone.
    Nothing in this domain is actually free, so the zero is read the same way
    a missing field already is: `price_kurus=None`, which is what keeps a dead
    row from looking like the cheapest option in the table, or the cheapest
    thing a basket optimizer could pick.
    """
    variants: list[Variant] = []
    for row in rows:
        size_ml = _read_size_ml(row, rules)
        if size_ml is None or size_ml <= 0:
            continue
        if _is_excluded(row, rules, size_ml):
            continue
        price_kurus = _to_kurus(row.price)
        variants.append(
            Variant(
                size_ml_x10=int((size_ml * 10).quantize(Decimal(1), ROUND_HALF_UP)),
                raw_title=row.title,
                product_url=row.url,
                price_kurus=price_kurus if price_kurus else None,
                in_stock=row.in_stock,
            )
        )
    return tuple(variants)


def _read_size_ml(row: RawVariant, rules: Mapping[str, Any]) -> Decimal | None:
    """Read one row's volume in millilitres, or None if the text does not say.

    "field" means the extraction layer already produced a bare number, so the
    pattern is skipped; the other two run it over the size label or the title.
    """
    source = row.size_raw if rules["size_from"] != "title" else row.title
    if not source:
        return None
    if rules["size_from"] == "field":
        text = source
    else:
        # Searched, not matched from the start, and case-insensitively: the unit
        # sits in the middle of "2,7 ml - metal sprey", runs into the number in
        # "30mldekant", and is written "ML" as often as "ml".
        match = re.search(str(rules["size_pattern"]), source, re.IGNORECASE)
        if match is None:
            return None
        text = match.group(1) if match.groups() else match.group(0)
    try:
        return parse_size_ml(text)
    except (ValueError, InvalidOperation):
        return None


def _is_excluded(row: RawVariant, rules: Mapping[str, Any], size_ml: Decimal) -> bool:
    """Whether this row is something other than a decant.

    The size threshold is inclusive: a profile saying 30 means 30 ml is already a
    bottle, not a sample. So a size labelled "30mldekant" is dropped despite the
    word in its own name, because what it is depends on how much is in it.
    """
    if size_ml >= Decimal(str(rules["max_size_ml"])):
        return True
    haystack = casefold_tr(" ".join(part for part in (row.title, row.size_raw) if part))
    return any(
        casefold_tr(str(keyword)) in haystack for keyword in rules["exclude_keywords"]
    )


def _to_kurus(price: Decimal | None) -> int | None:
    """Convert a price in lira to whole kuruş.

    Integers all the way, never a float: a basket total decides whether a free
    shipping threshold is met, and that comparison has to be exact at the
    boundary rather than nearly right.
    """
    if price is None:
        return None
    return int((price * 100).quantize(Decimal(1), ROUND_HALF_UP))


def _search_url(profile: dict[str, Any], query: str) -> str:
    """Fill the profile's search template with an escaped query.

    The query is escaped with nothing left safe, because the templates put it in
    two different places: one platform spells search as a path segment
    ("/arama/{query}") and another as a query string parameter ("?s={query}").
    Percent-escaping everything is correct in both, while leaving a space raw
    would send a malformed URL in the first case and silently search for the
    first word only in the second.
    """
    search = profile["search"]
    return str(search["url_template"]).format(
        base_url=profile["base_url"], query=quote(query, safe="")
    )


def _strategy(profile: dict[str, Any], role: str) -> Strategy:
    """Pick the fetch strategy for one page role.

    A site can need a browser for its search page and not for its product pages,
    which is one site's real shape rather than a hypothetical: results built in
    the browser come back as an empty shell over plain HTTP while the product
    pages arrive complete. Without the per-role override such a site has to run
    every request through a browser, or return nothing at all.
    """
    if role == "search":
        override = profile["search"].get("strategy")
        if override is not None:
            return override
    strategy: Strategy = profile["strategy"]
    return strategy


def _headers(profile: dict[str, Any], role: str) -> Mapping[str, str] | None:
    """Pick the request headers for one page role, same override rule as above.

    A header can be right for most of a site and fatal on one page of it. One
    platform's variant endpoint says nothing at all unless the request looks
    like an XHR, and the very same header makes that platform's search page
    answer 404. So the search page gets its own set when it needs one, and
    replaces rather than adds to the site's, because the case for having it is
    a page that wants the opposite of what the rest of the site wants.
    """
    if role == "search":
        override = profile["search"].get("request_headers")
        if override is not None:
            headers: Mapping[str, str] = override
            return headers
    site_wide: Mapping[str, str] | None = profile.get("request_headers")
    return site_wide


async def _fetch_page(
    profile: dict[str, Any],
    url: str,
    *,
    role: str,
    fetcher: Fetcher,
    method: Literal["GET", "POST"] = "GET",
    data: Mapping[str, str] | None = None,
) -> FetchResult:
    """Fetch one page with the strategy, headers and timeout the profile asks for."""
    return await fetcher(
        url,
        _strategy(profile, role),
        method=method,
        data=data,
        headers=_headers(profile, role),
        timeout_s=int(profile.get("timeout_s", 20)),
    )


def _read_candidates(
    profile: dict[str, Any], html: str, page_url: str
) -> tuple[ProductCandidate, ...]:
    """Read the result rows off a search page.

    Every site needs selectors here, whatever layer its product pages answer on:
    no search page seen so far declares its results as structured data, so the
    listing is always read out of the rendered markup.

    Links are resolved against the page that was actually fetched rather than
    against the profile's base_url, so a search that redirected still produces
    URLs on the page it landed on.

    A row whose link selector finds nothing is dropped: there is no page to open
    and no way to read its price, so carrying it would put a hit in the results
    that cannot ever hold a number.
    """
    search = profile["search"]
    candidates: list[ProductCandidate] = []
    for node in HTMLParser(html).css(str(search["result_item"])):
        href = select_field(node, str(search["result_url"]))
        if not href:
            continue
        candidates.append(
            ProductCandidate(
                raw_title=select_field(node, str(search["result_title"])),
                url=urljoin(page_url, href),
            )
        )
    return tuple(candidates)


async def _read_variants(
    profile: dict[str, Any],
    candidate: ProductCandidate,
    hooks: SiteHooks,
    fetcher: Fetcher,
    cache: MutableMapping[CacheKey, VariantsRead] | None = None,
) -> VariantsRead:
    """Open one product page and read its sizes on the profile's layer.

    A `cache` remembers what a URL read for the rest of the scan. Two perfumes
    searched at the same shop routinely list the same product, and reading it
    twice costs a request and a rate-limit wait to learn what is already known.
    It lives no longer than the scan that owns it, so a price is never served
    from an earlier run.

    A site's `parse_variants` hook is offered the page first and may take the
    whole job. It hands back the same raw rows the four extraction layers do,
    never finished variants, so the profile's `variant_rules` still decide what
    counts as a decant and the prices are still converted in one place.

    Returning None means the hook declined this page, and the profile's own layer
    runs as usual. That is what lets a hook cover only the one product shape it
    was written for instead of having to reimplement the normal case as well.

    What the product page said comes back next to the rows, because the size
    picker that says how many sizes there should be lives in the page and not in
    whatever the layer read. It is read off the markup once and kept as the two
    answers rather than as the page, so a scan holds what it learned and not
    every document it learned it from. A GET endpoint profile normally never
    opens that page at all, so one is fetched here only when such a profile asks
    for the check by naming a `variant_control`. That is a second request per
    product on those sites, which is why it is opt-in rather than always on.
    """
    if cache is None:
        return await _read_product(profile, candidate, hooks, fetcher)
    # Keyed by site as well as URL so one dict can be shared by every site of a
    # scan. Two shops can carry the same path, and one profile's rows read
    # through another profile's rules would be nonsense.
    key = (str(profile["id"]), candidate.url)
    if key not in cache:
        cache[key] = await _read_product(profile, candidate, hooks, fetcher)
    return cache[key]


async def _read_product(
    profile: dict[str, Any],
    candidate: ProductCandidate,
    hooks: SiteHooks,
    fetcher: Fetcher,
) -> VariantsRead:
    """Do the reading _read_variants may serve from its cache instead.

    The page is read for what it says about its sizes here, once, and then let
    go. Every branch below hands back the markup it worked from, so the one
    `_page_evidence` call at the end is what every path is judged by, and no
    branch gets to answer for a page out of the reason it took that branch.
    """
    rows, root = await _read_product_rows(profile, candidate, hooks, fetcher)
    return rows, _page_evidence(profile, root)


async def _read_product_rows(
    profile: dict[str, Any],
    candidate: ProductCandidate,
    hooks: SiteHooks,
    fetcher: Fetcher,
) -> tuple[tuple[RawVariant, ...], Node | None]:
    """Read one product's size rows, next to the markup they were read off.

    The markup comes back parsed rather than as text: the POST endpoint branch
    has already had to parse it to find the size options, and handing the tree on
    is what keeps the page from being parsed a second time to answer two
    questions about it.
    """
    layer = profile["extraction"]
    page: FetchResult | None = None
    if hooks.parse_variants is not None:
        page = await _fetch_page(
            profile, candidate.url, role="product", fetcher=fetcher
        )
        rows = await hooks.parse_variants(profile, candidate, page.html)
        if rows is not None:
            return tuple(rows), _root(page.html)

    if layer == "endpoint":
        return await _read_endpoint_variants(
            profile, candidate, hooks_page=page, fetcher=fetcher
        )
    if page is None:
        page = await _fetch_page(
            profile, candidate.url, role="product", fetcher=fetcher
        )
    if layer == "jsonld":
        return extract_jsonld_variants(page.html), _root(page.html)
    if layer == "embedded_json":
        return (
            extract_embedded_variants(page.html, profile["embedded_json"]),
            _root(page.html),
        )
    if layer == "css":
        return (
            extract_css_variants(page.html, profile.get("product") or {}),
            _root(page.html),
        )
    raise ExtractionFailed(
        f"{profile['id']}: unknown extraction layer {layer!r}, "
        f"expected one of {EXTRACTION_LAYERS}"
    )


async def _read_endpoint_variants(
    profile: dict[str, Any],
    candidate: ProductCandidate,
    *,
    hooks_page: FetchResult | None,
    fetcher: Fetcher,
) -> tuple[tuple[RawVariant, ...], Node | None]:
    """Ask a platform's variant endpoint for every size.

    A GET endpoint answers everything in one request built from the profile's
    URL template, which is why that branch never opens the product page: the
    whole point of the layer is that one request answers what the page would
    need several to say. It opens it anyway, once, when the profile named a
    `variant_control`, because the picker that check counts is only there.

    A POST endpoint does not work that way: it answers one size option at a
    time, and which options exist and which product they belong to are not
    something a URL can template ahead of time, only something sitting in the
    product page's own markup. `_read_endpoint_variants_post` opens that page
    first and asks the endpoint once per option instead.
    """
    config = profile["endpoint"]
    if config.get("method") == "POST":
        return await _read_endpoint_variants_post(profile, config, candidate, fetcher)
    url = str(config["product_json"]).format(
        base_url=profile["base_url"], product_url=candidate.url
    )
    result = await _fetch_page(profile, url, role="product", fetcher=fetcher)
    rows = _parse_endpoint_document(profile["id"], url, result.html, config)
    page = hooks_page
    if page is None and profile.get("variant_control"):
        page = await _fetch_page(
            profile, candidate.url, role="product", fetcher=fetcher
        )
    return rows, _root(page.html) if page is not None else None


async def _read_endpoint_variants_post(
    profile: dict[str, Any],
    config: Mapping[str, Any],
    candidate: ProductCandidate,
    fetcher: Fetcher,
) -> tuple[tuple[RawVariant, ...], Node | None]:
    """Drive a platform's POST variant endpoint, one size option per request.

    `body` names the endpoint's static form fields and, for each, the selector
    that reads its value off the product page, such as a product id sitting on
    the add-to-cart button. `option_selector` finds every size option's own id
    on that same page; `option_body_key` is the form field one of those ids
    goes in, one request per id. A static field the page does not have aborts
    the product outright, since posting the request anyway would either be
    silently rejected by the endpoint or, worse, answered for the wrong product.

    Unless the page names no options at all, in which case there is nothing to
    post and no reason to want the fields: that is a plain full bottle, sold as
    one thing with no size list, and this shop lists plenty of them next to its
    decants. Ending the site over one of those is the same mistake the embedded
    layer already avoids, and it costs every decant the shop does sell.

    Or unless the page says it is sold out, which reaches the same nothing by the
    other road: the options are all there, the field the request needs is not,
    because it sits on an add-to-cart button the shop stopped rendering.
    """
    page = await _fetch_page(profile, candidate.url, role="product", fetcher=fetcher)
    root = HTMLParser(page.html).root
    if root is None:
        raise ExtractionFailed(
            f"{profile['id']}: {candidate.url} parsed to no markup "
            f"({len(page.html.encode())} byte body)"
        )
    option_ids = select_all(root, str(config["option_selector"]))
    if not option_ids:
        return (), root
    body: dict[str, str] = {}
    for name, selector in config["body"].items():
        value = select_field(root, str(selector))
        if value is None:
            if _page_says_sold_out(profile, root):
                # The fields live on the add-to-cart button, and a shop that has
                # run out replaces it with a "notify me" button rather than
                # leaving a dead one. So the page still lists its sizes and no
                # longer says which product to ask about, and there is nothing to
                # post: the same nothing as the full bottle above, arrived at for
                # a stock reason instead of a catalog one. Both perfumes this hit
                # in the field were out of stock, not unreadable.
                return (), root
            raise ExtractionFailed(
                f"{profile['id']}: could not read the POST field {name!r} "
                f"({selector!r}) off {candidate.url}"
            )
        body[name] = value
    option_key = str(config["option_body_key"])
    url = str(config["product_json"]).format(base_url=profile["base_url"])
    rows: list[RawVariant] = []
    for option_id in option_ids:
        result = await _fetch_page(
            profile,
            url,
            role="product",
            fetcher=fetcher,
            method="POST",
            data={**body, option_key: option_id},
        )
        rows.extend(_parse_endpoint_document(profile["id"], url, result.html, config))
    return tuple(rows), root


def _parse_endpoint_document(
    site_id: str, url: str, raw: str, config: Mapping[str, Any]
) -> tuple[RawVariant, ...]:
    """Parse one endpoint response and read its variant rows out of it."""
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ExtractionFailed(
            f"{site_id}: the variant endpoint {url} did not answer with JSON ({e})"
        ) from e
    return extract_endpoint_variants(document, config)
