"""Tests for the profile-driven search in parfum_finder.engine.

What these defend is the claim the whole design rests on: a site is driven by its
profile and nothing else. So every case here changes only the profile dict and
expects the behavior to change with it, never a branch on which site it is.

The pages come from the local HTTP server in conftest, so the fetch, the redirect
handling and the URL resolution are all real, with no network.
"""

import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from selectolax.parser import HTMLParser

from parfum_finder import engine
from parfum_finder.engine import (
    ExtractionFailed,
    apply_variant_rules,
    run_site,
    run_sites,
    search_site,
)
from parfum_finder.extract import RawVariant
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
from parfum_finder.matcher import parse_query, title_could_match
from parfum_finder.probe import _PRODUCT_MARKUP_SELECTOR


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


async def test_a_post_endpoint_asks_once_per_size_option_off_the_page(
    server_url: str,
) -> None:
    # The one platform this project has met whose variant endpoint is a POST
    # answers one size at a time, and which sizes exist only sits in the
    # product page's own markup: a product id on the add-to-cart button, a
    # group id on the option list, and one id per size option.
    profile = _profile(
        server_url,
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/engine-related-options",
            "method": "POST",
            "body": {
                "parent_product_id": (
                    'a.add-to-cart-button[data-context="detail"]::attr(data-product-id)'
                ),
                "selected_option_group_id": (
                    "div.variant-list-group::attr(data-group-id)"
                ),
            },
            "option_selector": "span.variant-text::attr(data-option-id)",
            "option_body_key": "selected_options[]",
            "variants_path": "data.options",
            "field_map": {
                "size_raw": "option_title",
                "price": "product_price.sale_price",
                "in_stock": "product_stock_amount",
                "title": "product_name",
                "url": "product_url",
                "sku": "product_sku",
            },
        },
    )
    profile["search"]["url_template"] = (
        "{base_url}/engine-search-post-endpoint?q={query}"
    )

    hits = await search_site(profile, "test")

    assert [v.size_ml_x10 for v in hits[0].variants] == [50, 100]
    assert [v.price_kurus for v in hits[0].variants] == [15000, 29000]
    # product_price.price also sits in the response, at 125.0 for the 5 ml row;
    # picking it instead of sale_price would put 12500 here, not 15000.
    assert [v.in_stock for v in hits[0].variants] == [True, False]


async def test_a_post_endpoint_missing_a_static_body_field_fails_loudly(
    server_url: str,
) -> None:
    # A selector for the parent product id that matches nothing on the page is
    # a broken profile, not an empty answer. Posting the request anyway would
    # either be rejected by the endpoint or, worse, answered for some other
    # product, and both look like success from here unless this is caught.
    profile = _profile(
        server_url,
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/engine-related-options",
            "method": "POST",
            "body": {"parent_product_id": "a.does-not-exist::attr(data-product-id)"},
            "option_selector": "span.variant-text::attr(data-option-id)",
            "option_body_key": "selected_options[]",
            "variants_path": "data.options",
            "field_map": {
                "size_raw": "option_title",
                "price": "product_price.sale_price",
                "in_stock": "product_stock_amount",
            },
        },
    )
    profile["search"]["url_template"] = (
        "{base_url}/engine-search-post-endpoint?q={query}"
    )

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test")

    assert "parent_product_id" in str(excinfo.value)


# The ideasoft-shaped POST endpoint of the two tests above, as a value, because
# the sold-out cases below differ from the working one only in which page they
# are pointed at.
_POST_ENDPOINT: dict[str, Any] = {
    "product_json": "{base_url}/engine-related-options",
    "method": "POST",
    "body": {
        "parent_product_id": (
            'a.add-to-cart-button[data-context="detail"]::attr(data-product-id)'
        ),
        "selected_option_group_id": "div.variant-list-group::attr(data-group-id)",
    },
    "option_selector": "span.variant-text::attr(data-option-id)",
    "option_body_key": "selected_options[]",
    "variants_path": "data.options",
    "field_map": {
        "size_raw": "option_title",
        "price": "product_price.sale_price",
        "in_stock": "product_stock_amount",
    },
}


async def test_a_sold_out_page_is_not_a_broken_post_endpoint(server_url: str) -> None:
    # The shop ran out, so the add-to-cart button carrying the product id is gone
    # and replaced by a "notify me" one, while the sizes stay listed. That is a
    # stock fact about one perfume: the profile still describes the site, and
    # both live perfumes this hit were out of stock rather than unreadable.
    profile = _profile(
        server_url,
        extraction="endpoint",
        endpoint=_POST_ENDPOINT,
        out_of_stock='[data-selector="stock-warning"]',
    )
    profile["search"]["url_template"] = (
        "{base_url}/engine-search-post-endpoint-sold-out?q={query}"
    )

    result = await run_site(profile, "test parfum")

    assert result.status == "empty"
    assert result.hits == ()


