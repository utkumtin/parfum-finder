"""Site profile loading, schema validation, and platform-template merging.

Fields set on a site's own profile always win over the platform template it's based
on (deep merge, site overrides platform). A profile with `platform: null` skips
template merging entirely.

Validation runs on the *effective* (post-merge) profile, not the raw file on disk.
A site profile is allowed to omit anything its platform template already supplies;
the merged result is what has to satisfy schema/site.schema.json.

The `sites` table is a mirror of these profiles rather than a second source of
truth, so `sync_to_db()` writes it and nothing else does.

The optional Python escape hatch for a site, `hooks/<id>.py`, is loaded here too:
it is per-site configuration that the engine reads before driving a site, the same
as the JSON profile next to it.
"""

import importlib.util
import inspect
import json
import sqlite3
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema

from parfum_finder import paths

SCHEMA_DIR = paths.schema_dir()
DEFAULT_PLATFORMS_DIR = paths.platforms_dir()
DEFAULT_HOOKS_DIR = paths.hooks_dir()

# The only three names a hook file may define. Anything else public in there is
# rejected rather than ignored, which is what makes a typo visible.
HOOK_NAMES = ("before_search", "after_search", "parse_variants")

# parse_variants may issue its own requests, so it has to be awaited. The other
# two are plain transforms of a string and of a list, and calling them without
# awaiting would hand the engine a coroutine object where it expects a value.
_ASYNC_HOOKS = ("parse_variants",)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override onto base. override always wins on conflicts.

    Nested objects merge field by field; arrays and plain values are replaced
    wholesale, never combined.
    """
    merged = dict(base)
    for key, value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(value, dict):
            merged[key] = deep_merge(base_value, value)
        else:
            merged[key] = value
    return merged


def load_platform_template(
    name: str, platforms_dir: Path = DEFAULT_PLATFORMS_DIR
) -> dict[str, Any]:
    """Load and schema-validate one platform template by name (without ".json")."""
    path = platforms_dir / f"{name}.json"
    template = _load_json(path)
    _validate(template, "platform.schema.json", path)
    return template


def load_platform_templates(
    platforms_dir: Path = DEFAULT_PLATFORMS_DIR,
) -> dict[str, dict[str, Any]]:
    """Load every template in the directory, keyed by file name without ".json".

    One unreadable template stops the whole load instead of being skipped. A
    caller that matches a page against this library believes the library is
    complete, and a platform that quietly dropped out of it looks exactly like a
    platform that was never in it.

    A template whose "name" disagrees with its file name is also an error: site
    profiles reference a platform by file name, so the two have to be the same
    string or the reference points at a template nobody can find.
    """
    templates: dict[str, dict[str, Any]] = {}
    for path in sorted(platforms_dir.glob("*.json")):
        template = load_platform_template(path.stem, platforms_dir)
        if template["name"] != path.stem:
            raise ValueError(
                f"{path}: template is named {template['name']!r} but its file is "
                f"{path.stem!r}. A site profile can only reference the file name."
            )
        templates[path.stem] = template
    return templates


def load_site_profile(
    path: Path, platforms_dir: Path = DEFAULT_PLATFORMS_DIR
) -> dict[str, Any]:
    """Load one site profile, applying its platform template if it has one.

    Returns the effective, schema-validated profile. Raises ValueError if the
    file is not valid JSON or the effective profile fails schema validation,
    instead of returning a broken profile for the caller to trip over later.
    """
    site = _load_json(path)
    platform_name = site.get("platform")
    if platform_name is not None:
        template = load_platform_template(platform_name, platforms_dir)
        effective = deep_merge(template["defaults"], site)
    else:
        effective = site
    _validate(effective, "site.schema.json", path)
    return effective


def sync_to_db(
    conn: sqlite3.Connection,
    profiles: Iterable[dict[str, Any]],
    *,
    synced_at: str,
) -> int:
    """Mirror site profiles into the sites table and return how many were written.

    The profiles are the effective ones from load_site_profile, and the table is
    a copy of them, not a second place to edit. Every column outside the key is
    overwritten on each sync, so a shipping cost corrected in the JSON reaches
    the basket totals on the next run instead of after somebody remembers to
    touch the database too.

    A profile that disappeared from sites/ keeps its row. products.site_id points
    at it, so dropping the row would either fail against the foreign key or take
    that shop's whole price history with it, and a shop nobody scans any more is
    still a shop whose old prices are worth comparing against.

    The timestamp is passed in rather than taken here: this module cannot import
    store, and every timestamp in the database has to come from its now_iso().
    """
    rows = [(*_site_row(profile), synced_at) for profile in profiles]
    with conn:
        conn.executemany(
            "INSERT INTO sites (site_id, name, base_url, enabled,"
            " free_shipping_threshold_kurus, shipping_cost_kurus, notes,"
            " profile_discovered_at, synced_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT (site_id) DO UPDATE SET"
            " name = excluded.name, base_url = excluded.base_url,"
            " enabled = excluded.enabled,"
            " free_shipping_threshold_kurus ="
            " excluded.free_shipping_threshold_kurus,"
            " shipping_cost_kurus = excluded.shipping_cost_kurus,"
            " notes = excluded.notes,"
            " profile_discovered_at = excluded.profile_discovered_at,"
            " synced_at = excluded.synced_at",
            rows,
        )
    return len(rows)


def _site_row(profile: dict[str, Any]) -> tuple[Any, ...]:
    """Flatten one profile into the column order of the sites table.

    The shipping fields are nested in the profile and flat in the table, and
    "enabled" is optional in the schema with a documented default of true.
    Reading it with .get and no default would store a NULL that later reads as
    "not enabled" and quietly drop the site from every scan.
    """
    shipping = profile["shipping"]
    return (
        profile["id"],
        profile["name"],
        profile["base_url"],
        int(profile.get("enabled", True)),
        shipping["free_shipping_threshold_kurus"],
        shipping["shipping_cost_kurus"],
        shipping.get("notes"),
        profile["discovered_at"],
    )


@dataclass(frozen=True)
class SiteHooks:
    """The Python overrides one site declares, or nothing at all.

    Every field is optional and defaults to None, so a site with no hook file and
    a site whose hook file only defines one of the three are the same shape to the
    caller: it checks a field for None instead of asking whether a file exists.

    The callables are typed loosely because their arguments and results are the
    engine's own types, and the engine reads profiles rather than the other way
    round. The exact shapes live in the engine, next to the code that calls them.
    """

    before_search: Callable[..., Any] | None = None
    after_search: Callable[..., Any] | None = None
    parse_variants: Callable[..., Any] | None = None


def load_site_hooks(site_id: str, hooks_dir: Path = DEFAULT_HOOKS_DIR) -> SiteHooks:
    """Load hooks/<id>.py if that site has one, else return empty hooks.

    A missing file is the normal case and means the site is driven from its
    profile alone. A file that exists but cannot be executed is not: it is raised,
    because a site that asked for an override and silently did not get one runs
    the generic flow while looking like it ran the special one.

    Hook files live outside the package, in a directory the user edits, so they
    are loaded from their path rather than imported by name. The module name they
    are given is namespaced by site id so two sites' hooks cannot shadow each
    other.

    A public name in the file that is not one of the three hooks is rejected. The
    reason is a misspelling: a file defining `parse_variant` would load, define
    nothing the engine looks for, and quietly do nothing at all. Helpers are still
    allowed, they just have to start with an underscore.
    """
    path = hooks_dir / f"{site_id}.py"
    if not path.is_file():
        return SiteHooks()

    spec = importlib.util.spec_from_file_location(
        f"parfum_finder_hooks.{site_id}", path
    )
    if spec is None or spec.loader is None:
        raise ValueError(f"{path}: cannot be loaded as a Python module")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise ValueError(f"{path}: hook file failed to load ({e})") from e

    _reject_unknown_hooks(module, path)
    hooks = SiteHooks(**{name: getattr(module, name, None) for name in HOOK_NAMES})
    if all(getattr(hooks, name) is None for name in HOOK_NAMES):
        raise ValueError(
            f"{path}: defines none of {', '.join(HOOK_NAMES)}, so nothing in it "
            f"would ever run. Delete the file, or name a hook the engine calls."
        )
    _check_hook_kinds(hooks, path)
    return hooks


def _reject_unknown_hooks(module: Any, path: Path) -> None:
    unknown = sorted(
        name
        for name, value in vars(module).items()
        if not name.startswith("_")
        and name not in HOOK_NAMES
        and callable(value)
        # Only what this file defines itself. Anything it imported is callable
        # too, and importing a helper is not a mistake.
        and getattr(value, "__module__", None) == module.__name__
    )
    if unknown:
        raise ValueError(
            f"{path}: defines {', '.join(unknown)}, which the engine never calls. "
            f"A hook is one of {', '.join(HOOK_NAMES)}; rename a helper with a "
            f"leading underscore."
        )


def _check_hook_kinds(hooks: SiteHooks, path: Path) -> None:
    for name in HOOK_NAMES:
        hook = getattr(hooks, name)
        if hook is None:
            continue
        is_async = inspect.iscoroutinefunction(hook)
        if is_async and name not in _ASYNC_HOOKS:
            raise ValueError(f"{path}: {name} must be a plain def, not async def")
        if not is_async and name in _ASYNC_HOOKS:
            raise ValueError(f"{path}: {name} must be an async def")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: invalid JSON ({e})") from e
    return data


def _validate(profile: dict[str, Any], schema_filename: str, source: Path) -> None:
    schema = json.loads((SCHEMA_DIR / schema_filename).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    try:
        validator.validate(profile)
    except jsonschema.ValidationError as e:
        field_path = "/".join(str(p) for p in e.absolute_path)
        location = f" at '{field_path}'" if field_path else ""
        raise ValueError(f"{source}: invalid profile{location}: {e.message}") from e
