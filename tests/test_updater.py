"""Tests for parfum_finder.updater: the version compare, the release read,
and the download that ends with the installer being handed control.

Nothing here touches the network or spawns a process. `fetch_latest_release`
is replaced by a plain function, the HTTP client by a fake that yields bytes
from memory, and the installer launch by a recorder -- the one thing this
module does that cannot be undone is exactly the thing a test must not do
for real.
"""

from __future__ import annotations

import tempfile
import threading
from pathlib import Path
from typing import Any

import httpx
import pytest

from parfum_finder import updater as updater_module
from parfum_finder.updater import (
    DownloadProgress,
    ReleaseInfo,
    UpdateDownload,
    UpdateHandoffError,
    check_for_update,
    fetch_latest_release,
    handoff_command,
    is_newer,
    launch_installer,
    parse_version,
)


@pytest.fixture(autouse=True)
def _enable_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    # check_for_update() answers "no update" outside a frozen build, which is
    # the behaviour a source checkout wants and the one that would make every
    # assertion below vacuous.
    monkeypatch.setenv("PARFUM_FINDER_FORCE_UPDATE_CHECK", "1")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("v0.2.1", (0, 2, 1)),
        ("1.0", (1, 0)),
        ("0.2.1-beta", None),
        ("", None),
        ("nightly", None),
    ],
)
def test_parse_version(text: str, expected: tuple[int, ...] | None) -> None:
    assert parse_version(text) == expected


@pytest.mark.parametrize(
    ("candidate", "current", "expected"),
    [
        ("v0.2.0", "0.1.0", True),
        ("v0.1.0", "0.1.0", False),
        ("v0.0.9", "0.1.0", False),
        # A shorter tag is the same version, not an older one: 0.2 == 0.2.0.
        ("v0.2", "0.2.0", False),
        ("v0.2.1", "0.2", True),
    ],
)
def test_is_newer(candidate: str, current: str, expected: bool) -> None:
    assert is_newer(candidate, current) is expected


def test_an_unreadable_tag_never_counts_as_an_update() -> None:
    """A tag nobody can order against must not open a dialog.

    The two failure directions are not equal: a missed update costs one
    launch, an invented one is a pop-up that comes back every single time
    and can never be satisfied by installing anything.
    """
    assert is_newer("release-candidate", "0.1.0") is False
    assert is_newer("v0.2.0", "not-a-version") is False


def test_check_reports_the_release_when_it_is_newer() -> None:
    release = ReleaseInfo(
        version="v0.2.0",
        notes="- sepet ekranı hızlandı",
        release_url="https://example.invalid/releases/v0.2.0",
        download_url="https://example.invalid/setup.exe",
    )
    result = check_for_update(current="0.1.0", fetch=lambda: release)

    assert result["update_available"] is True
    assert result["latest_version"] == "0.2.0"
    assert result["current_version"] == "0.1.0"
    assert result["notes"] == "- sepet ekranı hızlandı"
    assert result["download_url"] == "https://example.invalid/setup.exe"


def test_check_reports_nothing_when_the_release_is_the_installed_one() -> None:
    release = ReleaseInfo(
        version="v0.1.0", notes="x", release_url="u", download_url="d"
    )
    result = check_for_update(current="0.1.0", fetch=lambda: release)

    assert result["update_available"] is False
    assert result["latest_version"] is None


def test_check_survives_github_being_unreachable() -> None:
    """No network is not an error the user has to be told about.

    The check runs unprompted at every launch, so a machine that is simply
    offline has to come back "no update" rather than anything the app would
    put on screen.
    """
    result = check_for_update(current="0.1.0", fetch=lambda: None)

    assert result["update_available"] is False
    assert result["current_version"] == "0.1.0"


def test_check_is_off_outside_a_frozen_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PARFUM_FINDER_FORCE_UPDATE_CHECK", raising=False)

    def unreachable() -> ReleaseInfo | None:
        raise AssertionError("a source checkout must not ask GitHub anything")

    assert check_for_update(current="0.1.0", fetch=unreachable)["update_available"] is (
        False
    )


def _release_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "tag_name": "v0.3.0",
        "body": "notlar",
        "html_url": "https://example.invalid/releases/v0.3.0",
        "assets": [
            {"name": "graph.json", "browser_download_url": "https://x.invalid/g.json"},
            {
                "name": "parfum-finder-setup.exe",
                "browser_download_url": "https://x.invalid/setup.exe",
            },
        ],
    }
    payload.update(overrides)
    return payload