async def test_a_sold_out_page_the_profile_cannot_recognize_still_fails(
    server_url: str,
) -> None:
    # The same page under a profile that names no out-of-stock marker. Without
    # one there is nothing to tell a shop that ran out from a shop that moved its
    # add-to-cart button, and the loud failure is the right answer to both.
    profile = _profile(server_url, extraction="endpoint", endpoint=_POST_ENDPOINT)
    profile["search"]["url_template"] = (
        "{base_url}/engine-search-post-endpoint-sold-out?q={query}"
    )

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(profile, "test parfum")

    assert "parent_product_id" in str(excinfo.value)


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

    # Naming the layers that are actually accepted is what turns this into a
    # message someone can act on instead of just a confirmation something broke.
    message = str(excinfo.value)
    assert "unknown extraction layer" in message
    assert "jsonld" in message
    assert "endpoint" in message
    assert "embedded_json" in message
    assert "css" in message


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


def test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume() -> None:
    # One captured site prints "0,00 TL" in every price field of a size that is
    # out of stock rather than leaving the field empty. Nothing in this catalog
    # is actually free, so 0 kuruş has to collapse to the same None a missing
    # field already gets, or the row would look like the cheapest thing on the
    # page, and later the cheapest thing a basket optimizer could pick.
    rows = [_row("5 ml", price=Decimal("0"), in_stock=False)]

    (variant,) = apply_variant_rules(rows, _RULES)

    assert variant.price_kurus is None


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


def _write_hook(hooks_dir: Path, source: str) -> None:
    """Give the test profile's site id a hook file. The id is what binds them."""
    (hooks_dir / "testsite.py").write_text(source)


async def test_before_search_rewrites_the_query_that_is_actually_sent(
    server_url: str, tmp_path: Path
) -> None:
    # The escape hatch for a site whose search box wants something other than the
    # perfume name as typed. The echo page reports the URL it was asked for, so
    # this reads what really went out rather than what the hook returned.
    _write_hook(
        tmp_path,
        "def before_search(profile, query):\n    return query.replace(' ', '+')\n",
    )
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-echo?q={query}"

    (hit,) = await search_site(profile, "creed aventus", hooks_dir=tmp_path)

    assert hit.candidate.raw_title == "/engine-echo?q=creed%2Baventus"


async def test_after_search_can_drop_a_result_the_selectors_could_not(
    server_url: str, tmp_path: Path
) -> None:
    # Some listings mix in rows no selector separates, for instance a promoted
    # product. Without the hook the site would need a selector it does not have.
    _write_hook(
        tmp_path,
        "def after_search(profile, candidates, html):\n"
        "    return [c for c in candidates if 'EDP' not in (c.raw_title or '')]\n",
    )

    hits = await search_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)

    assert [h.candidate.raw_title for h in hits] == ["Test Parfum Dekant"]


async def test_parse_variants_takes_over_but_the_profile_still_filters(
    server_url: str, tmp_path: Path
) -> None:
    # The point of handing back raw rows instead of finished variants: the hook
    # only reads the page, while max_size_ml, the keyword list and the conversion
    # to kuruş stay in one place and stay the profile's.
    _write_hook(
        tmp_path,
        "from decimal import Decimal\n"
        "\n"
        "from parfum_finder.extract import RawVariant\n"
        "\n"
        "\n"
        "async def parse_variants(profile, candidate, html):\n"
        "    return (\n"
        "        RawVariant('El Yazimi', candidate.url, None, '5 ml', "
        "Decimal('120.50'), True),\n"
        "        RawVariant('Full Şişe', candidate.url, None, '100 ml', "
        "Decimal('4000'), True),\n"
        "    )\n",
    )

    hits = await search_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)

    # Both rows came from the hook; only the decant survived the profile's rules.
    assert [v.size_ml_x10 for v in hits[0].variants] == [50]
    assert [v.price_kurus for v in hits[0].variants] == [12050]
    assert [v.raw_title for v in hits[0].variants] == ["El Yazimi"]


async def test_parse_variants_returning_none_leaves_the_page_to_the_profile(
    server_url: str, tmp_path: Path
) -> None:
    # A hook written for one odd product shape must not have to reimplement the
    # normal one as well, so declining a page means the profile's layer runs.
    _write_hook(
        tmp_path,
        "async def parse_variants(profile, candidate, html):\n"
        "    if 'engine-product-bare' in candidate.url:\n"
        "        return ()\n"
        "    return None\n",
    )

    hits = await search_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)

    # Same result as with no hook at all: the embedded_json layer read both sizes.
    assert [v.size_ml_x10 for v in hits[0].variants] == [50, 100]


