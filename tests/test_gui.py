"""Tests for parfum_finder.gui: the desktop entry point's headless path.

`run_window()` opens a native WebView2/GTK window, which has nothing useful
to assert against under pytest. `run_selftest()` is the path this module is
actually exercised through outside a human at a Windows machine -- it's also
what the Windows CI smoke test runs against the frozen exe -- so it's what
gets a real test: a passing run is what proves ensure_user_data(), the
ephemeral-port bind, and the backend boot all still work together.
"""

from __future__ import annotations

import threading
from pathlib import Path

from parfum_finder.gui import _close_window_when_asked, run_selftest


def test_selftest_boots_the_backend_and_exits_zero(tmp_path: Path) -> None:
    sites_dir = tmp_path / "sites"
    sites_dir.mkdir()
    db_path = tmp_path / "db.sqlite3"

    assert run_selftest(sites_dir=sites_dir, db_path=db_path) == 0


def _run_watcher(
    quit_requested: threading.Event, window_closed: threading.Event
) -> tuple[threading.Thread, list[bool]]:
    destroyed: list[bool] = []
    thread = threading.Thread(
        target=lambda: _close_window_when_asked(
            quit_requested, window_closed, lambda: destroyed.append(True)
        )
    )
    thread.start()
    return thread, destroyed


def test_the_quit_watcher_ends_when_the_window_closes() -> None:
    """Bunu beklemeyen bir izleyici, uygulamayı kapanmaktan alıkoyar.

    pywebview bu işlevi kendi açtığı ve daemon olarak işaretlemediği bir
    thread'de çalıştırıyor. Olağan kapanışta (kimse güncelleme başlatmadan
    pencereyi kapattığında) quit_requested hiç kurulmuyor; izleyici orada
    beklemeye devam ederse yorumlayıcı çıkarken onu join ediyor ve süreç
    görev yöneticisinde kalmaya devam ediyor.
    """
    window_closed = threading.Event()
    thread, destroyed = _run_watcher(threading.Event(), window_closed)

    window_closed.set()
    thread.join(timeout=5)

    assert not thread.is_alive()
    assert destroyed == []


def test_the_quit_watcher_closes_the_window_when_the_backend_asks() -> None:
    # Güncelleme devredildikten sonra pencereyi kapatmanın tek yolu bu.
    quit_requested = threading.Event()
    thread, destroyed = _run_watcher(quit_requested, threading.Event())

    quit_requested.set()
    thread.join(timeout=5)

    assert not thread.is_alive()
    assert destroyed == [True]
