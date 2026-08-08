"""Tests for parfum_finder.extract.

Every case here is a shape a real store actually emits. The point of the JSON-LD
rung is that it keeps working when a theme changes, so what these tests defend is
tolerance: an unusual wrapper, a missing "@type" on a child, a broken block next to
a good one must all still yield the product, and an availability value nobody
recognizes must yield "unknown" rather than "out of stock".

The module is pure and synchronous, so nothing here needs the local HTTP server or
a browser.
"""

from decimal import Decimal
from pathlib import Path

from parfum_finder.extract import (
    extract_css_variants,
    extract_embedded_variants,
    extract_endpoint_variants,
    extract_jsonld_products,
    extract_jsonld_variants,
)

_FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"

_SIMPLE = """<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Test Parfum", "url": "https://x.test/p/1",
 "sku": "SKU-1",
 "offers": {"@type": "Offer", "price": "1250.00", "priceCurrency": "TRY",
            "availability": "https://schema.org/InStock"}}
</script>
</body></html>"""

# The same product, wrapped in the "@graph" array form, next to a non-Product node
# that must not turn into a row.
_GRAPH = """<html><body>
<script type="application/ld+json">
{"@context": "https://schema.org",
 "@graph": [{"@type": "BreadcrumbList"},
            {"@type": "Product", "name": "Graph Parfum"}]}
</script>
</body></html>"""

# The other wrapper: a root array instead of an object.
_ROOT_ARRAY = """<html><body>
<script type="application/ld+json">
[{"@type": "Organization", "name": "Store"},
 {"@type": "Product", "name": "Array Parfum"}]
</script>
</body></html>"""

# What a category or search page looks like: the products sit two levels down,
# under each ListItem's "item" key.
_ITEM_LIST = """<html><body>
<script type="application/ld+json">
{"@type": "ItemList", "itemListElement": [
  {"@type": "ListItem", "position": 1, "item": {"@type": "Product", "name": "One"}},
  {"@type": "ListItem", "position": 2, "item": {"@type": "Product", "name": "Two"}}
]}
</script>
</body></html>"""

# "@type" as a list, which feeds emit when a node is several things at once.
_TYPE_LIST = """<html><body>
<script type="application/ld+json">
{"@type": ["Product", "Thing"], "name": "Multi Type"}
</script>
</body></html>"""

# One product carrying several separate Offer objects, one per size.
_OFFER_LIST = """<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Many Offers", "offers": [
  {"@type": "Offer", "price": 149.9, "priceCurrency": "TRY",
   "availability": "InStock"},
  {"@type": "Offer", "price": 289.9, "priceCurrency": "TRY",
   "availability": "OutOfStock"}
]}
</script>
</body></html>"""

# An AggregateOffer: no "price" at all, a range instead, with the individual
# offers it summarizes nested inside it.
_AGGREGATE_OFFER = """<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Aggregate", "offers": {
  "@type": "AggregateOffer", "lowPrice": "149.90", "highPrice": "899.00",
  "priceCurrency": "TRY", "offerCount": 4,
  "offers": [{"@type": "Offer", "price": "149.90", "availability": "InStock"}]}}
</script>
</body></html>"""

# A variant parent: one product, four sizes underneath it. The children carry no
# "@type" of their own, which is common.
_HAS_VARIANT = """<html><body>
<script type="application/ld+json">
{"@type": "ProductGroup", "name": "Parent Parfum", "hasVariant": [
  {"name": "Parent Parfum 5 ml",
   "offers": {"@type": "Offer", "price": "149.90", "availability": "InStock"}},
  {"name": "Parent Parfum 10 ml",
   "offers": {"@type": "Offer", "price": "279.90", "availability": "OutOfStock"}}
]}
</script>
</body></html>"""

# A broken block shipped alongside a good one. Losing the good product with it
# would be the worse failure.
_MALFORMED_PLUS_VALID = """<html><body>
<script type="application/ld+json">{not valid json</script>
<script type="application/ld+json">{"@type": "Product", "name": "Survivor"}</script>
</body></html>"""

_NO_JSONLD = """<html><body>
<div class="product">No structured data</div>
</body></html>"""


def _one_product_html(fragment: str) -> str:
    """Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases."""
    return (
        '<html><body><script type="application/ld+json">'
        f'{{"@type": "Product", "name": "X", {fragment}}}'
        "</script></body></html>"
    )