async def test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(
    server_url: str, tmp_path: Path
) -> None:
    # The case that stays true for every site so far. An empty hooks directory
    # must not change a single thing about how the site is read.
    hits = await search_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)

    assert [v.size_ml_x10 for v in hits[0].variants] == [50, 100]


async def test_a_before_search_that_returns_no_query_is_refused(
    server_url: str, tmp_path: Path
) -> None:
    # A hook that forgets its return gives None back. Coercing it would search
    # the shop for the word "None", find nothing, and report that as the perfume
    # not being sold there, which is the one answer that must never be guessed.
    _write_hook(tmp_path, "def before_search(profile, query):\n    query.strip()\n")

    with pytest.raises(ValueError, match="before_search returned NoneType"):
        await search_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)


async def test_a_hook_that_reads_nothing_is_named_as_the_culprit(
    server_url: str, tmp_path: Path
) -> None:
    # The message decides which file gets opened next. When a hook did the
    # reading, blaming the profile's extraction layer sends the reader to code
    # that never ran on this page.
    _write_hook(
        tmp_path,
        "async def parse_variants(profile, candidate, html):\n    return ()\n",
    )

    with pytest.raises(ExtractionFailed) as excinfo:
        await search_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)

    assert "parse_variants hook" in str(excinfo.value)
    assert "embedded_json" not in str(excinfo.value)


async def test_a_working_site_reports_ok_with_what_it_saw(server_url: str) -> None:
    result = await run_site(_profile(server_url), "test parfum")

    assert result.status == "ok"
    assert result.site_id == "testsite"
    assert len(result.hits) == 2
    # The detail is filled in on success too, so a site that quietly starts
    # returning one size where it returned ten is visible without a rerun.
    assert result.detail == "testsite: 2 product(s), 4 decant size(s)"


async def test_a_shop_that_does_not_carry_it_is_empty_not_suspect(
    server_url: str,
) -> None:
    # The distinction the whole type exists for. Nothing is wrong with this
    # site, so flagging it would train the reader to ignore the flag.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-empty?q={query}"

    result = await run_site(profile, "yok boyle bir parfum")

    assert result.status == "empty"
    assert result.hits == ()


async def test_a_page_of_full_bottles_only_is_empty_too(server_url: str) -> None:
    # Results came back, prices were read, and the decant filter took them all.
    # The profile is provably still working, so this is an answer, not a break.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-mixed?q={query}"
    profile["variant_rules"] = {**profile["variant_rules"], "max_size_ml": 1}

    result = await run_site(profile, "test parfum")

    assert result.status == "empty"


async def test_a_page_that_says_it_found_nothing_is_believed(server_url: str) -> None:
    # Two of the six live sites hang their whole catalog off the header, so their
    # no-results page carries hundreds of product-shaped nodes and used to wear
    # the broken-profile badge on every perfume they simply do not stock. The
    # page says so itself, and that outranks counting chrome.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-says-empty?q={query}"

    result = await run_site(profile, "yok boyle bir parfum")

    assert result.status == "empty"
    assert result.hits == ()


async def test_the_no_results_page_would_otherwise_read_as_suspect(
    server_url: str,
) -> None:
    # Guards the test above against passing for the wrong reason. Without the
    # shop's own no-results marker the same page trips the product-markup floor,
    # which is what makes it a real regression test rather than a page that was
    # never going to be flagged. Read through the same fetch the engine uses, so
    # the page under test is the page the engine sees.
    html = (await fetch(f"{server_url}/engine-search-says-empty", "httpx")).html

    cards = len(HTMLParser(html).css(_PRODUCT_MARKUP_SELECTOR))

    assert cards >= engine.PRODUCT_MARKUP_FLOOR


async def test_a_lone_full_bottle_is_empty_not_suspect(server_url: str) -> None:
    # The one result has no size list on it at all, so there was never a price
    # for the layer to fail at. One shop's catalog is roughly four fifths full
    # bottles, and every perfume it sells only as one used to come back flagged.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-bottle-only?q={query}"

    result = await run_site(profile, "test parfum")

    assert result.status == "empty"
    assert result.hits == ()


