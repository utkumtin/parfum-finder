"""Tests for parfum_finder.probe.

probe() always tries all three strategies -- these tests check that commitment
directly (all three rungs show up in every report, in order) rather than just
checking the "winning" one, since a status-only early stop is exactly the bug
this module was written to avoid (a JS-rendered page returning 200 with an empty
shell would otherwise look identical to a page that actually worked).

Because probe() always runs the playwright rung and re-raises when playwright
can't run, every test that actually fetches something needs a working playwright
setup. Those tests are marked `requires_playwright` so a checkout without the
extra, or with the extra but no downloaded browser, skips them instead of
erroring out.
"""

import sys

import pytest
from conftest import requires_playwright

from parfum_finder import probe as probe_module
from parfum_finder.fetch import PlaywrightNotInstalled
from parfum_finder.probe import ProbeAttempt, ProbeReport, format_report, probe

_STRATEGIES = ("httpx", "curl_cffi", "playwright")


@requires_playwright
async def test_probe_tries_all_three_strategies_in_order(server_url: str) -> None:
    report = await probe(f"{server_url}/page")

    assert tuple(a.strategy for a in report.attempts) == _STRATEGIES


@requires_playwright
async def test_probe_reports_status_and_html_size_per_strategy(
    server_url: str,
) -> None:
    report = await probe(f"{server_url}/page")

    for attempt in report.attempts:
        assert attempt.error is None
        assert attempt.status_code == 200
        # playwright serializes the browser's parsed DOM rather than returning
        # the raw response bytes (it adds a <head></head>, for one), so exact
        # byte-for-byte size isn't comparable across strategies -- just check
        # the real page content made it through.
        assert attempt.html_chars and attempt.html_chars >= len("<body>ok</body>")
        # negative cases: a plain page has neither known markers nor cards
        assert attempt.platform_signatures == ()
        assert attempt.product_markup_nodes == 0


@requires_playwright
async def test_probe_counts_jsonld_product_and_platform_signature(
    server_url: str,
) -> None:
    report = await probe(f"{server_url}/product")

    for attempt in report.attempts:
        assert attempt.jsonld_block_count == 1
        assert attempt.jsonld_product_count == 1
        assert attempt.platform_signatures == ("shopify",)


@requires_playwright
@pytest.mark.parametrize(
    "path", ["/product-graph", "/product-array"], ids=["at-graph", "root-array"]
)
async def test_probe_counts_product_across_jsonld_root_shapes(
    server_url: str, path: str
) -> None:
    report = await probe(f"{server_url}{path}")

    for attempt in report.attempts:
        assert attempt.jsonld_block_count == 1
        assert attempt.jsonld_product_count == 1


@requires_playwright
async def test_probe_counts_products_nested_below_the_top_level(
    server_url: str,
) -> None:
    # A category or search page hides its Products under ItemList entries. If
    # probe only looked at the top of each block it would report 0 here, which
    # would read as "this page has no structured data" and send the extraction
    # work down the wrong path.
    report = await probe(f"{server_url}/product-nested")

    for attempt in report.attempts:
        assert attempt.jsonld_block_count == 1
        assert attempt.jsonld_product_count == 2


@requires_playwright
async def test_probe_counts_product_markup_without_any_jsonld(
    server_url: str,
) -> None:
    # The case that decides whether a strategy really rendered the page: no
    # JSON-LD to lean on, so product-ish markup is the only evidence. An empty
    # shell would report 0 here at a comparable HTML size.
    report = await probe(f"{server_url}/cards")

    for attempt in report.attempts:
        assert attempt.jsonld_block_count == 0
        # 4, not 2: the count is of matching nodes, and each of the two cards
        # contributes both its own div and the product link inside it. The
        # "about" nav link matches nothing, which is what stops this from
        # degenerating into "count every anchor on the page".
        assert attempt.product_markup_nodes == 4


@requires_playwright
async def test_probe_reports_a_mix_when_only_one_strategy_gets_through(
    server_url: str,
) -> None:
    # The whole reason probe exists: a site that turns away a plain client but
    # serves an impersonated one. httpx and playwright both send our declared
    # user agent and get 403; curl_cffi impersonates Chrome and gets the real
    # page. A report that collapsed to a single verdict would lose this.
    report = await probe(f"{server_url}/blocks-plain-ua")

    by_strategy = {a.strategy: a for a in report.attempts}
    assert by_strategy["httpx"].status_code == 403
    assert by_strategy["playwright"].status_code == 403
    assert by_strategy["curl_cffi"].status_code == 200
    assert by_strategy["curl_cffi"].jsonld_product_count == 1
    assert by_strategy["httpx"].jsonld_product_count == 0


