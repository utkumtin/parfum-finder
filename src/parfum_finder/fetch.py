"""The fetch escalation ladder: one interface over httpx, curl_cffi, and playwright.

Which strategy a given site needs is recorded on that site's profile, and that value
comes from measurement, not a guess. `fetch()` only executes the strategy it is told
to use; it does not retry, rate-limit, or try other strategies itself. Rate limiting is
engine.py's job (per-site semaphore + rate_limit_ms delay). Trying each strategy in
turn to see which one a site needs is probe's job, built on top of the single-strategy
fetchers here.

Playwright is an optional extra, and it needs two things: the python package and a
downloaded browser. If a profile requires it and either piece is missing, this raises a
clear error naming the missing one, rather than silently falling back to something
weaker.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

import httpx
from curl_cffi.requests import AsyncSession as CurlAsyncSession

Strategy = Literal["httpx", "curl_cffi", "playwright"]
Method = Literal["GET", "POST"]

# A form field's value, or several of them under the same name -- the shape a
# platform's "selected_options[]"-style repeated key needs.
FormData = Mapping[str, "str | list[str]"]

# Extra request headers a profile asks for, merged over the defaults below.
Headers = Mapping[str, str]

# Identify as a real browser instead of e.g. "python-httpx/0.28" -- some sites reject
# or degrade responses to obvious script user agents even without real bot protection.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class PlaywrightNotInstalled(RuntimeError):
    """The "playwright" strategy was requested but cannot run at all.

    Covers both halves of the setup, because from the caller's side they are the
    same condition: the python package may be missing, or the package may be
    there while the browser binary was never downloaded. Either way the rung can
    never succeed until someone installs something, which is different from a
    site that merely refused this one request.

    Its own type, distinct from other RuntimeErrors this module can raise, so a
    caller like probe() can tell "the setup is incomplete, stop everything" apart
    from an ordinary failed navigation attempt that should just be recorded and
    moved past.
    """


class PlaywrightNoResponse(RuntimeError):
    """Navigation completed but playwright returned no Response object.

    Its own type rather than a bare RuntimeError, so callers can catch exactly
    this failure mode as "record and move on" without also catching unrelated
    RuntimeErrors that indicate a real bug elsewhere.
    """


@dataclass(frozen=True)
class FetchResult:
    """One fetched page, uniform regardless of which strategy produced it."""

    url: str  # final URL after redirects
    status_code: int
    html: str
    strategy: Strategy


class Fetcher(Protocol):
    """Anything that can stand in for `fetch`.

    Offline profile validation runs the real engine against saved fixtures, so it
    needs to hand the engine something that serves bytes off disk. Naming the
    shape here keeps that substitution honest: a stand-in that drifts from
    `fetch`'s signature is a type error instead of a surprise at runtime.
    """

    async def __call__(
        self,
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult: ...


async def fetch(
    url: str,
    strategy: Strategy,
    *,
    method: Method = "GET",
    data: FormData | None = None,
    headers: Headers | None = None,
    timeout_s: int = 20,
) -> FetchResult:
    """Fetch one URL using exactly the given strategy.

    `method`/`data` exist for the one platform whose variant endpoint is a
    POST with a form body, not a GET. Nothing else in this project needs them,
    so they default to a plain GET and stay optional everywhere else.

    `headers` is what a profile adds on top of the defaults. One platform's
    variant endpoint answers 200 with an empty body unless the request says
    X-Requested-With: XMLHttpRequest, which is a failure no fixture can show:
    a capture taken in a browser already carries the header, so only a live
    request ever sees it missing.

    Raises PlaywrightNotInstalled if strategy is "playwright" and playwright
    can't run here, whether the package or its browser binary is the missing
    piece. Raises NotImplementedError if strategy is "playwright" and method
    is "POST": nothing driving a browser needs a raw form POST, a page
    navigates instead, so this is left unbuilt rather than added on a guess.
    """
    if strategy == "playwright" and method == "POST":
        raise NotImplementedError(
            "strategy 'playwright' does not support method 'POST': "
            "no site currently needs a browser-driven form POST"
        )
    if strategy == "httpx":
        return await _fetch_httpx(
            url, method=method, data=data, headers=headers, timeout_s=timeout_s
        )
    if strategy == "curl_cffi":
        return await _fetch_curl_cffi(
            url, method=method, data=data, headers=headers, timeout_s=timeout_s
        )
    if strategy == "playwright":
        return await _fetch_playwright(url, headers=headers, timeout_s=timeout_s)
    raise ValueError(f"unknown fetch strategy: {strategy!r}")


async def _fetch_httpx(
    url: str,
    *,
    method: Method,
    data: FormData | None,
    headers: Headers | None,
    timeout_s: int,
) -> FetchResult:
    async with httpx.AsyncClient(
        headers={"User-Agent": DEFAULT_USER_AGENT, **(headers or {})},
        follow_redirects=True,
        timeout=timeout_s,
    ) as client:
        if method == "POST":
            response = await client.post(url, data=data)
        else:
            response = await client.get(url)
    return FetchResult(
        url=str(response.url),
        status_code=response.status_code,
        html=response.text,
        strategy="httpx",
    )


async def _fetch_curl_cffi(
    url: str,
    *,
    method: Method,
    data: FormData | None,
    headers: Headers | None,
    timeout_s: int,
) -> FetchResult:
    # impersonate="chrome" sets a matching TLS/JA3 fingerprint *and* header set
    # together. A profile's headers are added on top of that set, never instead
    # of it, so an endpoint can be told this is an XHR without desyncing the
    # fingerprint. Naming User-Agent here would desync it, which is a profile
    # mistake this cannot catch.
    async with CurlAsyncSession() as session:
        if method == "POST":
            response = await session.post(
                url,
                data=data,
                headers=dict(headers or {}),
                impersonate="chrome",
                timeout=timeout_s,
            )
        else:
            response = await session.get(
                url,
                headers=dict(headers or {}),
                impersonate="chrome",
                timeout=timeout_s,
            )
    return FetchResult(
        url=str(response.url),
        status_code=response.status_code,
        html=response.text,
        strategy="curl_cffi",
    )


async def _fetch_playwright(
    url: str, *, headers: Headers | None, timeout_s: int
) -> FetchResult:
    try:
        from playwright.async_api import Error as PlaywrightError
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise PlaywrightNotInstalled(
            "strategy 'playwright' requires the optional browser extra: "
            "install with `uv sync --extra browser`, "
            "then `uv run playwright install chromium`"
        ) from e

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
        except PlaywrightError as e:
            # A downloaded-browser check, not a navigation failure. Left as a
            # plain error row it would read like the site was unreachable, and
            # every other strategy would keep going as if playwright had been
            # fairly measured and lost.
            if "Executable doesn't exist" not in str(e):
                raise
            raise PlaywrightNotInstalled(
                "strategy 'playwright' requires a downloaded browser: "
                "run `uv run playwright install chromium`"
            ) from e
        try:
            page = await browser.new_page(
                user_agent=DEFAULT_USER_AGENT,
                extra_http_headers=dict(headers or {}),
            )
            response = await page.goto(url, timeout=timeout_s * 1000)
            html = await page.content()
        finally:
            await browser.close()

    if response is None:
        raise PlaywrightNoResponse(
            f"playwright navigation to {url!r} produced no response"
        )
    return FetchResult(
        url=response.url,
        status_code=response.status,
        html=html,
        strategy="playwright",
    )
