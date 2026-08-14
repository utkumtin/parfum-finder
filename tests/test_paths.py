"""Tests for parfum_finder.paths: frozen vs. source path resolution.

`ensure_user_data()` only ever runs inside a frozen build in production, so
these monkeypatch `is_frozen` to exercise it from a normal test run -- the one
guarantee in its docstring, that a first launch seeds sites/platforms/hooks
and a later one never overwrites what the user has already edited, has to be
checked somewhere.
"""

from pathlib import Path

import pytest

from parfum_finder import paths


def test_resource_dir_and_user_data_dir_are_the_repo_root_when_not_frozen() -> None:
    assert paths.is_frozen() is False
    assert paths.resource_dir() == Path(__file__).resolve().parent.parent
    assert paths.user_data_dir() == paths.resource_dir()


def _freeze(
    monkeypatch: pytest.MonkeyPatch, resource_dir: Path, user_data_dir: Path
) -> None:
    monkeypatch.setattr(paths, "is_frozen", lambda: True)
    monkeypatch.setattr(paths, "resource_dir", lambda: resource_dir)
    monkeypatch.setattr(paths, "user_data_dir", lambda: user_data_dir)


def test_ensure_user_data_seeds_sites_platforms_and_hooks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "bundle"
    user_data = tmp_path / "user_data"
    (bundle / "sites").mkdir(parents=True)
    (bundle / "sites" / "site-a.json").write_text("{}")
    (bundle / "platforms").mkdir()
    (bundle / "platforms" / "shopify.json").write_text("{}")
    (bundle / "hooks").mkdir()
    (bundle / "hooks" / "README.md").write_text("hooks go here")
    _freeze(monkeypatch, bundle, user_data)

    paths.ensure_user_data()

    assert (user_data / "sites" / "site-a.json").read_text() == "{}"
    assert (user_data / "platforms" / "shopify.json").read_text() == "{}"
    assert (user_data / "hooks" / "README.md").read_text() == "hooks go here"


def test_ensure_user_data_never_overwrites_an_edited_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "bundle"
    user_data = tmp_path / "user_data"
    (bundle / "sites").mkdir(parents=True)
    (bundle / "sites" / "site-a.json").write_text('{"version": "bundled"}')
    (user_data / "sites").mkdir(parents=True)
    (user_data / "sites" / "site-a.json").write_text('{"version": "user edited"}')
    _freeze(monkeypatch, bundle, user_data)

    paths.ensure_user_data()

    assert (
        user_data / "sites" / "site-a.json"
    ).read_text() == '{"version": "user edited"}'


def test_ensure_user_data_is_a_noop_when_not_frozen(tmp_path: Path) -> None:
    """A source run has nothing to seed: resource_dir and user_data_dir are
    already the same repo checkout, so copying one onto the other would be
    pointless at best and a self-overwrite at worst."""
    paths.ensure_user_data()  # must not raise, must not touch anything


def test_ensure_user_data_skips_when_seeded_is_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "bundle"
    user_data = tmp_path / "user_data"
    (bundle / "sites").mkdir(parents=True)
    (bundle / "sites" / "site-a.json").write_text("{}")
    _freeze(monkeypatch, bundle, user_data)

    paths.ensure_user_data(seeded=False)

    assert not user_data.exists()