async def test_a_dead_row_selector_on_a_full_page_is_suspect(server_url: str) -> None:
    # The expensive silent failure: the shop redesigned, the row selector matches
    # nothing, and a page full of perfumes reads as "not sold here". The site
    # would drop out of the comparison and the cheapest price would be decided on
    # a table with a hole in it.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-renamed?q={query}"

    result = await run_site(profile, "test parfum")

    assert result.status == "suspect"
    # The selector that stopped matching is named, because the fix is someone
    # opening that page and writing a new one.
    assert ".card" in str(result.detail)


async def test_a_dead_link_selector_is_suspect_not_empty(server_url: str) -> None:
    # One notch more certain than the case above and needing no heuristic: the
    # rows are provably still there, so the link selector under them is what
    # died. Every candidate gets dropped for having no page to open.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-no-links?q={query}"

    result = await run_site(profile, "test parfum")

    assert result.status == "suspect"
    assert "2 result row(s)" in str(result.detail)


async def test_some_rows_without_links_is_not_suspect(server_url: str) -> None:
    # Rows disappearing one at a time is normal and must not trip the check. One
    # captured shop lists five cards where only one is a product link, and
    # flagging that would mark a working site broken on every run.
    profile = _profile(server_url)
    profile["search"]["result_item"] = ".card, nav"

    result = await run_site(profile, "test parfum")

    assert result.status == "ok"


async def test_a_profile_that_reads_nothing_is_suspect_not_empty(
    server_url: str,
) -> None:
    # Results on the page, no price out of any of them. Reporting this as "not
    # sold here" is the silent-empty failure: the site would drop out of the
    # comparison and nobody would learn its profile needs rewriting.
    profile = _profile(server_url)
    profile["embedded_json"]["selector"] = "[data-product_variations_v2]"

    result = await run_site(profile, "test")

    assert result.status == "suspect"
    assert result.hits == ()
    # A suspect result has to say which layer stopped answering, because the
    # only fix is someone opening that page and checking that selector.
    assert "embedded_json" in str(result.detail)


async def test_an_unreachable_site_is_an_error_and_does_not_raise(
    unused_tcp_port: int,
) -> None:
    # Fault isolation: one dead site becomes a row in the report instead of an
    # exception that ends the run for the sites that were fine.
    profile = _profile(f"http://127.0.0.1:{unused_tcp_port}")

    result = await run_site(profile, "test parfum")

    assert result.status == "error"
    assert result.site_id == "testsite"
    # The exception type is in the message: a connection refused and a broken
    # profile field are both "error" and want completely different fixes.
    assert "Error" in str(result.detail)


async def test_a_broken_hook_is_an_error_not_a_silent_empty(
    server_url: str, tmp_path: Path
) -> None:
    # A hook bug is the profile's problem, not the shop's. It must never come
    # back looking like the perfume is unavailable there.
    _write_hook(tmp_path, "def before_search(profile, query):\n    query.strip()\n")

    result = await run_site(_profile(server_url), "test parfum", hooks_dir=tmp_path)

    assert result.status == "error"
    assert "ValueError" in str(result.detail)


_VARIANT_CONTROL = "select[name=attribute_pa_hacim] option::attr(value)"


async def test_a_size_picker_the_layer_keeps_up_with_passes(server_url: str) -> None:
    # Two options behind the picker, two rows out of the blob, and the picker's
    # leading "Bir secim yapin" placeholder carries no value so it does not
    # count. A profile that flagged this would flag every healthy WooCommerce
    # page, and a badge that is always on is a badge nobody reads.
    profile = _profile(server_url, variant_control=_VARIANT_CONTROL)

    hits = await search_site(profile, "test parfum")

    assert [v.size_ml_x10 for v in hits[0].variants] == [50, 100]


async def test_a_page_offering_more_sizes_than_it_prices_is_suspect(
    server_url: str,
) -> None:
    # Four sizes on offer, two in the blob. Without the picker to count against,
    # this reads as a complete answer: the table fills, the ₺/ml looks sane, and
    # the two missing sizes are simply never compared against any other shop.
    profile = _profile(server_url, variant_control=_VARIANT_CONTROL)
    profile["search"]["url_template"] = "{base_url}/engine-search-half?q={query}"

    result = await run_site(profile, "test parfum")

    assert result.status == "suspect"
    assert "4 sizes" in str(result.detail)
    assert "read 2" in str(result.detail)


async def test_the_same_half_read_page_passes_without_the_picker_declared(
    server_url: str,
) -> None:
    # The counterpart that pins why the profile field has to exist: nothing else
    # in the flow can tell this page from a healthy one. This is the behavior
    # before the check, kept as the reason the check is not optional decoration.
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-half?q={query}"

    result = await run_site(profile, "test parfum")

    assert result.status == "ok"


