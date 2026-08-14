"""The file logger's two promises: it writes to the file, and it stays silent.

Both matter for the same reason. The TUI owns the terminal, so a handler that
printed anything would land in the middle of the results table, and a handler
that wrote nowhere would lose the only record of why a site failed.
"""

from __future__ import annotations

import logging
from pathlib import Path

from parfum_finder import paths
from parfum_finder.logging_setup import DEFAULT_LOG_PATH, setup_logging


def _teardown() -> None:
    log = logging.getLogger("parfum_finder")
    for handler in list(log.handlers):
        if not isinstance(handler, logging.NullHandler):
            log.removeHandler(handler)
            handler.close()


def test_an_error_lands_in_the_given_file(tmp_path: Path) -> None:
    path = tmp_path / "parfum-finder.log"
    try:
        assert setup_logging(path) == path
        logging.getLogger("parfum_finder").error("site-a — bağlantı hatası")
    finally:
        _teardown()

    assert "site-a — bağlantı hatası" in path.read_text(encoding="utf-8")


def test_setting_up_without_logging_anything_creates_no_file(tmp_path: Path) -> None:
    # The tests run main() with a stubbed app, which reaches setup_logging. A
    # handler that opened its file eagerly would drop a log into the repo on
    # every clean run.
    path = tmp_path / "parfum-finder.log"
    try:
        setup_logging(path)
    finally:
        _teardown()

    assert not path.exists()


def test_setting_up_twice_does_not_double_the_lines(tmp_path: Path) -> None:
    path = tmp_path / "parfum-finder.log"
    try:
        setup_logging(path)
        setup_logging(path)
        logging.getLogger("parfum_finder").error("once")
    finally:
        _teardown()

    assert path.read_text(encoding="utf-8").count("once") == 1


def test_the_default_path_matches_paths_module() -> None:
    # Same shape as DEFAULT_DB_PATH: resolved through paths.py, not a bare
    # CWD-relative name, so a frozen build writes next to user data instead of
    # into its (unwritable) install directory.
    assert DEFAULT_LOG_PATH == paths.default_log_path()
    assert DEFAULT_LOG_PATH.name == "parfum-finder.log"
