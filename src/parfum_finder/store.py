"""SQLite persistence: an append-only price history.

Tables: sites, perfumes, products, product_variants, price_snapshots, basket_items.
A latest_prices view surfaces the most recent snapshot per variant. The identity key
for a price series is (site_id, brand, name, concentration, size_ml), never the
product URL, so history survives a store renaming its slugs.

Timestamps go through a single now_iso() helper (UTC, "YYYY-MM-DDTHH:MM:SSZ").
Nothing in this codebase calls datetime.now().isoformat() directly, because mixing
timestamp formats would silently break "most recent" ordering.

TODO: table creation, the latest_prices view, snapshot writes, and syncing a
profile's identity/shipping fields into the sites table.
"""

from datetime import UTC, datetime


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
