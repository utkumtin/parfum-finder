"""Command-line entry point.

Subcommands will be added incrementally as the project grows:
    probe <url>               - check which fetch strategy a site needs
    discover <url> [--id]     - generate a site profile
    validate [<id>] [--live]  - check that a profile still works
    search <query> [--site]   - search for a perfume across sites
    (default) tui              - launch the interactive app

No CLI framework has been chosen yet (argparse vs. something else). That decision
gets made once the first real subcommand is implemented.
"""


def main() -> None:
    raise NotImplementedError("No subcommands implemented yet.")
