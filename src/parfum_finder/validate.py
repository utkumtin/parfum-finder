"""Profile staleness checks. Two modes: offline (against saved fixtures) and live
(against the real site).

Offline mode runs against saved HTML fixtures and needs no network access. Live
mode hits the real site and, if something broke, reports which extraction layer
failed and whether falling back to a lower layer would still work.

What offline mode adds over "the tests pass" is a report that names the broken
step. A profile is a stack of small agreements with one site's markup, and when
one of them dies the useful output is not a traceback but a line saying which
one: the schema, the search selectors, the extraction layer, or the price. That
is also why the site's own `search_site` drives this rather than a second, more
convenient reimplementation of the ladder. A check that runs a different flow
than production only proves the check works.

Live mode asks the site the same question the fixtures answered, with the query
the fixture was captured with, and adds the one thing offline mode cannot see: a
profile that still agrees with a saved page from last month but not with the
site as it is today. When it breaks, the other three extraction layers are tried
on a real product page, so the report says whether the profile can be repaired
by moving it to another layer or whether the site stopped publishing the data
altogether.

Both reports also carry a profile's age, taken from its `discovered_at`. A
profile that passes every check can still be describing a site as it was months
ago, and the age is the only warning that exists before the checks start
failing. Marking a site suspect at runtime lives with the run itself, in
engine.run_site.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, unquote_plus, urljoin, urlparse

from selectolax.parser import HTMLParser

from parfum_finder.engine import ExtractionFailed, apply_variant_rules, search_site
from parfum_finder.extract import (
    RawVariant,
    extract_css_variants,
    extract_embedded_variants,
    extract_jsonld_variants,
    select_field,
)
from parfum_finder.fetch import (
    Fetcher,
    FetchResult,
    FormData,
    Headers,
    Method,
    Strategy,
    fetch,
)
from parfum_finder.profiles import (
    DEFAULT_HOOKS_DIR,
    DEFAULT_PLATFORMS_DIR,
    load_site_profile,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SITES_DIR = _REPO_ROOT / "sites"
DEFAULT_FIXTURES_DIR = _REPO_ROOT / "fixtures"

# The query offline mode searches for. The fixture router answers every search
# URL with the same saved page, so the word itself never reaches a site and only
# has to survive being formatted into a search URL template.
_OFFLINE_QUERY = "test"

# How old a profile gets before the report says so. Nothing breaks at this line,
# it is a prompt to re-run discover, so it is deliberately loose: shops redesign
# on the order of months, and a threshold tight enough to flag every profile
# every week would be read as noise and ignored.
STALE_PROFILE_DAYS = 90

# The one timestamp format profiles are allowed to carry, same as store.now_iso.
_DISCOVERED_AT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass(frozen=True)
class Check:
    """One agreement between a profile and its site, and whether it still holds.

    `detail` is written for whoever has to fix it, so it names the selector or
    the layer rather than restating the check's name. It is filled in on a pass
    as well: a passing check that reports what it saw is how someone notices a
    profile that technically works while reading the wrong thing.
    """

    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class SiteValidation:
    """Every check run against one site's profile, in the order they ran.

    Checks stop at the first failure. Each one builds on the one before it, so
    running the rest after a break would only report the same break again in
    less useful words.

    `fallbacks` is filled in by live mode when a profile broke: one entry per
    extraction layer other than the one the profile uses, saying whether that
    layer would read the page today. It is empty for a profile that works and
    for offline mode, which has nothing new to learn from a page it already
    knows the answer for.

    `age_days` is how long ago the profile was discovered, and it is kept apart
    from `checks` on purpose. Age is not a failure: an old profile that still
    reads its site correctly passes, and folding age into the checks would
    either report a working profile as broken or bury the real break under a
    warning. It is None when the age could not be read, which only happens for
    a profile the `profile` check already reported broken.
    """

    site_id: str
    checks: tuple[Check, ...]
    fallbacks: tuple[Check, ...] = field(default=())
    age_days: int | None = None

    @property
    def stale(self) -> bool:
        """Whether the profile is old enough to be worth re-discovering."""
        return self.age_days is not None and self.age_days >= STALE_PROFILE_DAYS

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    @property
    def failure(self) -> Check | None:
        """The check that broke, or None if the profile is intact."""
        return next((check for check in self.checks if not check.ok), None)


class _FixtureFetcher:
    """Serves one site's saved capture in place of the network.

    Only three kinds of request can happen: the search page, a candidate's
    product page, and, for a POST variant endpoint, one request per size option
    found on that product page. Anything else means the profile is asking for a
    page nobody captured, which is reported rather than guessed at.

    The POST endpoint gets the one real response captured for the one option it
    was captured for, and the endpoint's own real answer for an option it does
    not recognize (an empty options list) for the rest. That is what lets the
    per-option loop finish on a site where only one option's price was ever
    saved.

    One instance serves one run, because it tells the search page apart from the
    rest by being the first GET a run makes. That is what a run always does, and
    the alternative, treating every GET that is not the product page as the
    search page, would hand search HTML to a profile asking for a JSON endpoint
    nobody captured and report the site as answering with the wrong format.
    """

    def __init__(self, site_id: str, fixtures_dir: Path, profile: Mapping[str, Any]):
        self._served_search = False
        self._site_id = site_id
        self._directory = fixtures_dir / site_id
        self._profile = profile
        meta = json.loads((self._directory / "meta.json").read_text())
        self._product_url = str(meta["pages"]["product"]["url"])
        self._related_options = self._directory / "related-options.json"
        self._captured_option = (
            str(meta["pages"]["related_options"]["body"]["selected_options[]"])
            if self._related_options.exists()
            else None
        )

    @property
    def product_url(self) -> str:
        return self._product_url

    def search_page(self) -> str:
        """The one real result card that led to the captured product page.

        Cut out of the real search.html with the profile's own selectors rather
        than hand-copied, so a selector that stopped matching the real markup is
        caught here instead of being papered over by a stand-in. Serving the
        whole page instead would send the engine after product URLs this site
        has no saved bytes for.

        Raises LookupError when no card matches, which is the search-selector
        check failing.
        """
        search = self._profile["search"]
        tree = HTMLParser((self._directory / "search.html").read_text())
        for node in tree.css(str(search["result_item"])):
            href = select_field(node, str(search["result_url"]))
            if href and _path(href) == _path(self._product_url):
                return f"<html><body>{node.html}</body></html>"
        raise LookupError(
            f"no card matched by result_item {search['result_item']!r} + "
            f"result_url {search['result_url']!r} links to {self._product_url}"
        )

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
        if method == "POST":
            body = self._related_options_response(data)
            return FetchResult(url=url, status_code=200, html=body, strategy=strategy)
        if not self._served_search:
            self._served_search = True
            html = self.search_page()
        elif _path(url) == _path(self._product_url):
            html = (self._directory / "product.html").read_text()
        else:
            raise LookupError(
                f"the profile asked for {url}, which fixtures/{self._site_id}/ "
                f"has no saved bytes for; only its search page and "
                f"{self._product_url} were captured"
            )
        return FetchResult(url=url, status_code=200, html=html, strategy=strategy)

    def _related_options_response(self, data: FormData | None) -> str:
        if data is None or self._captured_option is None:
            raise LookupError(
                f"{self._site_id}: the profile posted to its variant endpoint, "
                f"but fixtures/{self._site_id}/ has no related-options.json"
            )
        key = str(self._profile["endpoint"]["option_body_key"])
        if str(data[key]) == self._captured_option:
            return self._related_options.read_text()
        return json.dumps({"success": True, "data": {"options": []}})


def _path(url: str) -> str:
    """A URL's path with no trailing slash, for comparing two spellings of one page."""
    return urlparse(url).path.rstrip("/")


