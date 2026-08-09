"""Extraction ladder: JSON-LD -> platform JSON endpoint -> embedded JS state -> CSS.

Structured data is always preferred over CSS selectors, in order of how well each
layer survives a site redesign. Discovery tries these top-down and records whichever
layer actually worked on that site's profile.

The JSON-LD rung reads the `application/ld+json` blocks of a page, tolerating the
shapes real stores emit: a bare object, a root array, an "@graph" wrapper, products
buried under an ItemList entry's "item" key, "@type" as a string or a list, "offers"
as a single object or a list, an AggregateOffer carrying lowPrice/highPrice instead
of price, and the several spellings of the availability value. The three lower rungs
are profile driven: where the JSON hides and which key holds which field differ per
site, so each takes a config block naming those.

All four rungs hand back the same `RawVariant` rows, so a caller can walk the ladder
without knowing which layer answered. The rows are raw on purpose: `size_raw` keeps
the site's own label ("2,7 ml - metal sprey", "30mldekant") instead of a parsed
number, because turning that into millilitres and dropping the non-decant rows is
profile-driven and belongs with the profile-driven search, not with the raw read of
what the page declares.

Two deliberate non-goals here. Nothing in this module performs I/O: the endpoint rung
takes an already-parsed JSON document rather than fetching it, because the request
that produces it is not always a GET (one platform needs a POST whose body is built
from attributes on the product page). And nothing filters out non-decant listings
(testers, full bottles, large sizes).
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from selectolax.parser import HTMLParser, Node

from parfum_finder.normalize import parse_price

# The ladder itself, most durable first, in the order a profile's `extraction`
# field is allowed to name. Kept here rather than beside either caller because
# both the engine, which dispatches on it, and validate, which walks it to say
# what a broken profile could still fall back to, need the same four names in
# the same order, and two copies of them would drift apart unnoticed.
EXTRACTION_LAYERS = ("jsonld", "endpoint", "embedded_json", "css")

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


# Selector suffixes borrowed from the scrapy convention the profile schema already
# writes: ".product-title::text" reads the node's text, "a::attr(href)" reads one of
# its attributes. A selector with neither suffix reads the text too, since that is
# what a person writing ".price" means.
_TEXT_SUFFIX = "::text"
_ATTR_SUFFIX = re.compile(r"::attr\(([^)]+)\)$")

# In a field map, this stands for the key a variant sits under rather than a field
# inside it. One store keys its size table by the label itself
# ({"1 ML": {...}, "2 ML": {...}}), so without this the size would be unreachable.
_KEY_TOKEN = "@key"

_TRUE_WORDS = frozenset({"true", "yes", "1", "instock", "in stock", "available"})
_FALSE_WORDS = frozenset(
    {"false", "no", "0", "outofstock", "out of stock", "unavailable"}
)


@dataclass(frozen=True)
class RawVariant:
    """One buyable size of one product, exactly as the page or feed states it.

    This is what every rung returns, so the caller can try the layers in order
    without branching on which one answered.

    `size_raw` is the site's own label, unparsed. `price` is a Decimal because the
    number is the one thing worth reading strictly here. `in_stock` stays tri-state
    for the same reason it is tri-state on an offer: None means the source said
    nothing, and calling that "out of stock" would hide a product that is for sale.
    """

    title: str | None
    url: str | None
    sku: str | None
    size_raw: str | None
    price: Decimal | None
    in_stock: bool | None


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


def extract_jsonld_variants(html: str) -> tuple[RawVariant, ...]:
    """Rung 1: read the page's JSON-LD as flat variant rows.

    A product that declares sizes contributes one row per size and none for
    itself, because the price on such a parent is usually a per-unit or
    starting-from figure rather than something anyone can buy.

    An AggregateOffer that only carries a lowPrice/highPrice range contributes
    nothing. The range names two of the sizes and stays silent about the ones in
    between, so treating either end as a variant price would state a size/price
    pairing the page never made. No rows is the answer that makes the caller drop
    to the next rung instead of trusting two numbers out of four.

    Exact duplicate rows are collapsed. A product that points back at its own
    parent group appears twice, once as itself and once inside that group's size
    list, and the same size listed twice would double a basket total.
    """
    seen: dict[RawVariant, None] = {}
    for product in extract_jsonld_products(html):
        for variant in _flatten_jsonld(product):
            seen.setdefault(variant)
    return tuple(seen)


def _flatten_jsonld(product: JsonLdProduct) -> Iterator[RawVariant]:
    """Turn one Product and everything under it into rows."""
    if product.variants:
        for variant in product.variants:
            yield from _flatten_jsonld(variant)
        return
    for offer in product.offers:
        if offer.price is None:
            continue
        yield RawVariant(
            title=product.name,
            url=product.url,
            sku=product.sku,
            size_raw=None,
            price=offer.price,
            in_stock=offer.in_stock,
        )


def extract_endpoint_variants(
    document: object, config: Mapping[str, Any]
) -> tuple[RawVariant, ...]:
    """Rung 2: read the variant list out of a platform's JSON response.

    `document` is already parsed and already fetched. The request that produces it
    is platform-specific and not always a GET, so building it is the fetch layer's
    job; everything from the parsed body onwards is the same work as the embedded
    rung and shares its implementation.

    `config` is the profile's `endpoint` block: `variants_path` locates the list
    inside the response, `field_map` names where each field sits inside one entry.
    """
    return _variants_from_document(document, config)


def extract_embedded_variants(
    html: str, config: Mapping[str, Any]
) -> tuple[RawVariant, ...]:
    """Rung 3: read the JSON blob the page carries but does not display.

    Two shapes of hiding place, told apart by `config["source"]`:

    "script" reads a `<script>` body. With a `marker` regex it scans forward from
    the match to the first brace or bracket and takes the balanced value that
    starts there, which is how a JS assignment (`var DATA = {...}`) gives up its
    payload without the surrounding statement having to be valid JSON. Without a
    marker the whole body is parsed, which is what a `<script type="application/
    json">` island needs.

    "attribute" reads an attribute value, the form used by shops that stash the
    entire variant table in something like `data-product_variations`.

    The first hiding place that yields rows wins. A page carries one variant
    table, and a script that happens to parse as JSON without matching the field
    map is not it, so the scan continues past it rather than reporting nothing.
    """
    for document in _embedded_documents(html, config):
        variants = _variants_from_document(document, config)
        if variants:
            return variants
    return ()


def extract_css_variants(
    html: str, config: Mapping[str, Any]
) -> tuple[RawVariant, ...]:
    """Rung 4: read the rendered markup with selectors. Last resort.

    `config["variant_container"]` selects one node per size; the remaining keys
    (`title`, `url`, `sku`, `size_raw`, `price`, `in_stock`) are selectors looked
    up inside each of those nodes. Without a container the whole document is read
    as a single variant, which is what a one-size product page is.

    A selector that matches nothing yields None for that field rather than
    dropping the row. Which missing field makes a row untrustworthy is a policy
    question, and answering it here would hide the row from the code whose job is
    to flag it.
    """
    tree = HTMLParser(html)
    container = config.get("variant_container")
    nodes = tree.css(container) if container else [tree.root]
    return tuple(_css_variant(node, config) for node in nodes if node is not None)


def _css_variant(node: Node, config: Mapping[str, Any]) -> RawVariant:
    """Read one variant's fields out of its container node."""
    return RawVariant(
        title=select_field(node, config.get("title")),
        url=select_field(node, config.get("url")),
        sku=select_field(node, config.get("sku")),
        size_raw=select_field(node, config.get("size_raw")),
        price=_parse_price_value(select_field(node, config.get("price"))),
        in_stock=_coerce_in_stock(select_field(node, config.get("in_stock"))),
    )