def test_reads_product_and_its_offer() -> None:
    (product,) = extract_jsonld_products(_SIMPLE)

    assert product.name == "Test Parfum"
    assert product.url == "https://x.test/p/1"
    assert product.sku == "SKU-1"
    (offer,) = product.offers
    assert offer.price == Decimal("1250.00")
    assert offer.currency == "TRY"
    assert offer.in_stock is True
    assert offer.availability_raw == "https://schema.org/InStock"


def test_reads_graph_wrapper_and_ignores_non_products() -> None:
    products = extract_jsonld_products(_GRAPH)

    assert [p.name for p in products] == ["Graph Parfum"]


def test_reads_root_array() -> None:
    products = extract_jsonld_products(_ROOT_ARRAY)

    assert [p.name for p in products] == ["Array Parfum"]


def test_reads_products_nested_under_an_item_list() -> None:
    products = extract_jsonld_products(_ITEM_LIST)

    assert [p.name for p in products] == ["One", "Two"]


def test_reads_type_given_as_a_list() -> None:
    products = extract_jsonld_products(_TYPE_LIST)

    assert [p.name for p in products] == ["Multi Type"]


def test_reads_every_offer_when_offers_is_a_list() -> None:
    (product,) = extract_jsonld_products(_OFFER_LIST)

    assert [o.price for o in product.offers] == [Decimal("149.9"), Decimal("289.9")]
    assert [o.in_stock for o in product.offers] == [True, False]


def test_reads_aggregate_offer_range_and_its_nested_offers() -> None:
    (product,) = extract_jsonld_products(_AGGREGATE_OFFER)

    aggregate, nested = product.offers
    # The aggregate advertises a range and no single price. Reading only "price"
    # would report this product as having no price at all.
    assert aggregate.price is None
    assert aggregate.low_price == Decimal("149.90")
    assert aggregate.high_price == Decimal("899.00")
    assert nested.price == Decimal("149.90")


def test_keeps_variants_nested_instead_of_flattening_them() -> None:
    products = extract_jsonld_products(_HAS_VARIANT)

    # One product, not three. Flattening would make a variant parent
    # indistinguishable from a site that lists each size as its own product, and
    # telling those two apart is the whole reason discovery visits a site.
    (product,) = products
    assert product.name == "Parent Parfum"
    assert [v.name for v in product.variants] == [
        "Parent Parfum 5 ml",
        "Parent Parfum 10 ml",
    ]
    assert [v.offers[0].price for v in product.variants] == [
        Decimal("149.90"),
        Decimal("279.90"),
    ]


def test_single_variant_given_as_an_object_is_read_too() -> None:
    # A product with exactly one size sometimes writes hasVariant as one object
    # instead of a one-element list.
    (product,) = extract_jsonld_products(
        _one_product_html('"hasVariant": {"name": "Only 5 ml"}')
    )

    assert [v.name for v in product.variants] == ["Only 5 ml"]


def test_sizes_listed_on_the_parent_group_are_not_lost() -> None:
    # The mirror image of the previous case: one size is the top-level product
    # and the rest of the range hangs off the group it points back to. Reading
    # only the product's own hasVariant would report a single size and drop the
    # others silently.
    (product,) = extract_jsonld_products(
        _one_product_html(
            '"isVariantOf": {"@type": "ProductGroup", "hasVariant": '
            '[{"name": "5 ml"}, {"name": "10 ml"}]}'
        )
    )

    assert [v.name for v in product.variants] == ["5 ml", "10 ml"]


def test_the_same_product_in_two_blocks_is_reported_twice() -> None:
    # No de-duplication across blocks. A store that repeats one product in a
    # "@graph" block and again standalone yields two rows, so a count of rows is
    # not a count of distinct products. Merging them would need an identity rule
    # (sku? url? name?) that nothing here can pick safely yet, and guessing wrong
    # would merge two genuinely different sizes into one.
    html = """<html><body>
<script type="application/ld+json">
{"@graph": [{"@type": "Product", "name": "Same", "sku": "S"}]}
</script>
<script type="application/ld+json">
{"@type": "Product", "name": "Same", "sku": "S"}
</script>
</body></html>"""

    assert [p.name for p in extract_jsonld_products(html)] == ["Same", "Same"]


