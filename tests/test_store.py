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

from parfum_finder.engine import ProductCandidate, SearchHit, SiteResult, Variant
from parfum_finder.matcher import PerfumeQuery, parse_query
from parfum_finder.store import (
    SnapshotRow,
    add_basket_item,
    basket_lines,
    basket_prices,
    basket_sites,
    cached_prices,
    connect,
    now_iso,
    price_history,
    recent_searches,
    record_search,
    record_snapshot,
    remove_basket_item,
    remove_wishlist_item,
    save_wishlist_item,
    set_basket_qty,
    snapshot_rows,
    wishlist_rows,
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


# The view exactly as earlier versions wrote it. A test that reopens a database
# carrying this is the only thing standing between a rewritten view and shipping
# a change that never reaches anybody: CREATE VIEW IF NOT EXISTS will not replace
# a view that is already there, and a suite that only ever sees fresh databases
# passes either way.
_OLD_LATEST_PRICES_SQL = """
CREATE VIEW IF NOT EXISTS latest_prices AS
SELECT
    p.site_id,
    p.perfume_id,
    p.match_score,
    v.variant_id,
    v.size_ml_x10,
    v.raw_title,
    v.product_url,
    s.price_kurus,
    s.in_stock,
    s.fetched_at,
    CAST(s.price_kurus AS REAL) * 10.0 / v.size_ml_x10 AS price_per_ml_kurus
FROM price_snapshots s
JOIN product_variants v USING (variant_id)
JOIN products         p USING (product_id)
WHERE s.snapshot_id = (
    SELECT s2.snapshot_id
    FROM price_snapshots s2
    WHERE s2.variant_id = s.variant_id
    ORDER BY s2.fetched_at DESC, s2.snapshot_id DESC
    LIMIT 1
);
"""


def test_reopening_an_old_database_replaces_the_view_it_carries(
    tmp_path: Path,
) -> None:
    # The whole point of the DROP. Without it this passes on a fresh database and
    # fails on every one that exists, which is the worst possible split: nobody
    # would find out until a basket screen got slow enough to notice.
    db_path = tmp_path / "old.db"
    stale = sqlite3.connect(db_path)
    stale.executescript(_OLD_LATEST_PRICES_SQL)
    stale.commit()
    stale.close()

    conn = connect(db_path)
    try:
        sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'latest_prices'"
        ).fetchone()[0]
    finally:
        conn.close()

    assert "FROM product_variants" in sql
    assert "FROM price_snapshots s\nJOIN" not in sql


def test_the_newest_snapshot_wins_even_when_two_share_a_timestamp(
    conn: sqlite3.Connection,
) -> None:
    # What the view is for, and the part a rewrite could quietly get wrong. Two
    # readings in the same second are not hypothetical: the timestamp's own
    # resolution is one second, and a refresh that writes twice within one is a
    # normal Tuesday. Falling back on snapshot_id is what keeps "latest" meaning
    # the one written last rather than whichever row the join happened to reach.
    variant_id = _seed_variant(conn)
    same_second = "2026-08-08T10:00:00Z"
    for price in (10_000, 20_000, 30_000):
        conn.execute(
            "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus,"
            " in_stock) VALUES (?, ?, ?, 1)",
            (variant_id, same_second, price),
        )
    # An older reading written afterwards must not win on insertion order alone.
    conn.execute(
        "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus,"
        " in_stock) VALUES (?, '2026-08-01T10:00:00Z', 99_999, 1)",
        (variant_id,),
    )
    conn.commit()

    rows = conn.execute(
        "SELECT price_kurus FROM latest_prices WHERE variant_id = ?", (variant_id,)
    ).fetchall()

    assert [row["price_kurus"] for row in rows] == [30_000]


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
    first.execute("DROP TABLE wishlist_items")
    first.commit()
    first.close()

    second = connect(db_path)
    try:
        row = second.execute(
            "SELECT variant_id FROM product_variants WHERE variant_id = ?",
            (variant_id,),
        ).fetchone()
        wishlist_table = second.execute(
            "SELECT name FROM sqlite_master"
            " WHERE type = 'table' AND name = 'wishlist_items'"
        ).fetchone()
    finally:
        second.close()

    assert row is not None
    assert wishlist_table is not None