def site_ids(sites_dir: Path = DEFAULT_SITES_DIR) -> tuple[str, ...]:
    """Every site that has a profile, sorted so reports read the same way twice."""
    return tuple(sorted(path.stem for path in sites_dir.glob("*.json")))


def profile_age_days(discovered_at: str, now: datetime | None = None) -> int:
    """Whole days between a profile's `discovered_at` and now.

    Only the exact UTC format the schema requires is accepted. Being lenient
    here would let a profile carrying a local-time or offset timestamp report an
    age that is quietly wrong by hours, and an age badge nobody can trust is
    worse than none: it is the one signal saying a passing profile might still
    be describing a site that has moved on.

    `now` is a parameter so the tests can ask about a fixed date instead of
    today, which is the only way to assert on an age at all.
    """
    stamp = datetime.strptime(discovered_at, _DISCOVERED_AT_FORMAT).replace(tzinfo=UTC)
    return ((now or datetime.now(UTC)) - stamp).days


async def validate_offline(
    site_id: str,
    *,
    sites_dir: Path = DEFAULT_SITES_DIR,
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    platforms_dir: Path = DEFAULT_PLATFORMS_DIR,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
) -> SiteValidation:
    """Check one site's profile against that site's saved fixtures.

    Never raises for a broken profile: a break is the answer this returns, and
    the whole point is to report it for every site instead of stopping at the
    first one. Only a missing profile file is an error, because there is then
    nothing to say anything about.
    """
    checks: list[Check] = []

    try:
        profile = load_site_profile(sites_dir / f"{site_id}.json", platforms_dir)
    except FileNotFoundError:
        raise
    except (ValueError, KeyError) as e:
        checks.append(Check("profile", False, str(e)))
        return SiteValidation(site_id, tuple(checks))
    checks.append(
        Check(
            "profile",
            True,
            f"loads, {profile['extraction']} layer over {profile['strategy']}",
        )
    )

    try:
        fetcher = _FixtureFetcher(site_id, fixtures_dir, profile)
    except (OSError, KeyError, json.JSONDecodeError) as e:
        checks.append(Check("fixtures", False, f"cannot read fixtures/{site_id}/: {e}"))
        return SiteValidation(site_id, tuple(checks))
    checks.append(Check("fixtures", True, f"fixtures/{site_id}/ read"))

    try:
        search_html = fetcher.search_page()
    except LookupError as e:
        checks.append(Check("search", False, str(e)))
        return SiteValidation(site_id, tuple(checks))
    checks.append(Check("search", True, f"result card found, {len(search_html)} bytes"))

    try:
        hits = await search_site(
            profile, _OFFLINE_QUERY, hooks_dir=hooks_dir, fetcher=fetcher
        )
    except (ExtractionFailed, LookupError, ValueError, KeyError) as e:
        checks.append(Check("extraction", False, str(e)))
        return SiteValidation(site_id, tuple(checks))

    variants = tuple(variant for hit in hits for variant in hit.variants)
    if not variants:
        checks.append(
            Check(
                "extraction",
                False,
                f"the {profile['extraction']!r} layer read no decant size off "
                f"{fetcher.product_url}",
            )
        )
        return SiteValidation(site_id, tuple(checks))
    checks.append(
        Check(
            "extraction",
            True,
            f"{len(variants)} decant size(s) off the {profile['extraction']} layer",
        )
    )

    priced = tuple(
        v for v in variants if v.price_kurus is not None and v.price_kurus > 0
    )
    if not priced:
        # Every size sold out is a real thing a saved page can show, but a whole
        # capture without one readable price means the price selector or the
        # site's number format moved.
        checks.append(
            Check(
                "prices",
                False,
                f"none of the {len(variants)} sizes carries a price, so nothing "
                f"here can be compared on cost",
            )
        )
        return SiteValidation(site_id, tuple(checks))
    checks.append(Check("prices", True, f"{len(priced)} of {len(variants)} priced"))

    return SiteValidation(site_id, tuple(checks))