def test_boolean_values_are_never_read_as_price_or_text() -> None:
    # bool is an int subclass in Python, so a stray `true` would otherwise turn
    # into a price of 1 and an sku of "True".
    (product,) = extract_jsonld_products(
        _one_product_html('"sku": true, "offers": {"price": true}')
    )

    assert product.sku is None
    assert product.offers[0].price is None


def test_a_broken_block_does_not_lose_the_valid_one() -> None:
    products = extract_jsonld_products(_MALFORMED_PLUS_VALID)

    assert [p.name for p in products] == ["Survivor"]


def test_page_without_jsonld_yields_nothing() -> None:
    assert extract_jsonld_products(_NO_JSONLD) == ()


def test_plain_numeric_price_string_is_read_as_written() -> None:
    # A three-decimal price is where guessing separator conventions goes wrong:
    # read as a thousands group this becomes 1250000, a thousandfold error that
    # would silently win every cheapest-first comparison.
    (product,) = extract_jsonld_products(
        _one_product_html('"offers": {"price": "1250.000"}')
    )

    assert product.offers[0].price == Decimal("1250.000")


def test_display_formatted_price_string_still_parses() -> None:
    # Some feeds put human-facing text in this field anyway, so the Turkish
    # convention has to survive: dot groups thousands, comma is the decimal point.
    (product,) = extract_jsonld_products(
        _one_product_html('"offers": {"price": "1.250,00 TL"}')
    )

    assert product.offers[0].price == Decimal("1250.00")


def test_numeric_price_is_read_without_float_drift() -> None:
    (product,) = extract_jsonld_products(
        _one_product_html('"offers": {"price": 149.9}')
    )

    assert product.offers[0].price == Decimal("149.9")


def test_missing_price_is_none_not_zero() -> None:
    # Zero would sort to the top of a cheapest-first list and read as a free
    # product, which is worse than admitting the page did not say.
    (product,) = extract_jsonld_products(
        _one_product_html('"offers": {"priceCurrency": "TRY"}')
    )

    assert product.offers[0].price is None


def test_unparseable_price_text_is_none() -> None:
    (product,) = extract_jsonld_products(
        _one_product_html('"offers": {"price": "Fiyat sorunuz"}')
    )

    assert product.offers[0].price is None


def test_availability_spellings_all_land_in_the_same_bucket() -> None:
    for value in (
        "https://schema.org/InStock",
        "http://schema.org/InStock",
        "InStock",
        "in_stock",
    ):
        (product,) = extract_jsonld_products(
            _one_product_html(f'"offers": {{"availability": "{value}"}}')
        )
        assert product.offers[0].in_stock is True, value

    for value in ("https://schema.org/OutOfStock", "SoldOut", "out-of-stock"):
        (product,) = extract_jsonld_products(
            _one_product_html(f'"offers": {{"availability": "{value}"}}')
        )
        assert product.offers[0].in_stock is False, value


def test_unrecognized_availability_is_unknown_and_keeps_the_raw_value() -> None:
    # Forcing an unknown value to False would hide a product that is actually on
    # sale, so the answer stays "unknown" and the raw text is kept for a human.
    (product,) = extract_jsonld_products(
        _one_product_html('"offers": {"availability": "https://schema.org/PreOrder"}')
    )

    assert product.offers[0].in_stock is None
    assert product.offers[0].availability_raw == "https://schema.org/PreOrder"


def test_missing_availability_is_unknown() -> None:
    (product,) = extract_jsonld_products(_one_product_html('"offers": {"price": 10}'))

    assert product.offers[0].in_stock is None
    assert product.offers[0].availability_raw is None


def test_numeric_sku_is_read_as_text() -> None:
    (product,) = extract_jsonld_products(_one_product_html('"sku": 12345'))

    assert product.sku == "12345"


def test_object_valued_text_field_is_dropped_not_stringified() -> None:
    # A repr of a dict shown as a product name in the results table would be
    # worse than an empty cell.
    (product,) = extract_jsonld_products(_one_product_html('"url": {"@id": "/p/1"}'))

    assert product.url is None


