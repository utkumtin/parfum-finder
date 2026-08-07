"""Tests for parfum_finder.discover.

Two things are under test here and they need different setups. The choice of
strategy is a rule applied to a measurement, so those tests feed a synthetic
measurement in and check which rung wins, including the cases where the answer
must be "none". The trial is a real fetch plus a real read, so those tests run
against the local server.

Feeding the measurement in also keeps most of this file runnable without a
browser: discover() re-raises when playwright cannot run, so anything that lets
the real probe() through needs a working playwright setup.
"""

import json
from pathlib import Path

import pytest
from conftest import requires_playwright

from parfum_finder import discover as discover_module
from parfum_finder.discover import (
    DiscoveryReport,
    collect_prices,
    discover,
    format_report,
)
from parfum_finder.fetch import Strategy
from parfum_finder.probe import ProbeAttempt, ProbeReport


def _attempt(
    strategy: Strategy,
    *,
    status_code: int | None = 200,
    error: str | None = None,
    jsonld_products: int | None = 1,
    markup_nodes: int | None = 5,
) -> ProbeAttempt:
    """A measurement row, with "this rung worked" as the default."""
    return ProbeAttempt(
        strategy=strategy,
        status_code=status_code,
        error=error,
        html_chars=1000 if error is None else None,
        jsonld_block_count=1 if error is None else None,
        jsonld_product_count=jsonld_products,
        product_markup_nodes=markup_nodes,
        platform_signatures=() if error is None else None,
    )


def _fake_probe(monkeypatch: pytest.MonkeyPatch, *attempts: ProbeAttempt) -> None:
    """Replace the measurement so a test can state the outcome it needs."""

    async def fake(url: str, *, timeout_s: int = 20) -> ProbeReport:
        return ProbeReport(url=url, attempts=attempts)

    monkeypatch.setattr(discover_module, "probe", fake)