def test_wishlist_identity_keeps_variants_separate_and_upserts_in_place(
    conn: sqlite3.Connection,
) -> None:
    first = ("site|a", "brand", "name|EDP", "EDT", 50)
    second = ("site", "a|brand", "name", "EDP|EDT", 100)

    def save(
        identity: tuple[str, str, str, str, int], payload: str, added_at: str
    ) -> None:
        save_wishlist_item(
            conn,
            site_id=identity[0],
            brand=identity[1],
            name=identity[2],
            concentration=identity[3],
            size_ml_x10=identity[4],
            row_json=payload,
            added_at=added_at,
        )

    def remove(identity: tuple[str, str, str, str, int]) -> bool:
        return remove_wishlist_item(
            conn,
            site_id=identity[0],
            brand=identity[1],
            name=identity[2],
            concentration=identity[3],
            size_ml_x10=identity[4],
        )

    save(first, '{"price": 100}', "2026-01-01T00:00:00Z")
    save(second, '{"price": 200}', "2026-01-02T00:00:00Z")
    save(first, '{"price": 90}', "2026-01-03T00:00:00Z")

    assert wishlist_rows(conn) == ['{"price": 90}', '{"price": 200}']

    assert remove(first) is True
    assert remove(first) is False
    assert wishlist_rows(conn) == ['{"price": 200}']


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


def test_snapshot_rows_drops_a_title_the_matcher_rejects() -> None:
    """Another house's bottle on the same results page must not enter this history.

    match_title returns None for a title naming a different brand, and that
    rejection has to survive all the way to the stored rows, not just to a
    printed report: a row that slipped through here would put a stranger's
    price into this perfume's series.
    """
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Dior Sauvage EDP Dekant", url="u"
                ),
                variants=(_variant(50, 12500, raw_title="Dior Sauvage EDP 5 ml"),),
            ),
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Chanel Bleu EDP Dekant", url="u2"
                ),
                variants=(_variant(50, 9900, raw_title="Chanel Bleu EDP 5 ml"),),
            ),
        ),
        detail="ok",
    )
    query = PerfumeQuery(brand="Dior", name="Sauvage", concentration="")

    rows = snapshot_rows(result, query)

    assert len(rows) == 1
    assert rows[0].variant.price_kurus == 12500


def test_snapshot_rows_stores_the_titles_own_concentration() -> None:
    """EDT and EDP are different products, so the row has to say which one this was.

    A row stamped with the queried concentration instead would merge whatever
    the shop actually sells into whichever concentration happened to be typed
    into the search box.
    """
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Dior Sauvage EDT Dekant", url="u"
                ),
                variants=(_variant(50, 12500, raw_title="Dior Sauvage EDT 5 ml"),),
            ),
        ),
        detail="ok",
    )
    # Asked with no concentration named, so the title's own EDT is what has to
    # end up on the row.
    query = PerfumeQuery(brand="Dior", name="Sauvage", concentration="")

    rows = snapshot_rows(result, query)

    assert rows[0].concentration == "EDT"


def test_snapshot_rows_files_a_low_score_match_under_its_own_name() -> None:
    """'Layton' finding 'Layton Exclusif' must not price the two as one bottle.

    A site that only sells Exclusif would otherwise be stored under the plain
    Layton searched for: same brand/name/concentration means same perfume_id,
    which means one shared price history and one shared basket key. Adding
    Layton to the basket would then also light up Exclusif's rows, and
    Exclusif's price would show up on Layton's basket line as if that shop
    sold Layton itself.
    """
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Parfums De Marly Layton Exclusif", url="u"
                ),
                variants=(
                    _variant(
                        50, 54000, raw_title="Parfums De Marly Layton Exclusif 5 ml"
                    ),
                ),
            ),
        ),
        detail="ok",
    )
    query = parse_query("Parfums de Marly Layton")

    rows = snapshot_rows(result, query)

    assert len(rows) == 1
    assert rows[0].match_score < 85
    assert rows[0].brand == "parfums"
    assert rows[0].name == "de marly layton exclusif"
    assert (rows[0].brand, rows[0].name) != (query.brand, query.name)