def select_field(node: Node, selector: str | None) -> str | None:
    """Run one "<css>::text" / "<css>::attr(name)" selector inside a node.

    The node itself is a candidate, not just its descendants: on a page where the
    container already is the price element, a selector meant to read it would
    otherwise find nothing.

    Public because reading a search result row needs exactly the same thing, and
    two copies of this would be two places for the two selector spellings to
    drift apart.
    """
    if not selector:
        return None
    css, attribute = _parse_selector(selector)
    found = node.css_first(css) if css else node
    return _read_selected(found, attribute)


def select_all(node: Node, selector: str | None) -> tuple[str, ...]:
    """Run one "<css>::text" / "<css>::attr(name)" selector, reading every match.

    Same selector syntax as `select_field`, but for the case where a page lists
    several equivalent things at once rather than one field once: a platform
    endpoint driven by POST needs the id of every selectable size option on a
    product page, not just the first, to know how many requests to make.
    """
    if not selector:
        return ()
    css, attribute = _parse_selector(selector)
    if not css:
        return ()
    values = (_read_selected(found, attribute) for found in node.css(css))
    return tuple(value for value in values if value is not None)


def _parse_selector(selector: str) -> tuple[str, str]:
    """Split a "<css>::text" / "<css>::attr(name)" selector into its two parts."""
    attr_match = _ATTR_SUFFIX.search(selector)
    if attr_match is not None:
        css, attribute = selector[: attr_match.start()], attr_match.group(1)
    else:
        css = selector.removesuffix(_TEXT_SUFFIX)
        attribute = ""
    return css.strip(), attribute


def _read_selected(found: Node | None, attribute: str) -> str | None:
    """Read the attribute or text of one already-selected node, or None."""
    if found is None:
        return None
    if attribute:
        value = found.attributes.get(attribute)
        return value.strip() if value else None
    text = found.text(deep=True).strip()
    return text or None