def test_product_without_offers_is_still_reported() -> None:
    (product,) = extract_jsonld_products(_one_product_html('"sku": "S"'))

    assert product.offers == ()
    assert product.variants == ()


# --- The other three rungs, and the flat RawVariant view of the first ---------
#
# The embedded_json cases below run against the golden HTML captured from the real
# target sites rather than against blobs written here. A blob written by hand
# cannot fail when the real one turns out to have a different shape, and every one
# of these four pages hides its variant table somewhere different.


def _fixture(site: str) -> str:
    """Read a captured product page."""
    return (_FIXTURE_ROOT / site / "product.html").read_text(encoding="utf-8")


# The variant table sits in a data- attribute, HTML-escaped, on the add-to-cart
# form. Two of the target sites do it this way.
_ATTRIBUTE_CONFIG = {
    "source": "attribute",
    "selector": "[data-product_variations]",
    "attribute": "data-product_variations",
    "field_map": {
        "size_raw": "attributes.attribute_pa_hacim",
        "price": "display_price",
        "in_stock": "is_in_stock",
    },
}

# The variant table sits inside a JS assignment, so the script body around it is
# not JSON and only the value after "variants:" can be parsed. Sizes are the keys
# of that object, not a field inside each entry.
_MARKER_CONFIG = {
    "source": "script",
    "marker": r"variants:\s*",
    "variants_path": "summary",
    "field_map": {
        "size_raw": "@key",
        "price": "price_list.fiyat",
        "in_stock": "in_stock",
    },
}

# The whole script body is JSON, so no marker is needed, but the variant list is
# buried four levels down and stock is a count rather than a flag.
_JSON_ISLAND_CONFIG = {
    "source": "script",
    "selector": "script#__NEXT_DATA__",
    "variants_path": "props.pageProps.pageSpecificData.variants",
    "field_map": {
        "size_raw": "variantValues.0.name",
        "price": "prices.0.sellPrice",
        "in_stock": "stocks.0.stockCount",
    },
}

# One size of one product as the İdeasoft variant endpoint answers. No golden copy
# of this response exists, because capturing it needs a POST whose body is built
# from attributes on the product page, so this is the shape written out by hand.
_ENDPOINT_RESPONSE = {
    "success": True,
    "data": {
        "options": [
            {
                "option_title": "3 ml",
                "product_name": "Amouage Blossom Love 3 ml",
                "product_url": "/urun/amouage-blossom-love-3-ml",
                "product_sku": "P2ANKDV2A4_66908",
                "product_stock_amount": 32.0,
                "product_price": {"price": 450.0, "currency_abbr": "TL"},
            },
            {
                "option_title": "5 ml",
                "product_name": "Amouage Blossom Love 5 ml",
                "product_url": "/urun/amouage-blossom-love-5-ml",
                "product_sku": "P2ANKDV2A4_66909",
                "product_stock_amount": 0.0,
                "product_price": {"price": 700.0, "currency_abbr": "TL"},
            },
        ]
    },
}

_ENDPOINT_CONFIG = {
    "variants_path": "data.options",
    "field_map": {
        "size_raw": "option_title",
        "price": "product_price.price",
        "in_stock": "product_stock_amount",
        "title": "product_name",
        "url": "product_url",
        "sku": "product_sku",
    },
}

# An AggregateOffer that names only the two ends of a price range and nests no
# individual offers, which is all one target site's product page declares.
_AGGREGATE_OFFER_RANGE_ONLY = """<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Range Only",
 "offers": {"@type": "AggregateOffer", "lowPrice": "180", "highPrice": "1570",
            "priceCurrency": "TRY"}}
</script>
</body></html>"""

# A product whose sizes are declared properly: one parent, two children, each
# child carrying its own price.
_HAS_VARIANT_PRICED = """<html><body>
<script type="application/ld+json">
{"@type": "ProductGroup", "name": "Parent", "url": "https://x.test/p/1",
 "offers": {"@type": "Offer", "price": "200.00"},
 "hasVariant": [
   {"name": "Parent 3 ml", "sku": "V3",
    "offers": {"price": "180", "availability": "InStock"}},
   {"name": "Parent 5 ml", "sku": "V5",
    "offers": {"price": "270", "availability": "OutOfStock"}}]}
</script>
</body></html>"""