def test_snapshot_rows_still_merges_a_confident_match_under_the_searched_name() -> None:
    """A shop that just writes the same bottle differently must not fork it.

    Filing every non-exact title under its own name would fragment one
    product's price history across however many ways shops phrase its title.
    The own-identity rule is for a low score only; a confident match stays
    under the identity that was searched for.
    """
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Parfums De Marly Layton Dekant", url="u"
                ),
                variants=(
                    _variant(50, 40000, raw_title="Parfums De Marly Layton 5 ml"),
                ),
            ),
        ),
        detail="ok",
    )
    query = parse_query("Parfums de Marly Layton")

    rows = snapshot_rows(result, query)

    assert len(rows) == 1
    assert rows[0].match_score >= 85
    assert (rows[0].brand, rows[0].name) == (query.brand, query.name)


def test_snapshot_rows_files_a_model_only_search_under_the_result_brand(
    conn: sqlite3.Connection,
) -> None:
    """A model word must not become the brand in the database.

    Different houses can use the same model name. Each accepted title therefore
    supplies its own brand while both keep the model the user searched for.
    """
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(raw_title="Lattafa Breeze", url="u1"),
                variants=(_variant(50, 40000, raw_title="Lattafa Breeze 5 ml"),),
            ),
            SearchHit(
                candidate=ProductCandidate(raw_title="Rayhaan Breeze", url="u2"),
                variants=(_variant(50, 41000, raw_title="Rayhaan Breeze 5 ml"),),
            ),
        ),
        detail="ok",
    )

    rows = snapshot_rows(result, parse_query("Breeze"))

    assert {(row.brand, row.name) for row in rows} == {
        ("lattafa", "breeze"),
        ("rayhaan", "breeze"),
    }
    _seed_site(conn)
    assert write_snapshots(conn, rows) == 2
    assert {
        (row["brand"], row["name"])
        for row in conn.execute("SELECT brand, name FROM perfumes")
    } == {("lattafa", "breeze"), ("rayhaan", "breeze")}


def test_snapshot_rows_recovers_a_multiword_model_search_brand() -> None:
    """The title prefix is the missing brand, not the model's first word."""
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Armani Stronger With You Intensely EDP", url="u"
                ),
                variants=(
                    _variant(
                        50,
                        50000,
                        raw_title="Armani Stronger With You Intensely EDP 5 ml",
                    ),
                ),
            ),
        ),
        detail="ok",
    )

    rows = snapshot_rows(result, parse_query("Stronger With You Intensely"))

    assert len(rows) == 1
    assert (rows[0].brand, rows[0].name, rows[0].concentration) == (
        "armani",
        "stronger with you intensely",
        "EDP",
    )


def test_add_basket_item_bumps_qty_instead_of_resetting_it(
    conn: sqlite3.Connection,
) -> None:
    """Adding the same perfume and size twice must accumulate, not clobber.

    The basket line stands for how many bottles someone wants, so re-adding a
    size that is already in the basket has to add to that count. Overwriting it
    back to whatever qty this call passed would silently lose an earlier add.
    """
    _seed_variant(conn)

    first_id = add_basket_item(
        conn,
        brand="Dior",
        name="Sauvage",
        concentration="EDT",
        size_ml_x10=50,
        qty=1,
        added_at="2026-08-07T10:00:00Z",
    )
    second_id = add_basket_item(
        conn,
        brand="Dior",
        name="Sauvage",
        concentration="EDT",
        size_ml_x10=50,
        qty=2,
        added_at="2026-08-08T10:00:00Z",
    )

    assert second_id == first_id
    row = conn.execute(
        "SELECT qty, added_at FROM basket_items WHERE basket_item_id = ?", (first_id,)
    ).fetchone()
    assert row["qty"] == 3
    # The basket screen orders by added_at, so a later top-up must not move a
    # line that was already sitting in the list.
    assert row["added_at"] == "2026-08-07T10:00:00Z"


