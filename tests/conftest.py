"""Shared pytest fixtures.

A local HTTP server used by fetch/probe tests: real request/response wiring
against real httpx/curl_cffi/playwright clients, without any network dependency
or mocking away the libraries themselves.
"""

import asyncio
import importlib.util
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
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