async def validate_all_offline(
    ids: tuple[str, ...] | None = None,
    *,
    sites_dir: Path = DEFAULT_SITES_DIR,
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    platforms_dir: Path = DEFAULT_PLATFORMS_DIR,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
) -> tuple[SiteValidation, ...]:
    """Validate every site, or just the ones named.

    Serial rather than concurrent: nothing here touches the network, so the only
    thing parallelism would buy is a report whose lines arrive out of order.

    The age is stapled on here rather than computed inside validate_offline
    because it is not a check: it comes straight off the profile file without
    running anything, and threading it through every early return of a function
    whose job is to stop at the first break would only spread it around.
    """
    return tuple(
        [
            replace(
                await validate_offline(
                    site_id,
                    sites_dir=sites_dir,
                    fixtures_dir=fixtures_dir,
                    platforms_dir=platforms_dir,
                    hooks_dir=hooks_dir,
                ),
                age_days=_age_of(sites_dir / f"{site_id}.json"),
            )
            for site_id in (ids if ids is not None else site_ids(sites_dir))
        ]
    )


def _age_of(path: Path) -> int | None:
    """The profile's age in days, or None if the file cannot say.

    Reads the site file directly instead of the merged profile: `discovered_at`
    is the site's own field and a platform template has no business supplying
    one. None means the file is unreadable or its timestamp is not in the schema
    format, and in both cases validate_offline's `profile` check has already
    reported the same file as broken with a better message.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return profile_age_days(raw["discovered_at"])
    except (OSError, ValueError, TypeError, KeyError):
        return None


# The extraction ladder, most durable first. Live mode walks it when a profile
# breaks, to say whether another layer can still read the page.
_LAYERS = ("jsonld", "endpoint", "embedded_json", "css")

# A search page that came back this small answered with something other than a
# result list -- a challenge page, an error page, a redirect stub. Zero results
# on a page like that says nothing about the profile's selectors, which is the
# distinction the fail-loud table draws between "0 results on a full page" and
# an empty answer.
_THIN_PAGE_BYTES = 5000


class _RecordingFetcher:
    """The real fetcher, remembering what came back.

    Live mode needs the search page's status code and size to tell a dead
    selector apart from a site that refused the request, and search_site does
    not hand those back. Wrapping the fetcher gets them without fetching the
    page a second time, and keeps production's own flow the thing being
    measured.
    """

    def __init__(self, inner: Fetcher):
        self._inner = inner
        self.pages: list[FetchResult] = []

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
        result = await self._inner(
            url,
            strategy,
            method=method,
            data=data,
            headers=headers,
            timeout_s=timeout_s,
        )
        self.pages.append(result)
        return result


def live_query(
    profile: Mapping[str, Any], fixtures_dir: Path = DEFAULT_FIXTURES_DIR
) -> str:
    """The query this site's fixture was captured with, read back out of its URL.

    Live mode has to search for something, and anything invented here can be a
    perfume the shop genuinely does not stock -- which comes back as an empty
    results page and reads exactly like a dead selector. The captured search URL
    is the one query this site is known to have answered with a real card, so it
    is the only query that makes an empty answer mean something.

    Raises LookupError when the profile's template cannot be matched against the
    captured URL. That is a mismatch between two things that are supposed to
    describe the same request, and guessing a query instead would turn it into a
    report that the site broke.
    """
    meta = json.loads((fixtures_dir / str(profile["id"]) / "meta.json").read_text())
    captured = str(meta["pages"]["search"]["url"])
    template = str(profile["search"]["url_template"])
    pattern = (
        re.escape(template)
        .replace(re.escape("{base_url}"), re.escape(str(profile["base_url"])))
        .replace(re.escape("{query}"), "(.+)")
    )
    match = re.fullmatch(pattern, captured)
    if match is None:
        raise LookupError(
            f"the search template {template!r} does not describe the captured "
            f"search URL {captured}, so the query it was captured with cannot "
            f"be read back"
        )
    # A query sitting in the query string may spell its spaces as "+", and one
    # real capture does. Reading that back with plain unquote would search for
    # "club+de+nuit" with the pluses still in it, which is not what was asked
    # the first time and comes back as a shop that stopped stocking anything.
    # In a path segment a "+" is a literal plus, so the two are decoded apart.
    question = captured.find("?")
    in_query_string = 0 <= question < match.start(1)
    return unquote_plus(match.group(1)) if in_query_string else unquote(match.group(1))


async def validate_live(
    site_id: str,
    *,
    sites_dir: Path = DEFAULT_SITES_DIR,
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    platforms_dir: Path = DEFAULT_PLATFORMS_DIR,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
    fetcher: Fetcher = fetch,
) -> SiteValidation:
    """Run one site's profile against the real site.

    Same contract as offline mode: a break is the return value, not an
    exception, so one unreachable host cannot end a run over every site. A
    transport error, a browser that is not installed and an HTTP 403 all land in
    the report as their own wording, because none of them is a broken profile
    and auditing selectors over one of them is an hour spent on nothing.

    When the profile does break, every other extraction layer is tried against a
    real product page and the result goes in `fallbacks`. That is what turns
    "css stopped working" into either "move this profile to jsonld" or "this
    site publishes nothing readable any more", which are very different amounts
    of work.

    `fetcher` is a parameter for the same reason it is one in search_site: the
    tests for this drive it with a stand-in, since a test that depends on a
    shop's inventory today is not a test of this module.
    """
    checks: list[Check] = []

    try:
        profile = load_site_profile(sites_dir / f"{site_id}.json", platforms_dir)
    except FileNotFoundError:
        raise
    except (ValueError, KeyError) as e:
        checks.append(Check("profile", False, str(e)))
        return SiteValidation(site_id, tuple(checks))
    checks.append(
        Check(
            "profile",
            True,
            f"loads, {profile['extraction']} layer over {profile['strategy']}",
        )
    )

    try:
        query = live_query(profile, fixtures_dir)
    except (OSError, LookupError, KeyError, json.JSONDecodeError) as e:
        checks.append(Check("query", False, str(e)))
        return SiteValidation(site_id, tuple(checks))
    checks.append(Check("query", True, f"searching the live site for {query!r}"))

    recorder = _RecordingFetcher(fetcher)
    try:
        hits = await search_site(profile, query, hooks_dir=hooks_dir, fetcher=recorder)
    except ExtractionFailed as e:
        checks.append(Check("extraction", False, str(e)))
        return SiteValidation(
            site_id,
            tuple(checks),
            await _probe_other_layers(profile, recorder, fetcher),
        )
    except Exception as e:  # noqa: BLE001 -- see below
        # Anything the network, a bot wall or a missing browser can throw. This
        # is deliberately wide: the alternative is a list of every exception
        # three fetch backends can raise, and the one that is not on the list
        # ends the whole multi-site run over a site that was merely down.
        checks.append(Check("reachable", False, f"{type(e).__name__}: {e}"))
        return SiteValidation(site_id, tuple(checks))

    page = recorder.pages[0] if recorder.pages else None
    if page is None or page.status_code != 200:
        status = page.status_code if page is not None else "no response"
        checks.append(Check("reachable", False, f"the search page answered {status}"))
        return SiteValidation(site_id, tuple(checks))
    checks.append(Check("reachable", True, f"search page 200, {len(page.html)} bytes"))

    cards = _count_result_cards(profile, page.html)
    if not cards:
        checks.append(_no_results_check(profile, page))
        return SiteValidation(
            site_id,
            tuple(checks),
            await _probe_other_layers(profile, recorder, fetcher),
        )
    checks.append(Check("search", True, f"{cards} result card(s) for {query!r}"))

    priced = tuple(
        variant
        for hit in hits
        for variant in hit.variants
        if variant.price_kurus is not None
    )
    if not priced:
        checks.append(
            Check(
                "prices",
                False,
                f"the {profile['extraction']!r} layer read no priced decant size "
                f"off any of the {cards} result(s)",
            )
        )
        return SiteValidation(
            site_id,
            tuple(checks),
            await _probe_other_layers(profile, recorder, fetcher),
        )
    checks.append(
        Check(
            "prices",
            True,
            f"{len(priced)} priced decant size(s) off the "
            f"{profile['extraction']} layer",
        )
    )
    return SiteValidation(site_id, tuple(checks))


def _no_results_check(profile: Mapping[str, Any], page: FetchResult) -> Check:
    """Why an empty results page is suspicious, or why it is not.

    A full page that answered 200 with no card the profile recognises is the
    first row of the fail-loud table: the selector most likely died. The same
    empty answer on a page of a few hundred bytes is a challenge or an error
    page wearing a 200, and blaming the selector for it sends whoever reads the
    report to the wrong file.
    """
    selector = profile["search"]["result_item"]
    if len(page.html) < _THIN_PAGE_BYTES:
        return Check(
            "search",
            False,
            f"the search page answered 200 with only {len(page.html)} bytes, "
            f"which is too little to be a result list; the site is likely "
            f"refusing the request rather than the profile being broken",
        )
    return Check(
        "search",
        False,
        f"no card matched by result_item {selector!r} on a {len(page.html)} byte "
        f"page that answered 200",
    )


def _count_result_cards(profile: Mapping[str, Any], html: str) -> int:
    """How many result rows the profile's own selectors find on a search page."""
    search = profile["search"]
    return sum(
        1
        for node in HTMLParser(html).css(str(search["result_item"]))
        if select_field(node, str(search["result_url"]))
    )


