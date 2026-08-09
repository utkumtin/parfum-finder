"""Command-line entry point.

Subcommands will be added incrementally as the project grows:
    probe <url>               - check which fetch strategy a site needs
    discover <url> [--id]     - generate a site profile
    validate [<id>...] [--live] - check that a profile still works
    search <perfume> [--site] [--db] - scan every site and store the prices
    tui [--db]                 - launch the interactive app
    (default, no subcommand)   - same as tui

CLI framework: argparse (stdlib). A handful of subcommands with plain
positional/flag arguments don't need a third-party library -- argparse's
subparsers cover this without adding a dependency.
"""

import argparse
import asyncio
import sqlite3
import sys
from pathlib import Path
from typing import get_args

from parfum_finder.discover import discover
from parfum_finder.discover import format_report as format_discovery_report
from parfum_finder.engine import SiteResult, run_sites
from parfum_finder.fetch import Strategy
from parfum_finder.matcher import PerfumeQuery, parse_query
from parfum_finder.probe import format_report as format_probe_report
from parfum_finder.probe import probe
from parfum_finder.profiles import load_site_profile, sync_to_db
from parfum_finder.store import DEFAULT_DB_PATH, connect, now_iso, snapshot_rows
from parfum_finder.store import write_snapshots as write_site_snapshots
from parfum_finder.validate import (
    format_live_report,
    validate_all_live,
    validate_all_offline,
)
from parfum_finder.validate import format_report as format_validation_report

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Golden fixtures live outside the installed package, next to sites/ and
# platforms/, because they are project data a person edits and reviews.
FIXTURES_DIR = _PROJECT_ROOT / "fixtures"
SITES_DIR = _PROJECT_ROOT / "sites"

STRATEGIES = get_args(Strategy)


