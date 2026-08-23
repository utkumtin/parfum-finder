"""GitHub'daki son sürümü sorar, yenisini indirir ve kurulumu devreder.

Güncellenecek tek şey paketlenmiş Windows kurulumudur: kaynaktan çalışan bir
kopya git ne diyorsa odur, bu yüzden `check_for_update` donmuş build dışında
"güncelleme yok" döner.

Burada hiçbir şey pencereye dokunmaz. API katmanı ilerlemeyi `UpdateDownload`
üzerinden okur ve kurulum başlatıldıktan sonra pencerenin kapanmasını ister:
Inno Setup, hâlâ çalışan parfum-finder.exe dosyasının üzerine yazamaz.
"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
import tempfile
import threading
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
_UPDATE_LOG_NAME = "parfum-finder-update.log"


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


def _powershell_literal(value: Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def handoff_command(
    installer: Path,
    app_exe: Path,
    *,
    parent_pid: int | None = None,
    log_path: Path | None = None,
) -> list[str]:
    """Uygulamanın kapanmasını bekleyen ayrık PowerShell komutu."""
    pid = os.getpid() if parent_pid is None else parent_pid
    log = (
        Path(tempfile.gettempdir()) / _UPDATE_LOG_NAME if log_path is None else log_path
    )
    script = f"""
$ErrorActionPreference = 'Stop'
$installer = {_powershell_literal(installer)}
$app = {_powershell_literal(app_exe)}
$logPath = {_powershell_literal(log)}
try {{
    $parent = Get-Process -Id {pid} -ErrorAction SilentlyContinue
    if ($null -ne $parent -and -not $parent.WaitForExit({_HANDOFF_TIMEOUT_MS})) {{
        $message = 'handoff error: app did not exit in time'
        Add-Content -LiteralPath $logPath -Value $message
        exit 1
    }}
    $setupArgs = '/SILENT /NORESTART /SUPPRESSMSGBOXES /LOG="' + $logPath + '"'
    $setup = Start-Process -FilePath $installer -ArgumentList $setupArgs -Wait -PassThru
    if ($setup.ExitCode -ne 0) {{
        $message = 'handoff error: installer exit code ' + $setup.ExitCode
        Add-Content -LiteralPath $logPath -Value $message
        exit $setup.ExitCode
    }}
    Start-Process -FilePath $app
}} catch {{
    Add-Content -LiteralPath $logPath -Value ('handoff error: ' + $_.Exception.Message)
    exit 1
}}
""".strip()
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    return [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle",
        "Hidden",
        "-EncodedCommand",
        encoded,
    ]


def launch_installer(installer: Path, *, app_exe: Path | None = None) -> None:
    command = handoff_command(
        installer, app_exe if app_exe is not None else Path(sys.executable)
    )
    creationflags = 0
    if sys.platform == "win32":
        # CREATE_BREAKAWAY_FROM_JOB, gui.py'nin kurduğu job object yüzünden
        # şart: o job kapanırken içindeki her şeyi öldürüyor ve bu zincir tam
        # da uygulama kapandıktan sonra çalışmak üzere var. DETACHED_PROCESS
        # tek başına job'dan çıkarmaz, sadece konsoldan ayırır.
        creationflags = (
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_BREAKAWAY_FROM_JOB
        )
    subprocess.Popen(command, creationflags=creationflags, close_fds=True)  # noqa: S603


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
        self._spawn(path)
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