async def _probe_other_layers(
    profile: Mapping[str, Any], recorder: _RecordingFetcher, fetcher: Fetcher
) -> tuple[Check, ...]:
    """Try every extraction layer the profile is not using, on a real page.

    Every layer is reported, including the ones that cannot be tried at all: a
    layer left out of the report reads as one that was tried and failed, and
    "no fallback exists" is the answer that makes someone rewrite a profile from
    scratch. A layer with no configuration in this profile has nothing to run,
    so it says so instead.

    The product page comes from the search results that were just fetched, so
    nothing is probed against a page the live search did not actually offer.
    """
    product_url = _first_result_url(profile, recorder)
    if product_url is None:
        return (
            Check(
                "fallback",
                False,
                "the live search offered no product page, so no other "
                "extraction layer could be tried",
            ),
        )
    # The run that just failed usually fetched this page already. Asking for it
    # a second time is a second request at a shop that may be rate-limiting, and
    # if that one gets refused the fallback diagnosis is lost with it, which is
    # the one thing the live pass went out to produce. The recorded page is only
    # missing for a layer that never opens the product page, such as a GET
    # endpoint that reads a JSON URL instead.
    html = next(
        (
            page.html
            for page in recorder.pages[1:]
            if page.status_code == 200 and _path(page.url) == _path(product_url)
        ),
        None,
    )
    if html is None:
        try:
            fetched = await fetcher(
                product_url,
                profile["strategy"],
                headers=profile.get("request_headers"),
                timeout_s=int(profile.get("timeout_s", 20)),
            )
        except Exception as e:  # noqa: BLE001 -- same reason as in validate_live
            return (Check("fallback", False, f"{product_url} could not be read: {e}"),)
        html = fetched.html

    return tuple(
        _probe_layer(profile, layer, html)
        for layer in _LAYERS
        if layer != profile["extraction"]
    )


