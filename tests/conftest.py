"""Shared pytest fixtures.

A local HTTP server used by fetch/probe tests: real request/response wiring
against real httpx/curl_cffi/playwright clients, without any network dependency
or mocking away the libraries themselves.
"""

import asyncio
import importlib.util
import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import pytest

from parfum_finder.fetch import (
    DEFAULT_USER_AGENT,
    PlaywrightNoResponse,
    PlaywrightNotInstalled,
    fetch,
)


def _playwright_usable() -> bool:
    """Whether the playwright rung can actually run here, binary included.

    Checking that the package imports is not enough: `uv sync --extra browser`
    without `playwright install chromium` leaves an importable package with no
    browser to drive, and tests guarded on package presence alone would then
    fail instead of skipping. Driving one real fetch is the only honest check,
    so it runs once per session and every playwright-dependent test reuses it.
    """
    if importlib.util.find_spec("playwright") is None:
        return False
    try:
        asyncio.run(fetch("about:blank", "playwright", timeout_s=10))
    except PlaywrightNotInstalled:
        return False
    except PlaywrightNoResponse:
        # The one outcome a working setup produces here: about:blank reaches no
        # server, so the browser launches and navigates but yields no Response.
        # Anything else is left to propagate on purpose. Reporting a corrupt
        # install or a blocked process spawn as "usable" would skip nothing and
        # fail everything, which is the failure mode these guards exist to stop.
        return True
    return True


PLAYWRIGHT_PACKAGE_PRESENT = importlib.util.find_spec("playwright") is not None
PLAYWRIGHT_USABLE = _playwright_usable()

requires_playwright = pytest.mark.skipif(
    not PLAYWRIGHT_USABLE,
    reason="playwright is not usable here (extra or browser binary missing)",
)

# For the narrower case of a test that needs the package importable but wants
# the browser binary to be absent.
requires_playwright_package = pytest.mark.skipif(
    not PLAYWRIGHT_PACKAGE_PRESENT, reason="playwright browser extra not installed"
)

_PAGE_HTML = b"<html><body>ok</body></html>"

# A JSON-LD Product block plus a Shopify marker, for probe's diagnostics.
_PRODUCT_HTML = b"""<html><body>
<script type="application/ld+json">{"@type": "Product", "name": "Test Product"}</script>
<div>asset from cdn.shopify.com</div>
</body></html>"""

# The same Product, wrapped in JSON-LD's "@graph" array form instead of a bare
# object, alongside a non-Product object that must not be counted.
_PRODUCT_GRAPH_HTML = b"""<html><body>
<script type="application/ld+json">
{"@graph": [{"@type": "Product", "name": "Test Product"}, {"@type": "BreadcrumbList"}]}
</script>
</body></html>"""

# The other JSON-LD variation: a root array instead of an object wrapper.
_PRODUCT_ARRAY_HTML = b"""<html><body>
<script type="application/ld+json">
[{"@type": "Product", "name": "Test Product"}]
</script>
</body></html>"""

# The shape a category or search page normally uses: the real Products sit two
# levels down, under an ItemList entry's "item" key, so a counter that only
# looks at the top level of each block would report 0 here.
_PRODUCT_NESTED_HTML = b"""<html><body>
<script type="application/ld+json">
{"@type": "ItemList", "itemListElement": [
  {"@type": "ListItem", "position": 1, "item": {"@type": "Product", "name": "One"}},
  {"@type": "ListItem", "position": 2, "item": {"@type": "Product", "name": "Two"}}
]}
</script>
</body></html>"""

# Malformed JSON-LD: must be counted as a block but contribute 0 Product objects,
# not crash the fetch.
_PRODUCT_MALFORMED_HTML = b"""<html><body>
<script type="application/ld+json">{not valid json</script>
</body></html>"""

# A rendered listing with no JSON-LD at all, which is where the product-card
# count is the only evidence that a strategy got real content rather than an
# empty shell. Two cards, one written the Turkish way, and a nav link that must
# not be mistaken for a card.
_CARDS_HTML = b"""<html><body>
<a href="/hakkimizda">about</a>
<div class="product-card"><a href="/product/one">One</a></div>
<div class="urun-kart"><a href="/urun/iki">Iki</a></div>
</body></html>"""


