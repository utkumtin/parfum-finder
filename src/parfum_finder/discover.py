"""Site discovery: turns a URL into a profile, with human review. Not fully automatic.

Flow: measure which fetch strategy the site needs, fingerprint the platform if it's
recognizable, walk the extraction ladder to find the most durable layer that works,
then run an end-to-end trial (a sample search plus a sample product page) and show
the extracted fields with evidence and a confidence score. Low-confidence fields get
flagged for manual review, and shipping data is never guessed. It's always entered
by hand afterward.

This version does the measurement, the platform fingerprint and the JSON-LD trial,
and it writes no profile to disk. It reads a page, says which fetch strategy it
picked and why, says which platform template recognizes the markup and what that
template would hand a profile, shows what the page's JSON-LD actually declares,
and flags the case where the markup offers a size selector but only one price
could be read. A human reads that output and writes down what the site is really
doing.

The sample-search half of the trial is still missing. A template that supplies a
search URL now makes it possible in principle, but running one needs a query term
and a way to read the results, and neither belongs to the fingerprint step.
Guessing here would produce a trial that measures the guess rather than the site.

TODO: per-field confidence scores, and writing the profile out with the
low-confidence fields listed for review.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from curl_cffi import CurlError
from selectolax.parser import HTMLParser

from parfum_finder.extract import JsonLdProduct, extract_jsonld_products
from parfum_finder.fetch import (
    PlaywrightNoResponse,
    PlaywrightNotInstalled,
    Strategy,
    fetch,
)
from parfum_finder.probe import ProbeAttempt, ProbeReport, probe
from parfum_finder.probe import format_report as format_probe_report
from parfum_finder.profiles import DEFAULT_PLATFORMS_DIR, load_platform_templates
from parfum_finder.store import now_iso

# What a request that never completed looks like, as opposed to a request that
# came back with a bad status. Kept apart from PlaywrightNotInstalled, which is
# re-raised: a setup that cannot run at all is not a property of the site being
# discovered, and hiding it inside a trial row would make the report look like
# the site refused us. Playwright's own error type only exists once the package
# is installed, so it is added conditionally and this module stays importable
# without the extra.
# Asked which of several matching templates to apply, and free to answer None
# for "none of them". The caller owns how the question is put, so a terminal can
# prompt and a test can answer without one. Declining has to stay possible: a
# question that only accepts a template forces a pick, which is the same wrong
# answer as picking silently, just with a person's name on it.
PlatformChooser = Callable[[tuple[str, ...]], str | None]

_FETCH_ERROR_TYPES: tuple[type[Exception], ...] = (
    httpx.RequestError,
    CurlError,
    PlaywrightNoResponse,
)
try:
    from playwright.async_api import Error as _PlaywrightError

    _FETCH_ERROR_TYPES = (*_FETCH_ERROR_TYPES, _PlaywrightError)
except ImportError:
    pass

# Markup that lets a shopper pick a size. Its presence next to a single readable
# price is the quiet failure this project cares most about: the other sizes exist,
# they just arrive by a request this page never made, so a naive read compares one
# site's 5 ml price against another's 50 ml price. Turkish stores write "varyant"
# and "secenek" as often as the English words, and CSS attribute matching is case
# sensitive, so the lowercase spellings are the ones that hit in practice.
_VARIANT_CONTROL_SELECTOR = ", ".join(
    (
        '[class*="variant"]',
        '[class*="varyant"]',
        '[class*="secenek"]',
        "[data-variant]",
        "[data-variant-id]",
        'select[name*="variant"]',
        'select[name*="varyant"]',
        'select[name*="option"]',
        'select[name*="secenek"]',
        # WooCommerce variable products spell it "variation", which shares no
        # substring with "variant", so the entries above miss them entirely.
        # Its markup is a form carrying every variation as an escaped JSON blob
        # plus one select per attribute, named attribute_pa_<something>. Both of
        # those belong to the product being sold. A looser match on "variation"
        # is not usable here: shop themes hang that word on the swatches of the
        # related-products grid too, so a simple product with no sizes of its
        # own would come back looking like it had them.
        "[data-product_variations]",
        '[class*="variations_form"]',
        'select[name^="attribute_"]',
    )
)


@dataclass(frozen=True)
class PageTrial:
    """One page fetched with the chosen strategy and read for JSON-LD.

    A fetch that never completed sets `error` and leaves the rest empty. A fetch
    that came back fills the rest and leaves `error` None.
    """

    url: str
    status_code: int | None
    error: str | None
    html_chars: int | None
    products: tuple[JsonLdProduct, ...]
    variant_control_present: bool
    # Platform templates whose fingerprint matched this page, in name order.
    # Per page rather than per site because the answer can differ: a search page
    # fetched as an empty shell carries none of the markers its product page does.
    platform_matches: tuple[str, ...]
    # The name this page was saved under, "search" or "product", and where it
    # landed. Both stay None when the page was only read and not kept.
    role: str | None = None
    fixture_path: Path | None = None
    sha256: str | None = None


@dataclass(frozen=True)
class DiscoveryReport:
    url: str
    strategy_report: ProbeReport
    # None when no strategy qualified. There is no fallback pick in that case:
    # naming a strategy that failed the measurement would put a guess into the
    # profile, which is the one thing this whole command exists to avoid.
    chosen_strategy: Strategy | None
    trials: tuple[PageTrial, ...]
    # Set only when the caller overrode the measurement. The measured winner
    # stays in chosen_strategy so the report can print both and a reader can
    # see that the override was a decision, not a measurement.
    forced_strategy: Strategy | None = None
    fixtures_dir: Path | None = None
    # The entry page's template matches. Empty both when nothing matched and
    # when no page was read at all; `trials` tells those two apart, and the
    # report spells out which one happened rather than leaving it to the reader.
    platform_matches: tuple[str, ...] = ()
    # The applied template's defaults, filled only when a platform was resolved.
    applied_defaults: dict[str, Any] | None = None
    # Set only when several templates matched and someone picked between them.
    # Kept apart from platform_matches so the report can still say that the
    # fingerprints collided, which stays a template bug after the pick is made.
    chosen_platform: str | None = None

    @property
    def trial_strategy(self) -> Strategy | None:
        """The strategy the trials actually ran with."""
        return self.forced_strategy or self.chosen_strategy

    @property
    def platform(self) -> str | None:
        """The template this site's profile would be based on, if any."""
        return _resolve_platform(self.platform_matches, self.chosen_platform)


