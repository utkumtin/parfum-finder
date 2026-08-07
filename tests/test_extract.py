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

from parfum_finder.extract import extract_jsonld_products

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
