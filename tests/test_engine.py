"""Tests for the profile-driven search in parfum_finder.engine.

What these defend is the claim the whole design rests on: a site is driven by its
profile and nothing else. So every case here changes only the profile dict and
expects the behavior to change with it, never a branch on which site it is.

The pages come from the local HTTP server in conftest, so the fetch, the redirect
handling and the URL resolution are all real, with no network.
"""

from dataclasses import replace
from decimal import Decimal
from typing import Any

import pytest

from parfum_finder.engine import ExtractionFailed, apply_variant_rules, search_site
from parfum_finder.extract import RawVariant


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
        "variant_rules": {
            "size_from": "variant_label",
            "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
            "exclude_keywords": ["tester", "full şişe"],
            "max_size_ml": 30,
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
    assert [v.size_ml_x10 for v in hits[0].variants] == [50, 100]
    assert [v.price_kurus for v in hits[0].variants] == [15000, 29000]
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
    assert [v.size_ml_x10 for v in hit.variants] == [50, 100]


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

    assert [v.size_ml_x10 for v in hits[0].variants] == [50, 100]
    assert [v.in_stock for v in hits[0].variants] == [True, False]


async def test_a_size_keeps_its_own_page_when_the_feed_names_one(
    server_url: str,
) -> None:
    # One platform gives every size its own product page. Those URLs have to
    # survive to the row, or opening a 10 ml result would land on the 5 ml page.
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
                "title": "name",
                "url": "url",
            },
        },
    )

    hits = await search_site(profile, "test")

    assert [v.raw_title for v in hits[0].variants] == [
        "Test Parfum 5 ml",
        "Test Parfum 10 ml",
    ]
    assert [v.product_url for v in hits[0].variants] == [
        "/urun/test-parfum-5-ml",
        "/urun/test-parfum-10-ml",
    ]


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

    assert [v.size_ml_x10 for v in hit.variants] == [50, 100]
    assert [v.price_kurus for v in hit.variants] == [15000, 29000]


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
    assert [v.price_kurus for v in hits[0].variants] == [15000, 29000]


# --- The variant rules on their own -------------------------------------------
#
# apply_variant_rules is pure, so these run without the server. Every size label
# below is one that a captured target site really emits; a tidy invented label
# ("5 ml") cannot fail the way the real ones do.

_RULES: dict[str, Any] = {
    "size_from": "variant_label",
    "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
    "exclude_keywords": ["tester", "full şişe", "orijinal şişe", "kutulu", "set"],
    "max_size_ml": 30,
}


def _row(size_raw: str | None, **overrides: Any) -> RawVariant:
    row = RawVariant(
        title="Bir Parfum",
        url="https://x.test/p/1",
        sku=None,
        size_raw=size_raw,
        price=Decimal("100"),
        in_stock=True,
    )
    return replace(row, **overrides)


def test_reads_the_size_out_of_the_labels_sites_actually_write() -> None:
    # Left to right: two spellings of the same size, a trailing space, a decimal
    # comma with a suffix after the unit, an uppercase unit, and "cc" for "ml".
    labels = ["3 ml", "3ml", "10 ml ", "2,7 ml - metal sprey", "1 ML", "5cc"]

    variants = apply_variant_rules([_row(label) for label in labels], _RULES)

    assert [v.size_ml_x10 for v in variants] == [30, 30, 100, 27, 10, 50]


def test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself() -> None:
    # One shop labels a size "30mldekant". At 30 ml the profile says bottle, and
    # what a size is depends on how much is in it, not on its own name.
    rows = [_row("10ml"), _row("30mldekant"), _row("100ml")]

    variants = apply_variant_rules(rows, _RULES)

    assert [v.size_ml_x10 for v in variants] == [100]


def test_an_uppercase_turkish_keyword_still_matches() -> None:
    # "ORİJİNAL ŞİŞE" folds to a string with a combining dot in it, so a plain
    # lower-case comparison against "orijinal şişe" finds nothing and a full
    # bottle stays in the price-per-ml ranking.
    rows = [
        _row("5 ml", title="ORİJİNAL ŞİŞE Bir Parfum"),
        _row("5 ml", title="TESTER Bir Parfum"),
        _row("5 ml", title="Bir Parfum"),
    ]

    variants = apply_variant_rules(rows, _RULES)

    assert len(variants) == 1


def test_a_keyword_in_the_size_label_excludes_the_row_too() -> None:
    # The giveaway sits in different places on different sites: one writes it in
    # the title, another in the size label.
    rows = [_row("5 ml tester"), _row("5 ml")]

    variants = apply_variant_rules(rows, _RULES)

    assert len(variants) == 1


def test_a_size_that_cannot_be_read_is_dropped() -> None:
    # No millilitres means no price per millilitre, and a row that cannot be
    # compared is worse than no row: it looks like data.
    rows = [_row("Standart"), _row(None), _row("5 ml")]

    variants = apply_variant_rules(rows, _RULES)

    assert [v.size_ml_x10 for v in variants] == [50]


def test_prices_become_whole_kurus() -> None:
    rows = [_row("5 ml", price=Decimal("1250.005")), _row("10 ml", price=None)]

    variants = apply_variant_rules(rows, _RULES)

    # Rounded half up, and integers throughout: a basket total decides whether a
    # free shipping threshold is met, and that comparison has to be exact.
    assert variants[0].price_kurus == 125001
    # A sold-out size often shows no price. Kept, so the stock column can say so
    # instead of the size disappearing from the table.
    assert variants[1].price_kurus is None
    assert variants[1].size_ml_x10 == 100


def test_size_from_title_reads_the_product_name() -> None:
    # One shop gives every size its own product page, so the size is in the title
    # and there is no separate label to read.
    rules = {**_RULES, "size_from": "title"}
    rows = [_row(None, title="Amouage Blossom Love 3 ml")]

    (variant,) = apply_variant_rules(rows, rules)

    assert variant.size_ml_x10 == 30


def test_size_from_field_still_needs_a_number() -> None:
    # "field" trusts the feed to hand over a size. When it hands over a word
    # instead, that trust is the thing that is wrong, so the row goes.
    rules = {**_RULES, "size_from": "field"}

    assert apply_variant_rules([_row("Standart")], rules) == ()


def test_size_from_field_skips_the_pattern() -> None:
    # A feed that already hands over a bare number needs no pattern, and running
    # one that expects a unit over "5" would find nothing.
    rules = {**_RULES, "size_from": "field"}

    (variant,) = apply_variant_rules([_row("5")], rules)

    assert variant.size_ml_x10 == 50