def _first_result_url(
    profile: Mapping[str, Any], recorder: _RecordingFetcher
) -> str | None:
    """The first product link on the recorded search page, if there is one."""
    if not recorder.pages:
        return None
    search = profile["search"]
    page = recorder.pages[0]
    for node in HTMLParser(page.html).css(str(search["result_item"])):
        href = select_field(node, str(search["result_url"]))
        if href:
            return urljoin(page.url, href)
    return None


def _probe_layer(profile: Mapping[str, Any], layer: str, html: str) -> Check:
    """Whether one extraction layer could read priced decants off this page.

    The profile's own variant rules still decide what counts as a decant, so a
    layer that "works" here works in the sense the site needs it to: it produces
    rows the engine would keep, not merely rows.
    """
    try:
        rows = _rows_for_layer(profile, layer, html)
    except _LayerUnavailable as e:
        return Check(layer, False, str(e))
    except Exception as e:  # noqa: BLE001 -- a layer that throws is a layer that
        # does not work here, and that is the whole question being asked.
        return Check(layer, False, f"{type(e).__name__}: {e}")
    variants = apply_variant_rules(rows, profile["variant_rules"])
    priced = [v for v in variants if v.price_kurus is not None]
    if not priced:
        return Check(layer, False, f"read no priced decant size ({len(rows)} raw rows)")
    return Check(layer, True, f"reads {len(priced)} priced decant size(s)")