def test_add_basket_item_refuses_a_perfume_with_no_price_on_record(
    conn: sqlite3.Connection,
) -> None:
    """A basket line for a perfume nobody has priced is a bug, not a state to keep.

    The TUI only ever holds brand/name/concentration, never a perfume_id, so
    without this check a typo or a perfume that was never scanned would
    silently create an empty perfume row instead of failing loud.
    """
    with pytest.raises(ValueError, match="no perfume on record"):
        add_basket_item(
            conn,
            brand="Dior",
            name="Sauvage",
            concentration="EDT",
            size_ml_x10=50,
        )


def test_price_history_is_newest_first_and_capped_at_limit(
    conn: sqlite3.Connection,
) -> None:
    """The trend panel reads row 0 as the latest reading, so order is the point.

    A history that came back oldest-first, or uncapped, would show yesterday's
    price where the panel expects today's, or flood a long-running variant's
    trend view with more rows than it asked for.
    """
    _seed_site(conn)
    stamps = [
        "2026-08-05T10:00:00Z",
        "2026-08-06T10:00:00Z",
        "2026-08-07T10:00:00Z",
        "2026-08-08T10:00:00Z",
    ]
    for i, ts in enumerate(stamps):
        _record(conn, _variant(price_kurus=10000 + i * 100), fetched_at=ts)

    rows = price_history(
        conn,
        site_id="ornek",
        brand="Dior",
        name="Sauvage",
        concentration="EDT",
        size_ml_x10=50,
        limit=2,
    )

    assert [row["fetched_at"] for row in rows] == stamps[::-1][:2]
    assert [row["price_kurus"] for row in rows] == [10300, 10200]


def test_price_history_is_empty_for_an_unknown_variant(
    conn: sqlite3.Connection,
) -> None:
    """No history yet is a normal state for a variant, not an error to raise on."""
    assert (
        price_history(
            conn,
            site_id="ornek",
            brand="Dior",
            name="Sauvage",
            concentration="EDT",
            size_ml_x10=50,
        )
        == []
    )


def test_cached_prices_serves_the_latest_reading_of_every_size(
    conn: sqlite3.Connection,
) -> None:
    """The search screen's second search must be answered with today's numbers.

    Two readings of the same size are two rows in price_snapshots, and the whole
    point of repainting a table from storage is that it shows the last thing the
    shop said. Serving the first reading would put a price on screen that a later
    scan already knew was wrong.
    """
    _seed_site(conn)
    _record(conn, _variant(50, 12500), fetched_at="2026-08-01T10:00:00Z")
    _record(conn, _variant(50, 13900), fetched_at="2026-08-08T10:00:00Z")
    _record(conn, _variant(100, 24000), fetched_at="2026-08-08T10:00:00Z")

    cached = cached_prices(conn, brand="Dior", name="Sauvage")

    assert {(c.size_ml_x10, c.price_kurus) for c in cached} == {
        (50, 13900),
        (100, 24000),
    }
    fresh = next(c for c in cached if c.size_ml_x10 == 50)
    assert fresh.fetched_at == "2026-08-08T10:00:00Z"
    assert (fresh.site_id, fresh.match_score, fresh.in_stock) == ("ornek", 95, True)
    assert fresh.raw_title == "Sauvage EDT 5 ml dekant"


def test_cached_prices_without_a_concentration_returns_every_one(
    conn: sqlite3.Connection,
) -> None:
    """A search that named no concentration is asking for all of them.

    "" means "any" on PerfumeQuery, and a live scan for it shows the EDT and the
    EDP side by side. A cache that answered the same search with one of the two
    would quietly drop half of what the table had before.
    """
    _seed_site(conn)
    _record(conn, _variant(50, 12500), concentration="EDT")
    _record(conn, _variant(50, 19900), concentration="EDP")

    any_concentration = cached_prices(conn, brand="Dior", name="Sauvage")
    just_edp = cached_prices(conn, brand="Dior", name="Sauvage", concentration="EDP")

    assert {c.concentration for c in any_concentration} == {"EDT", "EDP"}
    # Exact when it is given, because an EDT and an EDP are two products with
    # two prices and answering with the cheaper one is answering another search.
    assert [(c.concentration, c.price_kurus) for c in just_edp] == [("EDP", 19900)]


