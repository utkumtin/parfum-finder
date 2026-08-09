"""The Textual App root. Handles screen navigation and is the app's default entry point.

The search screen is the initial one. The basket sits on top of it, pushed by
[s] and popped by escape, so coming back from the basket finds the results
table exactly as it was left instead of an empty search.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from textual.app import App, SystemCommand
from textual.screen import Screen

from parfum_finder.engine import run_site
from parfum_finder.store import DEFAULT_DB_PATH
from parfum_finder.tui.search_screen import SearchScreen, SiteRunner
from parfum_finder.validate import DEFAULT_SITES_DIR

THEME = "textual-dark"
"""The one theme the app is tuned for. Not user switchable."""


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
        # Assigned here rather than as a class attribute: App.theme is a Reactive
        # descriptor and a plain class attribute would shadow it. Set before the
        # first screen goes up so nothing ever paints under another theme.
        # This also overrides $TEXTUAL_THEME, which is the point, the whole UI is
        # tuned for this one palette.
        self.theme = THEME
        self.push_screen(
            SearchScreen(
                sites_dir=self.sites_dir, db_path=self.db_path, runner=self.runner
            )
        )

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        # Drops the "Theme" entry from ctrl+p. It is the only way into the theme
        # picker, nothing binds a key to it, so filtering it here closes the door
        # for good. Matching on the callback instead of the title so a wording
        # change upstream cannot silently let it back in.
        for command in super().get_system_commands(screen):
            if command.callback != self.action_change_theme:
                yield command