# A product page that offers three sizes in a dropdown but states only one price
# in its structured data: the other two arrive by a later request that a plain
# fetch never makes. Discovery has to flag this, because reading it at face value
# compares this site's smallest size against another site's largest.
_VARIANT_SINGLE_PRICE_HTML = b"""<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Varyantli Parfum",
 "offers": {"@type": "Offer", "price": "149.90", "priceCurrency": "TRY"}}
</script>
<select class="variant-select" name="variant-id">
  <option value="1">5 ml</option>
  <option value="2">10 ml</option>
  <option value="3">20 ml</option>
</select>
</body></html>"""


# The opposite, healthy case: one product whose sizes and their prices are all
# stated on the page itself, so a plain fetch already sees every price per ml.
_VARIANT_PRICES_HTML = b"""<html><body>
<script type="application/ld+json">
{"@type": "ProductGroup", "name": "Tam Varyantli Parfum", "hasVariant": [
  {"name": "5 ml", "offers": {"@type": "Offer", "price": "149.90",
   "availability": "https://schema.org/InStock"}},
  {"name": "10 ml", "offers": {"@type": "Offer", "price": "279.90",
   "availability": "https://schema.org/OutOfStock"}}
]}
</script>
<select class="variant-select" name="variant-id">
  <option value="1">5 ml</option>
  <option value="2">10 ml</option>
</select>
</body></html>"""


# A WooCommerce variable product: four sizes, each with its own price, but the
# only prices in the structured data are the two ends of a range. The size
# control is a form whose class says "variation" and a select named
# attribute_pa_<attribute>, neither of which contains the word "variant".
_WOO_VARIATION_HTML = b"""<html><body>
<script type="application/ld+json">
{"@type": "Product", "name": "Woo Varyantli Parfum",
 "offers": {"@type": "AggregateOffer", "lowPrice": "180", "highPrice": "1570",
  "priceCurrency": "TRY"}}
</script>
<form class="variations_form cart" data-product_variations="[]">
  <select name="attribute_pa_hacim">
    <option value="3ml">3ml</option>
    <option value="5ml">5ml</option>
    <option value="10ml">10ml</option>
    <option value="30ml">30ml</option>
  </select>
</form>
</body></html>"""


# A search listing as the profile-driven engine has to read it: three rows, one
# of which has no link at all. That third row is what a theme's "no results,
# try these categories" box looks like, and following it would put a product in
# the table that can never carry a price.
_ENGINE_SEARCH_HTML = b"""<html><body>
<div class="card"><a href="engine-product">Test Parfum Dekant</a></div>
<div class="card"><a href="/engine-product">Test Parfum EDP Dekant</a></div>
<div class="card"><span>Kategoriye goz atin</span></div>
</body></html>"""

# A listing that names, as its one result's title, the path the request came in
# on. It turns "which URL did the caller build" into something a test can assert
# on without reaching into the server.
_ENGINE_ECHO_TEMPLATE = b"""<html><body>
<div class="card"><a href="/engine-product">%s</a></div>
</body></html>"""

# A listing off a mixed catalog: one decant product with a size table, one plain
# full bottle that has none. Both are ordinary rows on the same results page.
_ENGINE_SEARCH_MIXED_HTML = b"""<html><body>
<div class="card"><a href="/engine-product">Test Parfum Dekant</a></div>
<div class="card"><a href="/engine-product-bare">Test Parfum 100 ml Tam Sise</a></div>
</body></html>"""

# A listing whose titles name real brands, so a search run end to end has
# something the matcher can accept and something it has to reject. The second
# row is another house's bottle sitting on the same results page, which is what
# every shop's search returns for a common word.
_ENGINE_SEARCH_NAMED_HTML = b"""<html><body>
<div class="card"><a href="/engine-product">Dior Sauvage EDP Dekant</a></div>
<div class="card"><a href="/engine-product">Chanel Bleu EDP Dekant</a></div>
</body></html>"""

_ENGINE_SEARCH_CSS_HTML = b"""<html><body>
<div class="card"><a href="/engine-product-css">Test Parfum Dekant</a></div>
</body></html>"""

