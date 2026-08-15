"""Yol çözümü. Donmuş (PyInstaller) ve kaynaktan çalıştırma için tek yer."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_NAME = "parfum-finder"


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def resource_dir() -> Path:
    """Salt-okunur, uygulamayla birlikte gelen veri. Örnek: schema/, ui dist/."""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent.parent


def user_data_dir() -> Path:
    """Kullanıcının düzenleyebildiği ve yazılabilir veri. Kurulum dizinine yazmayız."""
    if is_frozen():
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
        return base / APP_NAME
    return Path(__file__).resolve().parent.parent.parent


def sites_dir() -> Path:
    return user_data_dir() / "sites"


def platforms_dir() -> Path:
    return user_data_dir() / "platforms"


def hooks_dir() -> Path:
    return user_data_dir() / "hooks"


def fixtures_dir() -> Path:
    return resource_dir() / "fixtures"


def schema_dir() -> Path:
    return resource_dir() / "schema"


def ui_dir() -> Path:
    """Built frontend (index.html + assets/), served by the backend at "/".

    The PyInstaller spec maps `ui/dist/` to `ui/` inside the bundle, so a
    frozen build's assets sit one level up from where they live in a source
    checkout.
    """
    if is_frozen():
        return resource_dir() / "ui"
    return resource_dir() / "ui" / "dist"


def default_db_path() -> Path:
    return user_data_dir() / "parfum-finder.db"


def default_log_path() -> Path:
    return user_data_dir() / "parfum-finder.log"


def ensure_user_data(seeded: bool = True) -> None:
    """Bundle'daki varsayılan profilleri kullanıcı dizinine kopyalar.
    Var olan dosyanın üstüne asla yazmaz, kullanıcının düzenlemesini korur."""
    if not seeded or not is_frozen():
        return
    user_data_dir().mkdir(parents=True, exist_ok=True)
    for name, dest in (
        ("sites", sites_dir()),
        ("platforms", platforms_dir()),
        ("hooks", hooks_dir()),
    ):
        src = resource_dir() / name
        if not src.is_dir():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target = dest / item.name
            if target.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
