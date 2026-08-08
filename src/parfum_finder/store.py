"""SQLite persistence: an append-only price history.

Tables: sites, perfumes, products, product_variants, price_snapshots, basket_items.
A latest_prices view surfaces the most recent snapshot per variant. The identity key
for a price series is (site_id, brand, name, concentration, size_ml), never the
product URL, so history survives a store renaming its slugs.

Timestamps go through a single now_iso() helper (UTC, "YYYY-MM-DDTHH:MM:SSZ").
Nothing in this codebase calls datetime.now().isoformat() directly, because mixing
timestamp formats would silently break "most recent" ordering.

The sites table is filled from the JSON profiles by profiles.sync_to_db(), which
is why nothing here writes to it.
"""

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from parfum_finder.engine import Variant

DEFAULT_DB_PATH = Path("parfum-finder.db")

# Transcribed from the schema doc. Money is INTEGER kurus and volume is INTEGER
# tenths of a ml on purpose: the basket matrix joins on size and compares totals
# against a free-shipping threshold, and REAL would make both of those flaky.
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sites (
    site_id                       TEXT PRIMARY KEY,
    name                          TEXT NOT NULL,
    base_url                      TEXT NOT NULL,
    enabled                       INTEGER NOT NULL DEFAULT 1,
    free_shipping_threshold_kurus INTEGER,
    shipping_cost_kurus           INTEGER NOT NULL DEFAULT 0,
    notes                         TEXT,
    profile_discovered_at         TEXT,
    synced_at                     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS perfumes (
    perfume_id    INTEGER PRIMARY KEY,
    brand         TEXT NOT NULL,
    name          TEXT NOT NULL,
    concentration TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    UNIQUE (brand, name, concentration)
);

CREATE TABLE IF NOT EXISTS products (
    product_id   INTEGER PRIMARY KEY,
    site_id      TEXT    NOT NULL REFERENCES sites(site_id),
    perfume_id   INTEGER NOT NULL REFERENCES perfumes(perfume_id),
    match_score  INTEGER NOT NULL,
    first_seen   TEXT    NOT NULL,
    last_seen    TEXT    NOT NULL,
    UNIQUE (site_id, perfume_id)
);

CREATE TABLE IF NOT EXISTS product_variants (
    variant_id   INTEGER PRIMARY KEY,
    product_id   INTEGER NOT NULL REFERENCES products(product_id),
    -- A zero here would be a failed ml parse, not a real variant. Rejecting it
    -- at the table keeps latest_prices from dividing by it and handing back a
    -- NULL price per ml that reads like "no data" instead of "broken row".
    size_ml_x10  INTEGER NOT NULL CHECK (size_ml_x10 > 0),
    raw_title    TEXT    NOT NULL,
    product_url  TEXT,
    first_seen   TEXT    NOT NULL,
    last_seen    TEXT    NOT NULL,
    UNIQUE (product_id, size_ml_x10)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    snapshot_id  INTEGER PRIMARY KEY,
    variant_id   INTEGER NOT NULL REFERENCES product_variants(variant_id),
    fetched_at   TEXT    NOT NULL,
    price_kurus  INTEGER NOT NULL,
    in_stock     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS basket_items (
    basket_item_id INTEGER PRIMARY KEY,
    perfume_id     INTEGER NOT NULL REFERENCES perfumes(perfume_id),
    size_ml_x10    INTEGER NOT NULL CHECK (size_ml_x10 > 0),
    qty            INTEGER NOT NULL DEFAULT 1 CHECK (qty > 0),
    added_at       TEXT    NOT NULL,
    UNIQUE (perfume_id, size_ml_x10)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_variant_time
    ON price_snapshots  (variant_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_variants_product
    ON product_variants (product_id);
CREATE INDEX IF NOT EXISTS idx_products_perfume
    ON products         (perfume_id);

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


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open the price database, creating the schema if it isn't there yet.

    Foreign keys are off by default in SQLite and the setting is per
    connection, so it gets turned on here. Without it a snapshot could point
    at a variant that no longer exists and nothing would complain, which is
    exactly the kind of quiet wrongness the price history can't tolerate.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def now_iso() -> str:
    """Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.

    Every timestamp written to the database goes through this function.
    The database picks the most recent price snapshot with a plain text
    ORDER BY, not a real datetime comparison, so that only gives the right
    answer if every writer produces the exact same fixed-width format.
    Mixing in microseconds, a UTC offset instead of 'Z', or local time would
    make "most recent" silently wrong.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class SnapshotRow:
    """One priced size of one perfume on one site, ready to be written.

    The perfume is named by its three identity parts rather than by an id,
    because that is the identity the price history is keyed on and the caller
    already holds it. `match_score` is the matcher's verdict on this site's
    wording, stored so a wrong match can be found again later instead of only
    being noticed once.
    """

    site_id: str
    brand: str
    name: str
    concentration: str
    match_score: int
    variant: Variant


def record_snapshot(
    conn: sqlite3.Connection,
    *,
    site_id: str,
    brand: str,
    name: str,
    concentration: str,
    match_score: int,
    variant: Variant,
    fetched_at: str | None = None,
) -> int | None:
    """Write one scan's reading of one size, and return its snapshot id.

    The perfume, the site-perfume match and the size row are upserted, so a
    second scan finds the same rows and only moves their last_seen. The price
    row is never upserted: price_snapshots is append-only, and every scan adds
    one line to it. That table is the only record of when something got cheaper,
    and an UPDATE would erase exactly the reading somebody wants to compare
    against.

    Returns None when the size had no price. The size still gets its row, since
    "this shop lists a 5 ml" is worth knowing even on a scan that could not read
    what it costs, but price_kurus has no honest value to hold: a 0 there reads
    as free and would come out of a basket optimizer as the cheapest offer on
    the table.

    Nothing is committed here beyond this one row, so a caller writing a whole
    site's results wants write_snapshots instead.
    """
    with conn:
        return _record(
            conn,
            site_id=site_id,
            brand=brand,
            name=name,
            concentration=concentration,
            match_score=match_score,
            variant=variant,
            fetched_at=fetched_at or now_iso(),
        )


def write_snapshots(
    conn: sqlite3.Connection,
    rows: Iterable[SnapshotRow],
    *,
    fetched_at: str | None = None,
) -> int:
    """Write a whole scan at once and return how many prices were recorded.

    Every row gets the same fetched_at, taken once at the start. A scan is one
    reading of the market, and letting each row stamp itself would spread a slow
    run across several timestamps and make a later "what did this cost on the
    same visit" comparison line up rows that were never compared.

    The count is of price rows, not of input rows: sizes that came back without
    a price are stored as sizes and do not count as prices.

    One transaction for the batch. A run that dies halfway through leaves the
    database as it was rather than a site with three of its eight sizes updated.
    """
    stamp = fetched_at or now_iso()
    written = 0
    with conn:
        for row in rows:
            snapshot_id = _record(
                conn,
                site_id=row.site_id,
                brand=row.brand,
                name=row.name,
                concentration=row.concentration,
                match_score=row.match_score,
                variant=row.variant,
                fetched_at=stamp,
            )
            if snapshot_id is not None:
                written += 1
    return written


def _record(
    conn: sqlite3.Connection,
    *,
    site_id: str,
    brand: str,
    name: str,
    concentration: str,
    match_score: int,
    variant: Variant,
    fetched_at: str,
) -> int | None:
    """Do the writing, without opening a transaction of its own."""
    if variant.raw_title is None:
        # The stored title is how a person checks later whether the match was
        # right, so a row without one cannot be audited at all. Getting here
        # means neither the size nor the listing it came from had a title,
        # which is a profile that stopped reading the page, not a shop selling
        # something nameless.
        raise ValueError(
            f"{site_id}: a {variant.size_ml_x10 / 10:g} ml size of "
            f"{brand} {name} came back with no title to store"
        )
    perfume_id = _perfume_id(conn, brand, name, concentration, fetched_at)
    product_id = _product_id(conn, site_id, perfume_id, match_score, fetched_at)
    variant_id = _variant_id(conn, product_id, variant, fetched_at)
    if variant.price_kurus is None:
        return None
    cursor = conn.execute(
        "INSERT INTO price_snapshots (variant_id, fetched_at, price_kurus, in_stock)"
        " VALUES (?, ?, ?, ?)",
        (variant_id, fetched_at, variant.price_kurus, int(bool(variant.in_stock))),
    )
    return int(cursor.lastrowid or 0)


def _perfume_id(
    conn: sqlite3.Connection, brand: str, name: str, concentration: str, ts: str
) -> int:
    conn.execute(
        "INSERT INTO perfumes (brand, name, concentration, created_at)"
        " VALUES (?, ?, ?, ?)"
        " ON CONFLICT (brand, name, concentration) DO NOTHING",
        (brand, name, concentration, ts),
    )
    return _scalar(
        conn,
        "SELECT perfume_id FROM perfumes"
        " WHERE brand = ? AND name = ? AND concentration = ?",
        (brand, name, concentration),
    )


def _product_id(
    conn: sqlite3.Connection, site_id: str, perfume_id: int, match_score: int, ts: str
) -> int:
    # match_score is overwritten rather than kept from the first sighting: a shop
    # that reworded its listing is judged on the wording it has now, and that is
    # the number the results table shows next to today's price.
    conn.execute(
        "INSERT INTO products (site_id, perfume_id, match_score, first_seen, last_seen)"
        " VALUES (?, ?, ?, ?, ?)"
        " ON CONFLICT (site_id, perfume_id) DO UPDATE SET"
        " match_score = excluded.match_score, last_seen = excluded.last_seen",
        (site_id, perfume_id, match_score, ts, ts),
    )
    return _scalar(
        conn,
        "SELECT product_id FROM products WHERE site_id = ? AND perfume_id = ?",
        (site_id, perfume_id),
    )


def _variant_id(
    conn: sqlite3.Connection, product_id: int, variant: Variant, ts: str
) -> int:
    # raw_title and product_url are refreshed on every sighting. They are not part
    # of the identity, so a renamed listing or a moved slug updates in place and
    # the price series carries on instead of starting over under a new row.
    conn.execute(
        "INSERT INTO product_variants"
        " (product_id, size_ml_x10, raw_title, product_url, first_seen, last_seen)"
        " VALUES (?, ?, ?, ?, ?, ?)"
        " ON CONFLICT (product_id, size_ml_x10) DO UPDATE SET"
        " raw_title = excluded.raw_title, product_url = excluded.product_url,"
        " last_seen = excluded.last_seen",
        (
            product_id,
            variant.size_ml_x10,
            variant.raw_title,
            variant.product_url,
            ts,
            ts,
        ),
    )
    return _scalar(
        conn,
        "SELECT variant_id FROM product_variants"
        " WHERE product_id = ? AND size_ml_x10 = ?",
        (product_id, variant.size_ml_x10),
    )


def _scalar(conn: sqlite3.Connection, sql: str, params: tuple[object, ...]) -> int:
    """Read back the id of a row that was just inserted or already existed.

    RETURNING would save the second statement, but only reports a row when the
    upsert actually touched one. Reading it back is the one form that answers
    the same way whether this scan created the row or the last one did.
    """
    row = conn.execute(sql, params).fetchone()
    if row is None:
        raise RuntimeError(f"row vanished right after being written: {sql}")
    return int(row[0])