# A genuine "we don't stock that" page, with the chrome a real shop's no-results
# page carries: category links in the header and footer that name products, and a
# nav wrapper whose class does too. This is the false-positive case for the
# empty-vs-suspect check, so a bare <p> here would make that test unable to fail.
_ENGINE_SEARCH_EMPTY_HTML = b"""<html><body>
<nav class="urun-menu">
  <a href="/urun-kategori/erkek">Erkek Parfum</a>
  <a href="/urun-kategori/kadin">Kadin Parfum</a>
</nav>
<p>Aradiginiz urun bulunamadi.</p>
<footer><a href="/urun-kategori/niche">Niche</a></footer>
</body></html>"""

# The other no-results page, and the one that made the count above unusable on
# its own: a shop that runs its whole catalog through the header. The mega-menu
# alone is more product-shaped markup than a page of results carries, and every
# node of it is chrome. What separates it from a redesign is the body class the
# platform writes when a search matched nothing, which is the page answering the
# question directly.
_ENGINE_SEARCH_SAYS_EMPTY_HTML = b"""<html>
<body class="archive search search-no-results post-type-archive-product">
<nav class="urun-menu">
  <a class="product-cat-link" href="/urun-kategori/erkek">Erkek Parfum</a>
  <a class="product-cat-link" href="/urun-kategori/kadin">Kadin Parfum</a>
  <a class="product-cat-link" href="/urun-kategori/unisex">Unisex Parfum</a>
  <a class="product-cat-link" href="/urun-kategori/niche">Niche Parfum</a>
  <a class="product-cat-link" href="/urun-kategori/arabian">Arabian Parfum</a>
</nav>
<p class="woocommerce-info woocommerce-no-products-found">
  Aramanizla eslesen urun bulunamadi.
</p>
<aside class="product_list_widget">
  <div class="product-tile"><a class="product-link" href="/engine-product">Bir</a></div>
  <div class="product-tile"><a class="product-link" href="/engine-product">Iki</a></div>
  <div class="product-tile"><a class="product-link" href="/engine-product">Uc</a></div>
</aside>
</body></html>"""

# The same shop after a redesign renamed its result rows. Plenty of perfumes on
# the page, and the profile's ".card" matches none of them.
_ENGINE_SEARCH_RENAMED_HTML = b"""<html><body>
<div class="product-grid">
  <div class="product-tile">
    <a class="product-link" href="/engine-product">Test Parfum Dekant</a>
    <span class="product-price">250,00 TL</span>
  </div>
  <div class="product-tile">
    <a class="product-link" href="/engine-product">Baska Parfum Dekant</a>
    <span class="product-price">300,00 TL</span>
  </div>
  <div class="product-tile">
    <a class="product-link" href="/engine-product">Ucuncu Parfum Dekant</a>
    <span class="product-price">180,00 TL</span>
  </div>
</div>
</body></html>"""

# Rows still match, the link inside them moved. Every hit gets dropped for having
# no page to open.
_ENGINE_SEARCH_NO_LINKS_HTML = b"""<html><body>
<div class="card"><span>Test Parfum Dekant</span></div>
<div class="card"><span>Baska Parfum Dekant</span></div>
</body></html>"""

# A product page whose sizes live in an escaped JSON attribute, the shape two of
# the captured sites use.
_ENGINE_PRODUCT_HTML = b"""<html><body>
<h1>Test Parfum Dekant</h1>
<select name="attribute_pa_hacim">
  <option value="">Bir secim yapin</option>
  <option value="5ml">5 ml</option>
  <option value="10ml">10 ml</option>
</select>
<form class="variations_form"
      data-product_variations="[{&quot;attributes&quot;:{&quot;attribute_pa_hacim&quot;:&quot;5ml&quot;},&quot;display_price&quot;:150,&quot;is_in_stock&quot;:true},{&quot;attributes&quot;:{&quot;attribute_pa_hacim&quot;:&quot;10ml&quot;},&quot;display_price&quot;:290,&quot;is_in_stock&quot;:false}]">
</form>
</body></html>"""

