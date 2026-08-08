"""Tests for parfum_finder.store: the timestamp helper and the schema.

The one hard requirement this timestamp format has to satisfy: plain string
comparison must agree with chronological order, because the database picks
the newest price snapshot with a text ORDER BY, not a real datetime column.
Anything that breaks that (extra precision, a UTC offset, local time) would
make "most recent" silently return the wrong row.
"""

import re
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from parfum_finder.store import connect, now_iso

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


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = connect(tmp_path / "test.db")
    try:
        yield connection
    finally:
        connection.close()


def _seed_variant(conn: sqlite3.Connection, size_ml_x10: int = 50) -> int:
    """Insert one site → perfume → product → variant chain, return the variant id."""
    ts = "2026-08-08T10:00:00Z"
    conn.execute(
        "INSERT OR IGNORE INTO sites (site_id, name, base_url, synced_at)"
        " VALUES ('ornek', 'Örnek', 'https://ornek-site.com', ?)",
        (ts,),
    )
    conn.execute(
        "INSERT OR IGNORE INTO perfumes (brand, name, concentration, created_at)"
        " VALUES ('Dior', 'Sauvage', 'EDT', ?)",
        (ts,),
    )
    conn.execute(
        "INSERT OR IGNORE INTO products"
        " (site_id, perfume_id, match_score, first_seen, last_seen)"
        " VALUES ('ornek', 1, 95, ?, ?)",
        (ts, ts),
    )
    cur = conn.execute(
        "INSERT INTO product_variants"
        " (product_id, size_ml_x10, raw_title, product_url, first_seen, last_seen)"
        " VALUES (1, ?, 'Sauvage EDT dekant', 'https://ornek-site.com/s', ?, ?)",
        (size_ml_x10, ts, ts),
    )
    return int(cur.lastrowid or 0)


def test_connect_enforces_foreign_keys(conn: sqlite3.Connection) -> None:
    """A snapshot pointing at a variant that doesn't exist has to be rejected.

    SQLite leaves foreign keys off unless the connection turns them on, so
    without the pragma this insert would quietly succeed and leave the price
    history with rows nothing can join back to.
    """
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus,"
            " in_stock) VALUES (999, '2026-08-08T10:00:00Z', 12500, 1)"
        )


def test_latest_prices_breaks_same_second_ties_by_snapshot_id(
    conn: sqlite3.Connection,
) -> None:
    """Two snapshots written in the same second must resolve to the newer one.

    A scan can write twice within one second, and fetched_at only has second
    precision. If the view didn't fall back to snapshot_id the winner would be
    whichever row SQLite happened to visit first, so the price shown could be
    the older one.
    """
    variant_id = _seed_variant(conn)
    same_second = "2026-08-08T10:00:00Z"
    conn.execute(
        "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus, in_stock)"
        " VALUES (?, ?, 12500, 1)",
        (variant_id, same_second),
    )
    conn.execute(
        "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus, in_stock)"
        " VALUES (?, ?, 13900, 0)",
        (variant_id, same_second),
    )

    rows = conn.execute("SELECT * FROM latest_prices").fetchall()

    assert len(rows) == 1
    assert rows[0]["price_kurus"] == 13900


def test_latest_prices_picks_the_newest_timestamp(conn: sqlite3.Connection) -> None:
    variant_id = _seed_variant(conn)
    for fetched_at, price in [
        ("2026-08-08T10:00:00Z", 12500),
        ("2026-08-07T10:00:00Z", 9900),
    ]:
        conn.execute(
            "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus,"
            " in_stock) VALUES (?, ?, ?, 1)",
            (variant_id, fetched_at, price),
        )

    row = conn.execute("SELECT * FROM latest_prices").fetchone()

    assert row["price_kurus"] == 12500
    assert row["fetched_at"] == "2026-08-08T10:00:00Z"


def test_latest_prices_computes_price_per_ml(conn: sqlite3.Connection) -> None:
    """5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths."""
    variant_id = _seed_variant(conn, size_ml_x10=50)
    conn.execute(
        "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus, in_stock)"
        " VALUES (?, '2026-08-08T10:00:00Z', 12500, 1)",
        (variant_id,),
    )

    row = conn.execute("SELECT price_per_ml_kurus FROM latest_prices").fetchone()

    assert row["price_per_ml_kurus"] == pytest.approx(2500.0)


def test_latest_prices_skips_variants_without_a_snapshot(
    conn: sqlite3.Connection,
) -> None:
    """No price yet means no row, so the basket LEFT JOIN reads it as missing."""
    _seed_variant(conn)

    assert conn.execute("SELECT * FROM latest_prices").fetchall() == []


def test_product_variants_rejects_a_zero_size(conn: sqlite3.Connection) -> None:
    """A zero ml variant is a parse failure, and it must not reach the table.

    If it did, latest_prices would divide by it and report a NULL price per ml,
    which the search table would show as an empty cell rather than as the
    broken row it is.
    """
    _seed_variant(conn)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO product_variants"
            " (product_id, size_ml_x10, raw_title, first_seen, last_seen)"
            " VALUES (1, 0, 'Sauvage EDT', '2026-08-08T10:00:00Z',"
            " '2026-08-08T10:00:00Z')"
        )


def test_basket_items_rejects_a_zero_size(conn: sqlite3.Connection) -> None:
    _seed_variant(conn)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO basket_items (perfume_id, size_ml_x10, qty, added_at)"
            " VALUES (1, 0, 1, '2026-08-08T10:00:00Z')"
        )


def test_basket_items_rejects_a_zero_quantity(conn: sqlite3.Connection) -> None:
    _seed_variant(conn)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO basket_items (perfume_id, size_ml_x10, qty, added_at)"
            " VALUES (1, 50, 0, '2026-08-08T10:00:00Z')"
        )


def test_connect_creates_the_expected_indexes(conn: sqlite3.Connection) -> None:
    names = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")
    }

    assert {
        "idx_snapshots_variant_time",
        "idx_variants_product",
        "idx_products_perfume",
    } <= names


def test_connect_is_idempotent_on_an_existing_database(tmp_path: Path) -> None:
    """Reopening an existing database must not wipe or re-raise on its schema."""
    db_path = tmp_path / "test.db"
    first = connect(db_path)
    variant_id = _seed_variant(first)
    first.commit()
    first.close()

    second = connect(db_path)
    try:
        row = second.execute(
            "SELECT variant_id FROM product_variants WHERE variant_id = ?",
            (variant_id,),
        ).fetchone()
    finally:
        second.close()

    assert row is not None