@requires_playwright
async def test_probe_ignores_malformed_jsonld_instead_of_crashing(
    server_url: str,
) -> None:
    report = await probe(f"{server_url}/product-malformed")

    for attempt in report.attempts:
        assert attempt.error is None
        assert attempt.jsonld_block_count == 1
        assert attempt.jsonld_product_count == 0


def test_format_report_renders_a_failed_attempt_as_an_error_row() -> None:
    report = ProbeReport(
        url="http://example.invalid",
        attempts=(
            ProbeAttempt(
                strategy="httpx",
                status_code=None,
                error="ConnectError: connection refused",
                html_chars=None,
                jsonld_block_count=None,
                jsonld_product_count=None,
                product_markup_nodes=None,
                platform_signatures=None,
            ),
        ),
    )

    text = format_report(report)

    assert "httpx" in text
    assert "ConnectError: connection refused" in text


def test_format_report_marks_unverified_platform_guesses() -> None:
    # ticimax and ideasoft are matched on the vendor name alone, which any page
    # merely mentioning them would trip. Printed next to a confirmed shopify
    # match with nothing to separate them, a reader would weigh a guess and a
    # fact the same way.
    report = ProbeReport(
        url="http://example.invalid",
        attempts=(
            ProbeAttempt(
                strategy="httpx",
                status_code=200,
                error=None,
                html_chars=100,
                jsonld_block_count=0,
                jsonld_product_count=0,
                product_markup_nodes=0,
                platform_signatures=("shopify", "ticimax"),
            ),
        ),
    )

    text = format_report(report)

    assert "ticimax?" in text
    assert "shopify," in text and "shopify?" not in text


def test_format_report_keeps_a_multiline_error_on_one_row() -> None:
    # playwright errors arrive with a call log stapled underneath. Printed raw,
    # they spill across the table's columns and the report stops being readable.
    report = ProbeReport(
        url="http://example.invalid",
        attempts=(
            ProbeAttempt(
                strategy="playwright",
                status_code=None,
                error="Error: Page.goto: net::ERR_UNSAFE_PORT\nCall log:\n  - nav",
                html_chars=None,
                jsonld_block_count=None,
                jsonld_product_count=None,
                product_markup_nodes=None,
                platform_signatures=None,
            ),
        ),
    )

    text = format_report(report)

    assert "ERR_UNSAFE_PORT" in text
    assert "Call log" not in text
    assert len(text.splitlines()) == 5  # title, blank, header, rule, one row


@requires_playwright
async def test_probe_records_connection_failure_with_the_exception_type(
    unused_tcp_port: int,
) -> None:
    # Nothing listens on this port: every strategy should fail fast and land as
    # a recorded attempt (status_code None, error set), not blow up probe().
    report = await probe(f"http://127.0.0.1:{unused_tcp_port}/", timeout_s=2)

    for attempt in report.attempts:
        assert attempt.status_code is None
        assert attempt.error
        # The exception class has to survive into the report. "connection
        # refused", "read timeout" and a TLS handshake failure point at three
        # different fixes, and the message text alone often can't tell them
        # apart, so an error row without a type is not a measurement.
        assert attempt.error.split(":")[0].isidentifier()


@requires_playwright
async def test_probe_playwright_no_response_is_recorded_not_raised() -> None:
    # "about:blank" makes every rung fail for a different reason: httpx and
    # curl_cffi reject the unsupported scheme, and playwright's own goto()
    # returns no Response object for it (verified separately) -- fetch.py turns
    # that into a PlaywrightNoResponse, distinct from PlaywrightNotInstalled, and
    # probe() must record it as a failed attempt rather than crash the run.
    report = await probe("about:blank")

    assert tuple(a.strategy for a in report.attempts) == _STRATEGIES
    for attempt in report.attempts:
        assert attempt.status_code is None
        assert attempt.error


async def test_probe_playwright_missing_extra_propagates_uncaught(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Even though httpx and curl_cffi already succeed against this URL, the
    # playwright rung is still attempted -- and its missing-extra error must not
    # be swallowed as if it were just another failed attempt. Recording the
    # calls proves the earlier rungs ran and were dropped on the floor, rather
    # than probe having bailed out before reaching playwright at all.
    tried: list[str] = []
    real_fetch = probe_module.fetch

    async def recording_fetch(url: str, strategy: str, **kwargs: object) -> object:
        tried.append(strategy)
        return await real_fetch(url, strategy, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(probe_module, "fetch", recording_fetch)
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.async_api", None)

    with pytest.raises(PlaywrightNotInstalled, match="browser extra"):
        await probe(f"{server_url}/page")

    assert tried == list(_STRATEGIES)
