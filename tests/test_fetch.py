"""Tests for parfum_finder.fetch.

httpx and curl_cffi are exercised against a real local HTTP server rather than
mocked, so a broken redirect-handling or response-decoding wire-up would actually
fail here. Playwright's browser automation is skipped when the optional browser
extra or the browser binary it drives is missing; its "clear error when missing"
behavior is tested separately via import injection.
"""

import sys

import pytest
from conftest import requires_playwright, requires_playwright_package

from parfum_finder.fetch import PlaywrightNoResponse, PlaywrightNotInstalled, fetch


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

    with pytest.raises(PlaywrightNotInstalled, match="browser extra"):
        await fetch("http://example.invalid", "playwright")


@requires_playwright_package
async def test_fetch_playwright_missing_browser_binary_raises_the_same_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Installing the extra but never running `playwright install` leaves an
    # importable package with no browser to drive. From the caller's side that
    # is the same "nothing here can work" condition as a missing extra, and it
    # has to abort just as loudly. Left as an ordinary error it would look like
    # the site was unreachable, and the strategy would be silently written off.
    # Pointing the browser path at nothing is how a real machine in that state
    # behaves, rather than asserting on a patched-in exception.
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", "/nonexistent/playwright-browsers")

    with pytest.raises(PlaywrightNotInstalled, match="playwright install chromium"):
        await fetch("http://example.invalid", "playwright")


@requires_playwright
async def test_fetch_playwright_returns_rendered_html(server_url: str) -> None:
    result = await fetch(f"{server_url}/page", "playwright")

    assert result.status_code == 200
    assert "ok" in result.html
    assert result.strategy == "playwright"


@requires_playwright
async def test_fetch_playwright_no_response_raises_its_own_error_type() -> None:
    # "about:blank" is a real target where playwright's own goto() returns no
    # Response object at all -- its own type, distinct from PlaywrightNotInstalled,
    # so probe() can tell "record this as a failed attempt" apart from "the
    # extra is missing, abort the whole run" without also catching unrelated bugs.
    with pytest.raises(PlaywrightNoResponse, match="produced no response"):
        await fetch("about:blank", "playwright")
