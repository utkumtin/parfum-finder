"""Strategy measurement: try every rung of the fetch ladder against one URL.

`probe()` always attempts httpx, curl_cffi, *and* playwright, in that order, and
reports diagnostics for each. It never stops early at the first strategy that
returns a 2xx status. A JS-rendered page can return 200 with an empty shell, so
an HTTP status alone can't tell you a strategy actually got usable content.
probe lays out evidence per strategy (status, HTML size, JSON-LD presence,
product-card-like markup, known platform markers) and a human reads the
comparison, rather than guessing "which one suffices" on its own.

Because every rung is always attempted, a machine where playwright cannot run at
all, whether the package is missing or its browser was never downloaded, always
surfaces as a loud PlaywrightNotInstalled here, never a silently skipped row.

This measurement is the foundation discover.py's own strategy selection will
build on once it exists.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx
from curl_cffi import CurlError
from selectolax.parser import HTMLParser

from parfum_finder.fetch import (
    PlaywrightNoResponse,
    PlaywrightNotInstalled,
    Strategy,
    fetch,
)

# A failed attempt to record, not a reason to abort the whole report: connection
# errors from httpx/curl_cffi, playwright navigation errors, and fetch.py's own
# PlaywrightNoResponse for a navigation that produced no Response object (e.g.
# an about:blank-style target). CurlError rather than curl_cffi's
# RequestException, because RequestException is a subclass of CurlError, so
# catching only the narrower one would let a bare CurlError raised below the
# requests layer escape and crash the whole run.
# PlaywrightNotInstalled is deliberately NOT here. It's caught and re-raised
# separately below. A playwright setup that can't run means the rung can never
# be tried at all, so it must abort the run loudly instead of silently skipping
# the row.
# Using the specific PlaywrightNoResponse type rather than bare RuntimeError
# matters too: a bare RuntimeError would also catch real bugs (a closed event
# loop, a defect in this module's own parsing helpers) and misreport them as an
# ordinary failed attempt instead of a crash. Playwright's own Error type is
# only added when the package is actually importable, so this module stays
# importable without the extra.
_NETWORK_ERROR_TYPES: tuple[type[Exception], ...] = (
    httpx.RequestError,
    CurlError,
    PlaywrightNoResponse,
)
try:
    from playwright.async_api import Error as _PlaywrightError

    _NETWORK_ERROR_TYPES = (*_NETWORK_ERROR_TYPES, _PlaywrightError)
except ImportError:
    pass

# Shopify's markers are its well-known theme global, CDN domain, and cart
# endpoint. WooCommerce and OpenCart are open-source platforms with stable,
# documented markers. Ticimax and Ideasoft have no confirmed marker yet, since
# no real target site has been fetched so far, so these two are best-effort
# guesses at the platform mentioning its own name in its CDN domain or generator
# tag. Guesses are reported with a "?" suffix so a reader never mistakes one for
# a confirmed match, and both should be revisited against real fetched pages.
_PLATFORM_SIGNATURES: dict[str, tuple[str, ...]] = {
    "shopify": ("Shopify.theme", "cdn.shopify.com", "/cart/add"),
    "woocommerce": ("woocommerce", "wp-content/plugins/woocommerce"),
    "opencart": ("index.php?route=", "catalog/view/theme"),
    "ticimax": ("ticimax", "cdn.ticimax.cloud"),
    "ideasoft": ("ideasoft", "cdn.myideasoft.com"),
}
_UNVERIFIED_PLATFORMS = frozenset({"ticimax", "ideasoft"})

# Coarse "does this page look like it lists products at all" signal, written as
# one selector list so a node matched by several of these is still counted once.
# The number is a count of matching NODES, not of products: a card div and the
# product link inside it both match, and a wrapper container will match too. So
# read it only as a relative figure, comparing one strategy against another on
# the same page. Twenty products can easily report sixty. That is enough for the
# one call it has to make, separating a rendered page from an empty JS shell,
# which HTML size alone cannot make because inline scripts inflate the size of a
# shell that renders nothing. Turkish stores commonly write "urun" in class
# names and URLs, hence both spellings.
_PRODUCT_MARKUP_SELECTOR = ", ".join(
    (
        '[class*="product"]',
        '[class*="urun"]',
        "[data-product-id]",
        'a[href*="/product"]',
        'a[href*="/urun"]',
    )
)

# Markup that lets a shopper pick a size. Its presence next to a single readable
# price is the quiet failure this project cares most about: the other sizes exist,
# they just arrive by a request this page never made, so a naive read compares one
# site's 5 ml price against another's 50 ml price. Turkish stores write "varyant"
# and "secenek" as often as the English words, and CSS attribute matching is case
# sensitive, so the lowercase spellings are the ones that hit in practice.
#
# Read the other way round, which is what the engine does with it, its absence
# says a product page has no size list to be missing anything from: a plain full
# bottle, sold as one thing. That reading is why this lives here next to the
# other page-shape signal rather than in the discovery tool that first needed it,
# and why it must stay written in the shop's markup rather than the profile's
# selectors. Evidence taken from the profile could not tell a full bottle apart
# from a profile that stopped being able to see the sizes, which is the one
# distinction both readings exist to make.
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
class ProbeAttempt:
    """One strategy's outcome against the probed URL.

    Either the request came back or it didn't, and the two cases fill disjoint
    halves of this record. A request that never completed (connection refused,
    timeout, TLS failure) sets error and leaves every diagnostic field None. A
    request that came back sets all the diagnostic fields and leaves error None.
    Only strategy is always populated.
    """

    strategy: Strategy
    status_code: int | None
    error: str | None
    html_chars: int | None
    jsonld_block_count: int | None
    jsonld_product_count: int | None
    product_markup_nodes: int | None
    platform_signatures: tuple[str, ...] | None


@dataclass(frozen=True)
class ProbeReport:
    url: str
    attempts: tuple[ProbeAttempt, ...]  # always httpx, curl_cffi, playwright, in order


async def probe(url: str, *, timeout_s: int = 20) -> ProbeReport:
    """Fetch `url` with every strategy and report diagnostics for each.

    timeout_s applies to each strategy on its own, so a completely unresponsive
    host takes up to three times that long overall.

    Raises PlaywrightNotInstalled, uncaught, if the playwright rung cannot run
    on this machine at all. See the module docstring.
    """
    attempts = []
    for strategy in ("httpx", "curl_cffi", "playwright"):
        attempts.append(await _attempt(url, strategy, timeout_s=timeout_s))
    return ProbeReport(url=url, attempts=tuple(attempts))


async def _attempt(url: str, strategy: Strategy, *, timeout_s: int) -> ProbeAttempt:
    try:
        result = await fetch(url, strategy, timeout_s=timeout_s)
    except PlaywrightNotInstalled:
        raise  # never swallow a missing extra, see module docstring
    except _NETWORK_ERROR_TYPES as e:
        return ProbeAttempt(
            strategy=strategy,
            status_code=None,
            # The exception type is half the measurement. Connection refused, a
            # read timeout and a TLS handshake failure can all render the same
            # in str(e) alone, yet they point at completely different fixes.
            error=f"{type(e).__name__}: {e}",
            html_chars=None,
            jsonld_block_count=None,
            jsonld_product_count=None,
            product_markup_nodes=None,
            platform_signatures=None,
        )

    tree = HTMLParser(result.html)
    block_count, product_count = _count_jsonld(tree)
    return ProbeAttempt(
        strategy=strategy,
        status_code=result.status_code,
        error=None,
        html_chars=len(result.html),
        jsonld_block_count=block_count,
        jsonld_product_count=product_count,
        product_markup_nodes=len(tree.css(_PRODUCT_MARKUP_SELECTOR)),
        platform_signatures=_detect_platforms(result.html),
    )


def _count_jsonld(tree: HTMLParser) -> tuple[int, int]:
    """Count JSON-LD script blocks and how many Product-typed objects they hold.

    A block that isn't valid JSON is counted but contributes 0 Product objects.
    This is a raw evidence count for a human to read, not the real JSON-LD
    normalization that the extraction layer will need to do later.
    """
    blocks = tree.css('script[type="application/ld+json"]')
    product_count = 0
    for node in blocks:
        try:
            data = json.loads(node.text())
        except json.JSONDecodeError:
            continue
        product_count += _count_product_objects(data)
    return len(blocks), product_count


def _count_product_objects(data: object) -> int:
    """Count Product-typed objects anywhere inside a parsed JSON-LD block.

    Descends through every nested value, not just "@graph" wrappers and root
    arrays. Category and search pages routinely nest products two levels deep,
    for example an ItemList whose itemListElement entries each wrap the real
    Product under an "item" key. Stopping at the top level would report 0
    products for a page that plainly has them.
    """
    if isinstance(data, dict):
        type_field = data.get("@type")
        if isinstance(type_field, str) and "Product" in type_field:
            return 1
        if isinstance(type_field, list) and any(
            isinstance(t, str) and "Product" in t for t in type_field
        ):
            return 1
        return sum(_count_product_objects(value) for value in data.values())
    if isinstance(data, list):
        return sum(_count_product_objects(item) for item in data)
    return 0


def _detect_platforms(html: str) -> tuple[str, ...]:
    """Return the plain platform names whose markers appear in the page.

    Names come back unadorned so callers can compare them directly. Marking the
    unconfirmed ones is the report renderer's job, not this function's.
    """
    lowered = html.lower()
    return tuple(
        name
        for name, markers in _PLATFORM_SIGNATURES.items()
        if any(marker.lower() in lowered for marker in markers)
    )


def format_report(report: ProbeReport) -> str:
    """Render a ProbeReport as a plain-text table, one row per strategy."""
    lines = [f"probe: {report.url}", ""]
    header = (
        f"{'strategy':<10} {'status':<8} {'chars':>8} {'json-ld':>8} "
        f"{'product':>8} {'markup':>8} platform"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for a in report.attempts:
        if a.error is not None:
            lines.append(f"{a.strategy:<10} {'error':<8} {_one_line(a.error)}")
            continue
        platforms = (
            ", ".join(_label_platform(p) for p in a.platform_signatures or ()) or "-"
        )
        lines.append(
            f"{a.strategy:<10} {a.status_code!s:<8} {a.html_chars!s:>8} "
            f"{a.jsonld_block_count!s:>8} {a.jsonld_product_count!s:>8} "
            f"{a.product_markup_nodes!s:>8} {platforms}"
        )
    return "\n".join(lines)


def _label_platform(name: str) -> str:
    """Flag a platform whose markers are still an unverified guess with a "?".

    Without this a guessed match would sit in the same column as a confirmed
    one, and a reader would have no way to tell how much weight to give it.
    """
    return f"{name}?" if name in _UNVERIFIED_PLATFORMS else name


def _one_line(text: str, *, limit: int = 120) -> str:
    """Squash a message into one truncated line so the table stays aligned.

    Playwright errors in particular come back with a multi-line call log
    appended, which would otherwise spill across the table's columns.
    """
    # splitlines rather than a split on "\n", so a CRLF message doesn't leave a
    # stray carriage return that redraws over the row already printed.
    parts = text.splitlines() or [text]
    first = f"{parts[0]} [...]" if len(parts) > 1 else parts[0]
    return first if len(first) <= limit else f"{first[: limit - 3]}..."
