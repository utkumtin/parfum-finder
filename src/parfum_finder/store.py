"""SQLite persistence: an append-only price history.

Tables: sites, perfumes, products, product_variants, price_snapshots, basket_items.
A latest_prices view surfaces the most recent snapshot per variant. The identity key
for a price series is (site_id, brand, name, concentration, size_ml), never the
product URL, so history survives a store renaming its slugs.

Timestamps go through a single now_iso() helper (UTC, "YYYY-MM-DDTHH:MM:SSZ").
Nothing in this codebase calls datetime.now().isoformat() directly, because mixing
timestamp formats would silently break "most recent" ordering.

TODO: snapshot writes, and syncing a profile's identity/shipping fields into
the sites table.
"""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

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
