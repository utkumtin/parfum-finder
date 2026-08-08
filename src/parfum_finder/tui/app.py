"""The Textual App root. Handles screen navigation and is the app's default entry point.

The search screen is the initial one. The basket sits on top of it, pushed by
[s] and popped by escape, so coming back from the basket finds the results
table exactly as it was left instead of an empty search.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from parfum_finder.engine import run_site
from parfum_finder.store import DEFAULT_DB_PATH
from parfum_finder.tui.search_screen import SearchScreen, SiteRunner
from parfum_finder.validate import DEFAULT_SITES_DIR


class ParfumFinderApp(App[None]):
    """Root app: pushes the search screen on mount."""

    TITLE = "parfum-finder"

    def __init__(
        self,
        *,
        sites_dir: Path = DEFAULT_SITES_DIR,
        db_path: Path = DEFAULT_DB_PATH,
        runner: SiteRunner = run_site,
    ) -> None:
        super().__init__()
        self.sites_dir = sites_dir
        self.db_path = db_path
        self.runner = runner

    def on_mount(self) -> None:
        self.push_screen(
            SearchScreen(
                sites_dir=self.sites_dir, db_path=self.db_path, runner=self.runner
            )
        )
