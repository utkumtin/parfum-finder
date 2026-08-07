"""Tests for parfum_finder.cli.

Runs main() end-to-end against a local server rather than mocking probe() out,
so an argparse wiring mistake (wrong dest, subcommand never dispatched, url
argument dropped) actually fails here instead of only showing up by hand.
"""

from pathlib import Path

import pytest
from conftest import requires_playwright

from parfum_finder import cli
from parfum_finder.cli import main
from parfum_finder.discover import DiscoveryReport
from parfum_finder.probe import ProbeReport


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


def test_no_subcommand_exits_with_usage_error() -> None:
    import sys

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(sys, "argv", ["parfum-finder"])
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0