async def test_a_full_bottle_page_is_not_checked_against_the_picker(
    server_url: str,
) -> None:
    # A plain full bottle has no size picker for the selector to match, and no
    # size table to be missing anything from. Counting zero options as a broken
    # profile would sink a shop for stocking bottles next to its decants.
    profile = _profile(server_url, variant_control=_VARIANT_CONTROL)
    profile["search"]["url_template"] = "{base_url}/engine-search-mixed?q={query}"

    (hit,) = await search_site(profile, "test parfum")

    assert hit.candidate.raw_title == "Test Parfum Dekant"


async def test_a_get_endpoint_profile_opens_the_page_just_for_the_picker(
    server_url: str,
) -> None:
    # This layer answers in one request and never opens the product page, so
    # asking it to count a picker costs a second request per product. Opt-in
    # through the profile field, and only worth it on a site whose feed has been
    # caught dropping sizes: the feed here names two, the picker four.
    profile = _profile(
        server_url,
        variant_control=_VARIANT_CONTROL,
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/engine-product.js",
            "variants_path": "variants",
            "field_map": {
                "size_raw": "title",
                "price": "price",
                "in_stock": "available",
            },
        },
    )
    profile["search"]["url_template"] = "{base_url}/engine-search-half?q={query}"

    result = await run_site(profile, "test parfum")

    assert result.status == "suspect"
    assert "4 sizes" in str(result.detail)


async def test_a_variantless_product_does_not_sink_the_post_endpoint_layer(
    server_url: str,
) -> None:
    # A plain full bottle has no option list and so no product id to post with.
    # Reading that as a broken profile ends the site over a product that was
    # never going to carry a decant price, and takes the shop's real decants
    # down with it. The missing-field check above still stands for a page that
    # does list options.
    profile = _profile(
        server_url,
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/engine-related-options",
            "method": "POST",
            "body": {
                "parent_product_id": (
                    'a.add-to-cart-button[data-context="detail"]::attr(data-product-id)'
                ),
                "selected_option_group_id": (
                    "div.variant-list-group::attr(data-group-id)"
                ),
            },
            "option_selector": "span.variant-text::attr(data-option-id)",
            "option_body_key": "selected_options[]",
            "variants_path": "data.options",
            "field_map": {
                "size_raw": "option_title",
                "price": "product_price.sale_price",
                "in_stock": "product_stock_amount",
            },
        },
    )
    profile["search"]["url_template"] = (
        "{base_url}/engine-search-post-endpoint-mixed?q={query}"
    )

    (hit,) = await search_site(profile, "test")

    assert hit.candidate.raw_title == "Test Parfum Dekant"
    assert [v.size_ml_x10 for v in hit.variants] == [50, 100]


