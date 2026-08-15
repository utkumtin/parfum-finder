"""Tests for parfum_finder.gui: the desktop entry point's headless path.

`run_window()` opens a native WebView2/GTK window, which has nothing useful
to assert against under pytest. `run_selftest()` is the path this module is
actually exercised through outside a human at a Windows machine -- it's also
what the Windows CI smoke test runs against the frozen exe -- so it's what
gets a real test: a passing run is what proves ensure_user_data(), the
ephemeral-port bind, and the backend boot all still work together.
"""

from __future__ import annotations

from pathlib import Path

from parfum_finder.gui import run_selftest


def test_selftest_boots_the_backend_and_exits_zero(tmp_path: Path) -> None:
    sites_dir = tmp_path / "sites"
    sites_dir.mkdir()
    db_path = tmp_path / "db.sqlite3"

    assert run_selftest(sites_dir=sites_dir, db_path=db_path) == 0
