"""Tests for the real platform templates shipped in platforms/.

tests/test_profiles.py covers the loading and merging *logic* against synthetic
templates written into tmp_path. This file covers the *data*: the three templates
that actually live in the repo. Without it, a template could be malformed, or
carry a key the site schema rejects, and nothing would notice, because sites/
holds no profile yet that would load one.

The trap this guards against: site.schema.json is additionalProperties:false at
the top level and load_site_profile validates the merged result. So a key that a
template invents, however harmless it looks in the template file, breaks every
site profile based on that platform.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from parfum_finder.profiles import (
    DEFAULT_PLATFORMS_DIR,
    load_platform_template,
    load_site_profile,
)

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

# Captured pages of the sites each template was written from. A template whose
# markers no longer appear in the HTML it was derived from is a template that
# will silently stop recognizing its platform.
FIXTURE_IDS: dict[str, list[str]] = {
    "ideasoft": ["dekantparfum", "dekantdoktoru", "splitcim"],
    "woocommerce": ["luxurydekant", "ruxangroup"],
    "ikas": ["decantall"],
}

PLATFORM_NAMES = list(FIXTURE_IDS)

# Which selectors pick result rows out of a listing is a theme detail, not a
# platform one: two shops on the same platform run different themes. So no
# template supplies these and every site profile writes its own.
SEARCH_SELECTORS: dict[str, Any] = {
    "result_item": ".product-card",
    "result_url": "a::attr(href)",
    "result_title": ".product-title::text",
}

# Identity and shipping are never scraped, so they stay the site owner's job no
# matter which platform a profile is based on.
SITE_IDENTITY: dict[str, Any] = {
    "schema_version": 1,
    "id": "ornek",
    "name": "Örnek Site",
    "base_url": "https://ornek-site.com",
    "strategy": "httpx",
    "variant_rules": {
        "size_from": "variant_label",
        "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
        "exclude_keywords": ["tester"],
        "max_size_ml": 30,
    },
    "shipping": {
        "free_shipping_threshold_kurus": 50000,
        "shipping_cost_kurus": 6900,
    },
    "discovered_at": "2026-08-07T12:00:00Z",
    "needs_review": [],
}

# Everything a site on this platform still has to write by hand, on top of
# SITE_IDENTITY. The point of a template is that these dicts stay small.
REMAINING_SITE_FIELDS: dict[str, dict[str, Any]] = {
    "ideasoft": {"search": SEARCH_SELECTORS},
    "woocommerce": {"search": SEARCH_SELECTORS},
    # ikas is a one-site platform so far, and that one site builds its search
    # results in the browser. There is no second site to prove a shared search
    # URL shape, so the template does not guess one.
    "ikas": {
        "search": {"url_template": "{base_url}/search?s={query}", **SEARCH_SELECTORS}
    },
}


def _write_site(tmp_path: Path, platform: str) -> Path:
    site = {
        **SITE_IDENTITY,
        "platform": platform,
        **REMAINING_SITE_FIELDS[platform],
    }
    path = tmp_path / f"{platform}-site.json"
    path.write_text(json.dumps(site))
    return path


@pytest.mark.parametrize("name", PLATFORM_NAMES)
def test_template_file_is_valid(name: str) -> None:
    template = load_platform_template(name)
    assert template["name"] == name


@pytest.mark.parametrize("name", PLATFORM_NAMES)
def test_template_merges_into_a_valid_site_profile(name: str, tmp_path: Path) -> None:
    site_path = _write_site(tmp_path, name)
    effective = load_site_profile(site_path)
    assert effective["platform"] == name


@pytest.mark.parametrize("name", PLATFORM_NAMES)
def test_template_markers_still_match_the_captured_pages(name: str) -> None:
    markers = load_platform_template(name)["fingerprint"]["any"]
    for fixture_id in FIXTURE_IDS[name]:
        for page in ("search.html", "product.html"):
            html = (_FIXTURES_DIR / fixture_id / page).read_text().lower()
            matched = [m for m in markers if m.lower() in html]
            assert matched, f"no {name} marker in {fixture_id}/{page}"


def test_woocommerce_template_carries_search_and_extraction() -> None:
    # Both WooCommerce sites share the same search URL shape and read their
    # variant prices out of the same embedded JSON blob, so a second WooCommerce
    # site should need neither of these two fields in its own profile.
    defaults = load_platform_template("woocommerce")["defaults"]
    assert (
        defaults["search"]["url_template"] == "{base_url}/?s={query}&post_type=product"
    )
    assert defaults["extraction"] == "embedded_json"


def test_ideasoft_template_carries_the_post_variant_endpoint() -> None:
    # Both ideasoft sites share the same theme JS, so the endpoint's URL, its
    # request shape and its field map are all platform facts, not per-site
    # ones. A second ideasoft site should need neither of these in its own
    # profile, only the search URL is theme-specific and stays here too.
    defaults = load_platform_template("ideasoft")["defaults"]
    assert defaults["extraction"] == "endpoint"
    assert defaults["search"]["url_template"] == "{base_url}/arama/{query}"
    endpoint = defaults["endpoint"]
    assert endpoint["method"] == "POST"
    assert endpoint["option_body_key"] == "selected_options[]"
    assert endpoint["field_map"]["price"] == "product_price.sale_price"


def test_every_shipped_template_is_backed_by_a_captured_site() -> None:
    # Only platforms seen on a real target site get a template. A template for a
    # platform nobody uses is an untested guess that reads as a verified fact.
    # New templates are welcome, but each one has to bring the pages it was read
    # from, so the marker test above can hold it to them.
    shipped = {p.stem for p in DEFAULT_PLATFORMS_DIR.glob("*.json")}
    assert shipped <= set(FIXTURE_IDS)