def test_cached_prices_leaves_out_a_disabled_site(conn: sqlite3.Connection) -> None:
    """A price nobody will scan again may not be offered as a result.

    Refreshing is what makes a cached row trustworthy, and a disabled site is
    never scanned, so its stored price can only get older. Showing it would put
    a number on screen that [r] cannot do anything about.
    """
    _seed_site(conn, "kapali")
    conn.execute("UPDATE sites SET enabled = 0 WHERE site_id = 'kapali'")
    record_snapshot(
        conn,
        site_id="kapali",
        brand="Dior",
        name="Sauvage",
        concentration="EDT",
        match_score=95,
        variant=_variant(50, 12500),
    )

    assert cached_prices(conn, brand="Dior", name="Sauvage") == []


def test_cached_prices_is_empty_for_a_perfume_nobody_scanned(
    conn: sqlite3.Connection,
) -> None:
    """Nothing on record is the state before a first search, not an error.

    The search screen turns an empty answer here straight into a live scan, so
    this returning [] rather than raising is what keeps a first search from
    needing a keypress to produce prices.
    """
    assert cached_prices(conn, brand="dior", name="sauvage") == []


def test_a_scanned_perfume_can_be_read_back_by_basket_and_history(
    conn: sqlite3.Connection,
) -> None:
    """The identity a real scan writes must be the identity these lookups accept.

    add_basket_item and price_history take brand/name/concentration by hand,
    but the only row they ever have to find in practice is one snapshot_rows
    wrote from a parsed query, which folds brand and name to lowercase and the
    concentration to its canonical spelling. A test that seeds 'Dior'/'Sauvage'
    directly and then looks it up the same way could pass while the real path,
    which writes 'dior'/'sauvage', silently never matches.
    """
    _seed_site(conn)
    query = parse_query("Dior Sauvage EDT")
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title="Dior Sauvage EDT Dekant", url="u"
                ),
                variants=(_variant(50, 12500, raw_title="Dior Sauvage EDT 5 ml"),),
            ),
        ),
        detail="ok",
    )
    written = write_snapshots(conn, snapshot_rows(result, query))
    assert written == 1

    history = price_history(
        conn,
        site_id="ornek",
        brand=query.brand,
        name=query.name,
        concentration="EDT",
        size_ml_x10=50,
    )
    basket_item_id = add_basket_item(
        conn,
        brand=query.brand,
        name=query.name,
        concentration="EDT",
        size_ml_x10=50,
    )

    assert len(history) == 1
    assert history[0]["price_kurus"] == 12500
    assert basket_item_id is not None


def test_basket_lines_orders_by_added_at_and_carries_the_perfume_identity(
    conn: sqlite3.Connection,
) -> None:
    """The basket screen prints brand/name/concentration straight off this row.

    Ordering by added_at is the whole point of the join: a line added first
    has to stay first, or the basket would reshuffle itself every time the
    screen redraws.
    """
    _seed_variant(conn)
    conn.execute(
        "INSERT INTO perfumes (brand, name, concentration, created_at)"
        " VALUES ('Chanel', 'Bleu de Chanel', 'EDP', '2026-08-08T09:00:00Z')"
    )
    later_id = add_basket_item(
        conn,
        brand="Dior",
        name="Sauvage",
        concentration="EDT",
        size_ml_x10=50,
        added_at="2026-08-08T11:00:00Z",
    )
    earlier_id = add_basket_item(
        conn,
        brand="Chanel",
        name="Bleu de Chanel",
        concentration="EDP",
        size_ml_x10=100,
        added_at="2026-08-08T10:00:00Z",
    )

    lines = basket_lines(conn)

    assert [line.basket_item_id for line in lines] == [earlier_id, later_id]
    assert lines[0].brand == "Chanel"
    assert lines[0].name == "Bleu de Chanel"
    assert lines[0].concentration == "EDP"
    assert lines[0].size_ml_x10 == 100
    assert lines[0].qty == 1