def ask_which_platform(candidates: tuple[str, ...]) -> str | None:
    """Ask at the terminal which of several matching templates to apply.

    Asked while discover is still running, so the question appears above the
    report rather than after it. Nothing of the report is lost by that: the
    answer changes what the report says, so it has to be given first.

    Without a terminal to ask at, there is no answer and nothing is applied.
    A default pick here would put a guess into a piped or scripted run, where
    nobody is watching the output to catch it.

    Declining is a first-class answer, and so is an interrupt: someone who hits
    Ctrl-C at this prompt has not chosen a template.
    """
    if not sys.stdin.isatty():
        return None
    print("\nseveral platform templates matched this page:")
    for index, name in enumerate(candidates, start=1):
        print(f"  {index}. {name}")
    print("  0. none of them, apply nothing")
    while True:
        try:
            answer = input(f"apply which template? [0-{len(candidates)}] ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if answer in ("", "0"):
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(candidates):
            return candidates[int(answer) - 1]
        print(f"answer with a number from 0 to {len(candidates)}.")


def run_search(
    query_text: str,
    *,
    site_ids: tuple[str, ...] = (),
    sites_dir: Path = SITES_DIR,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Scan every site for one perfume, store what came back, and print it.

    Returns the number of prices written, so the caller can tell a scan that
    found nothing from one that never ran.

    The sites table is synced before anything is scanned, and from every profile
    rather than only the ones being run. The snapshot rows point at it by
    foreign key, so a site absent from the table cannot be written at all; and a
    site left out of this run by --site is still a site whose shipping terms the
    basket screen has to be able to read.

    Disabled profiles are synced and not scanned. That is what the flag is for,
    and dropping their row instead would take their price history with it.
    """
    query = parse_query(query_text)
    profiles = [load_site_profile(path) for path in sorted(sites_dir.glob("*.json"))]
    if site_ids:
        known = {profile["id"] for profile in profiles}
        unknown = sorted(set(site_ids) - known)
        if unknown:
            # Asking about a site that has no profile is a mistake in the
            # request. Scanning the rest of them would answer a question nobody
            # asked and bury the typo in a report that looks fine.
            raise FileNotFoundError(f"no profile under {sites_dir} for: {unknown}")
    conn = connect(db_path)
    try:
        sync_to_db(conn, profiles, synced_at=now_iso())
        wanted = [
            profile
            for profile in profiles
            if profile.get("enabled", True)
            and (not site_ids or profile["id"] in site_ids)
        ]
        results = asyncio.run(run_sites(wanted, query_text))
        written = 0
        for result in results:
            written += _store_site_result(conn, result, query)
            print(_report_line(result))
        return written
    finally:
        conn.close()


def _store_site_result(
    conn: sqlite3.Connection, result: SiteResult, query: PerfumeQuery
) -> int:
    """Write one site's rows in a transaction of its own.

    Per site rather than per run on purpose. write_snapshots is one transaction,
    so a single unstorable row from one shop would roll back every other shop's
    prices too, and this command exists to prove that one site breaking leaves
    the others alone.

    The matching and row-building itself lives in store.snapshot_rows, so the
    TUI's own scan can call the same function and never drift from these rules.
    """
    return write_site_snapshots(conn, snapshot_rows(result, query))


def _report_line(result: SiteResult) -> str:
    """One line per site: which site, how it went, and what it said.

    The site id is printed here rather than taken from the detail. An error's
    detail is the exception's own message, which knows nothing about which shop
    raised it, so a report built from details alone would show a bare
    "connection failed" with no way to tell whose it was.
    """
    marks = {"ok": " ", "empty": " ", "suspect": "⚠", "error": "✗"}
    detail = result.detail or ""
    detail = detail.removeprefix(f"{result.site_id}: ")
    return f"{marks[result.status]} {result.site_id:<16} {result.status:<8} {detail}"


def main() -> None:
    parser = argparse.ArgumentParser(prog="parfum-finder")
    subparsers = parser.add_subparsers(dest="command")

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

    validate_parser = subparsers.add_parser(
        "validate", help="check that site profiles still work against their fixtures"
    )
    validate_parser.add_argument(
        "site_id",
        nargs="*",
        metavar="ID",
        help="only validate these sites (default: every profile under sites/)",
    )
    validate_parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "after the offline pass, run each profile against the real site "
            "with the query its fixture was captured with. A profile that "
            "breaks live is reported together with what the other extraction "
            "layers can still read off the page."
        ),
    )

    search_parser = subparsers.add_parser(
        "search", help="search every site for one perfume and store the prices"
    )
    search_parser.add_argument(
        "query", metavar="PERFUME", help='what to look for, e.g. "Dior Sauvage EDP"'
    )
    search_parser.add_argument(
        "--site",
        dest="site_id",
        action="append",
        default=[],
        metavar="ID",
        help=(
            "only scan this site (repeatable). Every profile is still synced "
            "to the database; default is to scan all enabled ones."
        ),
    )
    search_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        metavar="PATH",
        help=f"price database to write to (default: {DEFAULT_DB_PATH})",
    )

    tui_parser = subparsers.add_parser("tui", help="launch the interactive app")
    tui_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        metavar="PATH",
        help=f"price database to read and write (default: {DEFAULT_DB_PATH})",
    )

    args = parser.parse_args()

    if args.command is None or args.command == "tui":
        # Imported here, not at module load, so that every other subcommand
        # keeps running without textual installed and without waiting on it.
        from parfum_finder.tui.app import ParfumFinderApp

        db_path = args.db if args.command == "tui" else DEFAULT_DB_PATH
        ParfumFinderApp(sites_dir=SITES_DIR, db_path=db_path).run()
    elif args.command == "probe":
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
                chooser=ask_which_platform,
            )
        )
        print(format_discovery_report(discovery))
    elif args.command == "search":
        try:
            written = run_search(
                args.query,
                site_ids=tuple(args.site_id),
                sites_dir=SITES_DIR,
                db_path=args.db,
            )
        except (FileNotFoundError, ValueError) as e:
            # A bad request, not a finding about a site. Same exit code as
            # validate uses for the same kind of mistake.
            print(e)
            sys.exit(2)
        print(f"\n{written} price(s) written to {args.db}")
    elif args.command == "validate":
        ids = tuple(args.site_id) or None
        try:
            results = asyncio.run(validate_all_offline(ids))
            # Live mode runs the same sites in the same order, so the two passes
            # zip into the side-by-side report without matching them up by id.
            live = asyncio.run(validate_all_live(ids)) if args.live else ()
        except FileNotFoundError as e:
            # Being asked about a site that has no profile is a mistake in the
            # request, not a finding about a profile, so it gets its own exit
            # code and leaves 1 to mean "a profile is broken". Reporting the
            # site id rather than the raw OSError avoids saying "no profile"
            # and "no such file" in the same breath about the same thing.
            site_id = Path(e.filename).stem if e.filename else str(e)
            print(f"no profile under sites/ for: {site_id!r}")
            sys.exit(2)
        if args.live:
            print(format_live_report(tuple(zip(results, live, strict=True))))
        else:
            print(format_validation_report(results))
        if any(not result.ok for result in (*results, *live)):
            # A broken profile has to fail the command, not just print in red:
            # this is what lets CI run offline validation as a gate instead of
            # producing output nobody reads.
            sys.exit(1)