class _LayerUnavailable(Exception):
    """This profile carries no configuration for the layer being probed."""


def _rows_for_layer(
    profile: Mapping[str, Any], layer: str, html: str
) -> tuple[RawVariant, ...]:
    """Run one extraction layer over a product page's bytes."""
    if layer == "jsonld":
        return extract_jsonld_variants(html)
    if layer == "embedded_json":
        config = profile.get("embedded_json")
        if not config:
            raise _LayerUnavailable(
                "not tried: this profile has no embedded_json block to run"
            )
        return extract_embedded_variants(html, config)
    if layer == "css":
        config = profile.get("product")
        if not config:
            raise _LayerUnavailable("not tried: this profile has no product selectors")
        return extract_css_variants(html, config)
    config = profile.get("endpoint")
    if not config:
        raise _LayerUnavailable("not tried: this profile has no endpoint block")
    # Neither endpoint shape can be answered from the product page's bytes: a
    # GET endpoint lives at its own URL and a POST one answers a size option at
    # a time, built out of ids read off the page. Running either from here would
    # be a second copy of the engine's request loop, and a subtly wrong copy
    # would report a fallback that production cannot actually use.
    raise _LayerUnavailable(
        "not tried: the endpoint layer is its own request, which this probe "
        "does not make"
    )