def test_basket_lines_breaks_a_same_second_tie_by_basket_item_id(
    conn: sqlite3.Connection,
) -> None:
    """Two lines added within the same second must still read back the same way twice.

    added_at alone can't order them, so without the id tiebreaker sqlite is
    free to hand the two rows back in either order on different reads, and
    the basket screen would look like it swapped two lines for no reason.
    """
    _seed_variant(conn)
    conn.execute(
        "INSERT INTO perfumes (brand, name, concentration, created_at)"
        " VALUES ('Chanel', 'Bleu de Chanel', 'EDP', '2026-08-08T09:00:00Z')"
    )
    same_second = "2026-08-08T10:00:00Z"
    first_id = add_basket_item(
        conn,
        brand="Dior",
        name="Sauvage",
        concentration="EDT",
        size_ml_x10=50,
        added_at=same_second,
    )
    second_id = add_basket_item(
        conn,
        brand="Chanel",
        name="Bleu de Chanel",
        concentration="EDP",
        size_ml_x10=100,
        added_at=same_second,
    )

    lines = basket_lines(conn)

    assert [line.basket_item_id for line in lines] == [first_id, second_id]


def test_basket_prices_has_no_row_for_a_line_no_site_prices(
    conn: sqlite3.Connection,
) -> None:
    """A basket line nobody sells must still be visible via basket_lines.

    basket_prices uses a LEFT JOIN so it can tell "nobody sells it" apart
    from "this one site does not", but the caller only gets that distinction
    if the unpriced line is dropped here rather than showing up as a row of
    NULLs.
    """
    _seed_variant(conn)
    _record(conn)  # priced at the default 5 ml
    add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=50
    )
    unpriced_id = add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=100
    )

    prices = basket_prices(conn)
    lines = basket_lines(conn)

    assert unpriced_id in {line.basket_item_id for line in lines}
    assert unpriced_id not in {p.basket_item_id for p in prices}
    assert len(prices) == 1
    assert prices[0].price_kurus == 12500


def test_basket_prices_reports_only_the_latest_snapshot(
    conn: sqlite3.Connection,
) -> None:
    """A stale reading must never outrank the one taken after it.

    latest_prices already guarantees this at the view level; this checks the
    basket matrix query doesn't accidentally pick up both snapshots instead
    of the newest one.
    """
    _seed_variant(conn)
    _record(conn, _variant(price_kurus=12500), fetched_at="2026-08-07T10:00:00Z")
    _record(conn, _variant(price_kurus=11900), fetched_at="2026-08-08T10:00:00Z")
    add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=50
    )

    prices = basket_prices(conn)

    assert len(prices) == 1
    assert prices[0].price_kurus == 11900
    assert prices[0].fetched_at == "2026-08-08T10:00:00Z"


def test_basket_prices_joins_on_the_exact_integer_size(
    conn: sqlite3.Connection,
) -> None:
    """A 10 ml listing must never fill a basket line asking for 5 ml.

    The matrix joins on size_ml_x10 as an integer specifically so this can't
    happen; a fuzzier join (nearest size, or dropping the tenths) would let a
    bigger bottle's price stand in for a smaller one nobody actually offers.
    """
    _seed_variant(conn, size_ml_x10=100)
    _record(conn, _variant(size_ml_x10=100, price_kurus=20000))
    add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=50
    )

    assert basket_prices(conn) == []


def test_basket_prices_keeps_out_of_stock_rows_with_in_stock_false(
    conn: sqlite3.Connection,
) -> None:
    """Whether an out-of-stock price counts as missing is the caller's call.

    Dropping it here instead would take that decision away from whatever
    screen or optimizer reads this list next.
    """
    _seed_variant(conn)
    _record(conn, _variant(price_kurus=12500, in_stock=False))
    add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=50
    )

    prices = basket_prices(conn)

    assert len(prices) == 1
    assert prices[0].in_stock is False


