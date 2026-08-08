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

from parfum_finder.engine import Variant
from parfum_finder.store import (
    SnapshotRow,
    connect,
    now_iso,
    record_snapshot,
    write_snapshots,
)

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


def _seed_site(conn: sqlite3.Connection, site_id: str = "ornek") -> None:
    conn.execute(
        "INSERT OR IGNORE INTO sites (site_id, name, base_url, synced_at)"
        " VALUES (?, 'Örnek', 'https://ornek-site.com', '2026-08-08T10:00:00Z')",
        (site_id,),
    )


def _variant(
    size_ml_x10: int = 50,
    price_kurus: int | None = 12500,
    *,
    raw_title: str | None = "Sauvage EDT 5 ml dekant",
    product_url: str | None = "https://ornek-site.com/sauvage-5ml",
    in_stock: bool | None = True,
) -> Variant:
    return Variant(
        size_ml_x10=size_ml_x10,
        raw_title=raw_title,
        product_url=product_url,
        price_kurus=price_kurus,
        in_stock=in_stock,
    )


def _record(
    conn: sqlite3.Connection,
    variant: Variant | None = None,
    *,
    concentration: str = "EDT",
    match_score: int = 95,
    fetched_at: str | None = None,
) -> int | None:
    return record_snapshot(
        conn,
        site_id="ornek",
        brand="Dior",
        name="Sauvage",
        concentration=concentration,
        match_score=match_score,
        variant=variant if variant is not None else _variant(),
        fetched_at=fetched_at,
    )


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


def test_record_snapshot_writes_the_whole_chain(conn: sqlite3.Connection) -> None:
    """One call has to leave a row the search table can read straight off.

    The caller holds a perfume by its name, not by an id, so if this didn't
    create the perfume, product and variant on the way down, every caller would
    have to hand-roll the same four inserts and the identity key would end up
    spelled slightly differently in each of them.
    """
    _seed_site(conn)

    snapshot_id = _record(conn, fetched_at="2026-08-08T10:00:00Z")

    row = conn.execute("SELECT * FROM latest_prices").fetchone()
    assert snapshot_id is not None
    assert row["site_id"] == "ornek"
    assert row["size_ml_x10"] == 50
    assert row["price_kurus"] == 12500
    assert row["in_stock"] == 1
    assert row["match_score"] == 95
    assert row["raw_title"] == "Sauvage EDT 5 ml dekant"
    assert row["fetched_at"] == "2026-08-08T10:00:00Z"


def test_a_second_scan_appends_instead_of_overwriting(
    conn: sqlite3.Connection,
) -> None:
    """The old price has to survive, and it must not become a second variant.

    Append-only is the whole reason this table exists: an UPDATE would erase
    the reading someone wants to compare today's price against. The identity
    rows above it must not multiply either, or the same size would show up as
    two rows in the results table with two separate half-histories.
    """
    _seed_site(conn)

    _record(conn, _variant(price_kurus=12500), fetched_at="2026-08-07T10:00:00Z")
    _record(conn, _variant(price_kurus=9900), fetched_at="2026-08-08T10:00:00Z")

    prices = [
        row["price_kurus"]
        for row in conn.execute(
            "SELECT price_kurus FROM price_snapshots ORDER BY fetched_at"
        )
    ]
    counts = conn.execute(
        "SELECT (SELECT COUNT(*) FROM perfumes) AS p,"
        " (SELECT COUNT(*) FROM products) AS pr,"
        " (SELECT COUNT(*) FROM product_variants) AS v"
    ).fetchone()

    assert prices == [12500, 9900]
    assert (counts["p"], counts["pr"], counts["v"]) == (1, 1, 1)


def test_a_second_scan_moves_last_seen_and_keeps_first_seen(
    conn: sqlite3.Connection,
) -> None:
    """first_seen is what says how long a shop has carried a size."""
    _seed_site(conn)

    _record(conn, fetched_at="2026-08-07T10:00:00Z")
    _record(conn, fetched_at="2026-08-08T10:00:00Z")

    row = conn.execute("SELECT first_seen, last_seen FROM product_variants").fetchone()

    assert row["first_seen"] == "2026-08-07T10:00:00Z"
    assert row["last_seen"] == "2026-08-08T10:00:00Z"


def test_a_renamed_listing_keeps_its_price_history(conn: sqlite3.Connection) -> None:
    """The title and URL are information, not identity.

    A shop that rewords a listing or moves its slug is still selling the same
    5 ml of the same perfume. Starting a new row there would split the history
    in two and quietly hide when the price changed.
    """
    _seed_site(conn)
    _record(conn, _variant(price_kurus=12500), fetched_at="2026-08-07T10:00:00Z")

    _record(
        conn,
        _variant(
            price_kurus=9900,
            raw_title="Dior Sauvage EDT 5ml dekant (yeni)",
            product_url="https://ornek-site.com/dior-sauvage-edt-5-ml",
        ),
        fetched_at="2026-08-08T10:00:00Z",
    )

    variants = conn.execute("SELECT * FROM product_variants").fetchall()
    assert len(variants) == 1
    assert variants[0]["raw_title"] == "Dior Sauvage EDT 5ml dekant (yeni)"
    assert variants[0]["product_url"] == "https://ornek-site.com/dior-sauvage-edt-5-ml"
    assert conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0] == 2


