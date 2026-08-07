"""Command-line entry point.

Subcommands will be added incrementally as the project grows:
    probe <url>               - check which fetch strategy a site needs
    discover <url> [--id]     - generate a site profile
    validate [<id>] [--live]  - check that a profile still works
    search <query> [--site]   - search for a perfume across sites
    (default) tui              - launch the interactive app

CLI framework: argparse (stdlib). A handful of subcommands with plain
positional/flag arguments don't need a third-party library -- argparse's
subparsers cover this without adding a dependency.
"""

import argparse
import asyncio
from pathlib import Path
from typing import get_args

from parfum_finder.discover import discover
from parfum_finder.discover import format_report as format_discovery_report
from parfum_finder.fetch import Strategy
from parfum_finder.probe import format_report as format_probe_report
from parfum_finder.probe import probe

# Golden fixtures live outside the installed package, next to sites/ and
# platforms/, because they are project data a person edits and reviews.
FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"

STRATEGIES = get_args(Strategy)


def main() -> None:
    parser = argparse.ArgumentParser(prog="parfum-finder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe_parser = subparsers.add_parser(
        "probe", help="check which fetch strategy a URL needs"
    )
    probe_parser.add_argument("url")
    probe_parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        metavar="SECONDS",
        help=(
            "per-strategy timeout in seconds (default: 20). "
            "All three strategies run in turn, so an unresponsive host can take "
            "up to three times this long."
        ),
    )

    discover_parser = subparsers.add_parser(
        "discover", help="measure a site and report what its JSON-LD declares"
    )
    discover_parser.add_argument("url")
    discover_parser.add_argument(
        "--product-url",
        metavar="URL",
        help=(
            "a second page from the same site to read as well, normally one "
            "product page. Comparing it against the first page is what shows "
            "whether each size is its own product or one product holds them all."
        ),
    )
    discover_parser.add_argument(
        "--search-url",
        metavar="URL",
        help=(
            "a search results page from the same site, normally the site's own "
            "search URL with a perfume name in it. Read like the other pages, "
            "and saved as search.html when --id is given."
        ),
    )
    discover_parser.add_argument(
        "--id",
        dest="site_id",
        metavar="SLUG",
        help=(
            "save the pages fetched below as golden fixtures under "
            "fixtures/<slug>/, next to a meta.json naming their source URLs. "
            "Needs at least one of --search-url / --product-url."
        ),
    )
    discover_parser.add_argument(
        "--strategy",
        choices=STRATEGIES,
        help=(
            "fetch the pages with this strategy instead of the measured winner. "
            "The measurement still runs and is still reported. Needed when one "
            "page of a site needs a heavier strategy than its front page did, "
            "for instance a search page rendered in the browser."
        ),
    )
    discover_parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        metavar="SECONDS",
        help="per-request timeout in seconds (default: 20)",
    )

    args = parser.parse_args()

    if args.command == "probe":
        probe_report = asyncio.run(probe(args.url, timeout_s=args.timeout))
        print(format_probe_report(probe_report))
    elif args.command == "discover":
        if args.site_id and not (args.search_url or args.product_url):
            # Saving nothing under a slug would leave an empty directory that
            # looks like a captured site on the next person's disk.
            discover_parser.error(
                "--id needs at least one page to save: pass --search-url "
                "and/or --product-url"
            )
        discovery = asyncio.run(
            discover(
                args.url,
                product_url=args.product_url,
                search_url=args.search_url,
                timeout_s=args.timeout,
                strategy=args.strategy,
                fixtures_dir=FIXTURES_DIR / args.site_id if args.site_id else None,
            )
        )
        print(format_discovery_report(discovery))
