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

from parfum_finder import paths
from parfum_finder.engine import SiteResult, Variant
from parfum_finder.matcher import PerfumeQuery, match_title

DEFAULT_DB_PATH = paths.default_db_path()

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


# A price older than this is called out to whoever is reading it. It is not
# the profile staleness number: a profile that was described three months ago
# can still be reading the site correctly, while a two week old price is
# simply a price the shop has had plenty of time to change.
STALE_PRICE_DAYS = 14


def snapshot_age_days(fetched_at: str, now: datetime | None = None) -> int:
    """Whole days between a price snapshot and now.

    Only the one UTC format now_iso() writes is accepted. Being lenient would
    let a row carrying a local time report an age that is quietly a few hours
    wrong, and the whole point of this number is that somebody trusts it enough
    to skip a refresh.
    """
    stamp = datetime.strptime(fetched_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    return ((now or datetime.now(UTC)) - stamp).days


@dataclass(frozen=True)
class SnapshotRow:
    """One priced size of one perfume on one site, ready to be written.

    The perfume is named by its three identity parts rather than by an id,
    because that is the identity the price history is keyed on and the caller
    already holds it. `match_score` is the matcher's verdict on this site's
    wording, stored so a wrong match can be found again later instead of only
    being noticed once.

    `clone_of` is empty for a real hit. It is filled when the site is selling an
    imitation that names the searched perfume in parentheses, and it is what the
    screen marks such a row with. It says nothing about where the row is stored:
    a clone is filed under its own house and name, so it gets a price history of
    its own and never lends a cheap number to the perfume it imitates.

    `own_identity` is that guarantee, made checkable. It is False only for a
    clone whose own title was too short to name a house and a perfume, which
    leaves brand/name holding the searched perfume's identity rather than this
    bottle's. Those rows are shown and never written.
    """

    site_id: str
    brand: str
    name: str
    concentration: str
    match_score: int
    variant: Variant
    clone_of: str = ""
    own_identity: bool = True


def snapshot_rows(result: SiteResult, query: PerfumeQuery) -> list[SnapshotRow]:
    """Turn one site's hits into the rows write_snapshots is ready to store.

    Shared by the CLI and the TUI so the two can never diverge on which titles
    get stored as this perfume: both call this, neither hand-rolls the match.
    """
    rows: list[SnapshotRow] = []
    for hit in result.hits:
        if hit.candidate.raw_title is None:
            continue
        match = match_title(hit.candidate.raw_title, query)
        if match is None:
            # A rejection, not a weak score: the title names another brand or
            # another concentration. Storing it would put a different perfume's
            # price into this one's history.
            continue
        # A clone is a different bottle that happens to have been found by this
        # search, so it is filed under what its own title says it is. Using the
        # query here would put an imitation's price into the searched perfume's
        # history, and the concentration would be wrong too: match.concentration
        # is the one read off the parenthesis, which belongs to the original.
        #
        # A non-clone match that missed `confident` gets the same treatment.
        # "Layton" matching "Layton Exclusif" at a low score is the matcher
        # working as intended, not a mistake, but the two are different bottles
        # with different prices. Filing the low-score one under the searched
        # perfume's identity would give both one shared price history and one
        # shared basket line, so adding "Layton" to the basket would light up
        # "Layton Exclusif" rows too and hand its price to "Layton".
        identity = (
            match.clone_identity
            if match.clone_of
            else match.own_identity
            if not match.confident
            else None
        )
        rows.extend(
            SnapshotRow(
                site_id=result.site_id,
                brand=identity.brand if identity else query.brand,
                name=identity.name if identity else query.name,
                # What the title named, not what was asked for. An EDT and an
                # EDP are two products with two prices, and a query that named
                # neither would otherwise merge them into one perfume row.
                concentration=(
                    identity.concentration if identity else match.concentration
                ),
                match_score=match.score,
                variant=variant,
                clone_of=match.clone_of,
                own_identity=not match.clone_of or identity is not None,
            )
            for variant in hit.variants
            if variant.raw_title is not None
        )
    return rows


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

    A row that has no identity of its own is dropped here rather than at the
    caller. Every writer goes through this function, so this is the one place
    that can guarantee a bottle never lands in another perfume's price history.
    In practice that is the clone whose own title was too short to read a house
    and a perfume off; every other clone is stored, as itself.

    One transaction for the batch. A run that dies halfway through leaves the
    database as it was rather than a site with three of its eight sizes updated.
    """
    stamp = fetched_at or now_iso()
    written = 0
    with conn:
        for row in rows:
            if not row.own_identity:
                continue
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


def add_basket_item(
    conn: sqlite3.Connection,
    *,
    brand: str,
    name: str,
    concentration: str,
    size_ml_x10: int,
    qty: int = 1,
    added_at: str | None = None,
) -> int:
    """Add a size of a perfume to the basket, and return the basket_item_id.

    The perfume must already exist: it is named by brand/name/concentration
    because that is all the TUI ever holds, but a basket line for a perfume
    nobody has priced is a bug, not a state worth inventing a row for.

    Adding the same perfume and size again bumps qty instead of failing or
    overwriting, and keeps the original added_at so the basket screen's
    ordering by it does not move just because someone added one more bottle.
    """
    with conn:
        row = conn.execute(
            "SELECT perfume_id FROM perfumes"
            " WHERE brand = ? AND name = ? AND concentration = ?",
            (brand, name, concentration),
        ).fetchone()
        if row is None:
            raise ValueError(
                f"no perfume on record for {brand} {name} {concentration};"
                " it has to be scanned before it can be put in the basket"
            )
        perfume_id = int(row[0])
        ts = added_at or now_iso()
        conn.execute(
            "INSERT INTO basket_items (perfume_id, size_ml_x10, qty, added_at)"
            " VALUES (?, ?, ?, ?)"
            " ON CONFLICT (perfume_id, size_ml_x10) DO UPDATE SET"
            " qty = qty + excluded.qty",
            (perfume_id, size_ml_x10, qty, ts),
        )
        return _scalar(
            conn,
            "SELECT basket_item_id FROM basket_items"
            " WHERE perfume_id = ? AND size_ml_x10 = ?",
            (perfume_id, size_ml_x10),
        )


def price_history(
    conn: sqlite3.Connection,
    *,
    site_id: str,
    brand: str,
    name: str,
    concentration: str,
    size_ml_x10: int,
    limit: int = 20,
) -> list[sqlite3.Row]:
    """Return one variant's past readings, newest first, capped at limit.

    Empty for a perfume/site/size nobody has scanned yet: a variant with no
    history is a normal state, not an error to raise on.
    """
    return conn.execute(
        "SELECT s.fetched_at, s.price_kurus, s.in_stock"
        " FROM price_snapshots s"
        " JOIN product_variants v USING (variant_id)"
        " JOIN products         p USING (product_id)"
        " JOIN perfumes         pf ON pf.perfume_id = p.perfume_id"
        " WHERE p.site_id = ? AND pf.brand = ? AND pf.name = ?"
        " AND pf.concentration = ? AND v.size_ml_x10 = ?"
        " ORDER BY s.fetched_at DESC, s.snapshot_id DESC"
        " LIMIT ?",
        (site_id, brand, name, concentration, size_ml_x10, limit),
    ).fetchall()


@dataclass(frozen=True)
class CachedPrice:
    """One stored price for one size of one perfume on one site.

    What the results table is repainted from when a perfume that has been
    searched before is searched again. It carries the same facts a live scan
    produces, plus the reading's own timestamp, since a price served from
    storage has to be able to say how old it is.

    Only priced sizes come back. A size whose price never read has no row in
    price_snapshots at all, so it simply is not in the cache, and inventing a
    priceless row here would put a "-" on screen that no reading produced.
    """

    site_id: str
    brand: str
    name: str
    concentration: str
    match_score: int
    size_ml_x10: int
    raw_title: str
    product_url: str | None
    price_kurus: int
    in_stock: bool
    fetched_at: str


def cached_prices(
    conn: sqlite3.Connection,
    *,
    brand: str,
    name: str,
    concentration: str = "",
) -> list[CachedPrice]:
    """Return the latest stored price of every size of this perfume, per site.

    Brand and name are matched exactly, because they are written by parse_query
    and read back with the same parse_query output: they are a database key, not
    something anyone types twice by hand. Concentration is the one part a search
    may leave out, and an empty string here means "any", the same thing it means
    on PerfumeQuery. Matching it exactly when it is given matters, since an EDT
    and an EDP are two products with two prices.

    Disabled sites are left out. A price nobody is going to scan again is a
    number that can only get older, and offering it as a result would invite a
    refresh that will never touch it.

    Empty for a perfume nobody has scanned yet, which is the normal state before
    the first search rather than an error.
    """
    sql = (
        "SELECT lp.site_id, pf.brand, pf.name, pf.concentration, lp.match_score,"
        " lp.size_ml_x10, lp.raw_title, lp.product_url, lp.price_kurus,"
        " lp.in_stock, lp.fetched_at"
        " FROM latest_prices lp"
        " JOIN perfumes pf ON pf.perfume_id = lp.perfume_id"
        " JOIN sites    s  ON s.site_id     = lp.site_id"
        " WHERE s.enabled = 1 AND pf.brand = ? AND pf.name = ?"
    )
    params: list[object] = [brand, name]
    if concentration:
        sql += " AND pf.concentration = ?"
        params.append(concentration)
    rows = conn.execute(sql, tuple(params)).fetchall()
    return [
        CachedPrice(
            site_id=row["site_id"],
            brand=row["brand"],
            name=row["name"],
            concentration=row["concentration"],
            match_score=row["match_score"],
            size_ml_x10=row["size_ml_x10"],
            raw_title=row["raw_title"],
            product_url=row["product_url"],
            price_kurus=row["price_kurus"],
            in_stock=bool(row["in_stock"]),
            fetched_at=row["fetched_at"],
        )
        for row in rows
    ]


@dataclass(frozen=True)
class BasketLine:
    """One row of the basket: a size of a perfume, with the identity spelled out.

    The basket screen wants brand/name/concentration to print next to each
    line, and joining perfumes back in here means it never has to make a
    second trip just to say what basket_item_id 7 actually is.
    """

    basket_item_id: int
    perfume_id: int
    brand: str
    name: str
    concentration: str
    size_ml_x10: int
    qty: int
    added_at: str


@dataclass(frozen=True)
class BasketPrice:
    """One site's latest price for one basket line, only when it has one.

    Rows with no price on any site are left out here entirely; basket_lines
    is what still lists them, so a caller comparing the two can tell "nobody
    sells it" apart from a basket line that simply has zero site rows.
    """

    basket_item_id: int
    site_id: str
    price_kurus: int
    in_stock: bool
    fetched_at: str


@dataclass(frozen=True)
class BasketSite:
    """A site the basket screen is willing to show a column for.

    Deliberately just sites, not sites that happen to appear in a price
    join: a site that prices nothing in this basket is exactly the state the
    basket screen exists to show as a column of dashes, and it would vanish
    if the column list came from the join result instead.
    """

    site_id: str
    name: str
    free_shipping_threshold_kurus: int | None
    shipping_cost_kurus: int
    notes: str | None


def basket_lines(conn: sqlite3.Connection) -> list[BasketLine]:
    """Return every basket line, oldest add first.

    Ordered by added_at with basket_item_id as a tiebreaker, because two
    lines added within the same second (the timestamp's own resolution)
    would otherwise be free to swap places between two reads and make the
    basket screen look like it reordered itself for no reason.
    """
    rows = conn.execute(
        "SELECT b.basket_item_id, b.perfume_id, pf.brand, pf.name,"
        " pf.concentration, b.size_ml_x10, b.qty, b.added_at"
        " FROM basket_items b"
        " JOIN perfumes pf ON pf.perfume_id = b.perfume_id"
        " ORDER BY b.added_at, b.basket_item_id"
    ).fetchall()
    return [
        BasketLine(
            basket_item_id=row["basket_item_id"],
            perfume_id=row["perfume_id"],
            brand=row["brand"],
            name=row["name"],
            concentration=row["concentration"],
            size_ml_x10=row["size_ml_x10"],
            qty=row["qty"],
            added_at=row["added_at"],
        )
        for row in rows
    ]


def basket_prices(conn: sqlite3.Connection) -> list[BasketPrice]:
    """Return the basket price matrix: one row per (line, site) that has a price.

    This is the query the schema doc pins down for the basket matrix, LEFT
    JOIN and all. The LEFT JOIN matters even though it means filtering NULLs
    out in Python afterward: an INNER JOIN would make a basket line no site
    prices simply not show up in the site's own results, which reads exactly
    like "this site does not carry it" and there is no way back from that to
    "nobody carries it" without re-running the query. Keeping the LEFT JOIN
    and dropping the NULL rows here means a caller who wants that distinction
    can still get it, by comparing this list against basket_lines.

    in_stock comes back exactly as the database has it. Turning an
    out-of-stock row into a missing one is the caller's call to make, not
    this function's, because a screen showing "out of stock" and a screen
    treating it as unavailable for pricing purposes are two different
    readers of the same fact.
    """
    rows = conn.execute(
        "SELECT b.basket_item_id, lp.site_id, lp.price_kurus, lp.in_stock,"
        " lp.fetched_at"
        " FROM basket_items b"
        " LEFT JOIN latest_prices lp"
        "        ON lp.perfume_id  = b.perfume_id"
        "       AND lp.size_ml_x10 = b.size_ml_x10"
        " ORDER BY b.added_at"
    ).fetchall()
    return [
        BasketPrice(
            basket_item_id=row["basket_item_id"],
            site_id=row["site_id"],
            price_kurus=row["price_kurus"],
            in_stock=bool(row["in_stock"]),
            fetched_at=row["fetched_at"],
        )
        for row in rows
        if row["site_id"] is not None
    ]


def basket_sites(conn: sqlite3.Connection) -> list[BasketSite]:
    """Return every enabled site, for the basket screen's fixed set of columns.

    Sourced from sites rather than from whatever basket_prices happens to
    return, on purpose: a site that prices none of the basket's lines still
    has to show up as a column full of dashes, and a site list built from
    the price join would quietly drop exactly that site.
    """
    rows = conn.execute(
        "SELECT site_id, name, free_shipping_threshold_kurus,"
        " shipping_cost_kurus, notes"
        " FROM sites WHERE enabled = 1 ORDER BY site_id"
    ).fetchall()
    return [
        BasketSite(
            site_id=row["site_id"],
            name=row["name"],
            free_shipping_threshold_kurus=row["free_shipping_threshold_kurus"],
            shipping_cost_kurus=row["shipping_cost_kurus"],
            notes=row["notes"],
        )
        for row in rows
    ]


def remove_basket_item(conn: sqlite3.Connection, *, basket_item_id: int) -> bool:
    """Delete one basket line, and say whether there was one to delete.

    Returns False rather than raising when the id is already gone: two
    windows on the same basket both deleting the row a user just removed is
    a race, not a bug, and the second call should just report it didn't do
    anything.
    """
    with conn:
        cursor = conn.execute(
            "DELETE FROM basket_items WHERE basket_item_id = ?", (basket_item_id,)
        )
        return cursor.rowcount > 0


def set_basket_qty(conn: sqlite3.Connection, *, basket_item_id: int, qty: int) -> int:
    """Set a basket line's quantity, clamped to at least 1, and return it.

    The table's CHECK (qty > 0) would reject a qty of 0 outright, and the
    basket screen's '-' key needs to be able to sit at quantity 1 without the
    press below it turning into an error. Removing the line has its own key,
    so pressing '-' one more time at 1 is a no-op rather than a delete.

    Raises ValueError for an id that isn't there: unlike removal, an update
    aimed at a row that doesn't exist means the caller is out of sync with
    the basket, which is worth failing loud on rather than swallowing.
    """
    clamped = max(qty, 1)
    with conn:
        cursor = conn.execute(
            "UPDATE basket_items SET qty = ? WHERE basket_item_id = ?",
            (clamped, basket_item_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"no basket item with id {basket_item_id}")
    return clamped


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
