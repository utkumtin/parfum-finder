"""Tests for parfum_finder.profiles: loading, schema validation, platform merge.

The load path validates the *effective* (post-merge) profile, so a broken merge
or a broken raw file both need to surface as a loud error, never a silently
half-populated profile a scraper would later choke on.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from parfum_finder.profiles import (
    deep_merge,
    load_platform_template,
    load_platform_templates,
    load_site_hooks,
    load_site_profile,
    sync_to_db,
)
from parfum_finder.store import connect

SHOPIFY_TEMPLATE: dict[str, Any] = {
    "schema_version": 1,
    "name": "shopify",
    "fingerprint": {"any": ["cdn.shopify.com", "Shopify.theme", "/cart/add"]},
    "defaults": {
        "extraction": "endpoint",
        "search": {
            "url_template": "{base_url}/search?q={query}",
            "result_item": ".product-card",
            "result_url": "a::attr(href)",
            "result_title": ".product-title::text",
        },
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
    "search": {
        "url_template": "{base_url}/search?q={query}",
        "result_item": ".product-card",
        "result_url": "a::attr(href)",
        "result_title": ".product-title::text",
    },
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


def test_load_platform_templates_keys_them_by_file_name(tmp_path: Path) -> None:
    _write_json(tmp_path / "shopify.json", SHOPIFY_TEMPLATE)
    _write_json(
        tmp_path / "bare.json",
        {
            "schema_version": 1,
            "name": "bare",
            "fingerprint": {"any": ["bare-marker"]},
            "defaults": {},
        },
    )

    templates = load_platform_templates(tmp_path)

    # The file name is what a site profile's "platform" field refers to, so it
    # has to be the key a caller looks a template up by.
    assert sorted(templates) == ["bare", "shopify"]


def test_load_platform_templates_rejects_a_name_that_disagrees_with_its_file(
    tmp_path: Path,
) -> None:
    # A template calling itself something its file is not can never be reached:
    # "platform": "ticimax" in a site profile looks for ticimax.json.
    _write_json(tmp_path / "ticimax.json", SHOPIFY_TEMPLATE)

    with pytest.raises(ValueError, match="but its file is"):
        load_platform_templates(tmp_path)


def test_load_platform_templates_stops_on_one_broken_file(tmp_path: Path) -> None:
    # Skipping the broken one would hand the caller a library it believes is
    # complete, and a platform that dropped out of it is indistinguishable from
    # a platform that was never in it.
    _write_json(tmp_path / "shopify.json", SHOPIFY_TEMPLATE)
    (tmp_path / "broken.json").write_text("{not valid json")

    with pytest.raises(ValueError, match="invalid JSON"):
        load_platform_templates(tmp_path)


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


def _write_hook(hooks_dir: Path, site_id: str, source: str) -> Path:
    path = hooks_dir / f"{site_id}.py"
    path.write_text(source)
    return path


def test_load_site_hooks_returns_nothing_when_the_site_has_no_hook_file(
    tmp_path: Path,
) -> None:
    # The normal case by far. A site with no hook file is not an error and must
    # not need the caller to ask whether the file exists first.
    hooks = load_site_hooks("hooksuz-site", hooks_dir=tmp_path)

    assert (hooks.before_search, hooks.after_search, hooks.parse_variants) == (
        None,
        None,
        None,
    )


def test_load_site_hooks_loads_the_three_hooks_a_file_defines(tmp_path: Path) -> None:
    _write_hook(
        tmp_path,
        "kancali-site",
        "def before_search(profile, query):\n"
        "    return query.upper()\n"
        "\n"
        "\n"
        "def after_search(profile, candidates, html):\n"
        "    return candidates[:1]\n"
        "\n"
        "\n"
        "async def parse_variants(profile, candidate, html):\n"
        "    return ()\n",
    )

    hooks = load_site_hooks("kancali-site", hooks_dir=tmp_path)

    assert hooks.before_search is not None
    assert hooks.before_search({}, "aventus") == "AVENTUS"
    assert hooks.after_search is not None
    assert hooks.after_search({}, ["a", "b"], "") == ["a"]
    assert hooks.parse_variants is not None


def test_load_site_hooks_takes_only_the_hooks_that_are_there(tmp_path: Path) -> None:
    # A hook file exists to override one step, not all three. Defining just one
    # must leave the other two alone rather than being rejected as incomplete.
    _write_hook(
        tmp_path, "tek-kanca", "def before_search(profile, query):\n    return query\n"
    )

    hooks = load_site_hooks("tek-kanca", hooks_dir=tmp_path)

    assert hooks.before_search is not None
    assert hooks.after_search is None
    assert hooks.parse_variants is None


def test_load_site_hooks_rejects_a_public_name_that_is_not_a_hook(
    tmp_path: Path,
) -> None:
    # The failure this exists for: a misspelled hook loads fine, defines nothing
    # the engine looks for, and the site quietly runs the generic flow while
    # looking like it runs the overridden one.
    _write_hook(
        tmp_path,
        "yanlis-isim",
        "def parse_variant(profile, candidate, html):\n    return ()\n",
    )

    with pytest.raises(ValueError, match="parse_variant"):
        load_site_hooks("yanlis-isim", hooks_dir=tmp_path)


def test_load_site_hooks_allows_underscore_helpers_and_imports(tmp_path: Path) -> None:
    # A hook doing real work needs helpers and imports. Only public names it
    # defines itself are suspicious, so neither of these may trip the guard.
    _write_hook(
        tmp_path,
        "yardimcili",
        "from decimal import Decimal\n"
        "\n"
        "\n"
        "def _to_price(text):\n"
        "    return Decimal(text)\n"
        "\n"
        "\n"
        "def before_search(profile, query):\n"
        "    return query\n",
    )

    hooks = load_site_hooks("yardimcili", hooks_dir=tmp_path)

    assert hooks.before_search is not None


def test_load_site_hooks_raises_when_the_file_is_broken(tmp_path: Path) -> None:
    # A file that exists but will not execute is the one case where staying quiet
    # is worst: the site asked for an override and would silently not get one.
    _write_hook(
        tmp_path, "bozuk", "def before_search(profile, query)\n    return query\n"
    )

    with pytest.raises(ValueError, match="failed to load"):
        load_site_hooks("bozuk", hooks_dir=tmp_path)


def test_load_site_hooks_rejects_a_parse_variants_that_is_not_async(
    tmp_path: Path,
) -> None:
    # parse_variants is awaited so it can issue its own request. Written as a
    # plain def it returns rows the engine would try to await, and that only
    # shows up against a live site.
    _write_hook(
        tmp_path,
        "senkron",
        "def parse_variants(profile, candidate, html):\n    return ()\n",
    )

    with pytest.raises(ValueError, match="must be an async def"):
        load_site_hooks("senkron", hooks_dir=tmp_path)


def test_load_site_hooks_rejects_an_async_before_search(tmp_path: Path) -> None:
    # The reverse mistake is quieter: an awaited-nowhere coroutine object would be
    # str()'d into the search URL, and the site would be searched for gibberish.
    _write_hook(
        tmp_path,
        "asenkron",
        "async def before_search(profile, query):\n    return query\n",
    )

    with pytest.raises(ValueError, match="must be a plain def"):
        load_site_hooks("asenkron", hooks_dir=tmp_path)


def test_two_sites_hooks_do_not_shadow_each_other(tmp_path: Path) -> None:
    # Both files define a function with the same name. Loaded under one module
    # name the second would replace the first, and a site would run another
    # site's override.
    _write_hook(
        tmp_path, "birinci", "def before_search(profile, query):\n    return 'bir'\n"
    )
    _write_hook(
        tmp_path, "ikinci", "def before_search(profile, query):\n    return 'iki'\n"
    )

    first = load_site_hooks("birinci", hooks_dir=tmp_path)
    second = load_site_hooks("ikinci", hooks_dir=tmp_path)

    assert first.before_search is not None and second.before_search is not None
    assert first.before_search({}, "") == "bir"
    assert second.before_search({}, "") == "iki"


def test_load_site_hooks_rejects_a_file_that_defines_no_hook_at_all(
    tmp_path: Path,
) -> None:
    # Every hook renamed, commented out, or made private. The file sits there
    # claiming the site is special while the site runs the generic flow, and
    # nothing about the run says so.
    _write_hook(
        tmp_path, "olu-dosya", "def _before_search(profile, query):\n    return query\n"
    )

    with pytest.raises(ValueError, match="defines none of"):
        load_site_hooks("olu-dosya", hooks_dir=tmp_path)


def test_sync_to_db_flattens_the_profile_into_the_sites_table(tmp_path: Path) -> None:
    # The table's column names are not the profile's field names: notes sits
    # under shipping, and discovered_at becomes profile_discovered_at. Reading
    # either one off the wrong key stores a NULL that the basket screen and the
    # profile-age badge both read as "nothing to show".
    profile = {
        **STANDALONE_SITE,
        "shipping": {
            "free_shipping_threshold_kurus": None,
            "shipping_cost_kurus": 5000,
            "notes": "kargo hafta içi çıkıyor",
        },
    }
    conn = connect(tmp_path / "test.db")

    assert sync_to_db(conn, [profile], synced_at="2026-08-08T09:00:00Z") == 1

    row = conn.execute("SELECT * FROM sites WHERE site_id = 'bagimsiz'").fetchone()
    assert row["name"] == "Bağımsız Site"
    assert row["base_url"] == "https://bagimsiz-site.com"
    assert row["free_shipping_threshold_kurus"] is None
    assert row["shipping_cost_kurus"] == 5000
    assert row["notes"] == "kargo hafta içi çıkıyor"
    assert row["profile_discovered_at"] == "2026-08-07T11:22:00Z"
    assert row["synced_at"] == "2026-08-08T09:00:00Z"


def test_sync_to_db_defaults_a_profile_without_enabled_to_enabled(
    tmp_path: Path,
) -> None:
    # "enabled" is optional in the schema and defaults to true, and jsonschema
    # does not fill defaults in. A site left out of every scan because nobody
    # typed the field is a silent scan gap, not a configuration choice.
    conn = connect(tmp_path / "test.db")

    sync_to_db(conn, [STANDALONE_SITE], synced_at="2026-08-08T09:00:00Z")

    assert _column(conn, "enabled") == 1


def test_sync_to_db_stores_a_disabled_site_as_disabled(tmp_path: Path) -> None:
    conn = connect(tmp_path / "test.db")

    sync_to_db(
        conn, [{**STANDALONE_SITE, "enabled": False}], synced_at="2026-08-08T09:00:00Z"
    )

    assert _column(conn, "enabled") == 0


def test_sync_to_db_updates_a_site_in_place_on_a_second_sync(tmp_path: Path) -> None:
    # A shipping cost corrected in the JSON has to reach the basket totals on the
    # next run. A second row under the same id, or an ignored conflict leaving the
    # old number, would both make the app quote a price the profile no longer says.
    conn = connect(tmp_path / "test.db")
    sync_to_db(conn, [STANDALONE_SITE], synced_at="2026-08-08T09:00:00Z")

    corrected = {
        **STANDALONE_SITE,
        "name": "Bağımsız Parfüm",
        "shipping": {
            "free_shipping_threshold_kurus": 60000,
            "shipping_cost_kurus": 7500,
        },
    }
    sync_to_db(conn, [corrected], synced_at="2026-08-09T09:00:00Z")

    rows = conn.execute("SELECT * FROM sites").fetchall()
    assert len(rows) == 1
    assert rows[0]["name"] == "Bağımsız Parfüm"
    assert rows[0]["free_shipping_threshold_kurus"] == 60000
    assert rows[0]["shipping_cost_kurus"] == 7500
    assert rows[0]["synced_at"] == "2026-08-09T09:00:00Z"


def test_sync_to_db_keeps_the_row_of_a_profile_that_is_no_longer_listed(
    tmp_path: Path,
) -> None:
    # products.site_id references this row, so removing a site whose profile was
    # deleted would take its price history with it. Old prices stay comparable.
    conn = connect(tmp_path / "test.db")
    sync_to_db(conn, [STANDALONE_SITE], synced_at="2026-08-08T09:00:00Z")

    sync_to_db(conn, [MINIMAL_SITE_ON_SHOPIFY], synced_at="2026-08-09T09:00:00Z")

    assert {row["site_id"] for row in conn.execute("SELECT site_id FROM sites")} == {
        "bagimsiz",
        "ikinci-site",
    }


def _column(conn: sqlite3.Connection, name: str) -> Any:
    row = conn.execute(f"SELECT {name} FROM sites").fetchone()
    return row[0]
