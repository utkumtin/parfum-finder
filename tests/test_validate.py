"""M5's own criterion: when a profile stops agreeing with its site's real markup,
offline validation catches it and names the step that broke.

Every case here works by corrupting one field of a real profile and asserting
which check fails. That is the point of the module: a broken profile has to
produce a named failure rather than a traceback or, worse, a quietly empty
result. Asserting only `ok is False` would pass even if every break reported the
same useless step, so each case pins the step by name.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from parfum_finder.validate import (
    format_report,
    site_ids,
    validate_all_offline,
    validate_offline,
)

_ROOT = Path(__file__).resolve().parent.parent
_SITES_DIR = _ROOT / "sites"


def _corrupted_sites_dir(
    tmp_path: Path, site_id: str, mutate: Any = None, **fields: Any
) -> Path:
    """A sites/ directory holding one real profile with fields overwritten.

    The real fixtures stay untouched; only the profile moves. That is the drift
    being simulated: the site's markup is what it always was and the profile
    stopped matching it.
    """
    profile = json.loads((_SITES_DIR / f"{site_id}.json").read_text())
    if mutate is not None:
        mutate(profile)
    profile.update(fields)
    directory = tmp_path / "sites"
    directory.mkdir(exist_ok=True)
    (directory / f"{site_id}.json").write_text(json.dumps(profile))
    return directory


async def test_every_real_profile_passes_against_its_own_fixtures() -> None:
    # The baseline the corruption cases are measured against. If this ever fails
    # on its own, a real profile drifted from a real capture and the failing
    # site's report line says which step.
    results = await validate_all_offline()

    assert results, "no site profiles were found to validate"
    assert [r.site_id for r in results] == list(site_ids())
    broken = [(r.site_id, r.failure) for r in results if not r.ok]
    assert not broken, format_report(results)


async def test_a_dead_search_selector_is_caught_as_the_search_step(
    tmp_path: Path,
) -> None:
    # The most common way a profile dies: the site renames its result card class.
    # Nothing about the fetch or the extraction layer changed, so blaming either
    # would send whoever reads this to the wrong file.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        mutate=lambda p: p["search"].update({"result_item": ".no-such-card"}),
    )

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "search"
    assert ".no-such-card" in result.failure.detail


async def test_a_dead_price_selector_is_caught_as_the_extraction_step(
    tmp_path: Path,
) -> None:
    # venco reads its sizes out of an embedded JSON blob, so a field_map that
    # points the price at a key the blob does not have is the "extraction layer
    # answered but the required field is empty" row of the fail-loud table: rows
    # still come back, none of them carries a number. search_site raises
    # ExtractionFailed for it, and validate has to report that as a step rather
    # than let it escape as a traceback.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        mutate=lambda p: p["embedded_json"]["field_map"].update({"price": "nope"}),
    )

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "extraction"


async def test_the_wrong_extraction_layer_is_caught_as_the_extraction_step(
    tmp_path: Path,
) -> None:
    # decantall's sizes live in an embedded JSON blob. A profile claiming its
    # product pages declare them as JSON-LD is the "site changed how it publishes
    # its data" case, and the report has to name the layer that read nothing.
    sites_dir = _corrupted_sites_dir(tmp_path, "decantall", extraction="jsonld")

    result = await validate_offline("decantall", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "extraction"


async def test_a_page_nobody_captured_is_reported_as_a_missing_fixture(
    tmp_path: Path,
) -> None:
    # A profile on the GET endpoint layer asks for a JSON URL that no capture
    # holds. Answering it with the search page instead would make the site look
    # like it stopped replying in JSON, which is a lie about a site that was
    # never asked. The report has to say the fixture is missing.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        extraction="endpoint",
        endpoint={
            "product_json": "{base_url}/api/product.json",
            "variants_path": "variants",
            "field_map": {"size_raw": "title", "price": "price", "in_stock": "stock"},
        },
    )

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "extraction"
    assert "no saved bytes" in result.failure.detail


async def test_a_profile_that_fails_schema_validation_is_caught_first(
    tmp_path: Path,
) -> None:
    # Nothing downstream can be checked once the profile itself is invalid, and
    # reporting a "search" failure for it would be a lie about where the problem
    # is.
    sites_dir = _corrupted_sites_dir(tmp_path, "venco", extraction="telepathy")

    result = await validate_offline("venco", sites_dir=sites_dir)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "profile"
    assert [check.name for check in result.checks] == ["profile"]


async def test_missing_fixtures_are_reported_not_raised(tmp_path: Path) -> None:
    # A site whose capture was never saved, or was deleted. Offline validation
    # cannot say anything about it, and that is a reported state rather than a
    # crash that hides every other site's result.
    empty_fixtures = tmp_path / "fixtures"
    empty_fixtures.mkdir()

    result = await validate_offline("venco", fixtures_dir=empty_fixtures)

    assert not result.ok
    assert result.failure is not None
    assert result.failure.name == "fixtures"


async def test_a_site_with_no_profile_file_raises(tmp_path: Path) -> None:
    # Being asked about a site that does not exist is a mistake in the request,
    # not a finding about a profile, so it is not folded into the report.
    empty = tmp_path / "sites"
    empty.mkdir()

    with pytest.raises(FileNotFoundError):
        await validate_offline("nosuchsite", sites_dir=empty)


async def test_the_report_names_the_broken_site_and_step(tmp_path: Path) -> None:
    # What a person actually reads. A break has to be findable in the output
    # without knowing which site to look for.
    sites_dir = _corrupted_sites_dir(
        tmp_path,
        "venco",
        mutate=lambda p: p["search"].update({"result_item": ".no-such-card"}),
    )
    good = await validate_offline("decantall")
    bad = await validate_offline("venco", sites_dir=sites_dir)

    report = format_report((good, bad))

    assert "BROKEN" in report
    assert "venco" in report
    assert "search" in report
    assert "1/2 profiles pass offline" in report
    assert "broken: venco" in report


async def test_an_empty_sites_directory_says_so_instead_of_passing(
    tmp_path: Path,
) -> None:
    # "0/0 profiles pass" reads as a clean run, which is the one thing this must
    # not report when there is nothing to validate at all.
    empty = tmp_path / "sites"
    empty.mkdir()

    results = await validate_all_offline(sites_dir=empty)

    assert results == ()
    assert format_report(results) == "no site profiles to validate."
