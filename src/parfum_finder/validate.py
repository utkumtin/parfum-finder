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

TODO: --live mode, marking a site "suspect" at runtime when checks fail, and an
age badge based on when a profile was last (re)discovered.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from selectolax.parser import HTMLParser

from parfum_finder.engine import ExtractionFailed, search_site
from parfum_finder.extract import select_field
from parfum_finder.fetch import FetchResult, FormData, Method, Strategy
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
    """

    site_id: str
    checks: tuple[Check, ...]

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
    """
    return tuple(
        [
            await validate_offline(
                site_id,
                sites_dir=sites_dir,
                fixtures_dir=fixtures_dir,
                platforms_dir=platforms_dir,
                hooks_dir=hooks_dir,
            )
            for site_id in (ids if ids is not None else site_ids(sites_dir))
        ]
    )


def format_report(results: tuple[SiteValidation, ...]) -> str:
    """Render the validations as the offline half of the report in APP_FLOW §6.

    A passing site takes one line, because a wall of green is what makes the one
    red line easy to miss. A failing site gets the name of the step that broke
    and its detail underneath, which is the whole reason to run this.
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
    broken = [result.site_id for result in results if not result.ok]
    lines.append("")
    lines.append(
        f"{len(results) - len(broken)}/{len(results)} profiles pass offline"
        + (f"; broken: {', '.join(broken)}" if broken else "")
    )
    return "\n".join(lines)
