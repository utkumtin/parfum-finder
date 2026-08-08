"""Async orchestration: parallel across sites, serial within a site, fault-isolated.

Built on asyncio.TaskGroup. Each site gets its own semaphore, a delay between
requests, and retries with backoff. If one site fails, the others keep going.

Results are never silently empty. If a site looks broken, for example zero results
on a page that clearly has products, a price that won't parse, or a variant selector
that only yielded one price, it gets marked "suspect" instead of "no matches."
Suspect results are excluded from basket totals as unknown, not treated as simply
expensive.

`search_site` is the single-site half of that: it drives one site end to end from
its profile alone, with no site-specific Python anywhere. Run a query, read the
result list, open each hit, and read its sizes with whichever extraction layer the
profile names.

That layer is used and no other. Falling through to a lower rung at runtime would
paper over exactly the profile rot this project treats as a first-class failure: a
site whose top layer quietly stopped answering would keep returning plausible rows
from a weaker layer, and nobody would learn the profile needs rewriting. Trying the
rungs in order is discovery's job, and reporting that a lower rung could take over
is `validate`'s.

TODO: define a SiteResult type here (site_id, status, variants, error/diagnostic)
and the multi-site run loop. Blocked on the concrete shape of the Variant type,
which needs the profile's variant rules (ml parsing, the non-decant filter) that
`search_site` deliberately does not apply yet.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urljoin

from selectolax.parser import HTMLParser

from parfum_finder.extract import (
    RawVariant,
    extract_css_variants,
    extract_embedded_variants,
    extract_endpoint_variants,
    extract_jsonld_variants,
    select_field,
)
from parfum_finder.fetch import FetchResult, Strategy, fetch


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
class ProductCandidate:
    """One hit on a search results page, before its product page is opened.

    `raw_title` is the listing's own wording, kept verbatim: it is what makes a
    wrong match visible to a person reading the results table, so nothing here
    tidies it up.
    """

    raw_title: str | None
    url: str


@dataclass(frozen=True)
class SearchHit:
    """A candidate together with the sizes its product page turned out to offer."""

    candidate: ProductCandidate
    variants: tuple[RawVariant, ...]


async def search_site(profile: dict[str, Any], query: str) -> tuple[SearchHit, ...]:
    """Run one query against one site and read every hit's sizes.

    Everything site-specific comes from `profile`: the search URL shape, which
    fetch strategy each page needs, the selectors that pick result rows out of
    the listing, and which extraction layer the product pages answer on.

    The rows come back raw. Turning "30mldekant" into millilitres and dropping the
    testers and full bottles needs the profile's variant rules, and pairing a hit
    with the perfume that was actually asked for needs the matcher; both read
    these rows rather than being folded in here.

    A single hit that yields no priced size is dropped, not fatal. Search results
    mix decant listings with plain full bottles, and one shop's catalog is known
    to be roughly four fifths of the latter: a full bottle has no size table to
    read, and letting one of those end the site would throw away the decants
    listed next to it.

    Raises ExtractionFailed only when the search returned hits and not one of them
    gave up a price. An empty result list is not an error, because a shop may
    genuinely not stock the perfume, but a page full of results where every single
    product page reads as empty is a broken profile until proven otherwise. That
    is the difference between "not sold here" and "we stopped being able to see
    it", which is the distinction a silent empty result destroys.
    """
    result = await _fetch_page(profile, _search_url(profile, query), role="search")
    candidates = _read_candidates(profile, result.html, result.url)

    hits: list[SearchHit] = []
    for candidate in candidates:
        variants = await _read_variants(profile, candidate)
        if any(variant.price is not None for variant in variants):
            hits.append(SearchHit(candidate=candidate, variants=variants))
    if candidates and not hits:
        raise ExtractionFailed(
            f"{profile['id']}: the {profile['extraction']!r} layer read no priced "
            f"size from any of the {len(candidates)} search results, starting with "
            f"{candidates[0].url}"
        )
    return tuple(hits)


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


async def _fetch_page(profile: dict[str, Any], url: str, *, role: str) -> FetchResult:
    """Fetch one page with the strategy and timeout the profile asks for."""
    return await fetch(
        url,
        _strategy(profile, role),
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
    profile: dict[str, Any], candidate: ProductCandidate
) -> tuple[RawVariant, ...]:
    """Open one product page and read its sizes on the profile's layer."""
    layer = profile["extraction"]
    if layer == "endpoint":
        return await _read_endpoint_variants(profile, candidate)

    result = await _fetch_page(profile, candidate.url, role="product")
    if layer == "jsonld":
        return extract_jsonld_variants(result.html)
    if layer == "embedded_json":
        return extract_embedded_variants(result.html, profile["embedded_json"])
    if layer == "css":
        return extract_css_variants(result.html, profile.get("product") or {})
    raise ExtractionFailed(f"{profile['id']}: unknown extraction layer {layer!r}")


async def _read_endpoint_variants(
    profile: dict[str, Any], candidate: ProductCandidate
) -> tuple[RawVariant, ...]:
    """Ask a platform's variant endpoint for every size in one request.

    The endpoint URL is built from the profile's template, which is why this rung
    never opens the product page itself: the whole point of the layer is that one
    request answers what the page would need several to say.

    Only endpoints reachable by a plain GET work here. One platform in use needs a
    POST whose body is assembled from ids sitting in the product page's markup,
    and fetch.py issues GETs only, so a profile for it cannot be written yet.
    """
    config = profile["endpoint"]
    url = str(config["product_json"]).format(
        base_url=profile["base_url"], product_url=candidate.url
    )
    result = await _fetch_page(profile, url, role="product")
    try:
        document = json.loads(result.html)
    except json.JSONDecodeError as e:
        raise ExtractionFailed(
            f"{profile['id']}: the variant endpoint {url} did not answer with "
            f"JSON ({e})"
        ) from e
    return extract_endpoint_variants(document, config)
