"""Tests for schema/site.schema.json and schema/platform.schema.json.

These check the schema definitions themselves, independent of profiles.py's
loader (which does not exist yet). A schema that is too loose would let a
broken profile through to load without any error; a schema that is too
strict would reject a legitimate profile. Both failure modes defeat the
point of validating on load.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).parent.parent / "schema"

# A minimal valid site profile: shopify platform, httpx strategy, jsonld extraction.
VALID_SITE_PROFILE: dict[str, Any] = {
    "schema_version": 1,
    "id": "ornek",
    "name": "Örnek Dekant",
    "base_url": "https://ornek-site.com",
    "enabled": True,
    "platform": "shopify",
    "strategy": "httpx",
    "extraction": "jsonld",
    "rate_limit_ms": 800,
    "timeout_s": 20,
    "search": {
        "url_template": "{base_url}/search?q={query}",
        "result_item": ".product-card",
        "result_url": "a::attr(href)",
        "result_title": ".product-title::text",
    },
    "product": {
        "title": None,
        "price": None,
        "in_stock": None,
        "variant_container": ".variant-select",
    },
    "variant_rules": {
        "size_from": "title",
        "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
        "exclude_keywords": ["tester", "full şişe", "orijinal şişe", "kutulu", "set"],
        "max_size_ml": 30,
    },
    "shipping": {
        "free_shipping_threshold_kurus": 75000,
        "shipping_cost_kurus": 8900,
        "notes": "Havale ile %3 indirim",
    },
    "discovered_at": "2026-08-07T11:22:00Z",
    "needs_review": ["variant_rules.size_pattern"],
}

# A minimal valid platform template: shopify fingerprint plus endpoint-based defaults.
VALID_PLATFORM_TEMPLATE: dict[str, Any] = {
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


def _load_schema(filename: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / filename).read_text())


def _site_validator() -> jsonschema.Draft202012Validator:
    schema = _load_schema("site.schema.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def _platform_validator() -> jsonschema.Draft202012Validator:
    schema = _load_schema("platform.schema.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def test_site_schema_accepts_the_documented_example() -> None:
    _site_validator().validate(VALID_SITE_PROFILE)


def test_platform_schema_accepts_the_documented_example() -> None:
    _platform_validator().validate(VALID_PLATFORM_TEMPLATE)


@pytest.mark.parametrize(
    "missing_field", ["shipping", "variant_rules", "discovered_at"]
)
def test_site_schema_rejects_a_missing_required_field(missing_field: str) -> None:
    broken = {k: v for k, v in VALID_SITE_PROFILE.items() if k != missing_field}
    with pytest.raises(jsonschema.ValidationError):
        _site_validator().validate(broken)


def test_site_schema_rejects_css_extraction_without_a_product_block() -> None:
    # extraction=css reads the product page with selectors too, so a profile on
    # that layer without a product block would silently produce zero prices.
    broken = {**VALID_SITE_PROFILE, "extraction": "css"}
    broken.pop("product")
    with pytest.raises(jsonschema.ValidationError):
        _site_validator().validate(broken)


def test_site_schema_rejects_endpoint_extraction_without_endpoint_block() -> None:
    broken = {**VALID_SITE_PROFILE, "extraction": "endpoint"}
    with pytest.raises(jsonschema.ValidationError):
        _site_validator().validate(broken)


def test_site_schema_rejects_trailing_slash_on_base_url() -> None:
    # A trailing slash would double up when the engine builds
    # "{base_url}/search?q=..." from the search.url_template.
    broken = {**VALID_SITE_PROFILE, "base_url": "https://ornek-site.com/"}
    with pytest.raises(jsonschema.ValidationError):
        _site_validator().validate(broken)


def test_site_schema_accepts_a_search_page_with_its_own_strategy() -> None:
    # One site builds its search results in the browser while its product pages
    # arrive complete over plain HTTP. The engine reads search.strategy for that,
    # and the search block rejects unknown keys, so the schema and the engine have
    # to agree on this name or the first real profile using it fails to load.
    profile = {**VALID_SITE_PROFILE}
    profile["search"] = {**profile["search"], "strategy": "playwright"}

    _site_validator().validate(profile)


def test_site_schema_rejects_an_unknown_search_strategy() -> None:
    profile = {**VALID_SITE_PROFILE}
    profile["search"] = {**profile["search"], "strategy": "selenium"}
    with pytest.raises(jsonschema.ValidationError):
        _site_validator().validate(profile)


def test_site_schema_rejects_wrong_timestamp_format() -> None:
    # A "+03:00" offset instead of "Z" would silently break the
    # lexicographic "most recent" ordering the database relies on.
    broken = {**VALID_SITE_PROFILE, "discovered_at": "2026-08-07T11:22:00+03:00"}
    with pytest.raises(jsonschema.ValidationError):
        _site_validator().validate(broken)
