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
and the multi-site run loop, wrapping search_site in a per-site semaphore, the
profile's rate_limit_ms delay and retries. Until that lands search_site fires its
requests back to back with no pause between them, so it should not be pointed at
a live shop: the targets are small businesses, not infrastructure.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
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
from parfum_finder.normalize import parse_size_ml


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


async def search_site(profile: dict[str, Any], query: str) -> tuple[SearchHit, ...]:
    """Run one query against one site and read every hit's sizes.

    Everything site-specific comes from `profile`: the search URL shape, which
    fetch strategy each page needs, the selectors that pick result rows out of
    the listing, and which extraction layer the product pages answer on.

    Each hit's sizes come back already read in millilitres and filtered down to
    the decants, per the profile's variant rules. Pairing a hit with the perfume
    that was actually asked for still needs the matcher, which reads these rows
    rather than being folded in here.

    A hit that ends up with no decant sizes is dropped, not fatal. Search results
    mix decants with plain full bottles, and one shop's catalog is known to be
    roughly four fifths of the latter: a full bottle has no size table worth
    reading, and letting one of those end the site would throw away the decants
    listed next to it.

    Raises ExtractionFailed only when the search returned hits and the extraction
    layer read not one price from any of them, measured before the decant filter
    runs. An empty result list is not an error, because a shop may genuinely not
    stock the perfume, and neither is a page of nothing but full bottles. But a
    page full of results where every product page reads as empty is a broken
    profile until proven otherwise: that is the difference between "not sold
    here" and "we stopped being able to see it", which is what a silent empty
    result destroys.
    """
    result = await _fetch_page(profile, _search_url(profile, query), role="search")
    candidates = _read_candidates(profile, result.html, result.url)

    rules = profile["variant_rules"]
    hits: list[SearchHit] = []
    extracted_a_price = False
    for candidate in candidates:
        rows = await _read_variants(profile, candidate)
        rows = tuple(_with_candidate_identity(row, candidate) for row in rows)
        extracted_a_price |= any(row.price is not None for row in rows)
        variants = apply_variant_rules(rows, rules)
        if variants:
            hits.append(SearchHit(candidate=candidate, variants=variants))
    if candidates and not extracted_a_price:
        raise ExtractionFailed(
            f"{profile['id']}: the {profile['extraction']!r} layer read no priced "
            f"size from any of the {len(candidates)} search results, starting with "
            f"{candidates[0].url}"
        )
    return tuple(hits)


def _with_candidate_identity(
    row: RawVariant, candidate: ProductCandidate
) -> RawVariant:
    """Give a size the listing's title and URL when the page gave it none.

    A site that lists every size as its own product names each one; a site with
    one page per product and a size table names none of them, and every size
    there really does share the page's title and URL. Leaving those empty would
    show blank rows in the results table and give the browse-this-one key nothing
    to open.
    """
    if row.title is not None and row.url is not None:
        return row
    return replace(
        row,
        title=row.title if row.title is not None else candidate.raw_title,
        url=row.url if row.url is not None else candidate.url,
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
    """
    variants: list[Variant] = []
    for row in rows:
        size_ml = _read_size_ml(row, rules)
        if size_ml is None or size_ml <= 0:
            continue
        if _is_excluded(row, rules, size_ml):
            continue
        variants.append(
            Variant(
                size_ml_x10=int((size_ml * 10).quantize(Decimal(1), ROUND_HALF_UP)),
                raw_title=row.title,
                product_url=row.url,
                price_kurus=_to_kurus(row.price),
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
    haystack = _fold(" ".join(part for part in (row.title, row.size_raw) if part))
    return any(_fold(str(keyword)) in haystack for keyword in rules["exclude_keywords"])


def _fold(text: str) -> str:
    """Lower-case text for comparison, without breaking Turkish "İ".

    Python folds "İ" to "i" plus a separate combining dot, so "ORİJİNAL ŞİŞE"
    comes out as "ori̇jinal şi̇şe" and a keyword written "orijinal şişe" does not
    appear in it. The keyword would silently never match, and a full bottle would
    stay in a decant comparison. Mapping that one letter first is what makes the
    two strings comparable.
    """
    return text.replace("İ", "i").casefold()


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