async def validate_all_live(
    ids: tuple[str, ...] | None = None,
    *,
    sites_dir: Path = DEFAULT_SITES_DIR,
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR,
    platforms_dir: Path = DEFAULT_PLATFORMS_DIR,
    hooks_dir: Path = DEFAULT_HOOKS_DIR,
    fetcher: Fetcher = fetch,
) -> tuple[SiteValidation, ...]:
    """Validate every site against the live web, or just the ones named.

    Serial like the offline pass, and here for a second reason beyond ordered
    output: this is the one part of the project that hits several shops in a row
    on purpose, and doing it one request at a time is the polite version.
    """
    return tuple(
        [
            await validate_live(
                site_id,
                sites_dir=sites_dir,
                fixtures_dir=fixtures_dir,
                platforms_dir=platforms_dir,
                hooks_dir=hooks_dir,
                fetcher=fetcher,
            )
            for site_id in (ids if ids is not None else site_ids(sites_dir))
        ]
    )


def format_report(results: tuple[SiteValidation, ...]) -> str:
    """Render the validations as the offline half of the report in APP_FLOW §6.

    A passing site takes one line, because a wall of green is what makes the one
    red line easy to miss. A failing site gets the name of the step that broke
    and its detail underneath, which is the whole reason to run this.

    A stale profile adds its own line under the site, and the closing summary
    counts stale profiles separately from broken ones. They are different jobs:
    a broken profile needs fixing now, a stale one needs re-discovering before
    it breaks.
    """
    if not results:
        return "no site profiles to validate."
    width = max(len(result.site_id) for result in results)
    lines: list[str] = []
    for result in results:
        failure = result.failure
        if failure is None:
            last = result.checks[-1]
            lines.append(f"{result.site_id:<{width}}  ok       {last.detail}")
        else:
            lines.append(f"{result.site_id:<{width}}  BROKEN   {failure.name}")
            lines.append(f"{' ' * width}           -> {failure.detail}")
        age_line = _age_line(result)
        if age_line is not None:
            lines.append(f"{' ' * width}           {age_line}")
    broken = [result.site_id for result in results if not result.ok]
    stale = [result.site_id for result in results if result.stale]
    lines.append("")
    lines.append(
        f"{len(results) - len(broken)}/{len(results)} profiles pass offline"
        + (f"; broken: {', '.join(broken)}" if broken else "")
        + (f"; stale: {', '.join(stale)}" if stale else "")
    )
    return "\n".join(lines)