# A page whose size picker and whose blob disagree: four sizes on offer, two of
# them priced. This is the shape one shop really shipped, and the one a table
# built from the blob alone shows as a complete answer.
_ENGINE_PRODUCT_HALF_HTML = b"""<html><body>
<h1>Test Parfum Dekant</h1>
<select name="attribute_pa_hacim">
  <option value="">Bir secim yapin</option>
  <option value="5ml">5 ml</option>
  <option value="10ml">10 ml</option>
  <option value="20ml">20 ml</option>
  <option value="30ml">30 ml</option>
</select>
<form class="variations_form"
      data-product_variations="[{&quot;attributes&quot;:{&quot;attribute_pa_hacim&quot;:&quot;5ml&quot;},&quot;display_price&quot;:150,&quot;is_in_stock&quot;:true},{&quot;attributes&quot;:{&quot;attribute_pa_hacim&quot;:&quot;10ml&quot;},&quot;display_price&quot;:290,&quot;is_in_stock&quot;:false}]">
</form>
</body></html>"""

_ENGINE_SEARCH_HALF_HTML = b"""<html><body>
<div class="card"><a href="/engine-product-half">Test Parfum Dekant</a></div>
</body></html>"""

# The same page after a redesign dropped the blob: reachable, plausible, and
# worth nothing. Reading this as "no sizes" is the silent-empty failure.
_ENGINE_PRODUCT_BARE_HTML = b"""<html><body>
<h1>Test Parfum Dekant</h1>
</body></html>"""

# The same product for a site whose sizes are only in the rendered markup, with
# no JSON anywhere: the last-resort layer.
_ENGINE_PRODUCT_CSS_HTML = b"""<html><body>
<h1>Test Parfum Dekant</h1>
<div class="size-row" data-sku="V5">
  <span class="ml">5 ml</span><span class="tl">150,00 TL</span>
  <span class="stok">Stokta</span>
</div>
<div class="size-row" data-sku="V10">
  <span class="ml">10 ml</span><span class="tl">290,00 TL</span>
  <span class="stok">Tukendi</span>
</div>
</body></html>"""

# Every size is its own product behind this endpoint, with its own name and its
# own page, which is why the field map can ask for them per size.
_ENGINE_PRODUCT_JSON = (
    b'{"variants": ['
    b'{"title": "5 ml", "price": 150, "available": true,'
    b' "name": "Test Parfum 5 ml", "url": "/urun/test-parfum-5-ml"},'
    b'{"title": "10 ml", "price": 290, "available": false,'
    b' "name": "Test Parfum 10 ml", "url": "/urun/test-parfum-10-ml"}]}'
)

# A results page whose only hit is that full bottle. The mixed listing above
# proves a sizeless page next to a decant is harmless; this is the case where it
# is the only thing the search found, which is what a shop that sells this
# perfume in one piece answers.
_ENGINE_SEARCH_BOTTLE_ONLY_HTML = b"""<html><body>
<div class="card"><a href="/engine-product-bare">Test Parfum 100 ml Tam Sise</a></div>
</body></html>"""

# A listing pointing at the POST-endpoint product page below.
_ENGINE_SEARCH_POST_ENDPOINT_HTML = b"""<html><body>
<div class="card"><a href="/engine-product-post-endpoint">Test Parfum Dekant</a></div>
</body></html>"""

# The same listing plus a plain full bottle: no size list, no option ids, no
# product id to post with. This shop really does sell those next to its decants.
_ENGINE_SEARCH_POST_ENDPOINT_MIXED_HTML = b"""<html><body>
<div class="card"><a href="/engine-product-post-endpoint">Test Parfum Dekant</a></div>
<div class="card"><a href="/engine-product-bare">Test Parfum EDP 200 ML</a></div>
</body></html>"""

# The markup an ideasoft-shaped product page carries: a product id on the
# add-to-cart button, a group id on the variant list, and one span per size
# option with its own option id. Nothing here declares a price or a stock
# count; those only exist behind the POST endpoint below, one request per
# option id found here.
_ENGINE_PRODUCT_POST_ENDPOINT_HTML = b"""<html><body>
<h1>Test Parfum Dekant</h1>
<a class="add-to-cart-button" data-context="detail"
   data-product-id="900">Sepete Ekle</a>
<div class="variant-list-group" data-group-id="1">
  <span class="variant-text" data-option-id="10">5 ml</span>
  <span class="variant-text" data-option-id="20">10 ml</span>
</div>
</body></html>"""

