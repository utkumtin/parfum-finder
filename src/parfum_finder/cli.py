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

from parfum_finder.probe import format_report, probe


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

    args = parser.parse_args()

    if args.command == "probe":
        report = asyncio.run(probe(args.url, timeout_s=args.timeout))
        print(format_report(report))