def test_fetch_picks_the_installer_asset_not_the_first_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The .exe is what gets downloaded, whatever else is attached.

    Releases carry more than the installer, and the asset list is in whatever
    order GitHub returns. Taking assets[0] would eventually download a JSON
    file and try to run it.
    """
    _patch_get(monkeypatch, _release_payload())

    release = fetch_latest_release()

    assert release is not None
    assert release.download_url == "https://x.invalid/setup.exe"
    assert release.version == "v0.3.0"
    assert release.notes == "notlar"


def test_fetch_returns_a_release_without_an_installer_asset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_get(monkeypatch, _release_payload(assets=[]))

    release = fetch_latest_release()

    assert release is not None
    assert release.download_url is None


def test_fetch_swallows_an_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def raising(*_args: Any, **_kwargs: Any) -> httpx.Response:
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(httpx, "get", raising)

    assert fetch_latest_release() is None


def _patch_get(
    monkeypatch: pytest.MonkeyPatch, payload: Any, status: int = 200
) -> None:
    def fake_get(url: str, **kwargs: Any) -> httpx.Response:
        request = httpx.Request("GET", url)
        return httpx.Response(status, json=payload, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)


class _FakeStreamResponse:
    def __init__(self, chunks: list[bytes], total: int | None) -> None:
        self._chunks = chunks
        self.headers = {} if total is None else {"Content-Length": str(total)}

    def raise_for_status(self) -> None:
        return None

    def iter_bytes(self) -> Any:
        yield from self._chunks

    def __enter__(self) -> _FakeStreamResponse:
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None


class _FakeClient:
    def __init__(self, chunks: list[bytes], total: int | None, error: Exception | None):
        self._chunks = chunks
        self._total = total
        self._error = error

    def __enter__(self) -> _FakeClient:
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None

    def stream(self, _method: str, _url: str) -> _FakeStreamResponse:
        if self._error is not None:
            raise self._error
        return _FakeStreamResponse(self._chunks, self._total)


def _factory(
    chunks: list[bytes], total: int | None = None, error: Exception | None = None
) -> Any:
    return lambda **_kwargs: _FakeClient(chunks, total, error)


def _wait_for(download: UpdateDownload, state: str) -> DownloadProgress:
    # The download runs on its own thread; polling its snapshot is the same
    # thing the dialog does, only faster.
    tick = threading.Event()
    for _ in range(200):
        progress = download.progress()
        if progress.state == state:
            return progress
        tick.wait(0.02)
    raise AssertionError(f"download never reached {state}: {download.progress()}")


def test_download_writes_the_installer_and_reports_ready(tmp_path: Path) -> None:
    download = UpdateDownload(
        dest_dir=tmp_path, client_factory=_factory([b"MZ", b"payload"], total=9)
    )

    assert download.start("https://x.invalid/setup.exe") is not None
    progress = _wait_for(download, "ready")

    assert progress.received == 9
    assert progress.total == 9
    assert (tmp_path / "parfum-finder-setup.exe").read_bytes() == b"MZpayload"


def test_a_second_download_is_refused_while_one_runs(tmp_path: Path) -> None:
    download = UpdateDownload(dest_dir=tmp_path, client_factory=_factory([b"x"]))
    download.start("https://x.invalid/setup.exe")
    _wait_for(download, "ready")
    # Only a running download blocks a new one; a finished one can be redone.
    assert download.start("https://x.invalid/setup.exe") is not None


def test_a_failed_download_says_so_instead_of_going_quiet(tmp_path: Path) -> None:
    """An error state is what turns the button back on with a reason.

    Falling back to "idle" would leave the dialog looking untouched, which
    reads as a button that does nothing.
    """
    download = UpdateDownload(
        dest_dir=tmp_path,
        client_factory=_factory([], error=httpx.ConnectError("dns")),
    )
    download.start("https://x.invalid/setup.exe")
    progress = _wait_for(download, "error")

    assert "dns" in progress.message


def test_install_hands_the_downloaded_file_over(tmp_path: Path) -> None:
    spawned: list[Path] = []
    download = UpdateDownload(
        dest_dir=tmp_path,
        client_factory=_factory([b"MZ"]),
        spawn=spawned.append,
    )
    download.start("https://x.invalid/setup.exe")
    _wait_for(download, "ready")

    assert download.install() is True
    assert spawned == [tmp_path / "parfum-finder-setup.exe"]
    assert download.progress().state == "installing"


def test_copy_bootstrapper_uses_a_unique_temp_executable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    source = bundle_dir / "updater-bootstrapper.exe"
    source.write_bytes(b"MZ")
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()

    monkeypatch.setattr(updater_module.paths, "resource_dir", lambda: bundle_dir)
    monkeypatch.setattr(updater_module.paths, "is_frozen", lambda: True)
    monkeypatch.setattr(updater_module.tempfile, "gettempdir", lambda: str(temp_dir))
    monkeypatch.setattr(
        updater_module.uuid, "uuid4", lambda: type("Id", (), {"hex": "a"})()
    )

    copied = updater_module._copy_bootstrapper()

    assert copied == temp_dir / "parfum-finder-updater-a.exe"
    assert copied.read_bytes() == b"MZ"


def test_handoff_command_passes_structured_native_helper_arguments() -> None:
    command = handoff_command(
        Path(r"C:\Users\u\AppData\Local\Temp\parfum-finder-setup.exe"),
        helper=Path(r"C:\Users\u\AppData\Local\Temp\updater-bootstrapper.exe"),
        ready_event=r"Local\parfum-finder-update-123",
        parent_pid=42,
    )

    assert command == [
        r"C:\Users\u\AppData\Local\Temp\updater-bootstrapper.exe",
        "--parent-pid",
        "42",
        "--installer",
        r"C:\Users\u\AppData\Local\Temp\parfum-finder-setup.exe",
        "--ready-event",
        r"Local\parfum-finder-update-123",
        "--log",
        str(Path(tempfile.gettempdir()) / "parfum-finder-update.log"),
        "--setup-log",
        str(Path(tempfile.gettempdir()) / "parfum-finder-setup.log"),
    ]


def test_native_handoff_breaks_out_of_the_apps_job_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, int] = {}

    def fake_popen(command: list[str], **kwargs: Any) -> None:
        recorded["creationflags"] = kwargs["creationflags"]
        assert command[0] == "helper.exe"

    monkeypatch.setattr(updater_module.sys, "platform", "win32")
    for name, value in (
        ("CREATE_BREAKAWAY_FROM_JOB", 0x01000000),
        ("DETACHED_PROCESS", 0x00000008),
        ("CREATE_NEW_PROCESS_GROUP", 0x00000200),
    ):
        monkeypatch.setattr(updater_module.subprocess, name, value, raising=False)
    monkeypatch.setattr(updater_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(updater_module, "_create_ready_event", lambda _: 99)
    monkeypatch.setattr(updater_module, "_wait_for_ready", lambda *_: True)
    monkeypatch.setattr(updater_module, "_close_handle", lambda _: None)

    launch_installer(
        Path("setup.exe"), helper=Path("helper.exe"), ready_event="event-name"
    )

    assert recorded["creationflags"] & 0x01000000
    assert recorded["creationflags"] & 0x00000008


def test_native_handoff_fails_fast_when_the_helper_never_acknowledges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(updater_module.sys, "platform", "win32")
    for name, value in (
        ("CREATE_BREAKAWAY_FROM_JOB", 0x01000000),
        ("DETACHED_PROCESS", 0x00000008),
        ("CREATE_NEW_PROCESS_GROUP", 0x00000200),
    ):
        monkeypatch.setattr(updater_module.subprocess, name, value, raising=False)
    monkeypatch.setattr(updater_module.subprocess, "Popen", lambda *_a, **_k: None)
    monkeypatch.setattr(updater_module, "_create_ready_event", lambda _: 99)
    monkeypatch.setattr(updater_module, "_wait_for_ready", lambda *_: False)
    monkeypatch.setattr(updater_module, "_close_handle", lambda _: None)

    with pytest.raises(UpdateHandoffError, match="zamanında"):
        launch_installer(
            Path("setup.exe"),
            helper=Path("helper.exe"),
            ready_event="event-name",
            ready_timeout_ms=1,
        )


def test_install_keeps_the_application_open_when_handoff_fails(tmp_path: Path) -> None:
    def fail(_: Path) -> None:
        raise UpdateHandoffError("güncelleme yardımcısı başlatılamadı")

    download = UpdateDownload(
        dest_dir=tmp_path,
        client_factory=_factory([b"MZ"]),
        spawn=fail,
    )
    download.start("https://x.invalid/setup.exe")
    _wait_for(download, "ready")

    assert download.install() is False
    progress = download.progress()
    assert progress.state == "error"
    assert progress.message == "güncelleme yardımcısı başlatılamadı"


def test_install_refuses_before_anything_has_been_downloaded(tmp_path: Path) -> None:
    """Nothing is spawned unless a complete file is on disk.

    Running a half-written or absent installer is the one failure here that
    could leave the user with a broken installation instead of an old one.
    """
    spawned: list[Path] = []
    download = UpdateDownload(dest_dir=tmp_path, spawn=spawned.append)

    assert download.install() is False
    assert spawned == []
