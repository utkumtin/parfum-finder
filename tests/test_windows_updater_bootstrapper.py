"""Windows integration checks for the native update helper."""

from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="the updater bootstrapper is Windows-only"
)


def _kernel32() -> Any:
    import ctypes

    loader_name = "WinDLL"
    return getattr(ctypes, loader_name)("kernel32", use_last_error=True)


def _bootstrapper() -> Path:
    helper = (
        Path(__file__).resolve().parents[1]
        / "dist"
        / "parfum-finder"
        / "_internal"
        / "updater-bootstrapper.exe"
    )
    if not helper.is_file():
        pytest.skip("the Windows build has not produced the updater bootstrapper")
    return helper


def _ready_event(name: str) -> int:
    import ctypes

    kernel32 = _kernel32()
    kernel32.CreateEventW.argtypes = (
        ctypes.c_void_p,
        ctypes.c_bool,
        ctypes.c_bool,
        ctypes.c_wchar_p,
    )
    kernel32.CreateEventW.restype = ctypes.c_void_p
    handle = kernel32.CreateEventW(None, True, False, name)
    if not handle:
        function_name = "get_last_error"
        raise OSError(getattr(ctypes, function_name)(), "CreateEventW failed")
    return int(handle)


def _wait_for_event(handle: int) -> bool:
    import ctypes

    kernel32 = _kernel32()
    kernel32.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    kernel32.WaitForSingleObject.restype = ctypes.c_uint32
    return kernel32.WaitForSingleObject(handle, 2_000) == 0


def _close_handle(handle: int) -> None:
    _kernel32().CloseHandle(handle)


def _command(
    helper: Path, parent_pid: int, event_name: str, log_path: Path, setup_log: Path
) -> list[str]:
    missing_installer = log_path.parent / "β setup with spaces.exe"
    return [
        str(helper),
        "--parent-pid",
        str(parent_pid),
        "--installer",
        str(missing_installer),
        "--ready-event",
        event_name,
        "--log",
        str(log_path),
        "--setup-log",
        str(setup_log),
    ]


def test_bootstrapper_signals_ready_when_the_parent_already_exited(
    tmp_path: Path,
) -> None:
    helper = _bootstrapper()
    log_dir = tmp_path / "β logs with spaces"
    log_dir.mkdir()
    log_path = log_dir / "handoff.log"
    event_name = f"Local\\parfum-finder-test-{uuid.uuid4().hex}"
    event = _ready_event(event_name)
    try:
        process = subprocess.Popen(
            _command(helper, 0xFFFFFFFF, event_name, log_path, log_dir / "setup.log")
        )
        assert _wait_for_event(event)
        assert process.wait(timeout=5) != 0
    finally:
        _close_handle(event)

    assert "handoff parent already exited" in log_path.read_text(encoding="utf-8")


def test_bootstrapper_waits_for_a_live_parent_before_running_setup(
    tmp_path: Path,
) -> None:
    helper = _bootstrapper()
    log_path = tmp_path / "handoff.log"
    event_name = f"Local\\parfum-finder-test-{uuid.uuid4().hex}"
    event = _ready_event(event_name)
    parent = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.2)"])
    try:
        process = subprocess.Popen(
            _command(helper, parent.pid, event_name, log_path, tmp_path / "setup.log")
        )
        assert _wait_for_event(event)
        assert process.poll() is None
        parent.wait(timeout=5)
        assert process.wait(timeout=5) != 0
    finally:
        _close_handle(event)

    assert "installer launch failed" in log_path.read_text(encoding="utf-8")
