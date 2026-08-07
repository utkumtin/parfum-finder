"""Tests for parfum_finder.profiles: loading, schema validation, platform merge.

The load path validates the *effective* (post-merge) profile, so a broken merge
or a broken raw file both need to surface as a loud error, never a silently
half-populated profile a scraper would later choke on.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from parfum_finder.profiles import deep_merge, load_platform_template, load_site_profile

SHOPIFY_TEMPLATE: dict[str, Any] = {
    "schema_version": 1,
    "name": "shopify",
    "fingerprint": {"any": ["cdn.shopify.com", "Shopify.theme", "/cart/add"]},
    "defaults": {
        "extraction": "endpoint",
        "search": {"url_template": "{base_url}/search?q={query}"},
        "endpoint": {
            "product_json": "{product_url}.js",
            "variants_path": "variants",
            "field_map": {
                "size_raw": "title",
                "price": "price",
                "in_stock": "available",
            },
        },
    },
}

# What a real user would have to type for a second site on a known platform:
# identity and shipping (never scraped), nothing the platform already covers.
MINIMAL_SITE_ON_SHOPIFY: dict[str, Any] = {
    "schema_version": 1,
    "id": "ikinci-site",
    "name": "İkinci Site",
    "base_url": "https://ikinci-site.com",
    "platform": "shopify",
    "strategy": "httpx",
    "variant_rules": {
        "size_from": "title",
        "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
        "exclude_keywords": ["tester", "full şişe"],
        "max_size_ml": 30,
    },
    "shipping": {
        "free_shipping_threshold_kurus": 75000,
        "shipping_cost_kurus": 8900,
    },
    "discovered_at": "2026-08-07T11:22:00Z",
    "needs_review": [],
}

STANDALONE_SITE: dict[str, Any] = {
    "schema_version": 1,
    "id": "bagimsiz",
    "name": "Bağımsız Site",
    "base_url": "https://bagimsiz-site.com",
    "platform": None,
    "strategy": "httpx",
    "extraction": "jsonld",
    "search": {"url_template": "{base_url}/search?q={query}"},
    "variant_rules": {
        "size_from": "title",
        "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
        "exclude_keywords": ["tester"],
        "max_size_ml": 30,
    },
    "shipping": {
        "free_shipping_threshold_kurus": None,
        "shipping_cost_kurus": 5000,
    },
    "discovered_at": "2026-08-07T11:22:00Z",
    "needs_review": [],
}


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    path.write_text(json.dumps(data))
    return path


def test_deep_merge_fills_gaps_from_base() -> None:
    merged = deep_merge({"a": 1, "b": {"x": 1, "y": 2}}, {"b": {"y": 3}})
    assert merged == {"a": 1, "b": {"x": 1, "y": 3}}


def test_deep_merge_override_wins_on_conflict() -> None:
    merged = deep_merge({"extraction": "endpoint"}, {"extraction": "jsonld"})
    assert merged["extraction"] == "jsonld"


def test_deep_merge_replaces_arrays_wholesale_instead_of_combining() -> None:
    merged = deep_merge({"tags": ["a", "b"]}, {"tags": ["c"]})
    assert merged["tags"] == ["c"]


def test_deep_merge_does_not_mutate_its_inputs() -> None:
    base = {"b": {"x": 1}}
    deep_merge(base, {"b": {"x": 2}})
    assert base == {"b": {"x": 1}}


def test_load_platform_template_loads_and_validates(tmp_path: Path) -> None:
    _write_json(tmp_path / "shopify.json", SHOPIFY_TEMPLATE)
    template = load_platform_template("shopify", tmp_path)
    assert template["defaults"]["extraction"] == "endpoint"


def test_load_platform_template_rejects_a_broken_template(tmp_path: Path) -> None:
    broken = {**SHOPIFY_TEMPLATE, "fingerprint": {"any": []}}  # minItems: 1 violated
    _write_json(tmp_path / "broken.json", broken)
    with pytest.raises(ValueError, match="invalid profile"):
        load_platform_template("broken", tmp_path)


def test_load_site_profile_with_no_platform_validates_the_raw_file(
    tmp_path: Path,
) -> None:
    site_path = _write_json(tmp_path / "bagimsiz.json", STANDALONE_SITE)
    effective = load_site_profile(site_path, platforms_dir=tmp_path)
    assert effective["extraction"] == "jsonld"


def test_load_site_profile_fills_missing_fields_from_platform_defaults(
    tmp_path: Path,
) -> None:
    _write_json(tmp_path / "shopify.json", SHOPIFY_TEMPLATE)
    site_path = _write_json(tmp_path / "ikinci-site.json", MINIMAL_SITE_ON_SHOPIFY)

    effective = load_site_profile(site_path, platforms_dir=tmp_path)

    # None of these were in the site's own file; they only exist because the
    # platform template supplied them.
    assert effective["extraction"] == "endpoint"
    assert effective["endpoint"]["product_json"] == "{product_url}.js"


def test_load_site_profile_lets_site_override_platform_defaults(tmp_path: Path) -> None:
    _write_json(tmp_path / "shopify.json", SHOPIFY_TEMPLATE)
    overriding_site = {**MINIMAL_SITE_ON_SHOPIFY, "extraction": "jsonld"}
    site_path = _write_json(tmp_path / "ikinci-site.json", overriding_site)

    effective = load_site_profile(site_path, platforms_dir=tmp_path)

    assert effective["extraction"] == "jsonld"


def test_load_site_profile_rejects_a_profile_broken_after_merge(tmp_path: Path) -> None:
    # extraction=endpoint with no endpoint block anywhere (platform doesn't
    # provide one either) must fail loud, not load as a silently empty scraper.
    bare_platform = {
        "schema_version": 1,
        "name": "bare",
        "fingerprint": {"any": ["bare-marker"]},
        "defaults": {"extraction": "endpoint"},
    }
    _write_json(tmp_path / "bare.json", bare_platform)
    broken_site = {**MINIMAL_SITE_ON_SHOPIFY, "platform": "bare"}
    site_path = _write_json(tmp_path / "broken.json", broken_site)

    with pytest.raises(ValueError, match="invalid profile"):
        load_site_profile(site_path, platforms_dir=tmp_path)


def test_load_site_profile_rejects_malformed_json(tmp_path: Path) -> None:
    site_path = tmp_path / "malformed.json"
    site_path.write_text("{not valid json")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_site_profile(site_path, platforms_dir=tmp_path)
