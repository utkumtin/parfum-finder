"""Proof that M4's own criterion holds: every real site profile drives the
generic engine, with no site-specific Python class.

Each case here loads `sites/<id>.json` exactly the way the project loads it in
production: `load_site_profile` runs schema validation and the platform-template
merge. It is then driven through `search_site` with its `fetcher` set to a router
that serves that site's own `fixtures/<id>/` capture instead of the network.
Nothing served is invented: the search page is a trimmed excerpt of the real
search.html, cut out with the profile's own selectors, containing only the
one real card that led to the product.html actually captured for that site; the
İdeasoft sites' POST endpoint serves the one real `/product/related-options`
response that was captured live for this milestone, and an empty options list
(the endpoint's own real answer for an id it does not recognize, also observed
live) for every other size option the product page names.

If a profile's selectors stop matching the real markup they were written
against, or the extraction layer stops reading real prices out of it, this
fails the same way the profile would in production.
"""

import json
from pathlib import Path
from urllib.parse import urlparse

import pytest
from selectolax.parser import HTMLParser

from parfum_finder.engine import search_site
from parfum_finder.extract import select_field
from parfum_finder.fetch import (
    Fetcher,
    FetchResult,
    FormData,
    Headers,
    Method,
    Strategy,
)
from parfum_finder.profiles import load_site_profile

_ROOT = Path(__file__).resolve().parent.parent
_SITES_DIR = _ROOT / "sites"
_FIXTURES_DIR = _ROOT / "fixtures"


def _meta(site_id: str) -> dict:
    return json.loads((_FIXTURES_DIR / site_id / "meta.json").read_text())


def _path(url: str) -> str:
    return urlparse(url).path.rstrip("/")


def _single_result_search_html(site_id: str, profile: dict) -> str:
    """The one real search-result card that led to this site's captured product.

    Cut out of the real search.html with the profile's own `search` selectors,
    not hand-copied: a selector that no longer matches the real markup fails
    here exactly as it would in production, instead of a synthetic stand-in
    quietly hiding the drift.
    """
    product_url = _meta(site_id)["pages"]["product"]["url"]
    tree = HTMLParser((_FIXTURES_DIR / site_id / "search.html").read_text())
    search = profile["search"]
    for node in tree.css(str(search["result_item"])):
        href = select_field(node, str(search["result_url"]))
        if href and _path(href) == _path(product_url):
            return f"<html><body>{node.html}</body></html>"
    raise AssertionError(
        f"{site_id}: no card in the real search.html links to {product_url}"
    )


