"""File logging for the app's own diagnostics.

Nothing here ever writes to the console. The TUI owns the terminal, and a log
line printed into it lands in the middle of the results table. Site failures
show up on screen as a count, the detail behind that count lives in the file.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE_NAME = "parfum-finder.log"
"""Shown next to the error count, so the name is needed before any setup runs."""

DEFAULT_LOG_PATH = Path(LOG_FILE_NAME)
"""Relative to the working directory, same as DEFAULT_DB_PATH."""

_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 3

logger = logging.getLogger("parfum_finder")
# Keeps logging's lastResort handler from printing warnings to stderr when
# nothing has been set up, which is every test run and every library import.
logger.addHandler(logging.NullHandler())


def setup_logging(path: Path = DEFAULT_LOG_PATH) -> Path:
    """Attach the rotating file handler and return where it writes.

    Safe to call more than once, the second call replaces the first handler
    rather than doubling every line.
    """
    for handler in list(logger.handlers):
        if isinstance(handler, RotatingFileHandler):
            logger.removeHandler(handler)
            handler.close()
    # delay=True so the file appears only once something is actually logged. A
    # clean run leaves no file behind, which also keeps a stray log out of the
    # repo when the tests call main().
    handler = RotatingFileHandler(
        path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
        delay=True,
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return path
