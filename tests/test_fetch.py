"""Tests for parfum_finder.fetch.

httpx and curl_cffi are exercised against a real local HTTP server rather than
mocked, so a broken redirect-handling or response-decoding wire-up would actually
fail here. Playwright's browser automation is skipped when the optional browser
extra isn't installed (matches the documented `uv sync --extra browser` setup);
its "clear error when missing" behavior is tested separately via import injection.
"""

import importlib.util
import sys
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from parfum_finder.fetch import fetch

_PLAYWRIGHT_INSTALLED = importlib.util.find_spec("playwright") is not None


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/page")
            self.end_headers()
            return
        if self.path == "/page":
            body = b"<html><body>ok</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"not found")

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


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_fetch_returns_status_and_html(server_url: str, strategy: str) -> None:
    result = await fetch(f"{server_url}/page", strategy)  # type: ignore[arg-type]

    assert result.status_code == 200
    assert "ok" in result.html
    assert result.strategy == strategy


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_fetch_follows_redirects_to_final_url(
    server_url: str, strategy: str
) -> None:
    result = await fetch(f"{server_url}/redirect", strategy)  # type: ignore[arg-type]

    assert result.url == f"{server_url}/page"
    assert result.status_code == 200


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_fetch_reports_404_without_raising(
    server_url: str, strategy: str
) -> None:
    result = await fetch(f"{server_url}/missing", strategy)  # type: ignore[arg-type]

    assert result.status_code == 404


async def test_fetch_unknown_strategy_raises() -> None:
    with pytest.raises(ValueError, match="unknown fetch strategy"):
        await fetch("http://example.invalid", "bogus")  # type: ignore[arg-type]


async def test_fetch_playwright_missing_extra_raises_clear_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Simulate the optional browser extra not being installed, regardless of
    # whether it actually is in this environment: a None entry in sys.modules
    # makes the next import of that module raise ImportError. Both the top
    # package and the submodule are blanked out since a genuinely missing
    # extra fails on "playwright" itself, not just "playwright.async_api".
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.async_api", None)

    with pytest.raises(RuntimeError, match="browser extra"):
        await fetch("http://example.invalid", "playwright")


@pytest.mark.skipif(
    not _PLAYWRIGHT_INSTALLED, reason="playwright browser extra not installed"
)
async def test_fetch_playwright_returns_rendered_html(server_url: str) -> None:
    result = await fetch(f"{server_url}/page", "playwright")

    assert result.status_code == 200
    assert "ok" in result.html
    assert result.strategy == "playwright"