# The same product page after the shop ran out of it: every size still listed,
# the add-to-cart button gone and a "notify me" button in its place. The product
# id the POST body needs lived on that button, so the page now names its sizes
# and nothing that can be asked about them.
_ENGINE_PRODUCT_POST_ENDPOINT_SOLD_OUT_HTML = b"""<html><body>
<h1>Test Parfum Dekant</h1>
<a class="remind-me-button" data-selector="stock-warning">Gelince Haber Ver</a>
<div class="variant-list-group" data-group-id="1">
  <span class="variant-text variant-no-stock" data-option-id="10">5 ml</span>
  <span class="variant-text variant-no-stock" data-option-id="20">10 ml</span>
</div>
</body></html>"""

_ENGINE_SEARCH_POST_ENDPOINT_SOLD_OUT_HTML = b"""<html><body>
<div class="card">
  <a href="/engine-product-post-endpoint-sold-out">Test Parfum Dekant</a>
</div>
</body></html>"""

# What the POST endpoint answers per option id, keyed the same way the do_POST
# handler below looks them up. Shaped like the real ideasoft response: a
# "sale_price" that is the field actually shown to a buyer, and a "price" that
# is not (its ideasoft's tax-exclusive figure, unused here).
_ENGINE_POST_ENDPOINT_OPTIONS = {
    "10": {
        "option_id": 10,
        "option_title": "5 ml",
        "product_price": {"price": 125.0, "sale_price": 150.0},
        "product_stock_amount": 12,
        "product_name": "Test Parfum 5 ml",
        "product_url": "/urun/test-parfum-5-ml",
        "product_sku": "SKU5",
    },
    "20": {
        "option_id": 20,
        "option_title": "10 ml",
        "product_price": {"price": 241.67, "sale_price": 290.0},
        "product_stock_amount": 0,
        "product_name": "Test Parfum 10 ml",
        "product_url": "/urun/test-parfum-10-ml",
        "product_sku": "SKU10",
    },
}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path.startswith("/engine-redirect-search"):
            self.send_response(302)
            self.send_header("Location", "/shop/engine-search")
            self.end_headers()
            return
        if self.path.startswith("/engine-search-mixed"):
            self._send(200, _ENGINE_SEARCH_MIXED_HTML)
            return
        if self.path.startswith("/engine-search-named"):
            self._send(200, _ENGINE_SEARCH_NAMED_HTML)
            return
        if self.path.startswith("/engine-search-css"):
            self._send(200, _ENGINE_SEARCH_CSS_HTML)
            return
        if self.path.startswith("/engine-search-half"):
            self._send(200, _ENGINE_SEARCH_HALF_HTML)
            return
        if self.path.startswith("/engine-search-empty"):
            self._send(200, _ENGINE_SEARCH_EMPTY_HTML)
            return
        if self.path.startswith("/engine-search-says-empty"):
            self._send(200, _ENGINE_SEARCH_SAYS_EMPTY_HTML)
            return
        if self.path.startswith("/engine-search-bottle-only"):
            self._send(200, _ENGINE_SEARCH_BOTTLE_ONLY_HTML)
            return
        if self.path.startswith("/engine-search-renamed"):
            self._send(200, _ENGINE_SEARCH_RENAMED_HTML)
            return
        if self.path.startswith("/engine-search-no-links"):
            self._send(200, _ENGINE_SEARCH_NO_LINKS_HTML)
            return
        if self.path.startswith("/engine-search-post-endpoint-sold-out"):
            self._send(200, _ENGINE_SEARCH_POST_ENDPOINT_SOLD_OUT_HTML)
            return
        if self.path.startswith("/engine-search-post-endpoint-mixed"):
            self._send(200, _ENGINE_SEARCH_POST_ENDPOINT_MIXED_HTML)
            return
        if self.path.startswith("/engine-search-post-endpoint"):
            self._send(200, _ENGINE_SEARCH_POST_ENDPOINT_HTML)
            return
        if self.path.startswith(("/engine-search", "/shop/engine-search")):
            self._send(200, _ENGINE_SEARCH_HTML)
            return
        if self.path.startswith("/engine-echo"):
            # A listing whose one row is titled with the path this request
            # arrived on, so a test can read back the URL the caller built.
            self._send(200, _ENGINE_ECHO_TEMPLATE % self.path.encode())
            return
        if self.path == "/engine-product.js":
            self._send(200, _ENGINE_PRODUCT_JSON)
            return
        if self.path in ("/engine-product", "/shop/engine-product"):
            self._send(200, _ENGINE_PRODUCT_HTML)
            return
        if self.path == "/engine-product-css":
            self._send(200, _ENGINE_PRODUCT_CSS_HTML)
            return
        if self.path == "/engine-product-half":
            self._send(200, _ENGINE_PRODUCT_HALF_HTML)
            return
        if self.path == "/engine-product-bare":
            self._send(200, _ENGINE_PRODUCT_BARE_HTML)
            return
        if self.path == "/engine-product-post-endpoint-sold-out":
            self._send(200, _ENGINE_PRODUCT_POST_ENDPOINT_SOLD_OUT_HTML)
            return
        if self.path == "/engine-product-post-endpoint":
            self._send(200, _ENGINE_PRODUCT_POST_ENDPOINT_HTML)
            return
        if self.path == "/header-echo":
            # Reports one request header back as the body, so a test can assert
            # on what actually went out rather than on what was passed in.
            seen = self.headers.get("X-Requested-With", "absent")
            self._send(200, f"<html><body>{seen}</body></html>".encode())
            return
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/page")
            self.end_headers()
            return
        if self.path == "/page":
            self._send(200, _PAGE_HTML)
            return
        if self.path == "/product":
            self._send(200, _PRODUCT_HTML)
            return
        if self.path == "/product-graph":
            self._send(200, _PRODUCT_GRAPH_HTML)
            return
        if self.path == "/product-array":
            self._send(200, _PRODUCT_ARRAY_HTML)
            return
        if self.path == "/product-nested":
            self._send(200, _PRODUCT_NESTED_HTML)
            return
        if self.path == "/product-malformed":
            self._send(200, _PRODUCT_MALFORMED_HTML)
            return
        if self.path == "/variant-prices":
            self._send(200, _VARIANT_PRICES_HTML)
            return
        if self.path == "/woo-variation":
            self._send(200, _WOO_VARIATION_HTML)
            return
        if self.path == "/variant-single-price":
            self._send(200, _VARIANT_SINGLE_PRICE_HTML)
            return
        if self.path == "/cards":
            self._send(200, _CARDS_HTML)
            return
        if self.path == "/blocks-plain-ua":
            # Stands in for the bot protection probe exists to measure: reject
            # our own declared user agent, serve everyone else. httpx and
            # playwright both send DEFAULT_USER_AGENT and get turned away, while
            # curl_cffi impersonates a real Chrome and gets through, so one
            # report ends up with a mix of failing and succeeding rungs.
            if self.headers.get("User-Agent") == DEFAULT_USER_AGENT:
                self._send(403, b"<html><body>forbidden</body></html>")
            else:
                self._send(200, _PRODUCT_HTML)
            return
        self._send(404, b"not found")

    def do_POST(self) -> None:
        if self.path == "/engine-related-options":
            length = int(self.headers.get("Content-Length", 0))
            fields = parse_qs(self.rfile.read(length).decode())
            # The real endpoint answers one option at a time; a request naming
            # an id outside the two above gets an empty list back, the same as
            # the live site does for an id it does not recognize.
            option_id = fields.get("selected_options[]", [""])[0]
            option = _ENGINE_POST_ENDPOINT_OPTIONS.get(option_id)
            options = [option] if option is not None else []
            body = json.dumps({"success": True, "data": {"options": options}}).encode()
            self._send(200, body)
            return
        self._send(404, b"not found")

    def _send(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        pass  # keep test output clean, the server's own logging isn't under test


@pytest.fixture
def server_url() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        thread.join()
