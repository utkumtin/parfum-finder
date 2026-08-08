"""Tests for the profile-driven search in parfum_finder.engine.

What these defend is the claim the whole design rests on: a site is driven by its
profile and nothing else. So every case here changes only the profile dict and
expects the behavior to change with it, never a branch on which site it is.

The pages come from the local HTTP server in conftest, so the fetch, the redirect
handling and the URL resolution are all real, with no network.
"""

from decimal import Decimal
from typing import Any

import pytest

from parfum_finder.engine import ExtractionFailed, search_site


def _profile(server_url: str, **overrides: Any) -> dict[str, Any]:
    """A minimal working profile, with the fields a case cares about swapped in."""
    profile: dict[str, Any] = {
        "id": "testsite",
        "base_url": server_url,
        "strategy": "httpx",
        "extraction": "embedded_json",
        "timeout_s": 10,
        "search": {
            "url_template": "{base_url}/engine-search?q={query}",
            "result_item": ".card",
            "result_url": "a::attr(href)",
            "result_title": "a::text",
        },
        "embedded_json": {
            "source": "attribute",
            "selector": "[data-product_variations]",
            "attribute": "data-product_variations",
            "field_map": {
                "size_raw": "attributes.attribute_pa_hacim",
                "price": "display_price",
                "in_stock": "is_in_stock",
            },
        },
    }
    profile.update(overrides)
    return profile


async def test_drives_a_site_from_search_page_to_variant_prices(
    server_url: str,
) -> None:
    hits = await search_site(_profile(server_url), "test parfum")

    # Two rows, not three: the row with no link is dropped, because there is no
    # page behind it to read a price from.
    assert len(hits) == 2
    assert [h.candidate.raw_title for h in hits] == [
        "Test Parfum Dekant",
        "Test Parfum EDP Dekant",
    ]
    assert [v.size_raw for v in hits[0].variants] == ["5ml", "10ml"]
    assert [v.price for v in hits[0].variants] == [Decimal("150"), Decimal("290")]
    assert [v.in_stock for v in hits[0].variants] == [True, False]


async def test_query_is_escaped_for_a_query_string_template(
    server_url: str,
) -> None:
    # A multi-word perfume name sent raw would either break the URL or search for
    # the first word alone, and the second failure never looks like a failure.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-echo?q={query}"

    (hit,) = await search_site(profile, "creed aventus edp")

    assert hit.candidate.raw_title == "/engine-echo?q=creed%20aventus%20edp"


async def test_query_is_escaped_for_a_path_segment_template(
    server_url: str,
) -> None:
    # One platform spells search as a path, not a parameter. The same escaping has
    # to be right there too, so the two template shapes cannot need two behaviors.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-echo/{query}"

    (hit,) = await search_site(profile, "creed aventus edp")

    assert hit.candidate.raw_title == "/engine-echo/creed%20aventus%20edp"


async def test_relative_links_resolve_against_the_page_that_answered(
    server_url: str,
) -> None:
    # The search redirects into /shop/, and the first row's link is relative. Read
    # against base_url it would point at /engine-product; only resolving against
    # the URL the fetch actually landed on gives /shop/engine-product.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-redirect-search?q={query}"

    hits = await search_site(profile, "test")

    assert hits[0].candidate.url == f"{server_url}/shop/engine-product"
    assert len(hits[0].variants) == 2


async def test_a_site_with_no_stock_of_the_perfume_is_not_an_error(
    server_url: str,
) -> None:
    # No results is a real answer: the shop may simply not carry it. Only a page
    # opened as a product and offering nothing is suspect.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-empty?q={query}"

    assert await search_site(profile, "yok boyle bir parfum") == ()


async def test_a_product_page_that_yields_no_sizes_fails_loudly(
    server_url: str,
) -> None:
    # The silent-empty failure this project treats as a first-class bug: a page
    # that still loads while its blob is gone would otherwise read as "not sold
    # here", and the site would drop out of the comparison unnoticed.
    profile = _profile(server_url)
    profile["embedded_json"]["selector"] = "[data-product_variations_v2]"

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test")

    assert "embedded_json" in str(excinfo.value)
    assert "testsite" in str(excinfo.value)


