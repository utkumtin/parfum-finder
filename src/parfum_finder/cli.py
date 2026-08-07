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

from parfum_finder.discover import discover
from parfum_finder.discover import format_report as format_discovery_report
from parfum_finder.probe import format_report as format_probe_report
from parfum_finder.probe import probe


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
        discovery = asyncio.run(
            discover(args.url, product_url=args.product_url, timeout_s=args.timeout)
        )
        print(format_discovery_report(discovery))
