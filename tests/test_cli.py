"""Tests for parfum_finder.cli.

Runs main() end-to-end against a local server rather than mocking probe() out,
so an argparse wiring mistake (wrong dest, subcommand never dispatched, url
argument dropped) actually fails here instead of only showing up by hand.
"""

import pytest
from conftest import requires_playwright

from parfum_finder import cli
from parfum_finder.cli import main
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


def test_no_subcommand_exits_with_usage_error() -> None:
    import sys

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(sys, "argv", ["parfum-finder"])
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0
