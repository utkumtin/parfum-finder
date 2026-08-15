"""The Windows desktop entry point: an ephemeral-port FastAPI backend behind
a native pywebview window.

Nothing else in the package imports this module. `pywebview` is part of the
optional "gui" extra, and its Linux backend pulls in system GTK/Qt bindings
this project has no other reason to depend on. `cli.py` reaches this module
the same way it already reaches `tui.app`: through a lazy import inside the
"gui" subcommand, so every other subcommand keeps running without it.
"""

from __future__ import annotations

import contextlib
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import uvicorn

from parfum_finder import paths
from parfum_finder.api.app import DEFAULT_DB_PATH, DEFAULT_SITES_DIR, create_app

_WINDOW_TITLE = "parfum-finder"


@dataclass
class _RunningServer:
    port: int
    token: str
    server: uvicorn.Server
    thread: threading.Thread

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


def _start_server(
    *, sites_dir: Path | None = None, db_path: Path | None = None
) -> _RunningServer:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = sock.getsockname()[1]

    app = create_app(
        sites_dir=sites_dir if sites_dir is not None else DEFAULT_SITES_DIR,
        db_path=db_path if db_path is not None else DEFAULT_DB_PATH,
    )
    token: str = app.state.parfum.auth_token
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
    thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
    thread.start()
    return _RunningServer(port=port, token=token, server=server, thread=thread)


def _ping(
    port: int, token: str, path: str = "/api/config", timeout: float = 2.0
) -> bool:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", headers={"X-Auth-Token": token}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return bool(response.status == 200)
    except (OSError, urllib.error.URLError):
        return False


def _wait_until_ready(port: int, token: str, timeout_s: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if _ping(port, token):
            return True
        time.sleep(0.1)
    return False


def run_selftest(*, sites_dir: Path | None = None, db_path: Path | None = None) -> int:
    """Boot the backend headlessly, hit it once, exit. No window opens.

    This is what the Windows CI smoke test runs against the frozen exe: a
    bundle missing a module fails to import here with a clear traceback
    instead of a silent blank window, and a passing run proves the seed step
    and the backend both work on a machine nobody hand-configured.

    `sites_dir`/`db_path` exist for tests, which cannot be allowed to touch
    the real user-data directory a bare call would default to; production
    callers (`main()`, the CI smoke test) never pass them.
    """
    paths.ensure_user_data()
    running = _start_server(sites_dir=sites_dir, db_path=db_path)
    try:
        ok = _wait_until_ready(running.port, running.token) and _ping(
            running.port, running.token, path="/api/sites"
        )
    finally:
        running.stop()
    return 0 if ok else 1


def run_window() -> None:
    paths.ensure_user_data()
    running = _start_server()
    try:
        if not _wait_until_ready(running.port, running.token):
            raise RuntimeError("backend did not become ready in time")

        # Imported here, not at module load: see the module docstring.
        import webview

        try:
            webview.create_window(
                _WINDOW_TITLE,
                f"http://127.0.0.1:{running.port}/",
                width=1280,
                height=800,
            )
            webview.start()
        except Exception:
            _report_startup_failure()
            raise
    finally:
        running.stop()


def _report_startup_failure() -> None:
    """Best-effort native message box.

    A missing WebView2 Runtime is the expected way this fails on Windows 10
    (Windows 11 ships it): `webview.create_window`/`start` raise instead of
    opening anything, and `console=False` means there is no terminal to
    print the reason to. A silent blank window is exactly what "fail loud"
    forbids, so this tries a MessageBoxW before the exception propagates.
    """
    if sys.platform != "win32":
        return
    import ctypes

    message = (
        "parfum-finder açılamadı. Bu genellikle Microsoft Edge WebView2 "
        "Runtime'ın kurulu olmamasından kaynaklanır.\n\n"
        "https://developer.microsoft.com/microsoft-edge/webview2/ adresinden "
        '"Evergreen Bootstrapper"ı indirip kurduktan sonra tekrar deneyin.'
    )
    with contextlib.suppress(OSError):
        ctypes.windll.user32.MessageBoxW(0, message, _WINDOW_TITLE, 0x10)


def main(*, selftest: bool = False) -> int:
    if selftest:
        return run_selftest()
    run_window()
    return 0
