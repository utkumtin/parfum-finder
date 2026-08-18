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
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import uvicorn

from parfum_finder import paths
from parfum_finder.api.app import DEFAULT_DB_PATH, DEFAULT_SITES_DIR, create_app

_WINDOW_TITLE = "parfum-finder"

# packaging/installer.iss'teki AppMutex ile birebir aynı olmak zorunda.
APP_MUTEX_NAME = "parfum-finder-running"


@dataclass
class _RunningServer:
    port: int
    token: str
    server: uvicorn.Server
    thread: threading.Thread

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            # should_exit is the polite half: uvicorn waits for whatever is
            # still in flight, and a scan's WebSocket can outlast the person
            # who closed the window. force_exit drops those connections so
            # the loop, and with it the browser this scan may have started,
            # is torn down while the process is still around to do it.
            self.server.force_exit = True
            self.thread.join(timeout=5)


def _start_server(
    *,
    sites_dir: Path | None = None,
    db_path: Path | None = None,
    request_quit: Callable[[], None] | None = None,
) -> _RunningServer:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = sock.getsockname()[1]

    app = create_app(
        sites_dir=sites_dir if sites_dir is not None else DEFAULT_SITES_DIR,
        db_path=db_path if db_path is not None else DEFAULT_DB_PATH,
        request_quit=request_quit,
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
    _hold_app_mutex()
    _kill_children_with_app()
    quit_requested = threading.Event()
    window_closed = threading.Event()
    running = _start_server(request_quit=quit_requested.set)
    try:
        if not _wait_until_ready(running.port, running.token):
            raise RuntimeError("backend did not become ready in time")

        # Imported here, not at module load: see the module docstring.
        import webview

        try:
            window = webview.create_window(
                _WINDOW_TITLE,
                f"http://127.0.0.1:{running.port}/",
                width=1280,
                height=800,
            )

            def destroy_window() -> None:
                if window is not None:
                    window.destroy()

            try:
                webview.start(
                    lambda: _close_window_when_asked(
                        quit_requested, window_closed, destroy_window
                    )
                )
            finally:
                # webview.start() only returns once the window is gone, and
                # the watcher above has to learn that from here: nothing else
                # tells it, and it is what keeps the process alive if it never
                # finds out.
                window_closed.set()
        except Exception:
            _report_startup_failure()
            raise
    finally:
        running.stop()


# Pencere kapanmışsa izleyici bu kadar sonra öğrenir. Kapanış gecikmesi olarak
# fark edilmeyecek kadar kısa, boşta dönmeyecek kadar uzun.
_QUIT_POLL_S = 0.25


def _close_window_when_asked(
    quit_requested: threading.Event,
    window_closed: threading.Event,
    destroy: Callable[[], None],
) -> None:
    """Güncelleme kurulumu devredildiğinde pencereyi kapatır.

    webview.start(func) bunu kendi açtığı bir thread'de çalıştırır ve o thread
    daemon değil. quit_requested'ı süresiz beklemek, olağan kapanışta (kimse
    kurulum başlatmadan pencereyi kapattığında) bu thread'i sonsuza kadar orada
    tutuyordu: yorumlayıcı çıkarken onu join ediyor, süreç görev yöneticisinde
    portu, mutex'i ve yüz megabayt civarı belleğiyle kalmaya devam ediyordu.
    Bu yüzden bekleme yoklamalı, ve pencerenin kapanması da onu bitiriyor.
    """
    while not window_closed.is_set():
        if quit_requested.wait(timeout=_QUIT_POLL_S):
            destroy()
            return


def _hold_app_mutex() -> None:
    """Kurulum dosyasının uygulamanın açık olduğunu görmesini sağlar.

    packaging/installer.iss aynı adı AppMutex olarak tanımlıyor; Inno Setup
    hâlâ açık olan bir exe'nin üzerine yazmak yerine böyle duruyor. Mutex'i
    kimse bırakmıyor: handle süreçle birlikte ölüyor, yani tam da kurulumun
    devam edebileceği anda.
    """
    if sys.platform != "win32":
        return
    import ctypes

    with contextlib.suppress(OSError):
        ctypes.windll.kernel32.CreateMutexW(None, False, APP_MUTEX_NAME)


# SetInformationJobObject'in beklediği sınıf numarası ve iki sınır bayrağı;
# Windows SDK'da JobObjectExtendedLimitInformation, JOB_OBJECT_LIMIT_BREAKAWAY_OK
# ve JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE.
_JOB_EXTENDED_LIMIT_INFORMATION = 9
_JOB_LIMIT_BREAKAWAY_OK = 0x00000800
_JOB_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000


def _kill_children_with_app() -> None:
    """Uygulama ölünce çocuk süreçlerini de işletim sistemine öldürtür.

    Tarama, JS ile render eden site için playwright başlatıyor; playwright de
    kendi node sürücüsünü, o da Edge'i ayrı süreçler olarak açıyor. Windows'ta
    bir süreç ölünce çocukları ölmüyor, yani temiz kapanışın kaçırıldığı her
    durumda (çökme, görev yöneticisinden sonlandırma, kapanış sırasında hâlâ
    süren bir tarama) geride yüz megabaytlarca tarayıcı kalıyor.

    Job object bunu koda değil çekirdeğe bağlıyor: handle süreçle birlikte
    kapanıyor ve KILL_ON_JOB_CLOSE o anda job'daki her şeyi sonlandırıyor.
    Handle bilerek kapatılmıyor, kimsenin tutmasına da gerek yok.

    BREAKAWAY_OK'in yanında durmasının tek sebebi güncelleme devri: updater.py
    kurulumu yapan cmd zincirini CREATE_BREAKAWAY_FROM_JOB ile başlatıyor,
    çünkü onun uygulamadan sonra yaşaması gerekiyor. O bayrak olmadan zincir
    uygulama kapanır kapanmaz ölür ve güncelleme hiç kurulmaz.
    """
    if sys.platform != "win32":
        return
    import ctypes

    class _BasicLimits(ctypes.Structure):
        _fields_ = (
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        )

    class _IoCounters(ctypes.Structure):
        _fields_ = (
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        )

    class _ExtendedLimits(ctypes.Structure):
        _fields_ = (
            ("BasicLimitInformation", _BasicLimits),
            ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        )

    kernel32 = ctypes.windll.kernel32
    # Varsayılan restype C int; 64 bitte handle'ı kırpar.
    kernel32.CreateJobObjectW.restype = ctypes.c_void_p
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p

    with contextlib.suppress(OSError):
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return
        limits = _ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = (
            _JOB_LIMIT_KILL_ON_JOB_CLOSE | _JOB_LIMIT_BREAKAWAY_OK
        )
        assigned = kernel32.SetInformationJobObject(
            ctypes.c_void_p(job),
            _JOB_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ) and kernel32.AssignProcessToJobObject(
            ctypes.c_void_p(job), ctypes.c_void_p(kernel32.GetCurrentProcess())
        )
        if not assigned:
            # Uygulamanın kendisi zaten çıkışa izin vermeyen bir job'ın içinde
            # olabilir. Burada yapılacak bir şey yok; kapanış yolu tek başına
            # da tarayıcıyı kapatıyor, bu sadece onun ağı.
            kernel32.CloseHandle(ctypes.c_void_p(job))


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