def test_two_concentrations_are_two_price_series(conn: sqlite3.Connection) -> None:
    """EDT and EDP are different products at different prices.

    Folding them into one series would average two unrelated prices into a
    history that describes neither bottle.
    """
    _seed_site(conn)

    _record(conn, concentration="EDT")
    _record(conn, _variant(price_kurus=17900), concentration="EDP")

    rows = conn.execute(
        "SELECT price_kurus FROM latest_prices ORDER BY price_kurus"
    ).fetchall()

    assert [row["price_kurus"] for row in rows] == [12500, 17900]


def test_a_size_without_a_price_is_stored_but_not_priced(
    conn: sqlite3.Connection,
) -> None:
    """A sold-out size often shows no price at all, and 0 would mean free.

    Writing a zero there would put the cheapest offer on the table on a row
    nobody can buy, and a basket optimizer would pick it. Keeping the variant
    still records that the shop lists this size.
    """
    _seed_site(conn)

    snapshot_id = _record(conn, _variant(price_kurus=None, in_stock=False))

    assert snapshot_id is None
    assert conn.execute("SELECT COUNT(*) FROM product_variants").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0] == 0


def test_an_unknown_stock_state_is_written_as_out_of_stock(
    conn: sqlite3.Connection,
) -> None:
    """The column is 0/1, so the tri-state has to land somewhere on purpose.

    Unknown becomes 0: the stock filter is there to hide what cannot be bought,
    and calling an unread field "in stock" would put a possibly dead row in
    front of someone filtering for buyable ones.
    """
    _seed_site(conn)

    _record(conn, _variant(in_stock=None))

    assert conn.execute("SELECT in_stock FROM price_snapshots").fetchone()[0] == 0


def test_a_variant_with_no_title_is_refused(conn: sqlite3.Connection) -> None:
    """raw_title is the audit trail for a wrong match, so it cannot be blank.

    A row without one can never be checked by eye afterwards, and getting here
    means the profile stopped reading the page rather than the shop selling
    something nameless.
    """
    _seed_site(conn)

    with pytest.raises(ValueError, match="no title"):
        _record(conn, _variant(raw_title=None))


def test_a_snapshot_for_an_unknown_site_is_refused(conn: sqlite3.Connection) -> None:
    """Sites come from the profiles, so an id nothing synced is a mistake."""
    with pytest.raises(sqlite3.IntegrityError):
        _record(conn)


def test_write_snapshots_stamps_one_scan_with_one_timestamp(
    conn: sqlite3.Connection,
) -> None:
    """A slow site must not spread one reading across several timestamps.

    Rows written under different stamps stop being comparable as one visit,
    which is what "what did these cost at the same moment" needs.
    """
    _seed_site(conn)
    rows = [
        SnapshotRow("ornek", "Dior", "Sauvage", "EDT", 95, _variant(50, 12500)),
        SnapshotRow("ornek", "Dior", "Sauvage", "EDT", 95, _variant(100, 23000)),
    ]

    stamps = iter(["2026-08-08T10:00:00Z", "2026-08-08T10:00:09Z"])
    with patch("parfum_finder.store.now_iso", lambda: next(stamps)):
        written = write_snapshots(conn, rows)

    assert written == 2
    assert {
        row["fetched_at"] for row in conn.execute("SELECT * FROM price_snapshots")
    } == {"2026-08-08T10:00:00Z"}


def test_write_snapshots_counts_prices_not_rows(conn: sqlite3.Connection) -> None:
    """The number reported is what landed in the history, not what was offered."""
    _seed_site(conn)
    rows = [
        SnapshotRow("ornek", "Dior", "Sauvage", "EDT", 95, _variant(50, 12500)),
        SnapshotRow("ornek", "Dior", "Sauvage", "EDT", 95, _variant(100, None)),
    ]

    assert write_snapshots(conn, rows) == 1


def test_write_snapshots_rolls_the_whole_batch_back_on_failure(
    conn: sqlite3.Connection,
) -> None:
    """Half a site's sizes updated is worse than none of them.

    The basket compares sizes against each other, so a run that died partway
    through would leave one size at today's price next to another at last
    week's and read as a real spread.
    """
    _seed_site(conn)
    rows = [
        SnapshotRow("ornek", "Dior", "Sauvage", "EDT", 95, _variant(50, 12500)),
        SnapshotRow(
            "ornek", "Dior", "Sauvage", "EDT", 95, _variant(100, 23000, raw_title=None)
        ),
    ]

    with pytest.raises(ValueError):
        write_snapshots(conn, rows)

    assert conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM product_variants").fetchone()[0] == 0
