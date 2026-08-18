"""Tests for parfum_finder.fetch.

httpx and curl_cffi are exercised against a real local HTTP server rather than
mocked, so a broken redirect-handling or response-decoding wire-up would actually
fail here. Playwright's browser automation is skipped when the optional browser
extra or the browser binary it drives is missing; its "clear error when missing"
behavior is tested separately via import injection.
"""

import asyncio
import sys
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

import pytest
from conftest import requires_playwright, requires_playwright_package

from parfum_finder import fetch as fetch_module
from parfum_finder.fetch import (
    PlaywrightNoResponse,
    PlaywrightNotInstalled,
    browser_session,
    fetch,
)


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
    # The message has to name the valid strategies, not just the bad value,
    # or a typo in a site profile gives no hint what to write instead.
    with pytest.raises(
        ValueError, match="unknown fetch strategy.*httpx.*curl_cffi.*playwright"
    ):
        await fetch("http://example.invalid", "bogus")  # type: ignore[arg-type]


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_fetch_post_sends_the_form_body(server_url: str, strategy: str) -> None:
    result = await fetch(
        f"{server_url}/engine-related-options",
        strategy,  # type: ignore[arg-type]
        method="POST",
        data={"selected_options[]": "10"},
    )

    assert result.status_code == 200
    assert '"option_id": 10' in result.html


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_fetch_post_with_no_matching_id_still_answers(
    server_url: str, strategy: str
) -> None:
    # An id the endpoint does not recognize is not a network failure, it is an
    # empty answer, same as the real site gives for an id it has never heard of.
    result = await fetch(
        f"{server_url}/engine-related-options",
        strategy,  # type: ignore[arg-type]
        method="POST",
        data={"selected_options[]": "does-not-exist"},
    )

    assert result.status_code == 200
    assert '"options": []' in result.html


