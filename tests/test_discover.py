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
from typing import Any

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

    # The trial is forced onto httpx. What this test is about is the choice
    # rule, and letting the trial follow the pick would send a real playwright
    # fetch at the local server, so the rule could only be checked on a machine
    # with a browser downloaded. The pick itself is reported from the
    # measurement and the override does not touch it.
    report = await discover(f"{server_url}/product", strategy="httpx")

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


def _write_template(
    platforms_dir: Path,
    name: str,
    markers: list[str],
    defaults: dict[str, Any] | None = None,
) -> Path:
    """A platform template built around markers the local server really serves.

    Templates written here rather than reused from platforms/: this file tests
    the fingerprint rule, and pinning it to whichever platforms the project
    happens to ship would make an unrelated template edit fail these tests.
    """
    platforms_dir.mkdir(parents=True, exist_ok=True)
    path = platforms_dir / f"{name}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": name,
                "fingerprint": {"any": markers},
                "defaults": defaults or {},
            }
        )
    )
    return path


async def test_fingerprint_names_the_template_that_recognizes_the_page(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(
        tmp_path,
        "shopify",
        ["cdn.shopify.com"],
        {"search": {"url_template": "{base_url}/search?q={query}"}},
    )

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert report.platform == "shopify"
    assert report.applied_defaults == {
        "search": {"url_template": "{base_url}/search?q={query}"}
    }
    # A reader has to see what the template hands over, not just its name.
    # Inheriting a field silently is how a wrong template survives review.
    assert "search.url_template = {base_url}/search?q={query}" in format_report(report)


async def test_a_page_no_template_recognizes_inherits_nothing(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    report = await discover(f"{server_url}/cards", platforms_dir=tmp_path)

    assert report.platform_matches == ()
    assert report.platform is None
    assert report.applied_defaults is None
    assert "no template applies" in format_report(report)


async def test_a_template_with_no_defaults_says_so_instead_of_listing_nothing(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # A template that only knows how to recognize its platform is a real state
    # while that platform is half understood, and the report has to name it
    # rather than print an "applying" heading with an empty list under it.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert report.platform == "shopify"
    text = format_report(report)
    assert "supplies no field yet" in text
    assert "applying platforms/shopify.json" not in text


async def test_several_matching_templates_apply_nothing_with_nobody_to_ask(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Both markers sit in the same page. A site is on one platform, so a second
    # match means a fingerprint is wrong, and applying either template would
    # hand the profile fields taken from the wrong platform. With no chooser
    # there is nobody to ask, which is the shape a piped or scripted run has,
    # and the first match must not become the answer by default.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])
    _write_template(tmp_path, "ticimax", ["test product"], {"extraction": "jsonld"})

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert report.platform_matches == ("shopify", "ticimax")
    assert report.platform is None
    assert report.applied_defaults is None
    text = format_report(report)
    assert "WARNING: more than one template matched" in text
    assert "nobody picked between them" in text
    assert "extraction = jsonld" not in text


async def test_the_picked_template_is_the_one_applied(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Picking the second one proves the answer is used rather than coincidentally
    # matching what ordering would have produced anyway.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])
    _write_template(tmp_path, "ticimax", ["test product"], {"extraction": "jsonld"})
    asked: list[tuple[str, ...]] = []

    def pick_ticimax(candidates: tuple[str, ...]) -> str:
        asked.append(candidates)
        return "ticimax"

    report = await discover(
        f"{server_url}/product", platforms_dir=tmp_path, chooser=pick_ticimax
    )

    assert asked == [("shopify", "ticimax")]
    assert report.platform == "ticimax"
    assert report.applied_defaults == {"extraction": "jsonld"}
    text = format_report(report)
    assert "extraction = jsonld" in text
    # A pick is somebody's claim, not something the markup showed, and the
    # report has to keep the two apart.
    assert "picked by hand, not measured" in text


async def test_a_pick_does_not_silence_the_collision(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Choosing one template settles this run. It does not make the other
    # template's fingerprint right, and that is still the thing to go fix.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])
    _write_template(tmp_path, "ticimax", ["test product"])

    report = await discover(
        f"{server_url}/product",
        platforms_dir=tmp_path,
        chooser=lambda candidates: "shopify",
    )

    text = format_report(report)
    assert "WARNING: more than one template matched" in text
    assert report.platform_matches == ("shopify", "ticimax")


async def test_declining_to_pick_applies_nothing(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # "None of these" has to stay answerable. A prompt that only accepts a
    # template forces a pick, which is the same wrong answer as choosing
    # silently, only with somebody's name attached to it.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])
    _write_template(tmp_path, "ticimax", ["test product"], {"extraction": "jsonld"})

    report = await discover(
        f"{server_url}/product",
        platforms_dir=tmp_path,
        chooser=lambda candidates: None,
    )

    assert report.platform is None
    assert report.applied_defaults is None
    assert "extraction = jsonld" not in format_report(report)


async def test_a_single_match_is_never_put_to_a_chooser(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # One match is not a question. Asking anyway would train whoever runs this
    # to hit enter through a prompt that occasionally matters.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    def never_asked(candidates: tuple[str, ...]) -> str | None:
        raise AssertionError("a single match must not be put to a chooser")

    report = await discover(
        f"{server_url}/product", platforms_dir=tmp_path, chooser=never_asked
    )

    assert report.platform == "shopify"
    assert report.chosen_platform is None


async def test_an_answer_outside_the_candidates_is_an_error(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Naming a template that did not match is not a choice between these two,
    # it is a different claim about the site, and it would apply a template
    # whose markers are nowhere in the page.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])
    _write_template(tmp_path, "ticimax", ["test product"])

    with pytest.raises(ValueError, match="not one of the templates"):
        await discover(
            f"{server_url}/product",
            platforms_dir=tmp_path,
            chooser=lambda candidates: "ideasoft",
        )


async def test_the_entry_page_decides_the_platform_not_a_later_one(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The listing carries no marker and the product page does. The site verdict
    # follows the entry page, but the per-page evidence stays visible, because
    # a marker present on one page and missing on another is itself a finding.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    report = await discover(
        f"{server_url}/cards",
        product_url=f"{server_url}/product",
        platforms_dir=tmp_path,
    )

    listing, product = report.trials
    assert listing.platform_matches == ()
    assert product.platform_matches == ("shopify",)
    assert report.platform is None


async def test_no_page_read_means_no_fingerprint_claim(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Nothing qualified, so no page was read. Reporting "no platform" here would
    # read as a measured answer when nothing was measured at all.
    _fake_probe(
        monkeypatch,
        _attempt("httpx", status_code=503, jsonld_products=0, markup_nodes=0),
        _attempt("curl_cffi", status_code=503, jsonld_products=0, markup_nodes=0),
        _attempt("playwright", jsonld_products=0, markup_nodes=0),
    )
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert report.trials == ()
    assert report.platform_matches == ()
    assert "platform fingerprint: not run" in format_report(report)


def _score(report: DiscoveryReport, field: str) -> tuple[str, str]:
    """One field's confidence and value, or a clear failure if it went unscored."""
    scored = {f.field: f for f in report.fields}
    assert field in scored, f"{field} was not scored at all: {sorted(scored)}"
    return scored[field].confidence, scored[field].value


async def test_a_measured_strategy_and_a_single_template_need_no_review(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Both values came off this site's own pages, and a template that supplies
    # nothing cannot hand down an unchecked field. Nothing is left to confirm.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert _score(report, "strategy") == ("high", "httpx")
    assert _score(report, "platform") == ("high", "shopify")
    assert report.needs_review == ()


async def test_an_inherited_field_is_never_more_than_medium(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The template's search URL is right for the sites it was written from.
    # Nothing here ran a search on this one, so it stays a claim to check.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(
        tmp_path,
        "shopify",
        ["cdn.shopify.com"],
        {"search": {"url_template": "{base_url}/search?q={query}"}},
    )

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    confidence, value = _score(report, "search.url_template")
    assert confidence == "medium"
    # The dotted name is the one a profile uses, so the list can be pasted in
    # as it stands instead of translated back field by field.
    assert value == "{base_url}/search?q={query}"
    assert report.needs_review == ("search.url_template",)


async def test_a_field_cannot_be_surer_than_the_platform_it_came_from(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The template was a judgement call between two that both matched, so
    # everything inherited from it rests on that call, not on a measurement.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(
        tmp_path, "shopify", ["cdn.shopify.com"], {"extraction": "endpoint"}
    )
    _write_template(tmp_path, "ticimax", ["test product"])

    report = await discover(
        f"{server_url}/product",
        platforms_dir=tmp_path,
        chooser=lambda candidates: "shopify",
    )

    assert _score(report, "platform") == ("low", "shopify")
    assert _score(report, "extraction") == ("low", "endpoint")


async def test_a_strategy_given_by_hand_is_not_a_measured_one(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # httpx was measured and works here. The run was told to use playwright
    # anyway, so the profile would carry a rung this site never showed it needs.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(tmp_path, "shopify", ["cdn.shopify.com"])

    report = await discover(
        f"{server_url}/product", strategy="curl_cffi", platforms_dir=tmp_path
    )

    assert _score(report, "strategy") == ("low", "curl_cffi")
    assert "strategy" in report.needs_review


async def test_extraction_is_read_off_the_page_when_no_template_covers_it(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # No template matched, so nothing was inherited, but the page itself is
    # evidence: it declares a JSON-LD product with a price.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert _score(report, "extraction") == ("high", "jsonld")
    assert report.needs_review == ()


async def test_a_page_that_hides_its_other_sizes_scores_extraction_low(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # JSON-LD is present, so the naive read is that the top rung works. The
    # page also offers sizes it does not price, which is exactly the case
    # where that read produces a wrong price per ml.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(
        f"{server_url}/variant-single-price", platforms_dir=tmp_path
    )

    assert _score(report, "extraction") == ("low", "jsonld")
    assert "extraction" in report.needs_review


async def test_the_product_page_decides_the_extraction_layer(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The entry page is a listing with no product markup. Scoring the layer on
    # it would leave the field unscored for a site whose product pages are fine.
    _fake_probe(monkeypatch, _attempt("httpx"))

    report = await discover(
        f"{server_url}/cards",
        product_url=f"{server_url}/product",
        platforms_dir=tmp_path,
    )

    assert _score(report, "extraction") == ("high", "jsonld")


async def test_nothing_is_scored_when_no_page_was_read(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # No rung qualified, so there is no evidence for any field. An empty review
    # list here would read as "all confirmed" when nothing was looked at.
    _fake_probe(
        monkeypatch,
        _attempt("httpx", status_code=503, jsonld_products=0, markup_nodes=0),
        _attempt("curl_cffi", status_code=503, jsonld_products=0, markup_nodes=0),
        _attempt("playwright", jsonld_products=0, markup_nodes=0),
    )

    report = await discover(f"{server_url}/product", platforms_dir=tmp_path)

    assert report.fields == ()
    assert report.needs_review == ()
    assert "field confidence: nothing scored" in format_report(report)


async def test_the_review_list_is_printed_ready_to_paste_into_a_profile(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Retyping this list by hand is where a field quietly falls off it, so the
    # report prints the JSON array a profile's needs_review holds.
    _fake_probe(monkeypatch, _attempt("httpx"))
    _write_template(
        tmp_path,
        "shopify",
        ["cdn.shopify.com"],
        {"search": {"url_template": "{base_url}/search?q={query}"}},
    )

    report = await discover(
        f"{server_url}/product", strategy="httpx", platforms_dir=tmp_path
    )

    assert 'needs_review: ["strategy", "search.url_template"]' in format_report(report)
    # Shipping is never scraped, so it was never claimed and is not a field
    # awaiting review. It still has to be written by hand, and the report says
    # that in words rather than leaving the empty spot to imply it.
    assert not [f for f in report.needs_review if f.startswith("shipping")]


async def test_a_broken_template_stops_the_run_before_any_request(
    server_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Fingerprinting against half a library reports "no platform" for a site
    # whose template is sitting right there, unreadable. That is a wrong answer
    # dressed as a measured one, so the run stops instead.
    async def never_called(url: str, *, timeout_s: int = 20) -> None:
        raise AssertionError("the templates must be read before anything is fetched")

    monkeypatch.setattr(discover_module, "probe", never_called)
    (tmp_path / "shopify.json").write_text("{not valid json")

    with pytest.raises(ValueError, match="invalid JSON"):
        await discover(f"{server_url}/product", platforms_dir=tmp_path)
