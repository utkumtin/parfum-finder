"""Site profile loading, schema validation, and platform-template merging.

Fields set on a site's own profile always win over the platform template it's based
on (deep merge, site overrides platform). A profile with `platform: null` skips
template merging entirely.

Validation runs on the *effective* (post-merge) profile, not the raw file on disk.
A site profile is allowed to omit anything its platform template already supplies;
the merged result is what has to satisfy schema/site.schema.json.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = _REPO_ROOT / "schema"
DEFAULT_PLATFORMS_DIR = _REPO_ROOT / "platforms"


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override onto base. override always wins on conflicts.

    Nested objects merge field by field; arrays and plain values are replaced
    wholesale, never combined, per SCHEMA.md's platform merge rule.
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


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data: Any = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: invalid JSON ({e})") from e
    return data


def _validate(profile: dict[str, Any], schema_filename: str, source: Path) -> None:
    schema = json.loads((SCHEMA_DIR / schema_filename).read_text())
    validator = jsonschema.Draft202012Validator(schema)
    try:
        validator.validate(profile)
    except jsonschema.ValidationError as e:
        field_path = "/".join(str(p) for p in e.absolute_path)
        location = f" at '{field_path}'" if field_path else ""
        raise ValueError(f"{source}: invalid profile{location}: {e.message}") from e