async def test_the_search_page_can_refuse_the_headers_the_rest_of_the_site_needs(
    server_url: str,
) -> None:
    # A real pairing, not a hypothetical: one platform's variant endpoint says
    # nothing at all without X-Requested-With, and that same header makes its
    # search page answer 404. Site-wide headers alone cannot express a site
    # like that, so the search page replaces the set the way it already
    # replaces the strategy.
    sent: list[tuple[str, Mapping[str, str] | None]] = []

    async def spy(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        sent.append((url, headers))
        return await fetch(
            url,
            strategy,
            method=method,
            data=data,
            headers=headers,
            timeout_s=timeout_s,
        )

    profile = _profile(
        server_url, request_headers={"X-Requested-With": "XMLHttpRequest"}
    )
    profile["search"]["request_headers"] = {}

    await search_site(profile, "test parfum", fetcher=spy)

    search_url, search_headers = sent[0]
    assert "engine-search" in search_url
    assert search_headers == {}
    product_headers = [h for url, h in sent[1:] if "engine-product" in url]
    assert product_headers == [{"X-Requested-With": "XMLHttpRequest"}] * len(
        product_headers
    )
    assert product_headers


async def test_sites_run_in_parallel_and_report_in_profile_order(
    server_url: str,
) -> None:
    # The point of the run loop: three unrelated shops have no reason to wait for
    # each other, so the run should cost the slowest site, not their sum. The
    # fetcher below refuses to answer until all three sites have a request in
    # flight, so a loop that ran them one after another would deadlock here
    # rather than merely be slow.
    started = asyncio.Event()
    in_flight = 0

    async def gated(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        nonlocal in_flight
        if "engine-search" in url:
            in_flight += 1
            if in_flight == 3:
                started.set()
            async with asyncio.timeout(5):
                await started.wait()
        return await fetch(
            url,
            strategy,
            method=method,
            data=data,
            headers=headers,
            timeout_s=timeout_s,
        )

    profiles = [_profile(server_url, id=site_id) for site_id in ("bir", "iki", "uc")]

    results = await run_sites(profiles, "test parfum", fetcher=gated)

    # Profile order, not finish order, so the same shops always read the same way.
    assert [r.site_id for r in results] == ["bir", "iki", "uc"]
    assert [r.status for r in results] == ["ok", "ok", "ok"]


async def test_a_dead_site_does_not_take_the_others_down(
    server_url: str, unused_tcp_port: int
) -> None:
    # The whole reason run_site swallows: inside a TaskGroup a raising task
    # cancels its siblings, and one shop being offline would then erase the
    # prices of every shop that answered.
    profiles = [
        _profile(server_url, id="saglam"),
        _profile(f"http://127.0.0.1:{unused_tcp_port}", id="olu"),
        _profile(server_url, id="saglam2"),
    ]

    results = await run_sites(profiles, "test parfum")

    assert [r.status for r in results] == ["ok", "error", "ok"]
    assert results[0].hits and results[2].hits


async def test_no_sites_is_an_empty_run_not_a_crash() -> None:
    assert await run_sites([], "test parfum") == ()


async def test_a_profile_that_breaks_on_setup_is_contained_too(
    server_url: str,
) -> None:
    # The isolation boundary has to cover the whole of a site's run, not just
    # the fetching. A bad rate_limit_ms breaks while the pacing is being built,
    # which is before any request goes out, and a failure there escaping into
    # the TaskGroup would cancel the shops that were answering fine.
    profiles = [
        _profile(server_url, id="saglam"),
        _profile(server_url, id="bozuk", rate_limit_ms="hizli"),
    ]

    results = await run_sites(profiles, "test parfum")

    assert [r.status for r in results] == ["ok", "error"]
    assert results[0].hits
    assert "ValueError" in str(results[1].detail)


# --- Pacing, one site at a time ------------------------------------------------
#
# The targets are small shops, so a run has to look like a person browsing rather
# than a burst. These check the three parts of that: requests inside one site are
# spaced, sites do not pace each other, and a refused request is retried a bounded
# number of times before the site is given up on.


@pytest.fixture
def slept(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record every delay the engine asks for instead of serving it.

    Waiting for real would make the suite pay the pacing it is checking, and it
    would push these cases into asserting on elapsed wall clock, which measures
    how busy the machine is more than what the code decided.
    """
    delays: list[float] = []

    async def record(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr(engine, "_sleep", record)
    return delays


def _counting_fetcher(
    results: Sequence[FetchResult | Exception],
) -> tuple[Fetcher, list[str]]:
    """Answer each call with the next canned result, then repeat the last one."""
    sent: list[str] = []

    async def canned(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        sent.append(url)
        answer = results[min(len(sent) - 1, len(results) - 1)]
        if isinstance(answer, Exception):
            raise answer
        return answer

    return canned, sent


async def test_a_sites_requests_are_spaced_by_its_own_rate_limit(
    server_url: str, slept: list[float]
) -> None:
    # One search page and two product pages, so two gaps. The first request waits
    # for nothing: there is nothing to be polite about yet, and starting every
    # site with a dead 800 ms would make a whole run feel broken.
    result = await run_site(_profile(server_url, rate_limit_ms=250), "test parfum")

    assert result.status == "ok"
    assert len(slept) == 2
    # Measured from when the previous request finished, so a slow page shortens
    # the wait that follows it rather than being chased immediately.
    assert all(0 < delay <= 0.25 for delay in slept)


async def test_one_site_waiting_does_not_hold_up_another(
    server_url: str, slept: list[float]
) -> None:
    # The pacing state has to be per site. A module-level gate or timestamp would
    # quietly serialize the whole run, and every other test would still pass.
    profiles = [
        _profile(server_url, id="yavas", rate_limit_ms=800),
        _profile(server_url, id="hizli", rate_limit_ms=0),
    ]

    results = await run_sites(profiles, "test parfum")

    assert [r.status for r in results] == ["ok", "ok"]
    # Only the slow site's two gaps. Shared state would have made the fast site
    # wait its neighbor's 800 ms as well.
    assert len(slept) == 2
    assert all(delay > 0.5 for delay in slept)


async def test_a_request_that_failed_once_is_retried_and_the_site_is_fine(
    slept: list[float],
) -> None:
    # A dropped connection is not a broken profile. Reporting the site as an
    # error over one blip drops a real shop out of the comparison.
    page = FetchResult(
        url="https://x.test/", status_code=200, html="", strategy="httpx"
    )
    fetcher, sent = _counting_fetcher([TimeoutError("connection reset"), page])
    profile = _profile("https://x.test", rate_limit_ms=0)
    profile["search"]["result_item"] = ".none"

    result = await run_site(profile, "test parfum", fetcher=fetcher)

    assert result.status == "empty"
    assert len(sent) == 2
    # Backing off, not retrying instantly, and not the site's own rate_limit_ms
    # either: that is spacing between requests that worked, this is recovering
    # from one that was refused, and a profile setting it to 0 must not turn a
    # refusal into three requests back to back.
    assert slept == [engine.RETRY_BACKOFF_MS / 1000]


async def test_a_shop_that_keeps_refusing_is_given_up_on(slept: list[float]) -> None:
    # Bounded, and doubling in between. Retrying forever would hang the run on
    # one dead shop, and retrying hard would be the request flood this avoids.
    fetcher, sent = _counting_fetcher([TimeoutError("connection reset")])

    result = await run_site(
        _profile("https://x.test", rate_limit_ms=0), "test parfum", fetcher=fetcher
    )

    assert result.status == "error"
    assert "TimeoutError" in str(result.detail)
    assert len(sent) == engine.MAX_ATTEMPTS
    assert slept == [1.0, 2.0]


async def test_a_shop_asking_for_a_pause_is_asked_again_after_one(
    slept: list[float],
) -> None:
    # 429 is the shop saying so directly. Reading its body as a product page
    # would report the site as suspect when nothing about the profile is wrong.
    refusal = FetchResult(
        url="https://x.test/", status_code=429, html="slow down", strategy="httpx"
    )
    empty = FetchResult(
        url="https://x.test/", status_code=200, html="", strategy="httpx"
    )
    fetcher, sent = _counting_fetcher([refusal, empty])
    profile = _profile("https://x.test", rate_limit_ms=0)
    profile["search"]["result_item"] = ".none"

    result = await run_site(profile, "test parfum", fetcher=fetcher)

    assert result.status == "empty"
    assert len(sent) == 2


async def test_a_page_that_is_simply_missing_is_not_asked_for_again(
    slept: list[float],
) -> None:
    # A 404 is an answer. Sending it twice more changes nothing and only adds
    # load to a shop that already said what it had to say.
    missing = FetchResult(
        url="https://x.test/", status_code=404, html="", strategy="httpx"
    )
    fetcher, sent = _counting_fetcher([missing])
    profile = _profile("https://x.test", rate_limit_ms=0)
    profile["search"]["result_item"] = ".none"

    result = await run_site(profile, "test parfum", fetcher=fetcher)

    assert result.status == "empty"
    assert len(sent) == 1
    assert slept == []


async def test_a_missing_browser_is_reported_at_once_not_retried(
    slept: list[float],
) -> None:
    # An install that is not there will not be there on the third try. Retrying
    # it only delays the one message that says what to install.
    fetcher, sent = _counting_fetcher([PlaywrightNotInstalled("no browser")])

    result = await run_site(
        _profile("https://x.test", rate_limit_ms=0), "test parfum", fetcher=fetcher
    )

    assert result.status == "error"
    assert "PlaywrightNotInstalled" in str(result.detail)
    assert len(sent) == 1
    assert slept == []


class _NoRootParser:
    """Stands in for HTMLParser when a page's markup cannot be read at all.

    selectolax gives up its root node only on a real parser failure, which
    ordinary text never triggers, so this is what forces that branch open
    for a test.
    """

    def __init__(self, html: str) -> None:
        self.root = None


def test_a_search_page_with_no_root_names_its_body_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A zero-byte body and a page that came back full but unparseable are two
    # different failures wearing the same "no markup" sentence. The byte count
    # is what tells them apart without opening the page.
    monkeypatch.setattr(engine, "HTMLParser", _NoRootParser)
    html = "not really markup, just enough bytes to matter"
    result = FetchResult(
        url="https://x.test/search", status_code=200, html=html, strategy="httpx"
    )

    with pytest.raises(ExtractionFailed) as excinfo:
        engine._check_empty_search({"id": "testsite"}, result)

    assert f"({len(html.encode())} byte body)" in str(excinfo.value)


async def test_a_product_page_with_no_root_names_its_body_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(engine, "HTMLParser", _NoRootParser)
    html = ""

    async def fetcher(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        return FetchResult(url=url, status_code=200, html=html, strategy="httpx")

    candidate = engine.ProductCandidate(raw_title=None, url="https://x.test/p/1")
    config = {"option_selector": ".size"}
    profile = {"id": "testsite", "strategy": "httpx"}

    with pytest.raises(ExtractionFailed) as excinfo:
        await engine._read_endpoint_variants_post(profile, config, candidate, fetcher)

    # An empty body is the clearest case the byte count has to catch: it says
    # in the message itself that nothing at all came back, not just that
    # parsing failed on something.
    assert "(0 byte body)" in str(excinfo.value)


def _watching_fetcher() -> tuple[Fetcher, list[str]]:
    """The real fetcher, with a list of every URL it was asked for."""
    sent: list[str] = []

    async def watched(
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        sent.append(url)
        return await fetch(
            url,
            strategy,
            method=method,
            data=data,
            headers=headers,
            timeout_s=timeout_s,
        )

    return watched, sent


def _named_profile(server_url: str) -> dict[str, Any]:
    """A profile whose search page lists two houses' bottles, as shops do."""
    profile = _profile(server_url)
    profile["search"]["url_template"] = "{base_url}/engine-search-named?q={query}"
    return profile


async def test_a_listing_from_another_house_costs_no_product_request(
    server_url: str,
) -> None:
    # Where a scan spends its time: one request per search result, spaced by the
    # rate limit, over a catalog that is mostly other perfumes. The Chanel row is
    # not this search, and its page was never going to contribute a row.
    query = parse_query("Dior Sauvage EDP")
    fetcher, sent = _watching_fetcher()

    hits = await search_site(
        _named_profile(server_url),
        "dior sauvage edp",
        fetcher=fetcher,
        keep_candidate=lambda title: title_could_match(title, query),
    )

    assert [hit.candidate.raw_title for hit in hits] == ["Dior Sauvage EDP Dekant"]
    assert sum("engine-product" in url for url in sent) == 1


async def test_without_a_filter_every_listing_is_still_opened(
    server_url: str,
) -> None:
    # The default has to stay what it was. A caller that passes no filter is
    # asking for every result, and the two rows here share one product page, so
    # the count is what proves the filter is the thing making the difference.
    fetcher, sent = _watching_fetcher()

    hits = await search_site(
        _named_profile(server_url), "dior sauvage edp", fetcher=fetcher
    )

    assert len(hits) == 2
    assert sum("engine-product" in url for url in sent) == 2


async def test_a_broken_profile_is_still_suspect_when_no_title_looked_right(
    server_url: str,
) -> None:
    # The reason one page is opened even when the filter keeps nothing. Without
    # it this shop answers "we don't sell that" for every search whose listings
    # look unpromising, while the real answer is that its product pages stopped
    # being readable.
    profile = _named_profile(server_url)
    profile["embedded_json"]["selector"] = "[data-product_variations_v2]"

    result = await run_site(
        profile, "louis vuitton ombre nomade", keep_candidate=lambda title: False
    )

    assert result.status == "suspect"
    assert "embedded_json" in str(result.detail)


async def test_a_scan_says_how_many_listings_it_skipped(server_url: str) -> None:
    # A filter that narrows the scan silently is the same failure as a dead
    # selector: the table looks complete either way.
    query = parse_query("Dior Sauvage EDP")

    result = await run_site(
        _named_profile(server_url),
        "dior sauvage edp",
        keep_candidate=lambda title: title_could_match(title, query),
    )

    assert result.status == "ok"
    assert "1 listing(s) skipped by title" in str(result.detail)


async def test_one_product_listed_under_two_searches_is_read_once(
    server_url: str,
) -> None:
    # What a multi-perfume search buys back. Both rows on this page are the same
    # product page, and so is the second search's, so three of the four possible
    # product reads are answers already in hand.
    fetcher, sent = _watching_fetcher()
    cache: dict[Any, Any] = {}
    profile = _named_profile(server_url)

    await search_site(
        profile, "dior sauvage edp", fetcher=fetcher, variants_cache=cache
    )
    await search_site(profile, "chanel bleu edp", fetcher=fetcher, variants_cache=cache)

    assert sum("engine-product" in url for url in sent) == 1
    # Both searches still went out. It is the product pages that are shared, not
    # the results page, which is different text for a different perfume.
    assert sum("engine-search-named" in url for url in sent) == 2


async def test_two_shops_sharing_a_url_do_not_read_each_others_pages(
    server_url: str,
) -> None:
    # One cache is handed to a whole scan, and shops really do share paths. A
    # key without the site in it would read one shop's page through another
    # shop's rules.
    fetcher, sent = _watching_fetcher()
    cache: dict[Any, Any] = {}
    first = _named_profile(server_url)
    second = _named_profile(server_url)
    second["id"] = "othersite"

    await search_site(first, "dior sauvage edp", fetcher=fetcher, variants_cache=cache)
    await search_site(second, "dior sauvage edp", fetcher=fetcher, variants_cache=cache)

    assert sum("engine-product" in url for url in sent) == 2
