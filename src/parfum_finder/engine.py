"""Async orchestration: parallel across sites, serial within a site, fault-isolated.

Built on asyncio.TaskGroup. Each site gets its own semaphore, a delay between
requests, and retries with backoff. If one site fails, the others keep going.

Results are never silently empty. If a site looks broken, for example zero results
on a page that clearly has products, a price that won't parse, or a variant selector
that only yielded one price, it gets marked "suspect" instead of "no matches."
Suspect results are excluded from basket totals as unknown, not treated as simply
expensive.

TODO: define a SiteResult type here (site_id, status, variants, error/diagnostic).
Blocked on deciding the concrete shape of the Variant type it would hold a list of.
That type isn't defined anywhere in the codebase yet.
"""
