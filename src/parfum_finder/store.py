"""SQLite persistence: an append-only price history.

Tables: sites, perfumes, products, product_variants, price_snapshots, basket_items.
A latest_prices view surfaces the most recent snapshot per variant. The identity key
for a price series is (site_id, brand, name, concentration, size_ml), never the
product URL, so history survives a store renaming its slugs.

Timestamps go through a single now_iso() helper (UTC, "YYYY-MM-DDTHH:MM:SSZ").
Nothing in this codebase calls datetime.now().isoformat() directly, because mixing
timestamp formats would silently break "most recent" ordering.

TODO: table creation, the latest_prices view, snapshot writes, and syncing a
profile's identity/shipping fields into the sites table. Also decide where
now_iso() itself should live (here, or in normalize.py).
"""
