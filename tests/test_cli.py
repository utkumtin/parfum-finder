"""Tests for parfum_finder.cli.

Runs main() end-to-end against a local server rather than mocking probe() out,
so an argparse wiring mistake (wrong dest, subcommand never dispatched, url
argument dropped) actually fails here instead of only showing up by hand.
"""

import json
import sys
import types
from pathlib import Path
from typing import Any

import pytest
from conftest import requires_playwright

from parfum_finder import cli
from parfum_finder.cli import main
from parfum_finder.discover import DiscoveryReport
from parfum_finder.probe import ProbeReport
from parfum_finder.store import connect


# probe() always runs the playwright rung and raises when playwright can't run,
# so any test that actually drives it needs a working playwright setup.
@requires_playwright
def test_probe_subcommand_prints_a_report_for_the_given_url(
    server_url: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["parfum-finder", "probe", f"{server_url}/page"])

    main()

    out = capsys.readouterr().out
    assert f"probe: {server_url}/page" in out
    assert "httpx" in out
    assert "curl_cffi" in out
    assert "playwright" in out


def test_timeout_flag_reaches_probe(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # An unreachable host is the case where the timeout actually matters, so a
    # flag that silently kept the 20 second default would leave the user with no
    # way to shorten a three-strategy wait.
    seen: dict[str, object] = {}

    async def fake_probe(url: str, *, timeout_s: int = 20) -> ProbeReport:
        seen["url"] = url
        seen["timeout_s"] = timeout_s
        return ProbeReport(url=url, attempts=())

    monkeypatch.setattr(cli, "probe", fake_probe)
    monkeypatch.setattr(
        "sys.argv",
        ["parfum-finder", "probe", "http://example.invalid", "--timeout", "3"],
    )

    main()

    assert seen == {"url": "http://example.invalid", "timeout_s": 3}


@requires_playwright
def test_discover_subcommand_prints_a_report_for_the_given_url(
    server_url: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "sys.argv", ["parfum-finder", "discover", f"{server_url}/product"]
    )

    main()

    out = capsys.readouterr().out
    assert f"discover: {server_url}/product" in out
    assert "chosen strategy: httpx" in out
    assert "json-ld products: 1" in out


def test_discover_flags_reach_discover(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: dict[str, object] = {}

    async def fake_discover(
        url: str,
        *,
        product_url: str | None = None,
        search_url: str | None = None,
        timeout_s: int = 20,
        strategy: str | None = None,
        fixtures_dir: Path | None = None,
        chooser: object = None,
    ) -> DiscoveryReport:
        seen["url"] = url
        seen["product_url"] = product_url
        seen["search_url"] = search_url
        seen["timeout_s"] = timeout_s
        seen["strategy"] = strategy
        seen["fixtures_dir"] = fixtures_dir
        seen["chooser"] = chooser
        return DiscoveryReport(
            url=url,
            strategy_report=ProbeReport(url=url, attempts=()),
            chosen_strategy=None,
            trials=(),
        )

    monkeypatch.setattr(cli, "discover", fake_discover)
    monkeypatch.setattr(
        "sys.argv",
        [
            "parfum-finder",
            "discover",
            "http://example.invalid",
            "--product-url",
            "http://example.invalid/p/1",
            "--search-url",
            "http://example.invalid/search?q=x",
            "--id",
            "ornek",
            "--strategy",
            "playwright",
            "--timeout",
            "3",
        ],
    )

    main()

    assert seen == {
        "url": "http://example.invalid",
        "product_url": "http://example.invalid/p/1",
        "search_url": "http://example.invalid/search?q=x",
        "timeout_s": 3,
        "strategy": "playwright",
        # The slug becomes a directory under fixtures/, never a bare name that
        # would land wherever the command happened to be run from.
        "fixtures_dir": cli.FIXTURES_DIR / "ornek",
        # Without this wired through, a page two templates recognize would
        # apply neither and nobody at the terminal would ever be asked.
        "chooser": cli.ask_which_platform,
    }


def test_id_without_a_page_to_save_is_a_usage_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # --id on its own would create fixtures/<slug>/ with nothing in it, and an
    # empty directory reads like a captured site to whoever finds it next.
    monkeypatch.setattr(
        "sys.argv",
        ["parfum-finder", "discover", "http://example.invalid", "--id", "ornek"],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code != 0


def _answers(monkeypatch: pytest.MonkeyPatch, *typed: str) -> None:
    """Sit a person at the terminal who types these lines, in order."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    remaining = list(typed)
    monkeypatch.setattr("builtins.input", lambda prompt="": remaining.pop(0))


def test_the_platform_prompt_returns_the_template_that_was_numbered(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _answers(monkeypatch, "2")

    assert cli.ask_which_platform(("shopify", "ticimax")) == "ticimax"

    # Answering by number only works if the numbers were on screen next to the
    # names they stand for.
    out = capsys.readouterr().out
    assert "1. shopify" in out
    assert "2. ticimax" in out


@pytest.mark.parametrize("typed", ["0", ""])
def test_the_platform_prompt_lets_a_person_pick_neither(
    typed: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Two templates matching means one of them is wrong, and the person at the
    # terminal may well know that neither fits. Enter is the same answer, so
    # the safe option is also the one that takes the least effort.
    _answers(monkeypatch, typed)

    assert cli.ask_which_platform(("shopify", "ticimax")) is None


def test_the_platform_prompt_asks_again_after_an_answer_it_cannot_use(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Treating a typo as "none of them" would apply nothing while the person
    # believes they picked one, and the report would then disagree with what
    # they remember answering.
    _answers(monkeypatch, "9", "elma", "1")

    assert cli.ask_which_platform(("shopify", "ticimax")) == "shopify"

    assert capsys.readouterr().out.count("answer with a number") == 2


def test_the_platform_prompt_treats_an_interrupt_as_no_answer(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    def interrupted(prompt: str = "") -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupted)

    assert cli.ask_which_platform(("shopify", "ticimax")) is None


def test_the_platform_prompt_picks_nothing_with_no_terminal_to_ask_at(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A piped or scheduled run has nobody watching. Defaulting to a template
    # there would put a guess into a profile that no one reviews.
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    def never_asked(prompt: str = "") -> str:
        raise AssertionError("nothing may be read when there is no terminal")

    monkeypatch.setattr("builtins.input", never_asked)

    assert cli.ask_which_platform(("shopify", "ticimax")) is None
    assert capsys.readouterr().out == ""


def _fake_tui_app(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Stand in for parfum_finder.tui.app.ParfumFinderApp before it exists.

    main() imports it lazily inside the branch that launches the TUI, so
    dropping fake modules into sys.modules under its exact dotted path is
    enough to test the wiring without the real textual app.
    """
    seen: dict[str, object] = {}

    class FakeApp:
        def __init__(
            self,
            *,
            sites_dir: Path,
            db_path: Path,
            sheets_credentials: Path | None = None,
            sheets_spreadsheet: str | None = None,
            sheets_worksheet: str | None = None,
        ) -> None:
            seen["sites_dir"] = sites_dir
            seen["db_path"] = db_path
            seen["sheets_credentials"] = sheets_credentials
            seen["sheets_spreadsheet"] = sheets_spreadsheet
            seen["sheets_worksheet"] = sheets_worksheet

        def run(self) -> None:
            seen["ran"] = True

    fake_tui = types.ModuleType("parfum_finder.tui")
    fake_app_module = types.ModuleType("parfum_finder.tui.app")
    fake_app_module.ParfumFinderApp = FakeApp  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "parfum_finder.tui", fake_tui)
    monkeypatch.setitem(sys.modules, "parfum_finder.tui.app", fake_app_module)
    return seen


def test_no_subcommand_launches_the_tui_against_the_default_db(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # dev-docs/APP_FLOW.md section 1: bare `parfum-finder` opens the TUI, the
    # same as `tui` with no --db.
    seen = _fake_tui_app(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["parfum-finder"])

    main()

    assert seen == {
        "sites_dir": cli.SITES_DIR,
        "db_path": cli.DEFAULT_DB_PATH,
        "sheets_credentials": None,
        "sheets_spreadsheet": None,
        "sheets_worksheet": None,
        "ran": True,
    }


def test_tui_subcommand_passes_the_db_flag_through(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen = _fake_tui_app(monkeypatch)
    db_path = tmp_path / "custom.db"
    monkeypatch.setattr(sys, "argv", ["parfum-finder", "tui", "--db", str(db_path)])

    main()

    assert seen == {
        "sites_dir": cli.SITES_DIR,
        "db_path": db_path,
        "sheets_credentials": None,
        "sheets_spreadsheet": None,
        "sheets_worksheet": None,
        "ran": True,
    }


def test_tui_subcommand_passes_the_sheet_flags_through(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen = _fake_tui_app(monkeypatch)
    creds = tmp_path / "service-account.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "parfum-finder",
            "tui",
            "--sheet-credentials",
            str(creds),
            "--sheet-id",
            "sheet-123",
            "--sheet-worksheet",
            "Wishlist",
        ],
    )

    main()

    assert seen == {
        "sites_dir": cli.SITES_DIR,
        "db_path": cli.DEFAULT_DB_PATH,
        "sheets_credentials": creds,
        "sheets_spreadsheet": "sheet-123",
        "sheets_worksheet": "Wishlist",
        "ran": True,
    }


def test_the_live_flag_runs_the_live_pass_and_prints_both_columns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Without --live nothing may touch the network, and with it both passes have
    # to reach the report: a live run that printed only the offline column would
    # hide the very break it went out to find.
    from parfum_finder.validate import Check, SiteValidation

    passing = SiteValidation("venco", (Check("prices", True, "2 priced"),))
    broken = SiteValidation(
        "venco",
        (Check("prices", False, "the 'css' layer read nothing"),),
        (Check("jsonld", True, "reads 3 priced decant size(s)"),),
    )

    async def fake_offline(ids: object = None, **kwargs: object) -> object:
        return (passing,)

    async def fake_live(ids: object = None, **kwargs: object) -> object:
        return (broken,)

    monkeypatch.setattr(cli, "validate_all_offline", fake_offline)
    monkeypatch.setattr(cli, "validate_all_live", fake_live)
    monkeypatch.setattr("sys.argv", ["parfum-finder", "validate", "--live"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    out = capsys.readouterr().out
    assert "ok offline" in out
    assert "BROKEN live" in out
    assert 'set "extraction": "jsonld"' in out
    # A break has to fail the command, not merely print, or CI reads as green.
    assert exit_info.value.code == 1


def test_validate_on_an_unknown_site_names_it_once(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # profiles.load_site_profile raises the plain OSError text ("[Errno 2] No
    # such file or directory: ...") that Python's own open() gives, so the CLI
    # has to turn that into one clean sentence rather than bolting its own
    # "no profile" wording onto the raw error and saying the same thing twice.
    async def fake_offline(ids: object = None, **kwargs: object) -> object:
        raise FileNotFoundError(
            2, "No such file or directory", "/repo/sites/does-not-exist.json"
        )

    monkeypatch.setattr(cli, "validate_all_offline", fake_offline)
    monkeypatch.setattr("sys.argv", ["parfum-finder", "validate", "does-not-exist"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    out = capsys.readouterr().out
    assert out.count("no profile") == 1
    assert "does-not-exist" in out
    assert "Errno" not in out
    assert exit_info.value.code == 2


def _search_profile(site_id: str, base_url: str) -> dict[str, Any]:
    """A profile the engine can drive against the conftest server."""
    return {
        "schema_version": 1,
        "id": site_id,
        "name": site_id.title(),
        "base_url": base_url,
        "platform": None,
        "strategy": "httpx",
        "extraction": "embedded_json",
        "timeout_s": 5,
        "rate_limit_ms": 0,
        "search": {
            "url_template": "{base_url}/engine-search-named?q={query}",
            "result_item": ".card",
            "result_url": "a::attr(href)",
            "result_title": "a::text",
        },
        "variant_rules": {
            "size_from": "variant_label",
            "size_pattern": r"(\d+[.,]?\d*)\s*(ml|cc)",
            "exclude_keywords": ["tester", "full şişe"],
            "max_size_ml": 30,
        },
        "embedded_json": {
            "source": "attribute",
            "selector": "[data-product_variations]",
            "attribute": "data-product_variations",
            "field_map": {
                "size_raw": "attributes.attribute_pa_hacim",
                "price": "display_price",
                "in_stock": "is_in_stock",
            },
        },
        "shipping": {
            "free_shipping_threshold_kurus": 75000,
            "shipping_cost_kurus": 8900,
        },
        "discovered_at": "2026-08-07T11:22:00Z",
        "needs_review": [],
    }


def _write_sites(tmp_path: Path, *profiles: dict[str, Any]) -> Path:
    sites_dir = tmp_path / "sites"
    sites_dir.mkdir()
    for profile in profiles:
        (sites_dir / f"{profile['id']}.json").write_text(json.dumps(profile))
    return sites_dir


def test_search_stores_the_healthy_sites_when_one_site_is_broken(
    server_url: str,
    unused_tcp_port: int,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The milestone's whole claim in one test: a run writes snapshots for every
    # site that answered, and the one that blew up is a line in the report rather
    # than a run that produced nothing. A shared transaction, or an exception
    # escaping the run loop, would take the healthy site's prices down with the
    # dead one and nobody would notice until the basket came up empty.
    sites_dir = _write_sites(
        tmp_path,
        _search_profile("saglam", server_url),
        _search_profile("olu", f"http://127.0.0.1:{unused_tcp_port}"),
    )
    db_path = tmp_path / "prices.db"

    written = cli.run_search("Dior Sauvage EDP", sites_dir=sites_dir, db_path=db_path)

    assert written > 0
    conn = connect(db_path)
    rows = conn.execute(
        "SELECT site_id, size_ml_x10, price_kurus FROM latest_prices ORDER BY 1, 2"
    ).fetchall()
    assert [row["site_id"] for row in rows] == ["saglam"] * len(rows)
    assert (50, 15000) in [(row["size_ml_x10"], row["price_kurus"]) for row in rows]

    # The results page also carried another house's bottle. Storing it would put
    # Chanel's price into Dior's history, so the matcher's rejection has to hold
    # all the way to the database, not just to the screen.
    perfumes = conn.execute(
        "SELECT brand, name, concentration FROM perfumes"
    ).fetchall()
    assert [tuple(row) for row in perfumes] == [("dior", "sauvage", "EDP")]

    out = capsys.readouterr().out
    assert "error" in out
    assert "olu" in out


def test_search_syncs_every_profile_even_the_ones_it_does_not_scan(
    server_url: str, tmp_path: Path
) -> None:
    # The sites row is what the snapshots point at and what the basket screen
    # reads shipping terms from, so it has to exist for a site this run skipped.
    # Syncing only the scanned sites would make --site quietly shrink the table.
    disabled = {**_search_profile("kapali", server_url), "enabled": False}
    sites_dir = _write_sites(tmp_path, _search_profile("saglam", server_url), disabled)
    db_path = tmp_path / "prices.db"

    cli.run_search(
        "Dior Sauvage EDP", site_ids=("saglam",), sites_dir=sites_dir, db_path=db_path
    )

    conn = connect(db_path)
    assert {row["site_id"] for row in conn.execute("SELECT site_id FROM sites")} == {
        "saglam",
        "kapali",
    }
    # Skipped and disabled both mean "not scanned", so neither has prices.
    scanned = {row["site_id"] for row in conn.execute("SELECT site_id FROM products")}
    assert scanned == {"saglam"}


def test_search_does_not_scan_a_disabled_site(server_url: str, tmp_path: Path) -> None:
    disabled = {**_search_profile("kapali", server_url), "enabled": False}
    sites_dir = _write_sites(tmp_path, disabled)
    db_path = tmp_path / "prices.db"

    assert cli.run_search("Dior Sauvage EDP", sites_dir=sites_dir, db_path=db_path) == 0


def test_search_subcommand_is_wired_to_run_search(
    server_url: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sites_dir = _write_sites(tmp_path, _search_profile("saglam", server_url))
    monkeypatch.setattr(cli, "SITES_DIR", sites_dir)
    db_path = tmp_path / "prices.db"
    monkeypatch.setattr(
        "sys.argv",
        [
            "parfum-finder",
            "search",
            "Dior Sauvage EDP",
            "--site",
            "saglam",
            "--db",
            str(db_path),
        ],
    )

    main()

    assert "price(s) written" in capsys.readouterr().out
    assert db_path.exists()


def test_search_rejects_an_unknown_site_id_instead_of_scanning_the_rest(
    server_url: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A typo in --site that quietly scanned every other site would answer a
    # question nobody asked, and the report would look perfectly normal.
    sites_dir = _write_sites(tmp_path, _search_profile("saglam", server_url))
    monkeypatch.setattr(cli, "SITES_DIR", sites_dir)
    monkeypatch.setattr(
        "sys.argv",
        ["parfum-finder", "search", "Dior Sauvage EDP", "--site", "yok-boyle"],
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2
    assert "yok-boyle" in capsys.readouterr().out


def test_search_scans_every_perfume_a_line_names(
    server_url: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The same " - " the search bar takes, so someone comparing a basket from the
    # terminal does not have to run the command once per bottle. Both perfumes
    # are on this shop's one results page.
    sites_dir = _write_sites(tmp_path, _search_profile("saglam", server_url))
    db_path = tmp_path / "prices.db"

    written = cli.run_search(
        "Dior Sauvage EDP - Chanel Bleu EDP", sites_dir=sites_dir, db_path=db_path
    )

    assert written > 0
    conn = connect(db_path)
    perfumes = conn.execute(
        "SELECT brand, name FROM perfumes ORDER BY brand"
    ).fetchall()
    assert [tuple(row) for row in perfumes] == [
        ("chanel", "bleu"),
        ("dior", "sauvage"),
    ]
    # Which perfume a block of site lines is about. Two reports of the same six
    # shops read identically otherwise.
    out = capsys.readouterr().out
    assert "Dior Sauvage EDP" in out
    assert "Chanel Bleu EDP" in out


def test_search_refuses_more_perfumes_than_it_will_scan(
    server_url: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Ten perfumes across six shops is already sixty site scans. A mispasted list
    # has to be refused before the first request, not trimmed to a length nobody
    # asked for.
    sites_dir = _write_sites(tmp_path, _search_profile("saglam", server_url))
    monkeypatch.setattr(cli, "SITES_DIR", sites_dir)
    line = " - ".join(f"Marka{n} Parfum{n}" for n in range(11))
    monkeypatch.setattr("sys.argv", ["parfum-finder", "search", line])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert "at most 10 perfumes" in capsys.readouterr().out
    assert exit_info.value.code == 2


def test_search_names_the_mistyped_perfume_before_scanning_anything(
    server_url: str, tmp_path: Path
) -> None:
    # Nothing is fetched until every piece has parsed. Finding out about a
    # brand-only piece after five minutes of scanning is finding out too late,
    # and there is no screen here to collect half a scan's notices on.
    sites_dir = _write_sites(tmp_path, _search_profile("saglam", server_url))
    db_path = tmp_path / "prices.db"

    with pytest.raises(ValueError, match="names only a brand"):
        cli.run_search(
            "Dior Sauvage EDP - Chanel", sites_dir=sites_dir, db_path=db_path
        )
