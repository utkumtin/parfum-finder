"""Site discovery: turns a URL into a profile, with human review. Not fully automatic.

Flow: measure which fetch strategy the site needs, fingerprint the platform if it's
recognizable, walk the extraction ladder to find the most durable layer that works,
then run an end-to-end trial (a sample search plus a sample product page) and show
the extracted fields with evidence and a confidence score. Low-confidence fields get
flagged for manual review, and shipping data is never guessed. It's always entered
by hand afterward.

This first version does the measurement and the JSON-LD trial only, and it writes
nothing to disk. It reads a page, says which fetch strategy it picked and why, shows
what the page's JSON-LD actually declares, and flags the case where the markup offers
a size selector but only one price could be read. A human reads that output and
writes down what the site is really doing.

The sample-search half of the trial is missing on purpose: a search needs the site's
search URL template, which comes from a profile or a platform template, and neither
exists yet. Guessing a template here would produce a trial that measures the guess
rather than the site.

TODO: platform fingerprinting plus template application, per-field confidence scores,
and writing the profile out with the low-confidence fields listed for review.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

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

# What a request that never completed looks like, as opposed to a request that
# came back with a bad status. Kept apart from PlaywrightNotInstalled, which is
# re-raised: a setup that cannot run at all is not a property of the site being
# discovered, and hiding it inside a trial row would make the report look like
# the site refused us. Playwright's own error type only exists once the package
# is installed, so it is added conditionally and this module stays importable
# without the extra.
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


@dataclass(frozen=True)
class DiscoveryReport:
    url: str
    strategy_report: ProbeReport
    # None when no strategy qualified. There is no fallback pick in that case:
    # naming a strategy that failed the measurement would put a guess into the
    # profile, which is the one thing this whole command exists to avoid.
    chosen_strategy: Strategy | None
    trials: tuple[PageTrial, ...]


async def discover(
    url: str, *, product_url: str | None = None, timeout_s: int = 20
) -> DiscoveryReport:
    """Measure the strategies a site needs, then read its JSON-LD with the winner.

    `product_url` is optional and takes a second page from the same site, so a
    listing URL and one product page can be compared in a single report. That
    comparison is what tells a reader whether each size is its own product or
    one product carries all the sizes.

    The winning strategy is fetched again for the trial rather than reusing the
    HTML from the measurement, which costs one extra request per page and buys
    an independent confirmation that the chosen strategy really works.

    Raises PlaywrightNotInstalled, uncaught, if the playwright rung cannot run
    on this machine. The measurement is only honest if every rung was actually
    tried, so an incomplete setup has to stop the run rather than quietly leave
    playwright out of the comparison.
    """
    strategy_report = await probe(url, timeout_s=timeout_s)
    chosen = _choose_strategy(strategy_report)
    trials: tuple[PageTrial, ...] = ()
    if chosen is not None:
        urls = [url] if product_url is None else [url, product_url]
        trials = tuple([await _trial(u, chosen, timeout_s=timeout_s) for u in urls])
    return DiscoveryReport(
        url=url,
        strategy_report=strategy_report,
        chosen_strategy=chosen,
        trials=trials,
    )


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


async def _trial(url: str, strategy: Strategy, *, timeout_s: int) -> PageTrial:
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
        )

    tree = HTMLParser(result.html)
    return PageTrial(
        url=result.url,
        status_code=result.status_code,
        error=None,
        html_chars=len(result.html),
        products=extract_jsonld_products(result.html),
        variant_control_present=bool(tree.css(_VARIANT_CONTROL_SELECTOR)),
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
    for index, trial in enumerate(report.trials):
        lines.append("")
        # Only the first trial is the page the strategy was measured on. The
        # second one borrows that verdict, which changes what an empty result
        # there is allowed to mean.
        lines.extend(_format_trial(trial, report.chosen_strategy, measured=index == 0))
    return "\n".join(lines)


def _format_choice(report: DiscoveryReport) -> list[str]:
    qualified = [a.strategy for a in report.strategy_report.attempts if _qualifies(a)]
    lines = [f"qualified (2xx + product evidence): {', '.join(qualified) or 'none'}"]
    if report.chosen_strategy is None:
        lines.append(
            "chosen strategy: NONE. No rung returned a usable page, so nothing "
            "was tried. Read the table above and check the URL by hand."
        )
    else:
        lines.append(f"chosen strategy: {report.chosen_strategy} (cheapest qualifying)")
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