def _resolve_platform(matches: tuple[str, ...], chosen: str | None) -> str | None:
    """Which of the matching templates gets applied, or None for none of them.

    One match is the answer on its own. Several is not a tie to be broken by
    ordering: two platforms cannot both be true, so one of the fingerprints is
    wrong, and applying either one unasked would write a guess into the profile.
    Someone has to say which, and `chosen` is that answer.
    """
    if chosen is not None:
        return chosen
    return matches[0] if len(matches) == 1 else None


def _ask_chooser(
    chooser: PlatformChooser | None, matches: tuple[str, ...]
) -> str | None:
    """Put the question only when there is one, and hold the answer to it.

    An answer naming a template that did not match is not a choice between the
    candidates, it is a different claim about the site, and letting it through
    would apply a template whose markers are nowhere in the page. Raised rather
    than ignored, because a chooser that answers off the list is broken and a
    silently dropped answer looks exactly like a person declining.
    """
    if len(matches) < 2 or chooser is None:
        return None
    picked = chooser(matches)
    if picked is not None and picked not in matches:
        raise ValueError(
            f"chooser picked {picked!r}, which is not one of the templates that "
            f"matched this page: {', '.join(matches)}."
        )
    return picked


async def discover(
    url: str,
    *,
    product_url: str | None = None,
    search_url: str | None = None,
    timeout_s: int = 20,
    strategy: Strategy | None = None,
    fixtures_dir: Path | None = None,
    platforms_dir: Path = DEFAULT_PLATFORMS_DIR,
    chooser: PlatformChooser | None = None,
) -> DiscoveryReport:
    """Measure the strategies a site needs, then read its JSON-LD with the winner.

    `product_url` and `search_url` are optional and each take one more page from
    the same site. A listing URL and one product page compared in a single report
    is what tells a reader whether each size is its own product or one product
    carries all the sizes.

    The winning strategy is fetched again for the trial rather than reusing the
    HTML from the measurement, which costs one extra request per page and buys
    an independent confirmation that the chosen strategy really works. `strategy`
    overrides that pick for the trials, which is needed when one page of a site
    needs a heavier rung than its front page did.

    `fixtures_dir` turns the trials into a golden capture: the search and product
    pages are written there as HTML alongside a meta.json recording where each
    came from. The first URL is never saved, because it is the page the strategies
    were measured against and nothing extracts from it.

    Every template in `platforms_dir` is matched against the entry page. Exactly
    one match names the platform and its defaults are reported as the base a
    profile would start from. Several matches ask `chooser` which one to apply,
    and with no chooser, or one that declines, nothing is applied. No caller
    ever gets the first match by default.

    Raises PlaywrightNotInstalled, uncaught, if the playwright rung cannot run
    on this machine. The measurement is only honest if every rung was actually
    tried, so an incomplete setup has to stop the run rather than quietly leave
    playwright out of the comparison.

    Raises ValueError, uncaught, if any template in `platforms_dir` is broken.
    It is raised before the first request, because a run that fingerprints
    against half a library reports "no platform" for a site whose template is
    sitting right there, unreadable.
    """
    templates = load_platform_templates(platforms_dir)
    strategy_report = await probe(url, timeout_s=timeout_s)
    chosen = _choose_strategy(strategy_report)
    used = strategy or chosen
    trials: tuple[PageTrial, ...] = ()
    if used is not None:
        targets: list[tuple[str, str | None]] = [(url, None)]
        if search_url is not None:
            targets.append((search_url, "search"))
        if product_url is not None:
            targets.append((product_url, "product"))
        trials = tuple(
            [
                await _trial(
                    u,
                    used,
                    timeout_s=timeout_s,
                    role=role,
                    fixtures_dir=fixtures_dir,
                    templates=templates,
                )
                for u, role in targets
            ]
        )
    # The entry page is the one the site is judged on. A search or product page
    # given on the command line can be a rendered shell that lost the markers.
    matches = trials[0].platform_matches if trials else ()
    picked = _ask_chooser(chooser, matches)
    platform = _resolve_platform(matches, picked)
    report = DiscoveryReport(
        url=url,
        strategy_report=strategy_report,
        chosen_strategy=chosen,
        trials=trials,
        forced_strategy=strategy,
        fixtures_dir=fixtures_dir,
        platform_matches=matches,
        applied_defaults=templates[platform]["defaults"] if platform else None,
        chosen_platform=picked,
    )
    if fixtures_dir is not None:
        _write_meta(report)
    return report