async def test_fetch_playwright_post_raises_not_implemented() -> None:
    # No target needs a browser-driven form POST, so this is left unbuilt
    # rather than guessed at.
    with pytest.raises(NotImplementedError, match="does not support method 'POST'"):
        await fetch("http://example.invalid", "playwright", method="POST")


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


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_profile_headers_reach_the_server(server_url: str, strategy: str) -> None:
    # One platform's variant endpoint answers 200 with an empty body unless the
    # request carries this header, which no saved fixture can ever show: a
    # capture taken in a browser already has it. Both HTTP strategies have to
    # carry it, since which one a site needs is a separate measurement.
    result = await fetch(
        f"{server_url}/header-echo",
        strategy,  # type: ignore[arg-type]
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert "XMLHttpRequest" in result.html


@pytest.mark.parametrize("strategy", ["httpx", "curl_cffi"])
async def test_no_headers_asked_for_means_none_sent(
    server_url: str, strategy: str
) -> None:
    # The header changes how some sites answer, so it must not appear on its
    # own: the same platform serves 404 for a search page requested this way.
    result = await fetch(f"{server_url}/header-echo", strategy)  # type: ignore[arg-type]

    assert "absent" in result.html


class _FakePage:
    def __init__(self, html: str) -> None:
        self._html = html
        self.closed = False

    # Playwright's own signature, and what the session passes it. Named
    # differently here only because the linter reads a "timeout" argument on an
    # async def as a missed asyncio.timeout.
    async def goto(self, url: str, **_: Any) -> Any:
        self.url = url
        return SimpleNamespace(url=url, status=200)

    async def content(self) -> str:
        return self._html

    async def close(self) -> None:
        self.closed = True


class _FakeBrowser:
    def __init__(self) -> None:
        self.pages: list[_FakePage] = []
        self.closed = False
        # The driver is a second process, stopped separately from the browser.
        self.driver_stopped = False

    async def new_page(self, **_: Any) -> _FakePage:
        page = _FakePage("<html><body>rendered</body></html>")
        self.pages.append(page)
        return page

    async def close(self) -> None:
        self.closed = True


def _fake_launch(
    monkeypatch: pytest.MonkeyPatch,
    browser_factory: Callable[[], _FakeBrowser] = _FakeBrowser,
) -> list[_FakeBrowser]:
    """Stand in for the browser process, and count how many were started."""
    started: list[_FakeBrowser] = []

    async def launch() -> tuple[Any, Any]:
        browser = browser_factory()
        started.append(browser)

        async def stop() -> None:
            browser.driver_stopped = True

        return SimpleNamespace(stop=stop), browser

    monkeypatch.setattr(fetch_module, "_launch_browser", launch)
    return started


async def test_a_session_never_starts_a_browser_it_does_not_need(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One shop of six needs a browser. A session that launched one up front would
    # make every other scan pay for it, and would stop working entirely on a
    # machine with no browser installed.
    started = _fake_launch(monkeypatch)

    async with browser_session() as fetcher:
        result = await fetcher(f"{server_url}/page", "httpx")

    assert result.strategy == "httpx"
    assert started == []


async def test_every_page_of_a_session_shares_one_browser(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The whole point: launching a chromium takes seconds and reading a page
    # takes a fraction of one, so ten perfumes must not cost ten launches.
    started = _fake_launch(monkeypatch)

    async with browser_session() as fetcher:
        first = await fetcher(f"{server_url}/page", "playwright")
        second = await fetcher(f"{server_url}/page", "playwright")

    assert first.html == second.html == "<html><body>rendered</body></html>"
    assert len(started) == 1
    # A page each, all closed: a page holds one request's cookies and headers,
    # and that is the part of a per-fetch browser worth keeping.
    assert len(started[0].pages) == 2
    assert all(page.closed for page in started[0].pages)


async def test_a_session_closes_the_browser_it_started(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A browser left running outlives the scan that wanted it, and nothing else
    # in the app would ever close it.
    started = _fake_launch(monkeypatch)

    async with browser_session() as fetcher:
        await fetcher(f"{server_url}/page", "playwright")

    assert started[0].closed


async def test_a_session_closes_the_browser_when_the_scan_blows_up(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    started = _fake_launch(monkeypatch)

    with pytest.raises(RuntimeError, match="scan died"):
        async with browser_session() as fetcher:
            await fetcher(f"{server_url}/page", "playwright")
            raise RuntimeError("scan died")

    assert started[0].closed


async def _read_one_page_then_hang(
    server_url: str, reading_done: asyncio.Event
) -> None:
    async with browser_session() as fetcher:
        await fetcher(f"{server_url}/page", "playwright")
        reading_done.set()
        await asyncio.Event().wait()


async def test_a_session_closes_the_browser_when_the_scan_is_cancelled(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Cancellation is the ordinary way a scan ends early: someone starts
    # another search, or closes the window. Both the browser and the driver
    # behind it are processes, and nothing else in the app knows they exist.
    started = _fake_launch(monkeypatch)
    reading_done = asyncio.Event()

    task = asyncio.create_task(_read_one_page_then_hang(server_url, reading_done))
    await reading_done.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert started[0].closed
    assert started[0].driver_stopped


async def test_a_session_finishes_a_close_that_is_cancelled_again(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Closing the window cancels the scan, and the shutdown behind it can
    # cancel again while the browser is still going down. Returning at that
    # point leaves the close half-run in a task nobody waits for, and the app
    # is on its way out: the loop stops first and the browser survives the
    # process. So what matters is not that the close eventually happens, it is
    # that it has happened by the time the session's teardown returns.
    closing = asyncio.Event()
    let_it_close = asyncio.Event()

    class _SlowBrowser(_FakeBrowser):
        async def close(self) -> None:
            closing.set()
            await let_it_close.wait()
            await super().close()

    started = _fake_launch(monkeypatch, _SlowBrowser)
    reading_done = asyncio.Event()
    done_on_teardown: list[bool] = []

    async def scan() -> None:
        try:
            await _read_one_page_then_hang(server_url, reading_done)
        except asyncio.CancelledError:
            done_on_teardown.append(started[0].closed and started[0].driver_stopped)
            raise

    task = asyncio.create_task(scan())
    await reading_done.wait()
    task.cancel()
    await closing.wait()
    task.cancel()
    # A few turns for the second cancellation to land, so releasing the browser
    # cannot be what rescues a teardown that had already given up on it.
    for _ in range(3):
        await asyncio.sleep(0)
    let_it_close.set()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert done_on_teardown == [True]


async def test_the_driver_stops_even_when_closing_the_browser_fails(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The driver is the process that holds the browser, so skipping it
    # because the browser refused to close leaves the whole tree running.
    class _StuckBrowser(_FakeBrowser):
        async def close(self) -> None:
            raise RuntimeError("browser refused to close")

    started = _fake_launch(monkeypatch, _StuckBrowser)

    with pytest.raises(RuntimeError, match="refused to close"):
        async with browser_session() as fetcher:
            await fetcher(f"{server_url}/page", "playwright")

    assert started[0].driver_stopped


async def test_a_session_refuses_a_browser_driven_post_like_fetch_does() -> None:
    # Same answer through both entry points. A session that quietly did
    # something else here would be a second set of rules for one strategy.
    async with browser_session() as fetcher:
        with pytest.raises(NotImplementedError, match="does not support method 'POST'"):
            await fetcher("http://example.invalid", "playwright", method="POST")


@requires_playwright
async def test_a_real_session_reads_two_pages_in_one_browser(server_url: str) -> None:
    async with browser_session() as fetcher:
        first = await fetcher(f"{server_url}/page", "playwright")
        second = await fetcher(f"{server_url}/page", "playwright")

    assert first.status_code == second.status_code == 200
    assert "ok" in first.html
    assert "ok" in second.html