async def test_cheapest_qualifying_strategy_wins(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # httpx got turned away, so the next rung up is the honest answer even
    # though the one after it works too.
    _fake_probe(
        monkeypatch,
        _attempt("httpx", status_code=403, jsonld_products=0, markup_nodes=0),
        _attempt("curl_cffi"),
        _attempt("playwright"),
    )

    report = await discover(f"{server_url}/product")

    assert report.chosen_strategy == "curl_cffi"


async def test_a_2xx_without_product_evidence_does_not_qualify(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The failure this rule exists for: a JS-rendered page answers 200 with an
    # empty shell, so status alone would hand the profile a strategy that can
    # never see a product.
    _fake_probe(
        monkeypatch,
        _attempt("httpx", jsonld_products=0, markup_nodes=0),
        _attempt("curl_cffi", jsonld_products=0, markup_nodes=0),
        _attempt("playwright"),
    )

    report = await discover(f"{server_url}/product")

    assert report.chosen_strategy == "playwright"


async def test_nothing_qualifies_means_no_strategy_and_no_trial(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # No fallback pick. Naming a strategy that failed the measurement would put
    # a guess into the profile, which is what the measurement is here to stop.
    _fake_probe(
        monkeypatch,
        _attempt("httpx", status_code=None, error="ConnectError: refused"),
        _attempt("curl_cffi", status_code=503, jsonld_products=0, markup_nodes=0),
        _attempt("playwright", jsonld_products=0, markup_nodes=0),
    )

    report = await discover(f"{server_url}/product")

    assert report.chosen_strategy is None
    assert report.trials == ()
    assert "chosen strategy: NONE" in format_report(report)


async def test_trial_reads_the_products_the_page_declares(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/product")

    (trial,) = report.trials
    assert trial.status_code == 200
    assert trial.error is None
    assert [p.name for p in trial.products] == ["Test Product"]


async def test_product_url_is_trialled_as_a_second_page(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/cards", product_url=f"{server_url}/product")

    listing, product = report.trials
    assert listing.url.endswith("/cards")
    assert product.url.endswith("/product")
    assert [p.name for p in product.products] == ["Test Product"]


async def test_size_selector_with_a_single_price_is_flagged(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The quiet failure this whole command is aimed at: three sizes on the page,
    # one readable price, and nothing in the output saying so would leave the
    # site looking cheaper per ml than it is.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/variant-single-price")

    (trial,) = report.trials
    assert trial.variant_control_present is True
    text = format_report(report)
    assert "WARNING: the markup offers a size selector" in text


async def test_woocommerce_variation_form_counts_as_a_size_selector(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # WooCommerce writes "variation" where other shops write "variant", so a
    # detector built on the word "variant" alone reports a four-size product as
    # having no sizes at all and nothing in the output contradicts it.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/woo-variation")

    (trial,) = report.trials
    assert trial.variant_control_present is True


async def test_range_only_pricing_next_to_a_size_selector_is_flagged(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Two numbers read off a range look like two prices but describe four sizes,
    # and the two in the middle are still missing. Left unflagged, the low end
    # gets taken for the product's price and the site looks cheaper per ml than
    # it is, which is the same wrong comparison the single-price warning exists
    # to prevent.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/woo-variation")

    (trial,) = report.trials
    assert len(collect_prices(trial.products[0])) == 2
    text = format_report(report)
    assert "every price here comes from a range" in text


async def test_fixtures_are_written_with_the_metadata_that_dates_them(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Offline validation reads these files instead of the live site, so a saved
    # page is only worth having if the URL it came from, the moment it was taken
    # and the strategy that fetched it travel with it. Without those three a
    # later "the profile still works" claim rests on a page nobody can place.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(
        f"{server_url}/cards",
        search_url=f"{server_url}/cards",
        product_url=f"{server_url}/product",
        fixtures_dir=tmp_path / "ornek",
    )

    assert (tmp_path / "ornek" / "search.html").exists()
    assert "Test Product" in (tmp_path / "ornek" / "product.html").read_text()
    meta = json.loads((tmp_path / "ornek" / "meta.json").read_text())
    assert meta["strategy"] == "httpx"
    assert meta["pages"]["product"]["url"].endswith("/product")
    assert meta["pages"]["product"]["sha256"] == report.trials[-1].sha256
    # The entry URL is measured against, not extracted from, so it is not kept.
    assert not (tmp_path / "ornek" / "cards.html").exists()
    # What was written has to be visible in the run's own output, otherwise a
    # capture that quietly saved the wrong page only shows up much later.
    text = format_report(report)
    assert "product.html" in text and "search.html" in text


async def test_the_entry_page_is_never_saved_as_a_fixture(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # A fixtures directory naming no saved page is a silent miss: the command
    # looks like it captured a site and leaves an empty directory behind.
    _fake_probe(monkeypatch, _attempt("httpx"))

    with pytest.raises(ValueError, match="no page was saved"):
        await discover(f"{server_url}/cards", fixtures_dir=tmp_path / "ornek")


async def test_strategy_override_replaces_the_measured_pick_for_the_trials(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Some sites render one page in the browser and serve the rest as plain
    # HTML. Measuring the front page then capturing a JS-rendered search page
    # with the same rung would save an empty shell as if it were the real page.
    _fake_probe(monkeypatch, _attempt("httpx"))
    used: list[str] = []

    async def spy_fetch(url: str, strategy: Strategy, *, timeout_s: int = 20) -> object:
        used.append(strategy)
        return await real_fetch(url, strategy, timeout_s=timeout_s)

    real_fetch = discover_module.fetch
    monkeypatch.setattr(discover_module, "fetch", spy_fetch)

    report = await discover(f"{server_url}/product", strategy="curl_cffi")

    assert used == ["curl_cffi"]
    assert report.chosen_strategy == "httpx"
    assert report.trial_strategy == "curl_cffi"
    assert "trials ran with: curl_cffi" in format_report(report)


async def test_override_still_runs_trials_when_no_strategy_qualified(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Measurement calls a page unusable when it carries nothing product-like,
    # which is the normal verdict for a front page. Refusing to fetch anything
    # after that would make the override useless exactly where it is needed.
    _fake_probe(monkeypatch, _attempt("httpx", jsonld_products=0, markup_nodes=0))

    report = await discover(f"{server_url}/product", strategy="httpx")

    assert report.chosen_strategy is None
    assert [p.name for p in report.trials[0].products] == ["Test Product"]
    assert "rest on the command line alone" in format_report(report)


async def test_page_without_jsonld_is_flagged_as_needing_a_lower_layer(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/cards")

    assert report.trials[0].products == ()
    assert "WARNING: no JSON-LD product" in format_report(report)


async def test_a_failed_trial_fetch_is_recorded_not_raised(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A site that answers the measurement and then refuses the next request must
    # still produce a readable report rather than a traceback.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover("http://127.0.0.1:1/unreachable")

    (trial,) = report.trials
    assert trial.status_code is None
    assert trial.error is not None
    assert "fetch failed" in format_report(report)


async def test_report_names_every_qualifying_rung_not_just_the_winner(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The rule has to be visible in the output. A bare winner would be exactly
    # the unexplained pick the measurement step exists to replace.
    _fake_probe(
        monkeypatch,
        _attempt("httpx"),
        _attempt("curl_cffi"),
        _attempt("playwright", jsonld_products=0, markup_nodes=0),
    )

    text = format_report(await discover(f"{server_url}/product"))

    assert "qualified (2xx + product evidence): httpx, curl_cffi" in text
    assert "chosen strategy: httpx" in text


async def test_a_page_holding_every_size_price_is_not_flagged(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Same size selector as the flagged page, but every price is stated here, so
    # a plain fetch already sees the full range. Warning on this one would train
    # a reader to ignore the warning that matters.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/variant-prices")

    (trial,) = report.trials
    assert trial.variant_control_present is True
    text = format_report(report)
    assert "WARNING" not in text
    # The range and the per-size stock answers both come from the variants, so a
    # reader can tell this page apart from one that states a single price.
    assert "prices=2 [149.90-279.90]" in text
    assert "stock=1in/1out/0unknown" in text


async def test_variant_prices_are_counted_in_the_report(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A variant parent's sizes each carry their own price, and the per-product
    # line has to count them, otherwise a page holding every size would read the
    # same as one holding a single price.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/product-nested")

    assert "json-ld products: 2" in format_report(report)


async def test_an_empty_second_page_does_not_claim_the_layer_is_wrong(
    server_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The strategy was measured on the first URL only. A second page that comes
    # back empty may carry no JSON-LD, or may just need a stronger strategy, and
    # stating the first as fact would send a reader off writing a CSS profile
    # for a site that only needed a browser.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/product", product_url=f"{server_url}/cards")

    text = format_report(report)
    assert "was measured on the first URL, not this one" in text
    assert "so a lower one is needed" not in text


@requires_playwright
async def test_real_ladder_falls_through_to_curl_cffi_when_httpx_is_blocked(
    server_url: str,
) -> None:
    # The whole path with nothing faked: httpx and playwright both send the
    # declared user agent and get a 403, curl_cffi impersonates a browser and
    # gets the page. The trial then has to run with curl_cffi, not quietly with
    # the first rung.
    report = await discover(f"{server_url}/blocks-plain-ua")

    assert report.chosen_strategy == "curl_cffi"
    (trial,) = report.trials
    assert trial.status_code == 200
    assert [p.name for p in trial.products] == ["Test Product"]


@requires_playwright
async def test_real_measurement_picks_httpx_for_a_plain_page(
    server_url: str,
) -> None:
    report = await discover(f"{server_url}/product")

    assert isinstance(report, DiscoveryReport)
    assert tuple(a.strategy for a in report.strategy_report.attempts) == (
        "httpx",
        "curl_cffi",
        "playwright",
    )
    assert report.chosen_strategy == "httpx"
    assert [p.name for p in report.trials[0].products] == ["Test Product"]
