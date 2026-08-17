"""The backend playwright drives: the real app, with the shops stubbed out.

Everything above the network is genuine -- the FastAPI routes, the scan
service, the matcher, ranking, the basket optimiser and a real sqlite file.
Only `SiteRunner` is replaced, because a browser test that went to the actual
shops would be slow, offline-hostile and would change its answer whenever a
price did.

The frontend is served by this process from `ui/dist`, which is also how the
packaged Windows app serves it: the token is injected into the page by
`create_app` rather than typed in anywhere, so the test drives the same surface
a user gets.

Started by playwright.config.ts, not by hand. The database is a fresh temp file
per run, so one run's basket cannot decide the next run's assertions.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import uvicorn

from parfum_finder.api.app import create_app
from parfum_finder.engine import ProductCandidate, SearchHit, SiteResult, Variant

PORT = int(os.environ.get("PARFUM_FINDER_E2E_PORT", "8765"))

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Two shops with deliberately different shipping, because that is what makes
# the basket's own arithmetic visible: A is cheaper per decant but charges more
# to post it, so which plan wins depends on the basket rather than on a
# constant.
_SITES: list[dict[str, Any]] = [
    {
        "id": "alfa",
        "name": "Alfa Dekant",
        "base_url": "https://alfa.example",
        "shipping": {
            "free_shipping_threshold_kurus": 50000,
            "shipping_cost_kurus": 4000,
        },
    },
    {
        "id": "beta",
        "name": "Beta Dekant",
        "base_url": "https://beta.example",
        "shipping": {
            "free_shipping_threshold_kurus": None,
            "shipping_cost_kurus": 1500,
        },
    },
]

# What each shop stocks, in the units the database uses: tenths of a millilitre
# and kuruş. A missing entry is a size that shop does not carry at all, which
# is a different fact from one that is out of stock and has to stay different
# all the way to the matrix.
_CATALOGUE: dict[str, dict[str, dict[int, int | None]]] = {
    "Dior Sauvage EDP": {
        "alfa": {30: 12000, 50: 18000},
        "beta": {30: 13500, 50: 17500, 100: 31000},
    },
    "Creed Aventus EDP": {
        "alfa": {30: 26000},
        "beta": {30: 24000, 50: None},
    },
}


def _profile(site: dict[str, Any]) -> dict[str, Any]:
    """A profile that passes schema validation and is never actually fetched."""
    return {
        "schema_version": 1,
        "id": site["id"],
        "name": site["name"],
        "base_url": site["base_url"],
        "enabled": True,
        "platform": None,
        "strategy": "httpx",
        "extraction": "jsonld",
        "search": {
            "url_template": "{base_url}/ara?q={query}",
            "result_item": ".card",
            "result_url": "a::attr(href)",
            "result_title": "a::text",
        },
        "variant_rules": {
            "size_from": "title",
            "size_pattern": r"(\d+) ?ml",
            "exclude_keywords": [],
            "max_size_ml": 30,
        },
        "shipping": site["shipping"],
        "discovered_at": "2026-08-01T00:00:00Z",
        "needs_review": [],
    }


def _matching_product(query: str) -> str | None:
    """Which catalogue product a typed query is about, by its leading words.

    Deliberately dumber than matcher.py: the point of the fixture is to answer
    a plausible listing for a plausible query, and letting it do its own clever
    matching would mean the test could pass on a match the real matcher would
    reject.
    """
    wanted = query.casefold().strip()
    for product in _CATALOGUE:
        head = product.casefold().split(" edp")[0]
        if wanted.startswith(head) or head.startswith(wanted):
            return product
    return None


async def _fake_runner(profile: dict[str, Any], query: str, **_: Any) -> SiteResult:
    site_id = str(profile["id"])
    product = _matching_product(query)
    if product is None:
        # The site answered fine and genuinely has nothing. Not an error, and
        # the results screen has to say so differently.
        return SiteResult(site_id, "empty", (), f"{site_id}: eşleşen ürün yok")

    sizes = _CATALOGUE[product].get(site_id, {})
    if not sizes:
        return SiteResult(site_id, "empty", (), f"{site_id}: bu ürün yok")

    slug = product.lower().replace(" ", "-")
    candidate = ProductCandidate(
        raw_title=f"{product} Dekant",
        url=f"{profile['base_url']}/urun/{slug}",
    )
    variants = tuple(
        Variant(
            size_ml_x10=size,
            raw_title=f"{product} Dekant {size // 10} ml",
            product_url=f"{profile['base_url']}/urun/{slug}",
            price_kurus=price,
            in_stock=price is not None,
        )
        for size, price in sorted(sizes.items())
    )
    return SiteResult(
        site_id, "ok", (SearchHit(candidate, variants),), f"{site_id}: ok"
    )


def main() -> None:
    workdir = Path(tempfile.mkdtemp(prefix="parfum-finder-e2e-"))
    sites_dir = workdir / "sites"
    sites_dir.mkdir()
    for site in _SITES:
        profile = _profile(site)
        (sites_dir / f"{profile['id']}.json").write_text(
            json.dumps(profile), encoding="utf-8"
        )

    app = create_app(
        sites_dir=sites_dir,
        db_path=workdir / "e2e.db",
        runner=_fake_runner,
        ui_dir=_REPO_ROOT / "ui" / "dist",
        # No release check: a test run must not depend on GitHub being up, and
        # an update modal over the first screen would block every other spec.
        update_checker=lambda: {
            "current_version": "0.0.0-e2e",
            "latest_version": "0.0.0-e2e",
            "update_available": False,
            "notes": "",
            "release_url": "https://example.com",
            "download_url": None,
        },
    )
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
