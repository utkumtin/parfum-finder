# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Windows desktop build.

Run from the repo root: `uv run pyinstaller packaging/parfum-finder.spec`.
`ui/dist/` must already exist (`npm run build` inside `ui/`) -- this spec
packages what's already built, it doesn't build the frontend itself.

`excludes` drops textual/rich (the TUI, not part of this build) -- lazily
imported inside `cli.py`'s subcommand branches, so PyInstaller's static
analysis never reaches them from this entry point.

playwright ships because decantall's search page needs it (see
`sites/decantall.json` -> `search.strategy`). Its own PyInstaller hook
(`playwright._impl.__pyinstaller`) pulls in the Node driver automatically --
no manual `datas`/`hiddenimports` entry needed. On Windows `fetch.py` launches
it via `channel="msedge"`, the Edge build every Windows 10/11 machine already
ships, so this does not also pull in a Chromium download.
"""

from pathlib import Path

REPO_ROOT = Path(SPECPATH).resolve().parent

# (source, destination-inside-bundle). destination is resolved at runtime
# through paths.resource_dir() -- never through Path(__file__).
datas = [
    (str(REPO_ROOT / "ui" / "dist"), "ui"),
    (str(REPO_ROOT / "schema"), "schema"),
    (str(REPO_ROOT / "sites"), "sites"),
    (str(REPO_ROOT / "platforms"), "platforms"),
    (str(REPO_ROOT / "hooks"), "hooks"),
]

a = Analysis(
    [str(REPO_ROOT / "packaging" / "entrypoint.py")],
    pathex=[str(REPO_ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    excludes=["textual", "rich"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="parfum-finder",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(REPO_ROOT / "packaging" / "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="parfum-finder",
)