def test_basket_sites_omits_a_disabled_site_and_keeps_one_that_prices_nothing(
    conn: sqlite3.Connection,
) -> None:
    """A disabled site loses its basket column, but an enabled quiet one keeps one.

    Sourcing the site list from the price matrix instead of from sites would
    make an enabled site that happens to price none of the basket's lines
    vanish, which is exactly the "this site has nothing" state the basket
    screen's dash column exists to show.
    """
    ts = "2026-08-08T10:00:00Z"
    conn.execute(
        "INSERT INTO sites (site_id, name, base_url, enabled, synced_at)"
        " VALUES ('kapali', 'Kapali', 'https://kapali.example', 0, ?)",
        (ts,),
    )
    conn.execute(
        "INSERT INTO sites (site_id, name, base_url, enabled, synced_at)"
        " VALUES ('sessiz', 'Sessiz', 'https://sessiz.example', 1, ?)",
        (ts,),
    )

    sites = basket_sites(conn)

    assert "kapali" not in {s.site_id for s in sites}
    assert "sessiz" in {s.site_id for s in sites}


def test_basket_sites_preserves_a_null_free_shipping_threshold_as_none(
    conn: sqlite3.Connection,
) -> None:
    """NULL means the site has no free shipping tier at all, not a threshold of zero.

    Coming back as anything but None would make the basket screen compute a
    'free shipping gap' toward a tier the site doesn't actually offer.
    """
    ts = "2026-08-08T10:00:00Z"
    conn.execute(
        "INSERT INTO sites (site_id, name, base_url, synced_at)"
        " VALUES ('nosiz', 'Nosiz', 'https://nosiz.example', ?)",
        (ts,),
    )

    sites = basket_sites(conn)

    assert sites[0].site_id == "nosiz"
    assert sites[0].free_shipping_threshold_kurus is None


def test_remove_basket_item_returns_false_the_second_time(
    conn: sqlite3.Connection,
) -> None:
    """Deleting a row that's already gone is a race between two screens, not a bug.

    A second delete of the same id has to report that it didn't do anything,
    rather than raise, so a caller can treat it as a normal outcome.
    """
    _seed_variant(conn)
    item_id = add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=50
    )

    assert remove_basket_item(conn, basket_item_id=item_id) is True
    assert remove_basket_item(conn, basket_item_id=item_id) is False


def test_set_basket_qty_clamps_zero_and_negatives_to_one(
    conn: sqlite3.Connection,
) -> None:
    """The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to
    survive it.

    Decrementing below 1 is a no-op rather than a delete: removal is a
    separate key, so pressing '-' at quantity 1 must leave the line in the
    basket at quantity 1, not blow up or vanish it.
    """
    _seed_variant(conn)
    item_id = add_basket_item(
        conn, brand="Dior", name="Sauvage", concentration="EDT", size_ml_x10=50
    )

    assert set_basket_qty(conn, basket_item_id=item_id, qty=0) == 1
    assert set_basket_qty(conn, basket_item_id=item_id, qty=-3) == 1

    stored = conn.execute(
        "SELECT qty FROM basket_items WHERE basket_item_id = ?", (item_id,)
    ).fetchone()
    assert stored["qty"] == 1


def test_set_basket_qty_on_an_unknown_id_raises(conn: sqlite3.Connection) -> None:
    """An update aimed at a row that isn't there means the caller is out of sync.

    Unlike remove_basket_item's idempotent False, silently doing nothing here
    would hide a basket screen holding a stale id from ever finding out.
    """
    with pytest.raises(ValueError, match="no basket item"):
        set_basket_qty(conn, basket_item_id=999, qty=2)