def _fake_fetch(
    site_id: str,
    profile: dict,
    *,
    calls: list[tuple[str, str, str]] | None = None,
) -> Fetcher:
    """Route every fetch call a site's search_site() run makes to real bytes.

    Only two kinds of request happen for a single-candidate run: GETs (the
    search page, then the one candidate's product page) and, for a POST
    endpoint, one POST per size option found on that product page.

    `calls`, when given, records (method, strategy, url) for every request in
    order, so a case that cares which strategy a role actually used (the
    per-page override decantall's search page needs) can inspect it.
    """
    product_url = _meta(site_id)["pages"]["product"]["url"]
    product_html = (_FIXTURES_DIR / site_id / "product.html").read_text()
    search_html = _single_result_search_html(site_id, profile)

    related_options_path = _FIXTURES_DIR / site_id / "related-options.json"
    captured_option = None
    if related_options_path.exists():
        captured_option = str(
            _meta(site_id)["pages"]["related_options"]["body"]["selected_options[]"]
        )
    empty_options = json.dumps({"success": True, "data": {"options": []}})

    async def fake_fetch(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        if calls is not None:
            calls.append((method, strategy, url))
        if method == "POST":
            assert data is not None
            option = str(data[str(profile["endpoint"]["option_body_key"])])
            body = (
                related_options_path.read_text()
                if option == captured_option
                else empty_options
            )
            return FetchResult(url=url, status_code=200, html=body, strategy=strategy)
        if _path(url) == _path(product_url):
            return FetchResult(
                url=url, status_code=200, html=product_html, strategy=strategy
            )
        return FetchResult(
            url=url, status_code=200, html=search_html, strategy=strategy
        )

    return fake_fetch


@pytest.mark.parametrize(
    "site_id",
    [
        "venco",
        "decantall",
        "luxurydekant",
        "ruxangroup",
        "dekantparfum",
        "dekantdoktoru",
        "splitcim",
    ],
)
async def test_every_target_site_is_driven_from_its_real_profile(site_id: str) -> None:
    profile = load_site_profile(_SITES_DIR / f"{site_id}.json")
    fetcher = _fake_fetch(site_id, profile)

    hits = await search_site(profile, "test", fetcher=fetcher)

    assert hits, f"{site_id}: the real profile produced no hits"
    variants = hits[0].variants
    assert variants, f"{site_id}: the real product page yielded no decant sizes"
    assert all(v.size_ml_x10 > 0 for v in variants)
    assert any(v.price_kurus is not None and v.price_kurus > 0 for v in variants)


async def test_venco_reads_its_three_real_decant_prices() -> None:
    # The site's own JSON blob, cross-checked against docs/discovery-report.md:
    # 2 ML = 425,00 TL, 3 ML = 600,00 TL, 5 ML = 1.000,00 TL. The other two
    # sizes it lists (1 ML, 10 ML) are out of stock and the site prints
    # "0,00 TL" for every price field on both, which apply_variant_rules reads
    # as no price (None), not a free perfume that would sort as the cheapest.
    profile = load_site_profile(_SITES_DIR / "venco.json")
    fetcher = _fake_fetch("venco", profile)

    (hit,) = await search_site(profile, "test", fetcher=fetcher)

    by_size = {v.size_ml_x10: v.price_kurus for v in hit.variants}
    assert by_size[20] == 42500
    assert by_size[30] == 60000
    assert by_size[50] == 100000
    assert by_size[10] is None
    assert by_size[100] is None


async def test_decantall_reads_its_four_real_decant_prices() -> None:
    # The ikas __NEXT_DATA__ blob, cross-checked against docs/discovery-report.md:
    # 3/5/10/15 ml at 360/600/1200/1800 TL, all under the 30 ml cutoff so all
    # four survive variant_rules.
    profile = load_site_profile(_SITES_DIR / "decantall.json")
    fetcher = _fake_fetch("decantall", profile)

    (hit,) = await search_site(profile, "test", fetcher=fetcher)

    by_size = {v.size_ml_x10: v.price_kurus for v in hit.variants}
    assert by_size == {30: 36000, 50: 60000, 100: 120000, 150: 180000}


async def test_decantall_search_page_uses_the_playwright_override() -> None:
    # This site's own quirk, per docs/discovery-report.md open question #1: the
    # search page is rendered in the browser while the product page is plain
    # httpx. search.strategy is what the profile uses to say so; this checks
    # the override actually reaches fetch() instead of just sitting unread in
    # the profile.
    profile = load_site_profile(_SITES_DIR / "decantall.json")
    calls: list[tuple[str, str, str]] = []
    fetcher = _fake_fetch("decantall", profile, calls=calls)

    await search_site(profile, "test", fetcher=fetcher)

    product_path = _path(_meta("decantall")["pages"]["product"]["url"])
    search_calls = [c for c in calls if _path(c[2]) != product_path]
    product_calls = [c for c in calls if _path(c[2]) == product_path]
    assert search_calls and product_calls  # sanity: both roles actually ran
    assert all(strategy == "playwright" for _, strategy, _ in search_calls)
    assert all(strategy == "httpx" for _, strategy, _ in product_calls)


async def test_luxurydekant_reads_its_real_decant_prices_and_drops_the_30ml_row() -> (
    None
):
    # The WooCommerce data-product_variations blob, cross-checked against
    # docs/discovery-report.md: 3/5/10/30 ml at 180/270/530/1570 TL. The 30 ml
    # row is exactly what ARCHITECTURE.md's size_ml >= 30 rule exists to catch,
    # so it must not appear here even though the report never calls it a bottle.
    profile = load_site_profile(_SITES_DIR / "luxurydekant.json")
    fetcher = _fake_fetch("luxurydekant", profile)

    (hit,) = await search_site(profile, "test", fetcher=fetcher)

    by_size = {v.size_ml_x10: v.price_kurus for v in hit.variants}
    assert by_size == {30: 18000, 50: 27000, 100: 53000}


async def test_ruxangroup_drops_the_full_bottle_next_to_the_decants() -> None:
    # The one product page fixture carries this shop's mixed-catalog shape in
    # miniature: 5 ml, 10 ml and 30mldekant sit in the same variant table as a
    # 100 ml full bottle. ARCHITECTURE.md's size_ml >= 30 rule has to drop both
    # the bottle and the 30 ml row, leaving only the two real decants.
    profile = load_site_profile(_SITES_DIR / "ruxangroup.json")
    fetcher = _fake_fetch("ruxangroup", profile)

    (hit,) = await search_site(profile, "test", fetcher=fetcher)

    assert sorted(v.size_ml_x10 for v in hit.variants) == [50, 100]


async def test_dekantparfum_drives_the_post_endpoint_for_a_real_price() -> None:
    # The one option this milestone actually captured live: Baccarat Rouge 540,
    # 3 ml, 540,00 TL. Every other size option the product page names gets the
    # endpoint's own real answer for an id it was not asked about (an empty
    # options list), so this also proves the N-requests-per-product loop
    # completes instead of raising on the options nobody captured a price for.
    profile = load_site_profile(_SITES_DIR / "dekantparfum.json")
    fetcher = _fake_fetch("dekantparfum", profile)

    (hit,) = await search_site(profile, "test", fetcher=fetcher)

    assert [v.size_ml_x10 for v in hit.variants] == [30]
    assert [v.price_kurus for v in hit.variants] == [54000]


async def test_dekantdoktoru_drives_the_post_endpoint_for_a_real_price() -> None:
    # The second ideasoft site, captured the same way: Amouage Blossom Love,
    # 3 ml, 540,00 TL. Same group id and option catalog shape as dekantparfum,
    # different site, proving the platform template rather than one profile.
    profile = load_site_profile(_SITES_DIR / "dekantdoktoru.json")
    fetcher = _fake_fetch("dekantdoktoru", profile)

    (hit,) = await search_site(profile, "test", fetcher=fetcher)

    assert [v.size_ml_x10 for v in hit.variants] == [30]
    assert [v.price_kurus for v in hit.variants] == [54000]
