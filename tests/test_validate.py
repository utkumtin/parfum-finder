"""M5's own criterion: when a profile stops agreeing with its site's real markup,
offline validation catches it and names the step that broke.

Every case here works by corrupting one field of a real profile and asserting
which check fails. That is the point of the module: a broken profile has to
produce a named failure rather than a traceback or, worse, a quietly empty
result. Asserting only `ok is False` would pass even if every break reported the
same useless step, so each case pins the step by name.
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote_plus

import pytest

from parfum_finder.fetch import FetchResult, FormData, Headers, Method, Strategy
from parfum_finder.profiles import load_site_profile
from parfum_finder.validate import (
    STALE_PROFILE_DAYS,
    format_live_report,
    format_report,
    live_query,
    profile_age_days,
    site_ids,
    validate_all_offline,
    validate_live,
    validate_offline,
)

_ROOT = Path(__file__).resolve().parent.parent
_SITES_DIR = _ROOT / "sites"
_FIXTURES_DIR = _ROOT / "fixtures"
_PLATFORMS_DIR = _ROOT / "platforms"


def _corrupted_sites_dir(
    tmp_path: Path, site_id: str, mutate: Any = None, **fields: Any
) -> Path:
    """A sites/ directory holding one real profile with fields overwritten.

    The real fixtures stay untouched; only the profile moves. That is the drift
    being simulated: the site's markup is what it always was and the profile
    stopped matching it.
    """
    profile = json.loads((_SITES_DIR / f"{site_id}.json").read_text())
    if mutate is not None:
        mutate(profile)
    profile.update(fields)
    directory = tmp_path / "sites"
    directory.mkdir(exist_ok=True)
    (directory / f"{site_id}.json").write_text(json.dumps(profile))
    return directory


def _iso_days_ago(days: int) -> str:
    """A discovered_at stamp that lands a fixed number of days in the past.

    Relative to now rather than a hard-coded date, because a profile written
    with a literal date would drift past the staleness threshold as time passes
    and quietly turn the fresh-profile case into a stale one.
    """
    stamp = datetime.now(UTC) - timedelta(days=days, hours=1)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


async def test_every_real_profile_passes_against_its_own_fixtures() -> None:
    # The baseline the corruption cases are measured against. If this ever fails
    # on its own, a real profile drifted from a real capture and the failing
    # site's report line says which step.
    results = await validate_all_offline()

    assert results, "no site profiles were found to validate"
    assert [r.site_id for r in results] == list(site_ids())
    broken = [(r.site_id, r.failure) for r in results if not r.ok]
    assert not broken, format_report(results)


async def test_a_dead_search_selector_is_caught_as_the_search_step(
    tmp_path: Path,
) -> None:
    # The most common way a profile dies: the site renames its result card class.
    # Nothing about the fetch or the extraction layer changed, so blaming either
    # would send whoever reads this to the wrong file.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        mutate=lambda p: p["search"].update({"result_item": ".no-such-card"}),
    )

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "search"
    assert ".no-such-card" in result.failure.detail


async def test_a_dead_price_selector_is_caught_as_the_extraction_step(
    tmp_path: Path,
) -> None:
    # venco reads its sizes out of an embedded JSON blob, so a field_map that
    # points the price at a key the blob does not have is the "extraction layer
    # answered but the required field is empty" row of the fail-loud table: rows
    # still come back, none of them carries a number. search_site raises
    # ExtractionFailed for it, and validate has to report that as a step rather
    # than let it escape as a traceback.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        mutate=lambda p: p["embedded_json"]["field_map"].update({"price": "nope"}),
    )

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "extraction"


async def test_the_wrong_extraction_layer_is_caught_as_the_extraction_step(
    tmp_path: Path,
) -> None:
    # decantall's sizes live in an embedded JSON blob. A profile claiming its
    # product pages declare them as JSON-LD is the "site changed how it publishes
    # its data" case, and the report has to name the layer that read nothing.
    sites_dir = _corrupted_sites_dir(tmp_path, "decantall", extraction="jsonld")

    result = await validate_offline("decantall", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "extraction"


async def test_a_page_nobody_captured_is_reported_as_a_missing_fixture(
    tmp_path: Path,
) -> None:
    # A profile on the GET endpoint layer asks for a JSON URL that no capture
    # holds. Answering it with the search page instead would make the site look
    # like it stopped replying in JSON, which is a lie about a site that was
    # never asked. The report has to say the fixture is missing.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/api/product.json",
            "variants_path": "variants",
            "field_map": {"size_raw": "title", "price": "price", "in_stock": "stock"},
        },
    )

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "extraction"
    assert "no saved bytes" in result.failure.detail


async def test_a_profile_that_fails_schema_validation_is_caught_first(
    tmp_path: Path,
) -> None:
    # Nothing downstream can be checked once the profile itself is invalid, and
    # reporting a "search" failure for it would be a lie about where the problem
    # is.
    sites_dir = _corrupted_sites_dir(tmp_path, "venco", extraction="telepathy")

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "profile"
    assert [check.name for check in result.checks] == ["profile"]


async def test_missing_fixtures_are_reported_not_raised(tmp_path: Path) -> None:
    # A site whose capture was never saved, or was deleted. Offline validation
    # cannot say anything about it, and that is a reported state rather than a
    # crash that hides every other site's result.
    empty_fixtures = tmp_path / "fixtures"
    empty_fixtures.mkdir()

    result = await validate_offline("venco", fixtures_dir=empty_fixtures)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "fixtures"


async def test_a_site_with_no_profile_file_raises(tmp_path: Path) -> None:
    # Being asked about a site that does not exist is a mistake in the request,
    # not a finding about a profile, so it is not folded into the report.
    empty = tmp_path / "sites"
    empty.mkdir()

    with pytest.raises(FileNotFoundError):
        await validate_offline("nosuchsite", sites_dir=empty)


async def test_the_report_names_the_broken_site_and_step(tmp_path: Path) -> None:
    # What a person actually reads. A break has to be findable in the output
    # without knowing which site to look for.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        mutate=lambda p: p["search"].update({"result_item": ".no-such-card"}),
    )
    good = await validate_offline("decantall")
    bad = await validate_offline("venco", sites_dir=sites_dir)

    report = format_report((good, bad))

    assert "BROKEN" in report
    assert "venco" in report
    assert "search" in report
    assert "1/2 profiles pass offline" in report
    assert "broken: venco" in report


async def test_an_empty_sites_directory_says_so_instead_of_passing(
    tmp_path: Path,
) -> None:
    # "0/0 profiles pass" reads as a clean run, which is the one thing this must
    # not report when there is nothing to validate at all.
    empty = tmp_path / "sites"
    empty.mkdir()

    results = await validate_all_offline(sites_dir=empty)

    assert results == ()
    assert format_report(results) == "no site profiles to validate."


class _FakeSite:
    """A stand-in for one live site, answering the search page then the rest.

    Live validation is about what a site does today, and a test that depends on
    a real shop's inventory today tests the shop, not this module. The fetcher
    is injectable for exactly this, so every live case here drives it with bytes
    the test chose.
    """

    def __init__(
        self,
        search_html: str,
        product_html: str,
        status_code: int = 200,
        redirect_url: str | None = None,
    ):
        self._search_html = search_html
        self._product_html = product_html
        self._status_code = status_code
        self._redirect_url = redirect_url
        self.served_search = False

    async def __call__(
        self,
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        requested_url = url
        html = self._product_html
        if not self.served_search:
            self.served_search = True
            html = self._search_html
            url = self._redirect_url or url
        return FetchResult(
            url=url,
            status_code=self._status_code,
            html=html,
            strategy=strategy,
            requested_url=requested_url,
        )


class _DeadSite:
    """A host that cannot be reached at all."""

    async def __call__(
        self,
        url: str,
        strategy: Strategy,
        *,
        method: Method = "GET",
        data: FormData | None = None,
        headers: Headers | None = None,
        timeout_s: int = 20,
    ) -> FetchResult:
        raise ConnectionError(f"connection refused: {url}")


def _fixture_site(site_id: str) -> _FakeSite:
    directory = _FIXTURES_DIR / site_id
    return _FakeSite(
        (directory / "search.html").read_text(),
        (directory / "product.html").read_text(),
    )


def test_every_profile_can_read_its_captured_query_back() -> None:
    # Anything invented here can be a perfume the shop does not stock, and an
    # empty results page for it looks exactly like a dead selector. The captured
    # URL is the one query each site is known to have answered.
    #
    # Asserted as a round-trip rather than "something came back": a query that
    # is read back but does not rebuild the captured URL sends a different
    # request than the one that was captured. A fixture spelling a space as "+"
    # is the real case, since it comes back with the plus still in it and gets
    # escaped to %2B on the way out. This gates every live run, so it covers
    # every profile rather than one.
    for site_id in site_ids():
        profile = load_site_profile(_SITES_DIR / f"{site_id}.json", _PLATFORMS_DIR)
        captured = json.loads((_FIXTURES_DIR / site_id / "meta.json").read_text())[
            "pages"
        ]["search"]["url"]

        query = live_query(profile, _FIXTURES_DIR)

        rebuilt = str(profile["search"]["url_template"]).format(
            base_url=profile["base_url"], query=quote(query, safe="")
        )
        # Compared decoded, because the engine escapes a space as %20 while one
        # capture spells it "+". Those two request the same search; a query that
        # lost or gained a character does not, and that is what this catches.
        assert unquote_plus(rebuilt) == unquote_plus(captured), site_id


def test_a_search_template_that_cannot_produce_the_captured_url_fails_loud() -> None:
    # Two descriptions of the same request disagreeing is a bug in the tooling.
    # Searching for a guessed word instead would report the site as broken.
    profile = json.loads((_SITES_DIR / "venco.json").read_text())
    profile["search"]["url_template"] = "{base_url}/nothing-like-it?q={query}"

    with pytest.raises(LookupError):
        live_query(profile, _FIXTURES_DIR)


async def test_a_working_profile_passes_against_a_site_that_still_answers() -> None:
    # The baseline: the site serves what it served when it was captured, so
    # nothing may be reported as having moved.
    result = await validate_live("venco", fetcher=_fixture_site("venco"))

    assert result.ok, result.failure
    assert [check.name for check in result.checks] == [
        "profile",
        "query",
        "reachable",
        "search",
        "prices",
    ]
    assert "result card(s)" in result.checks[3].detail
    assert result.fallbacks == ()


async def test_live_validation_reports_recognized_product_redirect_format() -> None:
    product_html = (_FIXTURES_DIR / "ruxangroup" / "product.html").read_text()
    fetcher = _FakeSite(
        product_html,
        product_html,
        redirect_url="https://ruxangroup.com/magaza/lattafa-khamrah/",
    )

    result = await validate_live("ruxangroup", fetcher=fetcher)

    assert result.ok, result.failure
    assert result.checks[3].name == "search"
    assert result.checks[3].detail == ("single-product redirect recognized by jsonld")


async def test_live_validation_reports_unclassified_redirect_as_search_failure() -> (
    None
):
    fetcher = _FakeSite(
        "<html><body><div class='related-product'>related</div></body></html>",
        (_FIXTURES_DIR / "ruxangroup" / "product.html").read_text(),
        redirect_url="https://ruxangroup.com/magaza/unclassified/",
    )

    result = await validate_live("ruxangroup", fetcher=fetcher)

    assert not result.ok
    assert [check.name for check in result.checks] == [
        "profile",
        "query",
        "reachable",
        "search",
    ]
    assert "material search redirect" in result.checks[-1].detail


async def test_an_unreachable_site_is_not_reported_as_a_broken_profile() -> None:
    # A shop being down is not a selector that died, and sending someone to
    # audit a profile over it wastes the hour this command exists to save.
    result = await validate_live("venco", fetcher=_DeadSite())

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "reachable"
    assert "ConnectionError" in result.failure.detail
    assert result.fallbacks == ()


async def test_zero_results_on_a_full_page_blames_the_result_selector() -> None:
    # The first row of the fail-loud table: HTTP 200, a page full of markup, and
    # nothing the profile recognises.
    full_page = "<html><body>" + ("<div class='x'>text</div>" * 500) + "</body></html>"
    site = _FakeSite(full_page, full_page)

    result = await validate_live("venco", fetcher=site)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "search"
    assert "result_item" in result.failure.detail


async def test_zero_results_on_a_thin_page_blames_the_site_not_the_profile() -> None:
    # The same empty answer on a few hundred bytes is a challenge or error page
    # wearing a 200. Calling that a dead selector is a lie about the profile.
    site = _FakeSite("<html><body>Access denied</body></html>", "")

    result = await validate_live("venco", fetcher=site)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "search"
    assert "refusing the request" in result.failure.detail


async def test_a_broken_layer_reports_which_other_layer_could_take_over(
    tmp_path: Path,
) -> None:
    # The reason live mode exists beyond "it broke": a profile reading a page on
    # a dead layer while the same page publishes JSON-LD is a one-field repair,
    # and a report that does not say so reads like the site stopped publishing.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        extraction="css",
        product={"variant_container": ".no-such-size"},
        mutate=lambda p: p["variant_rules"].update({"size_from": "title"}),
    )
    search_html = (
        "<html><body>" + "<div class='card-product'>"
        "<a class='c-p-i-link' href='/p/1'>Dior Sauvage 5 ml</a></div>"
        * 40
        + "</body></html>"
    )
    product_html = """
    <html><body><script type="application/ld+json">
    {"@type": "Product", "name": "Dior Sauvage EDP 5 ml",
     "offers": {"@type": "Offer", "price": "149.90", "priceCurrency": "TRY",
                "availability": "https://schema.org/InStock"}}
    </script></body></html>
    """
    site = _FakeSite(search_html, product_html)

    result = await validate_live("venco", sites_dir=sites_dir, fetcher=site)

    assert not result.ok
    working = [check.name for check in result.fallbacks if check.ok]
    assert working == ["jsonld"]
    # Every other layer is reported too, including the ones with no config to
    # run: a layer left out reads as one that was tried and failed.
    assert {check.name for check in result.fallbacks} == {
        "jsonld",
        "endpoint",
        "embedded_json",
    }


async def test_the_live_report_names_the_edit_that_would_repair_the_profile(
    tmp_path: Path,
) -> None:
    # The fix line has to name sites/<id>.json. A platform template is shared,
    # and repairing one site by editing it moves every other site on it.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        extraction="css",
        product={"variant_container": ".no-such-size"},
        mutate=lambda p: p["variant_rules"].update({"size_from": "title"}),
    )
    search_html = (
        "<html><body>" + "<div class='card-product'>"
        "<a class='c-p-i-link' href='/p/1'>Dior Sauvage 5 ml</a></div>"
        * 40
        + "</body></html>"
    )
    product_html = (
        '<html><body><script type="application/ld+json">'
        '{"@type": "Product", "name": "Dior Sauvage EDP 5 ml", "offers": '
        '{"@type": "Offer", "price": "149.90", "availability": "InStock"}}'
        "</script></body></html>"
    )
    offline = await validate_offline("venco")
    live = await validate_live(
        "venco", sites_dir=sites_dir, fetcher=_FakeSite(search_html, product_html)
    )

    report = format_live_report(((offline, live),))

    assert "ok offline" in report
    assert "BROKEN live" in report
    assert '"extraction": "jsonld"' in report
    assert "sites/venco.json" in report
    assert "0/1 profiles pass live" in report


def test_profile_age_is_counted_in_whole_days_from_the_schema_timestamp() -> None:
    # The age is asserted against a fixed "now" rather than today's date, because
    # a test that recomputes the current time would pass no matter what this
    # returns. A partial day does not count: 91 days and 23 hours is still 91.
    now = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)

    assert profile_age_days("2026-08-08T12:00:00Z", now) == 0
    assert profile_age_days("2026-05-09T13:00:00Z", now) == 90
    assert profile_age_days("2026-05-09T12:00:01Z", now) == 90


def test_a_timestamp_that_is_not_the_schema_format_is_rejected() -> None:
    # A local-time or offset stamp would silently shift the age by hours. Nothing
    # downstream can tell a wrong age from a right one, so it has to fail here.
    with pytest.raises(ValueError):
        profile_age_days("2026-08-07T11:22:00+03:00")


async def test_a_profile_that_passes_every_check_is_still_reported_as_stale(
    tmp_path: Path,
) -> None:
    # The reason this milestone step exists. Every check passing means the
    # profile agrees with a capture taken months ago, which is not the same as
    # agreeing with the site today. Without the age line the report would call
    # this site healthy and say nothing about the only evidence to the contrary.
    old = _iso_days_ago(STALE_PROFILE_DAYS + 4)
    sites_dir = _corrupted_sites_dir(tmp_path, "venco", discovered_at=old)

    results = await validate_all_offline(("venco",), sites_dir=sites_dir)

    assert results[0].ok
    assert results[0].stale
    report = format_report(results)
    assert "  ok  " in report
    assert "stale: venco" in report
    assert f"discovered {STALE_PROFILE_DAYS + 4} days ago" in report


async def test_a_fresh_profile_gets_no_age_line(tmp_path: Path) -> None:
    # The badge is only worth anything if it is rare. A line on every site would
    # be scrolled past, which is the same as not printing it.
    fresh = _iso_days_ago(STALE_PROFILE_DAYS - 1)
    sites_dir = _corrupted_sites_dir(tmp_path, "venco", discovered_at=fresh)

    results = await validate_all_offline(("venco",), sites_dir=sites_dir)

    assert not results[0].stale
    assert results[0].age_days == STALE_PROFILE_DAYS - 1
    assert "stale" not in format_report(results)


async def test_a_future_dated_profile_is_called_out_rather_than_read_as_fresh(
    tmp_path: Path,
) -> None:
    # A hand-edited discovered_at in the future would otherwise report as the
    # freshest profile in the list, which is exactly backwards: the one number
    # that can hide a stale profile is the one worth printing.
    sites_dir = _corrupted_sites_dir(
        tmp_path, "venco", discovered_at=_iso_days_ago(-10)
    )

    results = await validate_all_offline(("venco",), sites_dir=sites_dir)

    assert not results[0].stale
    assert "in the future" in format_report(results)


async def test_the_live_report_carries_the_age_from_the_offline_half(
    tmp_path: Path,
) -> None:
    # The live pass never reads discovered_at, so the age in the side-by-side
    # report can only come from the offline result it is paired with. A stale
    # profile that still works live is the case worth printing: nothing is
    # broken yet, and the age is the only reason to go look at it.
    old = _iso_days_ago(STALE_PROFILE_DAYS + 4)
    sites_dir = _corrupted_sites_dir(tmp_path, "venco", discovered_at=old)
    search_html = (
        "<html><body>" + "<div class='card-product'>"
        "<a class='c-p-i-link' href='/p/1'>Dior Sauvage 5 ml</a></div>"
        * 40
        + "</body></html>"
    )
    product_html = (
        '<html><body><script type="application/ld+json">'
        '{"@type": "Product", "name": "Dior Sauvage EDP 5 ml", "offers": '
        '{"@type": "Offer", "price": "149.90", "availability": "InStock"}}'
        "</script></body></html>"
    )
    offline = (await validate_all_offline(("venco",), sites_dir=sites_dir))[0]
    live = await validate_live(
        "venco", sites_dir=sites_dir, fetcher=_FakeSite(search_html, product_html)
    )

    report = format_live_report(((offline, live),))

    assert f"discovered {STALE_PROFILE_DAYS + 4} days ago" in report
    assert "; stale: venco" in report