def _choose_strategy(report: ProbeReport) -> Strategy | None:
    """Pick the cheapest strategy that came back with real content, or None.

    probe deliberately refuses to name a winner, because an HTTP status on its
    own cannot tell a rendered page from an empty shell. So the rule here needs
    more than a status: a rung qualifies only if it also brought back something
    that looks like a product. The rungs are already ordered cheapest first, so
    the first qualifying one wins, and format_report prints every rung's verdict
    so a reader can see the rule applied rather than take the answer on trust.
    """
    for attempt in report.attempts:
        if _qualifies(attempt):
            return attempt.strategy
    return None


def _qualifies(attempt: ProbeAttempt) -> bool:
    """Whether one strategy came back with a usable page."""
    if attempt.error is not None or attempt.status_code is None:
        return False
    if not 200 <= attempt.status_code < 300:
        return False
    return bool(attempt.jsonld_product_count) or bool(attempt.product_markup_nodes)


async def _trial(
    url: str,
    strategy: Strategy,
    *,
    timeout_s: int,
    templates: dict[str, dict[str, Any]],
    role: str | None = None,
    fixtures_dir: Path | None = None,
) -> PageTrial:
    try:
        result = await fetch(url, strategy, timeout_s=timeout_s)
    except PlaywrightNotInstalled:
        raise  # never swallow an unusable setup, see discover()'s docstring
    except _FETCH_ERROR_TYPES as e:
        return PageTrial(
            url=url,
            status_code=None,
            # The exception type is half the evidence: a connection refused, a
            # read timeout and a TLS failure all point at different fixes.
            error=f"{type(e).__name__}: {e}",
            html_chars=None,
            products=(),
            variant_control_present=False,
            platform_matches=(),
            role=role,
        )

    fixture_path = None
    digest = None
    if role is not None and fixtures_dir is not None:
        fixture_path, digest = _save_fixture(fixtures_dir, role, result.html)

    tree = HTMLParser(result.html)
    return PageTrial(
        url=result.url,
        status_code=result.status_code,
        error=None,
        html_chars=len(result.html),
        products=extract_jsonld_products(result.html),
        variant_control_present=bool(tree.css(_VARIANT_CONTROL_SELECTOR)),
        platform_matches=_match_platforms(result.html, templates),
        role=role,
        fixture_path=fixture_path,
        sha256=digest,
    )


