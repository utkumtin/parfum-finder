"""GitHub'daki son sürümü sorar, yenisini indirir ve kurulumu devreder.

Güncellenecek tek şey paketlenmiş Windows kurulumudur: kaynaktan çalışan bir
kopya git ne diyorsa odur, bu yüzden `check_for_update` donmuş build dışında
"güncelleme yok" döner.

Burada hiçbir şey pencereye dokunmaz. API katmanı ilerlemeyi `UpdateDownload`
üzerinden okur ve kurulum başlatıldıktan sonra pencerenin kapanmasını ister:
Inno Setup, hâlâ çalışan parfum-finder.exe dosyasının üzerine yazamaz.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import httpx

from parfum_finder import __version__, paths

LATEST_RELEASE_URL = (
    "https://api.github.com/repos/utkumtin/parfum-finder/releases/latest"
)

# Kaynaktan çalışırken kontrolü yine de denemek için kaçış kapısı. Gerçek
# kullanıcı bunu hiç görmez, geliştirme sırasında diyaloğu elle açmaya yarar.
_FORCE_ENV_VAR = "PARFUM_FINDER_FORCE_UPDATE_CHECK"

_CHECK_TIMEOUT_S = 5.0
_DOWNLOAD_TIMEOUT_S = 60.0
_INSTALLER_NAME = "parfum-finder-setup.exe"
_HANDOFF_TIMEOUT_MS = 60_000
_HANDOFF_READY_TIMEOUT_MS = 5_000
_UPDATE_LOG_NAME = "parfum-finder-update.log"
_SETUP_LOG_NAME = "parfum-finder-setup.log"
_BOOTSTRAPPER_NAME = "updater-bootstrapper.exe"


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    notes: str
    release_url: str
    download_url: str | None


@dataclass(frozen=True)
class DownloadProgress:
    """state: idle | downloading | ready | installing | error."""

    state: str
    received: int = 0
    total: int = 0
    message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "received": self.received,
            "total": self.total,
            "message": self.message,
        }


def parse_version(text: str) -> tuple[int, ...] | None:
    """v0.2.1 -> (0, 2, 1). Sayıya çevrilemeyen her şey None."""
    parts = text.strip().lstrip("vV").split(".")
    if not parts or len(parts) > 4:
        return None
    numbers = []
    for part in parts:
        if not part.isdigit():
            return None
        numbers.append(int(part))
    return tuple(numbers)


def is_newer(candidate: str, current: str) -> bool:
    """Okunamayan bir sürüm asla "yeni" sayılmaz.

    Yanlış tarafa düşmenin bedeli simetrik değil: kaçırılan bir güncelleme
    kullanıcının bir sonraki açılışta göreceği bir gecikme, uydurulmuş bir
    güncelleme ise kapanmayan bir pop-up.
    """
    left, right = parse_version(candidate), parse_version(current)
    if left is None or right is None:
        return False
    width = max(len(left), len(right))
    return _pad(left, width) > _pad(right, width)


def _pad(version: tuple[int, ...], width: int) -> tuple[int, ...]:
    return version + (0,) * (width - len(version))


def check_enabled() -> bool:
    return paths.is_frozen() or os.environ.get(_FORCE_ENV_VAR) == "1"


def _installer_asset(assets: list[dict[str, Any]]) -> str | None:
    for asset in assets:
        name = str(asset.get("name") or "")
        if name.lower().endswith(".exe"):
            url = str(asset.get("browser_download_url") or "")
            if url:
                return url
    return None


def fetch_latest_release(
    *, url: str = LATEST_RELEASE_URL, timeout: float = _CHECK_TIMEOUT_S
) -> ReleaseInfo | None:
    """En son yayımlanmış sürüm, ya da ulaşılamadıysa None.

    /releases/latest taslakları ve ön sürümleri kendisi eler, /releases elemez.
    """
    try:
        response = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers={"Accept": "application/vnd.github+json"},
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    tag = str(payload.get("tag_name") or "")
    if not tag:
        return None
    assets = payload.get("assets")
    return ReleaseInfo(
        version=tag,
        notes=str(payload.get("body") or "").strip(),
        release_url=str(payload.get("html_url") or ""),
        download_url=_installer_asset(assets if isinstance(assets, list) else []),
    )


def check_for_update(
    *,
    current: str = __version__,
    fetch: Callable[[], ReleaseInfo | None] = fetch_latest_release,
) -> dict[str, Any]:
    if not check_enabled():
        return _no_update(current)
    release = fetch()
    if release is None or not is_newer(release.version, current):
        return _no_update(current)
    return {
        "current_version": current,
        "latest_version": release.version.lstrip("vV"),
        "update_available": True,
        "notes": release.notes,
        "release_url": release.release_url,
        "download_url": release.download_url,
    }


def _no_update(current: str) -> dict[str, Any]:
    return {
        "current_version": current,
        "latest_version": None,
        "update_available": False,
        "notes": "",
        "release_url": "",
        "download_url": None,
    }


class UpdateHandoffError(RuntimeError):
    """The native helper could not take responsibility for an update."""


def _kernel32() -> Any:
    import ctypes

    loader_name = "WinDLL"
    return getattr(ctypes, loader_name)("kernel32", use_last_error=True)


def _windows_creation_flag(name: str) -> int:
    return int(getattr(subprocess, name))


def handoff_command(
    installer: Path,
    *,
    helper: Path,
    ready_event: str,
    parent_pid: int | None = None,
    log_path: Path | None = None,
) -> list[str]:
    """Build the native helper command without involving a command shell."""
    pid = os.getpid() if parent_pid is None else parent_pid
    log = (
        Path(tempfile.gettempdir()) / _UPDATE_LOG_NAME if log_path is None else log_path
    )
    return [
        str(helper),
        "--parent-pid",
        str(pid),
        "--installer",
        str(installer),
        "--ready-event",
        ready_event,
        "--log",
        str(log),
        "--setup-log",
        str(log.with_name(_SETUP_LOG_NAME)),
    ]


def _copy_bootstrapper() -> Path:
    resource_dir = paths.resource_dir()
    source = resource_dir / _BOOTSTRAPPER_NAME
    if not source.is_file() and not paths.is_frozen():
        source = resource_dir / "packaging" / _BOOTSTRAPPER_NAME
    if not source.is_file():
        raise UpdateHandoffError("güncelleme yardımcısı bulunamadı")
    destination = Path(tempfile.gettempdir()) / (
        f"parfum-finder-updater-{uuid.uuid4().hex}.exe"
    )
    try:
        shutil.copy2(source, destination)
    except OSError as exc:
        raise UpdateHandoffError("güncelleme yardımcısı kopyalanamadı") from exc
    return destination


def _create_ready_event(name: str) -> int:
    if sys.platform != "win32":
        raise UpdateHandoffError("güncelleme yalnızca Windows'ta kullanılabilir")
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
        raise UpdateHandoffError("güncelleme yardımcısı için olay oluşturulamadı")
    return int(handle)


def _wait_for_ready(handle: int, timeout_ms: int) -> bool:
    import ctypes

    kernel32 = _kernel32()
    kernel32.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    kernel32.WaitForSingleObject.restype = ctypes.c_uint32
    result = kernel32.WaitForSingleObject(handle, timeout_ms)
    return result == 0


def _close_handle(handle: int) -> None:
    import ctypes

    kernel32 = _kernel32()
    kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel32.CloseHandle(handle)


def launch_installer(
    installer: Path,
    *,
    ready_timeout_ms: int = _HANDOFF_READY_TIMEOUT_MS,
    helper: Path | None = None,
    parent_pid: int | None = None,
    ready_event: str | None = None,
    log_path: Path | None = None,
) -> None:
    helper_path = _copy_bootstrapper() if helper is None else helper
    event_name = (
        f"Local\\parfum-finder-update-{uuid.uuid4().hex}"
        if ready_event is None
        else ready_event
    )
    event_handle = _create_ready_event(event_name)
    command = handoff_command(
        installer,
        helper=helper_path,
        ready_event=event_name,
        parent_pid=parent_pid,
        log_path=log_path,
    )
    try:
        # The helper must leave the GUI job before that job is closed.
        creationflags = (
            _windows_creation_flag("DETACHED_PROCESS")
            | _windows_creation_flag("CREATE_NEW_PROCESS_GROUP")
            | _windows_creation_flag("CREATE_BREAKAWAY_FROM_JOB")
        )
        subprocess.Popen(command, creationflags=creationflags, close_fds=True)  # noqa: S603
        if not _wait_for_ready(event_handle, ready_timeout_ms):
            raise UpdateHandoffError("güncelleme yardımcısı zamanında başlamadı")
    except OSError as exc:
        raise UpdateHandoffError("güncelleme yardımcısı başlatılamadı") from exc
    finally:
        _close_handle(event_handle)


class UpdateDownload:
    """Kurulum dosyasının tek bir arka plan indirmesi ve devri.

    Süreç başına bir tane: indirme sürerken gelen ikinci bir start() sıraya
    alınmaz, reddedilir. Tek çağıran, tek penceredeki tek düğme.
    """

    def __init__(
        self,
        *,
        dest_dir: Path | None = None,
        client_factory: Callable[..., httpx.Client] = httpx.Client,
        spawn: Callable[[Path], None] = launch_installer,
    ) -> None:
        self._lock = threading.Lock()
        self._progress = DownloadProgress(state="idle")
        self._path: Path | None = None
        self._dest_dir = dest_dir
        self._client_factory = client_factory
        self._spawn = spawn

    def progress(self) -> DownloadProgress:
        with self._lock:
            return self._progress

    def start(self, url: str) -> DownloadProgress | None:
        """İndirmeyi başlatır. Zaten çalışıyorsa None."""
        with self._lock:
            if self._progress.state in ("downloading", "installing"):
                return None
            self._progress = DownloadProgress(state="downloading")
            self._path = None
            started = self._progress
        threading.Thread(target=self._run, args=(url,), daemon=True).start()
        return started

    def install(self) -> bool:
        """İnen kurulumu başlatır. Hazır değilse False."""
        with self._lock:
            if self._progress.state != "ready" or self._path is None:
                return False
            path = self._path
            self._progress = replace(self._progress, state="installing")
        try:
            self._spawn(path)
        except (OSError, UpdateHandoffError) as exc:
            with self._lock:
                self._progress = replace(
                    self._progress, state="error", message=str(exc)
                )
            return False
        return True

    def _set(self, progress: DownloadProgress) -> None:
        with self._lock:
            self._progress = progress

    def _target_path(self) -> Path:
        base = (
            self._dest_dir
            if self._dest_dir is not None
            else Path(tempfile.gettempdir())
        )
        base.mkdir(parents=True, exist_ok=True)
        return base / _INSTALLER_NAME

    def _run(self, url: str) -> None:
        try:
            target = self._target_path()
            received = 0
            total = 0
            with self._client_factory(
                timeout=_DOWNLOAD_TIMEOUT_S, follow_redirects=True
            ) as client:
                with client.stream("GET", url) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("Content-Length") or 0)
                    with target.open("wb") as handle:
                        for chunk in response.iter_bytes():
                            handle.write(chunk)
                            received += len(chunk)
                            self._set(DownloadProgress("downloading", received, total))
        except Exception as exc:  # noqa: BLE001
            # İndirme sırasında ne patlarsa patlasın kullanıcı bunu diyalogda
            # görmeli: sessizce "idle"a dönmek, düğmenin çalışmadığı izlenimi
            # veren tek sonuç.
            self._set(DownloadProgress("error", message=str(exc)))
            return
        with self._lock:
            self._path = target
            self._progress = DownloadProgress("ready", received, total or received)
