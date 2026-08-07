"""Extraction ladder: JSON-LD -> platform JSON endpoint -> embedded JS state -> CSS.

Structured data is always preferred over CSS selectors, in order of how well each
layer survives a site redesign. Discovery tries these top-down and records whichever
layer actually worked on that site's profile.

Only the JSON-LD rung exists so far. It reads the `application/ld+json` blocks of a
page and hands back a normalized view of every Product it finds, tolerating the
shapes real stores emit: a bare object, a root array, an "@graph" wrapper, products
buried under an ItemList entry's "item" key, "@type" as a string or a list, "offers"
as a single object or a list, an AggregateOffer carrying lowPrice/highPrice instead
of price, and the several spellings of the availability value.

Two deliberate non-goals here. Nothing in this module reads a site profile, because
JSON-LD is the one layer whose shape is fixed by a public vocabulary rather than by
the site. And nothing filters out non-decant listings (testers, full bottles, large
sizes). That filtering is profile-driven and belongs with the profile-driven search,
not with the raw read of what the page declares.

TODO: the remaining three rungs, plus profile-driven variant extraction and the
non-decant filter.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from selectolax.parser import HTMLParser

from parfum_finder.normalize import parse_price

_JSONLD_SELECTOR = 'script[type="application/ld+json"]'

# A price written as plain digits with at most one dot, the way schema.org asks for
# it. Such a value is already unambiguous, so it is read as-is instead of going
# through the price parser, whose job is the opposite one: guessing which separator
# convention a human-facing "1.250,00 TL" follows. That guess is wrong here. Given
# "1250.000" the parser sees a three-digit tail and reads it as a thousands group,
# turning 1250 into 1250000, while JSON-LD plainly means one thousand two hundred
# fifty. Strings with a currency symbol or two separators still fall back to the
# parser, because some feeds do emit display text in this field.
_PLAIN_NUMBER = re.compile(r"^\d+(\.\d+)?$")

# Availability values, matched on the last path segment of the value so that
# "https://schema.org/InStock", the http:// spelling and a bare "InStock" all land
# in the same bucket. Separators are stripped too, for the "in_stock" spelling.
_IN_STOCK_VALUES = frozenset(
    {"instock", "instoreonly", "onlineonly", "limitedavailability"}
)
_OUT_OF_STOCK_VALUES = frozenset({"outofstock", "soldout", "discontinued"})
# PreOrder, BackOrder and PreSale are intentionally in neither set. They describe an
# item that cannot be bought and shipped today but is not gone either, so forcing
# them into a yes/no answer would state something the page never said. They come
# back as None with the raw value kept.


@dataclass(frozen=True)
class JsonLdOffer:
    """One offer attached to a product.

    A plain Offer fills `price`. An AggregateOffer fills `low_price`/`high_price`
    and usually leaves `price` empty, so a reader that only knows about `price`
    would report "no price" for a page that advertises a whole range of them.

    `in_stock` is a tri-state on purpose: None means the page said nothing about
    availability, or said something this module does not recognize. Defaulting an
    unrecognized value to False would silently hide a product that is actually for
    sale, so the raw text is kept in `availability_raw` for a human to look at.
    """

    price: Decimal | None
    low_price: Decimal | None
    high_price: Decimal | None
    currency: str | None
    in_stock: bool | None
    availability_raw: str | None


@dataclass(frozen=True)
class JsonLdProduct:
    """One Product object as the page declares it.

    Variants stay nested rather than being flattened into the top-level result.
    The difference between "one product with five sizes" and "five separate
    products" is exactly the thing discovery has to find out about a site, and
    flattening would erase it: both would come back as five rows.
    """

    name: str | None
    url: str | None
    sku: str | None
    offers: tuple[JsonLdOffer, ...]
    variants: tuple[JsonLdProduct, ...]


def extract_jsonld_products(html: str) -> tuple[JsonLdProduct, ...]:
    """Read every JSON-LD Product declared on the page, in document order.

    A block that isn't valid JSON contributes nothing instead of aborting the
    page: stores routinely ship one broken block next to several good ones, and
    losing the good ones with it would be the worse outcome. An empty result is
    still the honest answer for a page whose only block is broken, and it makes
    the caller fall down to the next rung of the ladder rather than trust a
    half-read page.
    """
    products: list[JsonLdProduct] = []
    for node in HTMLParser(html).css(_JSONLD_SELECTOR):
        try:
            data = json.loads(node.text())
        except json.JSONDecodeError:
            continue
        _collect_products(data, products)
    return tuple(products)


def _collect_products(data: object, out: list[JsonLdProduct]) -> None:
    """Walk a parsed JSON-LD block and append every Product found, depth first.

    Descends through every nested value rather than only looking at "@graph" and
    root arrays, because listing pages put their products two levels down, under
    an ItemList entry's "item" key.

    Once a Product is reached the walk stops there instead of descending into it.
    Everything inside a Product that matters is read by _build_product, and
    descending further would re-report its own variants as separate top-level
    products, which is the distinction this module exists to preserve.
    """
    if isinstance(data, dict):
        if _has_type(data, "Product"):
            out.append(_build_product(data))
            return
        for value in data.values():
            _collect_products(value, out)
    elif isinstance(data, list):
        for item in data:
            _collect_products(item, out)


def _has_type(node: dict[str, object], name: str) -> bool:
    """Whether a node's "@type" names `name`, as a string or inside a list.

    Substring rather than equality, so the vocabulary's more specific product
    types ("ProductModel", "ProductGroup", "IndividualProduct") match too. Those
    are the types a store uses for exactly the variant-parent pages this project
    cares most about.
    """
    type_field = node.get("@type")
    if isinstance(type_field, str):
        return name in type_field
    if isinstance(type_field, list):
        return any(isinstance(t, str) and name in t for t in type_field)
    return False


def _build_product(node: dict[str, object]) -> JsonLdProduct:
    """Turn one Product node into a JsonLdProduct."""
    return JsonLdProduct(
        name=_as_str(node.get("name")),
        url=_as_str(node.get("url")),
        sku=_as_str(node.get("sku")),
        offers=_collect_offers(node.get("offers")),
        variants=_collect_variants(node.get("hasVariant")) + _sibling_variants(node),
    )


def _sibling_variants(node: dict[str, object]) -> tuple[JsonLdProduct, ...]:
    """Read the sizes listed by the parent group a product points back to.

    Some stores mark up a single size as the top-level Product and hang the rest
    of the range off "isVariantOf". Reading only hasVariant on the product itself
    would report one size and drop the others without a word, which is the exact
    way a wrong per-ml comparison gets built. The product itself is usually
    repeated inside that list, so a size can appear both as the product and as
    one of its own variants. Reporting one size twice is a much smaller problem
    than losing three.
    """
    parent = node.get("isVariantOf")
    if not isinstance(parent, dict):
        return ()
    return _collect_variants(parent.get("hasVariant"))


def _collect_variants(raw: object) -> tuple[JsonLdProduct, ...]:
    """Read a product's hasVariant entries.

    Every dict is accepted, whether or not it carries a "@type". A variant listed
    under hasVariant is already declared to be a product by its position, and
    plenty of feeds leave the type off the children while setting it on the
    parent. Requiring it would drop the sizes on exactly those pages.
    """
    if isinstance(raw, dict):
        return (_build_product(raw),)
    if isinstance(raw, list):
        return tuple(_build_product(item) for item in raw if isinstance(item, dict))
    return ()


def _collect_offers(raw: object) -> tuple[JsonLdOffer, ...]:
    """Read a product's "offers", which may be one object or a list of them.

    An AggregateOffer often nests the individual offers it summarizes under its
    own "offers" key. Those are flattened in next to the aggregate rather than
    dropped, so the per-variant prices survive alongside the range.
    """
    if isinstance(raw, dict):
        nested = _collect_offers(raw.get("offers"))
        return (_build_offer(raw), *nested)
    if isinstance(raw, list):
        offers: list[JsonLdOffer] = []
        for item in raw:
            offers.extend(_collect_offers(item))
        return tuple(offers)
    return ()


def _build_offer(node: dict[str, object]) -> JsonLdOffer:
    """Turn one Offer or AggregateOffer node into a JsonLdOffer."""
    availability = _as_str(node.get("availability"))
    return JsonLdOffer(
        price=_parse_price_value(node.get("price")),
        low_price=_parse_price_value(node.get("lowPrice")),
        high_price=_parse_price_value(node.get("highPrice")),
        currency=_as_str(node.get("priceCurrency")),
        in_stock=_parse_availability(availability),
        availability_raw=availability,
    )


def _parse_price_value(value: object) -> Decimal | None:
    """Read a JSON-LD price field, which may be a number or a string.

    Returns None when the field is missing or when nothing numeric can be read
    out of it. A missing price is not a zero price, and pretending otherwise
    would put a free product at the top of a cheapest-first ordering.
    """
    if isinstance(value, bool):
        # bool is an int subclass, so this has to be rejected before the numeric
        # branch, or a stray `true` would be read as a price of 1.
        return None
    if isinstance(value, int | float):
        return Decimal(str(value))
    if not isinstance(value, str):
        return None
    text = value.strip()
    if _PLAIN_NUMBER.match(text):
        return Decimal(text)
    try:
        return parse_price(text)
    except (ValueError, InvalidOperation):
        return None


def _parse_availability(value: str | None) -> bool | None:
    """Map an availability value to a yes/no answer, or None if it says neither."""
    if value is None:
        return None
    token = value.rsplit("/", 1)[-1].lower()
    token = re.sub(r"[\s_-]", "", token)
    if token in _IN_STOCK_VALUES:
        return True
    if token in _OUT_OF_STOCK_VALUES:
        return False
    return None


def _as_str(value: object) -> str | None:
    """Read a text field, accepting the numeric SKUs and prices feeds also emit.

    Anything else, a nested object for instance, comes back as None rather than
    as its repr, which would otherwise end up shown to the user as a product name.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return str(value)
    return None