def _match_platforms(
    html: str, templates: dict[str, dict[str, Any]]
) -> tuple[str, ...]:
    """Every template with at least one of its markers somewhere in the page.

    Case-insensitive, because a marker is usually a path or a domain that a theme
    is free to write either way, and matching on case would turn a real platform
    into an unrecognized one. Substring matching over the raw HTML rather than
    parsed markup: markers live in script bodies, attribute values and comments
    just as often as in tags.
    """
    lowered = html.lower()
    return tuple(
        name
        for name, template in sorted(templates.items())
        if any(marker.lower() in lowered for marker in template["fingerprint"]["any"])
    )


def _save_fixture(fixtures_dir: Path, role: str, html: str) -> tuple[Path, str]:
    """Write one page and return where it landed plus its digest.

    Saved as UTF-8 with the newlines the server sent, so the file on disk stays
    byte-comparable with a later capture of the same page. The digest is what
    makes "did this site change" answerable without diffing megabytes of markup.
    """
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    path = fixtures_dir / f"{role}.html"
    data = html.encode("utf-8")
    path.write_bytes(data)
    return path, hashlib.sha256(data).hexdigest()


def _write_meta(report: DiscoveryReport) -> None:
    """Record where each saved page came from, next to the pages themselves.

    Without this a fixture is an anonymous blob: nobody can tell which URL it
    is, how old it is, or whether the strategy that fetched it is still the one
    the profile claims. Validation needs all three to say anything trustworthy
    about a page it did not fetch itself.
    """
    assert report.fixtures_dir is not None
    pages = {
        trial.role: {
            "url": trial.url,
            "status_code": trial.status_code,
            "bytes": len(trial.fixture_path.read_bytes()),
            "sha256": trial.sha256,
        }
        for trial in report.trials
        if trial.role is not None and trial.fixture_path is not None
    }
    if not pages:
        # A run that names a fixtures directory but saves nothing into it is a
        # mistake worth stopping on, not an empty directory to discover later.
        raise ValueError(
            f"no page was saved to {report.fixtures_dir}. Pass --search-url or "
            "--product-url, and check the trial output above for a failed fetch."
        )
    report.fixtures_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "entry_url": report.url,
        "captured_at": now_iso(),
        "strategy": report.trial_strategy,
        "measured_strategy": report.chosen_strategy,
        "pages": pages,
    }
    (report.fixtures_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def collect_prices(product: JsonLdProduct) -> list[Decimal]:
    """Every price a product declares, its variants and price ranges included.

    Ranges contribute both ends, since a low and a high price are two prices the
    page really states. The count matters more than the values here: one price
    on a page that offers a size selector is the signal that the other sizes are
    loaded by a request this fetch never made.
    """
    prices: list[Decimal] = []
    for offer in product.offers:
        prices.extend(
            p for p in (offer.price, offer.low_price, offer.high_price) if p is not None
        )
    for variant in product.variants:
        prices.extend(collect_prices(variant))
    return prices


def _has_exact_price(product: JsonLdProduct) -> bool:
    """Whether any offer names one concrete price instead of only a range.

    An AggregateOffer that states lowPrice and highPrice tells us what the
    cheapest and the dearest size cost and nothing about the ones in between.
    Two numbers arriving that way is not the same evidence as two offers each
    naming their own price, so the two cases have to stay distinguishable.
    """
    if any(offer.price is not None for offer in product.offers):
        return True
    return any(_has_exact_price(variant) for variant in product.variants)


def format_report(report: DiscoveryReport) -> str:
    """Render a DiscoveryReport as plain text for a human to read and act on."""
    lines = [f"discover: {report.url}", "", "strategy measurement", ""]
    lines.append(format_probe_report(report.strategy_report))
    lines.append("")
    lines.extend(_format_choice(report))
    lines.append("")
    lines.extend(_format_fingerprint(report))
    for index, trial in enumerate(report.trials):
        lines.append("")
        # Only the first trial is the page the strategy was measured on. The
        # second one borrows that verdict, which changes what an empty result
        # there is allowed to mean.
        lines.extend(_format_trial(trial, report.trial_strategy, measured=index == 0))
    if report.fixtures_dir is not None:
        lines.append("")
        lines.extend(_format_fixtures(report))
    return "\n".join(lines)


def _format_fixtures(report: DiscoveryReport) -> list[str]:
    lines = [f"fixtures: {report.fixtures_dir}"]
    for trial in report.trials:
        if trial.fixture_path is None or trial.sha256 is None:
            continue
        lines.append(
            f"  {trial.fixture_path.name}  {trial.html_chars} chars  "
            f"sha256:{trial.sha256[:12]}  <- {trial.url}"
        )
    lines.append("  meta.json")
    return lines


def _format_choice(report: DiscoveryReport) -> list[str]:
    qualified = [a.strategy for a in report.strategy_report.attempts if _qualifies(a)]
    lines = [f"qualified (2xx + product evidence): {', '.join(qualified) or 'none'}"]
    if report.chosen_strategy is None and report.forced_strategy is None:
        lines.append(
            "chosen strategy: NONE. No rung returned a usable page, so nothing "
            "was tried. Read the table above and check the URL by hand."
        )
    elif report.chosen_strategy is None:
        lines.append(
            "chosen strategy: NONE. No rung returned a usable page, so the "
            "trials below rest on the command line alone, not on a measurement."
        )
    else:
        lines.append(f"chosen strategy: {report.chosen_strategy} (cheapest qualifying)")
    if report.forced_strategy is not None:
        lines.append(
            f"trials ran with: {report.forced_strategy} (given on the command "
            "line, not measured)"
        )
    return lines


def _format_fingerprint(report: DiscoveryReport) -> list[str]:
    if not report.trials:
        return [
            "platform fingerprint: not run. No page was read, so no markup was "
            "matched against the templates. The platform column in the table "
            "above is probe's own coarse guess, not a template match."
        ]
    matched = ", ".join(report.platform_matches) or "none"
    lines = [f"platform fingerprint: {matched}"]
    if len(report.platform_matches) > 1:
        # The collision survives the pick. Whoever chose one of these templates
        # chose it for this run; two fingerprints claiming the same page is
        # still a bug in one of them, and it stays a bug tomorrow.
        lines.append(
            "  WARNING: more than one template matched. Two platforms cannot "
            "both be right, which means one of these fingerprints is wrong. "
            "Read the markers by hand and fix the template that does not "
            "belong, whatever gets applied below."
        )
        if report.chosen_platform is None:
            lines.append(
                "  nobody picked between them, so nothing was applied. Every "
                "field of this site's profile has to come from the trials below."
            )
    elif not report.platform_matches:
        lines.append(
            "  no template applies, so nothing is inherited. Every field of "
            "this site's profile has to come from the trials below."
        )
    if report.platform is None:
        return lines
    # A pick is a claim someone made, not something the markup showed, so the
    # report has to say which of the two this line rests on.
    source = " (picked by hand, not measured)" if report.chosen_platform else ""
    if supplied := _format_defaults(report.applied_defaults):
        lines.append(f"  applying platforms/{report.platform}.json{source}:")
        lines.extend(f"    {line}" for line in supplied)
        lines.append("  every other field is still this site's own work.")
    else:
        # A template can be all fingerprint and no defaults, which is a real
        # state while a platform is only half understood. An "applying" header
        # with nothing under it would read as a rendering bug instead.
        lines.append(
            f"  platforms/{report.platform}.json{source} recognizes this site "
            "but supplies no field yet, so nothing is inherited."
        )
    return lines


def _format_defaults(defaults: dict[str, Any] | None, prefix: str = "") -> list[str]:
    """Flatten a template's defaults to one dotted key per line."""
    lines = []
    for key, value in (defaults or {}).items():
        path = f"{prefix}{key}"
        if isinstance(value, dict):
            lines.extend(_format_defaults(value, f"{path}."))
        else:
            lines.append(f"{path} = {value}")
    return lines


def _format_trial(
    trial: PageTrial, strategy: Strategy | None, *, measured: bool
) -> list[str]:
    lines = [f"trial: {trial.url} ({strategy})"]
    if trial.error is not None:
        lines.append(f"  fetch failed: {trial.error}")
        return lines

    lines.append(f"  status {trial.status_code}, {trial.html_chars} chars")
    lines.append(f"  json-ld products: {len(trial.products)}")
    for index, product in enumerate(trial.products, start=1):
        lines.append(f"    {index}. {_format_product(product)}")
    present = "yes" if trial.variant_control_present else "no"
    lines.append(f"  variant control in markup: {present}")
    lines.append(f"  platform markers: {', '.join(trial.platform_matches) or 'none'}")
    lines.extend(f"  {w}" for w in _warnings(trial, measured=measured))
    return lines


def _format_product(product: JsonLdProduct) -> str:
    prices = collect_prices(product)
    if not prices:
        price_text = "no price"
    elif len(prices) == 1:
        price_text = str(prices[0])
    else:
        price_text = f"{min(prices)}-{max(prices)}"
    return (
        f"{product.name!r} sku={product.sku} offers={len(product.offers)} "
        f"variants={len(product.variants)} prices={len(prices)} [{price_text}] "
        f"stock={_format_stock(product)}"
    )


def _format_stock(product: JsonLdProduct) -> str:
    """Summarize a product's stock answers as in/out/unknown counts."""
    answers = [o.in_stock for o in product.offers]
    for variant in product.variants:
        answers.extend(o.in_stock for o in variant.offers)
    in_stock = sum(1 for a in answers if a is True)
    out = sum(1 for a in answers if a is False)
    unknown = sum(1 for a in answers if a is None)
    return f"{in_stock}in/{out}out/{unknown}unknown"


def _warnings(trial: PageTrial, *, measured: bool) -> list[str]:
    """The findings a reader must not miss, spelled out rather than left implied.

    `measured` says whether the strategy was measured against this exact page.
    It was not, for a second page passed in by hand, and then an empty result
    has two possible causes instead of one: the page really carries no JSON-LD,
    or the strategy that sufficed for the first page is too weak for this one.
    Claiming the first cause while the second is open would send a reader off to
    write a CSS profile for a site that only needed a browser.
    """
    warnings = []
    price_count = sum(len(collect_prices(p)) for p in trial.products)
    exact_price = any(_has_exact_price(p) for p in trial.products)
    if trial.variant_control_present and price_count <= 1:
        warnings.append(
            f"WARNING: the markup offers a size selector but only {price_count} "
            "price could be read. The other sizes are probably fetched by a "
            "later request, so this page alone gives a wrong price per ml."
        )
    elif trial.variant_control_present and not exact_price:
        warnings.append(
            "WARNING: the markup offers a size selector and every price here "
            "comes from a range, not from an offer of its own. A range only "
            "names its two ends, so the sizes in between have no price in the "
            "structured data. They may still sit in the page somewhere a lower "
            "layer can reach, but reading the low end as this product's price "
            "is wrong per ml."
        )
    if not trial.products and measured:
        warnings.append(
            "WARNING: no JSON-LD product on this page. The top rung of the "
            "extraction ladder does not apply here, so a lower one is needed."
        )
    elif not trial.products:
        warnings.append(
            "WARNING: no JSON-LD product on this page, and the strategy above "
            "was measured on the first URL, not this one. Either the page "
            "carries no JSON-LD or it needs a stronger strategy. Run discover "
            "on this URL directly before concluding anything."
        )
    return warnings