# A size that points back at the group it belongs to, and appears again inside
# that group's own list. The same size, described twice.
_SELF_REFERENTIAL = """<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Solo 3 ml", "sku": "V3",
 "offers": {"price": "180"},
 "isVariantOf": {"@type": "ProductGroup", "hasVariant": [
   {"name": "Solo 3 ml", "sku": "V3", "offers": {"price": "180"}}]}}
</script>
</body></html>"""

_CSS_PAGE = """<html><body>
<div class="variant" data-sku="V3">
  <span class="size">3 ml</span>
  <span class="price">180,00 TL</span>
  <a class="buy" href="/urun/x-3-ml">Sepete ekle</a>
</div>
<div class="variant" data-sku="V5">
  <span class="size">5 ml</span>
  <span class="price">270,00 TL</span>
</div>
</body></html>"""

_CSS_CONFIG = {
    "variant_container": ".variant",
    "size_raw": ".size::text",
    "price": ".price::text",
    "sku": "::attr(data-sku)",
    "url": ".buy::attr(href)",
}


def test_jsonld_variants_reports_each_size_and_not_the_parent() -> None:
    # The 200.00 on the parent is a starting-from or per-ml figure. Reporting it
    # as a buyable row would put a price on a size nobody can order.
    variants = extract_jsonld_variants(_HAS_VARIANT_PRICED)

    assert [v.size_raw for v in variants] == [None, None]
    assert [v.title for v in variants] == ["Parent 3 ml", "Parent 5 ml"]
    assert [v.price for v in variants] == [Decimal("180"), Decimal("270")]
    assert [v.in_stock for v in variants] == [True, False]


def test_jsonld_variants_collapses_a_size_listed_twice() -> None:
    # Reporting one size twice would double it in a basket total.
    variants = extract_jsonld_variants(_SELF_REFERENTIAL)

    assert len(variants) == 1
    assert variants[0].sku == "V3"


def test_jsonld_variants_refuses_a_price_range() -> None:
    # An AggregateOffer's two ends name two of the sizes and say nothing about the
    # ones between. Emitting them as variants would pair a price with a size the
    # page never paired it with, so the honest result is nothing and a fall to the
    # next rung.
    variants = extract_jsonld_variants(_AGGREGATE_OFFER_RANGE_ONLY)

    assert variants == ()


def test_jsonld_variants_keeps_the_offers_nested_in_a_range() -> None:
    # The other half of the range decision: when an AggregateOffer does carry the
    # individual offers it summarizes, those are real prices someone can pay and
    # they must survive, even though the range around them is dropped.
    variants = extract_jsonld_variants(_AGGREGATE_OFFER)

    assert [v.price for v in variants] == [Decimal("149.90")]


def test_endpoint_reads_every_size_from_one_response() -> None:
    variants = extract_endpoint_variants(_ENDPOINT_RESPONSE, _ENDPOINT_CONFIG)

    assert [v.size_raw for v in variants] == ["3 ml", "5 ml"]
    assert [v.price for v in variants] == [Decimal("450.0"), Decimal("700.0")]
    assert [v.url for v in variants] == [
        "/urun/amouage-blossom-love-3-ml",
        "/urun/amouage-blossom-love-5-ml",
    ]
    # Stock arrives as a count, never as the word "stock". A zero count is the
    # only thing that means gone.
    assert [v.in_stock for v in variants] == [True, False]


def test_endpoint_without_a_field_map_reads_nothing() -> None:
    assert extract_endpoint_variants(_ENDPOINT_RESPONSE, {}) == ()


def test_embedded_attribute_reads_the_woocommerce_variation_table() -> None:
    variants = extract_embedded_variants(_fixture("luxurydekant"), _ATTRIBUTE_CONFIG)

    assert [v.size_raw for v in variants] == ["3ml", "5ml", "10ml", "30ml"]
    assert [v.price for v in variants] == [
        Decimal("180"),
        Decimal("270"),
        Decimal("530"),
        Decimal("1570"),
    ]
    # The same page's JSON-LD offers only the 180 and 1570 ends of the range. What
    # this rung adds is the two sizes in between, which is the whole reason the
    # ladder does not stop at the top rung.
    assert extract_jsonld_variants(_fixture("luxurydekant")) == ()