def test_snapshot_rows_marks_a_clone_instead_of_filing_it_as_the_original() -> None:
    """A shop's imitation must not be stored as the perfume it imitates.

    The clone is a different bottle at a different price. Filed under the
    searched perfume's identity it would sit in that perfume's price history
    as a sudden drop, and the basket would price the whole order off it.
    """
    result = SiteResult(
        site_id="ornek",
        status="ok",
        hits=(
            SearchHit(
                candidate=ProductCandidate(
                    raw_title=(
                        "Armaf – Club De Nuit Untold "
                        "(Maison Francis Kurkdjian – Baccarat Rouge 540)"
                    ),
                    url="u",
                ),
                variants=(_variant(50, 4900, raw_title="Untold 5 ml"),),
            ),
        ),
        detail="ok",
    )
    query = parse_query("Maison Francis Kurkdjian Baccarat Rouge 540")

    rows = snapshot_rows(result, query)

    assert len(rows) == 1
    assert rows[0].clone_of == "Maison Francis Kurkdjian – Baccarat Rouge 540"


def test_write_snapshots_never_records_a_row_without_its_own_identity(
    conn: sqlite3.Connection,
) -> None:
    """The drop happens here so no caller can forget it.

    Both the CLI and the screen write through this function, and a bottle stored
    under another perfume's brand and name would be indistinguishable from that
    perfume's own price once it was in the table. A clone that knows what it is
    goes in as itself; the one whose own title read as nothing is the only row
    left with nowhere to go, and it is dropped rather than filed under the
    perfume it imitates.
    """
    _seed_site(conn)
    real = SnapshotRow(
        site_id="ornek",
        brand="maison",
        name="francis kurkdjian baccarat rouge 540",
        concentration="",
        match_score=100,
        variant=_variant(50, 62000, raw_title="Baccarat Rouge 540 5 ml"),
    )
    clone = SnapshotRow(
        site_id="ornek",
        brand="armaf",
        name="club de nuit untold",
        concentration="",
        match_score=100,
        variant=_variant(50, 4900, raw_title="Armaf Club De Nuit Untold 5 ml"),
        clone_of="Maison Francis Kurkdjian – Baccarat Rouge 540",
    )
    nameless = SnapshotRow(
        site_id="ornek",
        brand="maison",
        name="francis kurkdjian baccarat rouge 540",
        concentration="",
        match_score=100,
        variant=_variant(50, 3900, raw_title="Untold 5 ml"),
        clone_of="Maison Francis Kurkdjian – Baccarat Rouge 540",
        own_identity=False,
    )

    assert write_snapshots(conn, [real, clone, nameless]) == 2
    rows = conn.execute(
        "SELECT pf.brand, s.price_kurus FROM price_snapshots s"
        " JOIN product_variants v ON v.variant_id = s.variant_id"
        " JOIN products p ON p.product_id = v.product_id"
        " JOIN perfumes pf ON pf.perfume_id = p.perfume_id"
        " ORDER BY s.price_kurus"
    ).fetchall()
    assert [tuple(row) for row in rows] == [("armaf", 4900), ("maison", 62000)]


def test_rerunning_a_search_moves_it_up_instead_of_adding_a_second_copy(
    conn: sqlite3.Connection,
) -> None:
    """The recents list has five slots, so a repeat must not consume two.

    Someone who searches the same two perfumes every morning would otherwise
    push everything else out with copies of one line.
    """
    record_search(conn, "dior sauvage edp", "2026-08-10T09:00:00Z")
    record_search(conn, "creed aventus", "2026-08-11T09:00:00Z")
    record_search(conn, "dior sauvage edp", "2026-08-12T09:00:00Z")

    assert recent_searches(conn) == [
        ("dior sauvage edp", "2026-08-12T09:00:00Z"),
        ("creed aventus", "2026-08-11T09:00:00Z"),
    ]


def test_recent_searches_stops_at_the_limit(conn: sqlite3.Connection) -> None:
    for i in range(8):
        record_search(conn, f"parfum {i}", f"2026-08-{10 + i:02d}T09:00:00Z")

    recent = recent_searches(conn, limit=5)

    assert len(recent) == 5
    assert [text for text, _ in recent] == [f"parfum {i}" for i in (7, 6, 5, 4, 3)]