def _embedded_documents(html: str, config: Mapping[str, Any]) -> Iterator[object]:
    """Yield every JSON document the page hides, in document order."""
    tree = HTMLParser(html)
    source = config.get("source")
    selector = config.get("selector")
    if source == "attribute":
        attribute = config.get("attribute")
        if not selector or not attribute:
            return
        for node in tree.css(selector):
            raw = node.attributes.get(attribute)
            if raw:
                yield from _loads_or_skip(raw)
        return
    marker = config.get("marker")
    for node in tree.css(selector or "script"):
        text = node.text()
        if marker:
            match = re.search(marker, text)
            if match is None:
                continue
            text = _balanced_value(text, match.end())
        yield from _loads_or_skip(text)


def _loads_or_skip(text: str) -> Iterator[object]:
    """Parse `text` as JSON, yielding nothing when it isn't JSON.

    Pages are full of script bodies that are not JSON at all, so a parse failure
    here is the normal case rather than an error worth raising.
    """
    if not text:
        return
    try:
        yield json.loads(text)
    except json.JSONDecodeError:
        return


def _balanced_value(text: str, start: int) -> str:
    """Return the JSON object or array beginning at or after `start`.

    Scanning for the matching close brace, rather than to the end of the line or
    the script, is what lets the payload be pulled out of a JS statement whose
    remainder ("};" plus another hundred lines of code) is not JSON. Braces inside
    string literals do not count, or a product name containing one would end the
    scan early.
    """
    opening = {"{": "}", "[": "]"}
    for index in range(start, len(text)):
        if text[index] in opening:
            break
    else:
        return ""
    close = opening[text[index]]
    depth = 0
    in_string = False
    escaped = False
    for cursor in range(index, len(text)):
        char = text[cursor]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == text[index]:
            depth += 1
        elif char == close:
            depth -= 1
            if depth == 0:
                return text[index : cursor + 1]
    return ""


def _variants_from_document(
    document: object, config: Mapping[str, Any]
) -> tuple[RawVariant, ...]:
    """Read variant rows out of a parsed JSON document.

    Shared by the endpoint and embedded rungs: once the JSON is in hand, the two
    differ only in where it came from.

    The variant container may be a list or an object keyed by the size label. Both
    are walked the same way, with the key handed along so a field map can ask for
    it by name.
    """
    field_map = config.get("field_map")
    if not isinstance(field_map, Mapping):
        return ()
    container = _resolve_path(document, config.get("variants_path"))
    if isinstance(container, Mapping):
        entries = list(container.items())
    elif isinstance(container, list):
        entries = [(None, item) for item in container]
    else:
        return ()
    return tuple(
        _map_variant(key, item, field_map)
        for key, item in entries
        if isinstance(item, Mapping)
    )


def _map_variant(
    key: str | None, item: Mapping[str, Any], field_map: Mapping[str, Any]
) -> RawVariant:
    """Turn one entry of a variant container into a row, following the field map."""

    def read(field: str) -> object:
        path = field_map.get(field)
        if not isinstance(path, str):
            return None
        if path == _KEY_TOKEN:
            return key
        return _resolve_path(item, path)

    return RawVariant(
        title=_as_str(read("title")),
        url=_as_str(read("url")),
        sku=_as_str(read("sku")),
        size_raw=_as_str(read("size_raw")),
        price=_parse_price_value(read("price")),
        in_stock=_coerce_in_stock(read("in_stock")),
    )


def _resolve_path(data: object, path: object) -> object:
    """Follow a dotted path into parsed JSON, e.g. "data.options.0.price".

    A segment made of digits indexes a list, so the single-element wrappers these
    feeds put around prices and stock counts can be reached without a second kind
    of syntax. An empty or missing path means the document itself, which is what a
    response whose whole body is the variant list needs.

    Anything unreachable comes back as None instead of raising. A feed dropping a
    field is a routine event, and the row is still worth reporting with that one
    field empty.
    """
    if not isinstance(path, str) or not path:
        return data
    current = data
    for segment in path.split("."):
        if isinstance(current, Mapping):
            current = current.get(segment)
        elif isinstance(current, list) and segment.isdigit():
            index = int(segment)
            current = current[index] if index < len(current) else None
        else:
            return None
    return current


def _coerce_in_stock(value: object) -> bool | None:
    """Read an availability field written as a flag, a count or a word.

    Counts are common: a feed says `stockCount: 2` or `product_stock_amount: 0`
    and never says the word "stock" anywhere. Zero means gone, anything above it
    means buyable.

    An unrecognized value comes back as None. Anything else amounts to guessing
    about the one field that decides whether a price is real.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return value > 0
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text in _TRUE_WORDS:
        return True
    if text in _FALSE_WORDS:
        return False
    return _parse_availability(value)


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