def _age_line(result: SiteValidation) -> str | None:
    """The age note for one site, or None when its age is unremarkable.

    A profile younger than the threshold says nothing worth a line. A profile
    dated in the future does: it means someone hand-edited `discovered_at`, and
    the number that hides a stale profile is exactly the one worth showing.
    """
    if result.age_days is None:
        return None
    if result.age_days < 0:
        return (
            f"suspect age: discovered_at is {-result.age_days} day(s) in the "
            f"future, so this profile's age says nothing"
        )
    if result.age_days < STALE_PROFILE_DAYS:
        return None
    return (
        f"stale: discovered {result.age_days} days ago, over the "
        f"{STALE_PROFILE_DAYS}-day mark -- re-run discover"
    )


def format_live_report(
    pairs: tuple[tuple[SiteValidation, SiteValidation], ...],
) -> str:
    """Render offline and live results side by side, as APP_FLOW §6 shows them.

    Both columns are printed even when the offline one passes, because the pair
    is the diagnosis: offline ok plus live broken means the site moved, while
    both broken means the profile was already wrong about the bytes on disk and
    the live run has nothing to add.

    A live break is followed by what the other extraction layers said, one line
    each, including the ones that could not be tried. A layer that works comes
    with the edit that would adopt it, naming sites/<id>.json rather than the
    platform template: a platform file is shared, and repairing one site by
    editing it moves every other site on that platform too.

    The age note comes from the offline half of the pair, since the age is a
    property of the profile file and the live pass never reads it.
    """
    if not pairs:
        return "no site profiles to validate."
    width = max(len(offline.site_id) for offline, _ in pairs)
    lines: list[str] = []
    for offline, live in pairs:
        offline_cell = "ok offline" if offline.ok else "BROKEN offline"
        live_cell = "ok live" if live.ok else "BROKEN live"
        summary = (
            live.checks[-1].detail
            if live.ok
            else f"{live.failure.name}: {live.failure.detail}"
            if live.failure is not None
            else "no checks ran"
        )
        lines.append(
            f"{offline.site_id:<{width}}  {offline_cell:<14}  "
            f"{live_cell:<11}  {summary}"
        )
        if not offline.ok and offline.failure is not None:
            lines.append(
                f"{' ' * width}  offline: {offline.failure.name}: "
                f"{offline.failure.detail}"
            )
        for fallback in live.fallbacks:
            mark = "works now" if fallback.ok else "no"
            lines.append(
                f"{' ' * width}  -> {fallback.name} layer {mark}: {fallback.detail}"
            )
            if fallback.ok:
                lines.append(
                    f'{" " * width}     set "extraction": "{fallback.name}" in '
                    f"sites/{live.site_id}.json"
                )
        age_line = _age_line(offline)
        if age_line is not None:
            lines.append(f"{' ' * width}  {age_line}")
    broken = [live.site_id for _, live in pairs if not live.ok]
    stale = [offline.site_id for offline, _ in pairs if offline.stale]
    lines.append("")
    lines.append(
        f"{len(pairs) - len(broken)}/{len(pairs)} profiles pass live"
        + (f"; broken: {', '.join(broken)}" if broken else "")
        + (f"; stale: {', '.join(stale)}" if stale else "")
    )
    return "\n".join(lines)