async def test_a_full_bottle_next_to_a_decant_does_not_sink_the_site(
    server_url: str,
) -> None:
    # A mixed catalog: one shop's listings are mostly plain full bottles, which
    # have no size table at all, sitting next to the few products that do. If one
    # of those ended the run, that shop would contribute nothing.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-mixed?q={query}"

    (hit,) = await search_site(profile, "test parfum")

    assert hit.candidate.raw_title == "Test Parfum Dekant"
    assert [v.size_raw for v in hit.variants] == ["5ml", "10ml"]


async def test_the_named_layer_is_the_only_one_tried(server_url: str) -> None:
    # The product page carries a working embedded blob, but this profile says its
    # layer is jsonld. Falling through to the blob would hide the fact that the
    # profile no longer describes the site, which is the whole reason a profile
    # records one layer instead of a preference order.
    profile = _profile(server_url, extraction="jsonld")

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test")

    assert "'jsonld'" in str(excinfo.value)


async def test_endpoint_layer_asks_the_variant_url_instead_of_the_page(
    server_url: str,
) -> None:
    profile = _profile(
        server_url,
        extraction="endpoint",
        endpoint={
            "product_json": "{product_url}.js",
            "variants_path": "variants",
            "field_map": {
                "size_raw": "title",
                "price": "price",
                "in_stock": "available",
            },
        },
    )

    hits = await search_site(profile, "test")

    assert [v.size_raw for v in hits[0].variants] == ["5 ml", "10 ml"]
    assert [v.in_stock for v in hits[0].variants] == [True, False]


async def test_an_endpoint_that_answers_html_fails_loudly(server_url: str) -> None:
    # A shop that removed its variant endpoint usually serves its 404 page rather
    # than a JSON error, so this arrives as markup where JSON was expected.
    profile = _profile(
        server_url,
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/engine-product-bare",
            "variants_path": "variants",
            "field_map": {
                "size_raw": "title",
                "price": "price",
                "in_stock": "available",
            },
        },
    )

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test")

    assert "did not answer with JSON" in str(excinfo.value)


async def test_css_layer_reads_sizes_out_of_the_rendered_markup(
    server_url: str,
) -> None:
    profile = _profile(server_url, extraction="css")
    profile["search"]["url_template"] = "{base_url}/engine-search-css?q={query}"
    profile["product"] = {
        "variant_container": ".size-row",
        "size_raw": ".ml::text",
        "price": ".tl::text",
        "sku": "::attr(data-sku)",
    }

    (hit,) = await search_site(profile, "test")

    assert [v.size_raw for v in hit.variants] == ["5 ml", "10 ml"]
    assert [v.price for v in hit.variants] == [Decimal("150.00"), Decimal("290.00")]
    assert [v.sku for v in hit.variants] == ["V5", "V10"]


async def test_rows_without_a_single_price_fail_loudly(server_url: str) -> None:
    # Sizes still listed, prices gone: a redesign renamed the price class. Left
    # alone this site would report every size at "no price" and quietly vanish
    # from a cheapest-first comparison instead of being flagged.
    profile = _profile(server_url, extraction="css")
    profile["search"]["url_template"] = "{base_url}/engine-search-css?q={query}"
    profile["product"] = {
        "variant_container": ".size-row",
        "size_raw": ".ml::text",
        "price": ".fiyat::text",
    }

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test")

    assert "no priced size" in str(excinfo.value)


async def test_an_unknown_extraction_layer_is_refused(server_url: str) -> None:
    # A typo in a hand-edited profile. Treating it as "nothing found" would make
    # a one-character mistake look like a shop that stopped stocking anything.
    profile = _profile(server_url, extraction="jsonld_v2")

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test")

    assert "unknown extraction layer" in str(excinfo.value)


async def test_the_search_page_can_use_its_own_fetch_strategy(
    server_url: str,
) -> None:
    # One site builds its results in the browser while its product pages arrive
    # complete over plain HTTP. Without a per-page strategy that site either
    # returns nothing or runs every request through a browser.
    profile = _profile(server_url)
    profile["search"]["strategy"] = "curl_cffi"

    hits = await search_site(profile, "test")

    assert len(hits) == 2
    assert [v.price for v in hits[0].variants] == [Decimal("150"), Decimal("290")]
