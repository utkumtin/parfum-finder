"""The fetch escalation ladder: one interface over httpx, curl_cffi, and playwright.

Which strategy a given site needs is recorded on that site's profile, and that value
comes from measurement, not a guess. `fetch()` only executes the strategy it is told
to use; it does not retry, rate-limit, or try other strategies itself. Rate limiting is
engine.py's job (per-site semaphore + rate_limit_ms delay, ARCHITECTURE.md §6). Trying
each strategy in turn to see which one a site needs is probe's job, built on top of the
single-strategy fetchers here.

Playwright is an optional extra. If a profile requires it and it isn't installed, this
raises a clear error rather than silently falling back to something weaker.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import httpx
from curl_cffi.requests import AsyncSession as CurlAsyncSession

Strategy = Literal["httpx", "curl_cffi", "playwright"]

# Identify as a real browser instead of e.g. "python-httpx/0.28" -- some sites reject
# or degrade responses to obvious script user agents even without real bot protection.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class FetchResult:
    """One fetched page, uniform regardless of which strategy produced it."""

    url: str  # final URL after redirects
    status_code: int
    html: str
    strategy: Strategy


async def fetch(url: str, strategy: Strategy, *, timeout_s: int = 20) -> FetchResult:
    """Fetch one URL using exactly the given strategy.

    Raises RuntimeError if strategy is "playwright" and the optional browser extra
    isn't installed.
    """
    if strategy == "httpx":
        return await _fetch_httpx(url, timeout_s=timeout_s)
    if strategy == "curl_cffi":
        return await _fetch_curl_cffi(url, timeout_s=timeout_s)
    if strategy == "playwright":
        return await _fetch_playwright(url, timeout_s=timeout_s)
    raise ValueError(f"unknown fetch strategy: {strategy!r}")


async def _fetch_httpx(url: str, *, timeout_s: int) -> FetchResult:
    async with httpx.AsyncClient(
        headers={"User-Agent": DEFAULT_USER_AGENT},
        follow_redirects=True,
        timeout=timeout_s,
    ) as client:
        response = await client.get(url)
    return FetchResult(
        url=str(response.url),
        status_code=response.status_code,
        html=response.text,
        strategy="httpx",
    )


async def _fetch_curl_cffi(url: str, *, timeout_s: int) -> FetchResult:
    # impersonate="chrome" sets a matching TLS/JA3 fingerprint *and* header set
    # together; overriding just the User-Agent header on top would desync the two
    # and defeat the point, so no custom headers are passed here.
    async with CurlAsyncSession() as session:
        response = await session.get(url, impersonate="chrome", timeout=timeout_s)
    return FetchResult(
        url=str(response.url),
        status_code=response.status_code,
        html=response.text,
        strategy="curl_cffi",
    )


async def _fetch_playwright(url: str, *, timeout_s: int) -> FetchResult:
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError(
            "strategy 'playwright' requires the optional browser extra: "
            "install with `uv sync --extra browser`, "
            "then `uv run playwright install chromium`"
        ) from e

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            page = await browser.new_page(user_agent=DEFAULT_USER_AGENT)
            response = await page.goto(url, timeout=timeout_s * 1000)
            html = await page.content()
        finally:
            await browser.close()

    if response is None:
        raise RuntimeError(f"playwright navigation to {url!r} produced no response")
    return FetchResult(
        url=response.url,
        status_code=response.status,
        html=html,
        strategy="playwright",
    )
