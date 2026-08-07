"""Tests for parfum_finder.store.now_iso.

The one hard requirement this timestamp format has to satisfy: plain string
comparison must agree with chronological order, because the database picks
the newest price snapshot with a text ORDER BY, not a real datetime column.
Anything that breaks that (extra precision, a UTC offset, local time) would
make "most recent" silently return the wrong row.
"""

import re
from datetime import UTC, datetime
from unittest.mock import patch

from parfum_finder.store import now_iso

_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def test_now_iso_matches_the_required_format() -> None:
    assert _TIMESTAMP_RE.match(now_iso())


def test_now_iso_string_order_matches_chronological_order() -> None:
    earlier = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
    later = datetime(2026, 1, 1, 10, 0, 1, tzinfo=UTC)

    with patch("parfum_finder.store.datetime") as mock_datetime:
        mock_datetime.now.return_value = earlier
        earlier_str = now_iso()
        mock_datetime.now.return_value = later
        later_str = now_iso()

    assert earlier_str < later_str