def test_embedded_attribute_reads_a_second_site_with_the_same_shape() -> None:
    variants = extract_embedded_variants(_fixture("ruxangroup"), _ATTRIBUTE_CONFIG)

    # "30mldekant" is kept exactly as written. Parsing it into millilitres and
    # deciding whether 100ml belongs in a decant comparison happens later, with
    # the profile's variant rules in hand.
    assert [v.size_raw for v in variants] == ["100ml", "10ml", "30mldekant", "5ml"]
    assert [v.price for v in variants] == [
        Decimal("2550"),
        Decimal("290"),
        Decimal("825"),
        Decimal("150"),
    ]


def test_embedded_marker_reads_a_blob_out_of_a_js_statement() -> None:
    variants = extract_embedded_variants(_fixture("venco"), _MARKER_CONFIG)

    # Sizes are the keys of the object, reachable only through "@key".
    assert [v.size_raw for v in variants] == ["1 ML", "2 ML", "3 ML", "5 ML", "10 ML"]
    assert [v.price for v in variants] == [
        Decimal("0.00"),
        Decimal("425.00"),
        Decimal("600.00"),
        Decimal("1000.00"),
        Decimal("0.00"),
    ]
    # The out-of-stock sizes stay in the table with the flag the page gave them,
    # and the page's JSON-LD knows about none of these prices: it carries the one
    # per-ml figure and nothing else.
    assert [v.in_stock for v in variants] == [False, True, True, True, False]
    assert len(extract_jsonld_variants(_fixture("venco"))) == 1


def test_embedded_json_island_reads_a_deeply_nested_variant_list() -> None:
    variants = extract_embedded_variants(_fixture("decantall"), _JSON_ISLAND_CONFIG)

    assert [v.size_raw for v in variants] == ["3 ml", "5 ml", "10 ml", "15 ml"]
    assert [v.price for v in variants] == [
        Decimal("360"),
        Decimal("600"),
        Decimal("1200"),
        Decimal("1800"),
    ]
    # This page's JSON-LD does list the same four prices, but its offers carry no
    # size label at all, so nothing there can be turned into a per-ml figure.
    # Same four numbers, and only this rung says which size each one buys.
    assert len(extract_jsonld_variants(_fixture("decantall"))) == 4


def test_embedded_marker_that_matches_nothing_reads_nothing() -> None:
    config = dict(_MARKER_CONFIG) | {"marker": r"NO_SUCH_GLOBAL\s*=\s*"}

    assert extract_embedded_variants(_fixture("venco"), config) == ()


def test_embedded_scan_is_not_ended_by_a_brace_inside_a_name() -> None:
    # A product name containing a brace, escaped quotes around it. Stopping at the
    # first "}" would truncate the blob and lose every size after this one.
    html = (
        "<html><body><script>var DATA = "
        '{"rows": [{"label": "3 ml {edition}", "amount": 180},'
        ' {"label": "5 ml", "amount": 270}]};'
        "\nmoreCode();</script></body></html>"
    )
    config = {
        "source": "script",
        "marker": r"DATA\s*=\s*",
        "variants_path": "rows",
        "field_map": {"size_raw": "label", "price": "amount", "in_stock": "n/a"},
    }

    variants = extract_embedded_variants(html, config)

    assert [v.size_raw for v in variants] == ["3 ml {edition}", "5 ml"]
    # "n/a" resolves to nothing, and an unreachable stock field is unknown rather
    # than out of stock.
    assert [v.in_stock for v in variants] == [None, None]


def test_css_reads_one_row_per_container() -> None:
    variants = extract_css_variants(_CSS_PAGE, _CSS_CONFIG)

    assert [v.size_raw for v in variants] == ["3 ml", "5 ml"]
    assert [v.price for v in variants] == [Decimal("180.00"), Decimal("270.00")]
    assert [v.sku for v in variants] == ["V3", "V5"]
    # The second row has no link, and that costs it only its url.
    assert [v.url for v in variants] == ["/urun/x-3-ml", None]
    assert [v.title for v in variants] == [None, None]


def test_css_without_a_container_reads_the_page_as_one_variant() -> None:
    html = '<html><body><h1 class="t">Tek Boy</h1></body></html>'

    (variant,) = extract_css_variants(html, {"title": ".t::text"})

    assert variant.title == "Tek Boy"
    assert variant.price is None
