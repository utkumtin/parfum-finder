; Inno Setup script for parfum-finder.
;
; Compiled by the Windows CI job (.github/workflows/build-windows.yml) after
; PyInstaller has produced dist\parfum-finder\. Local build:
;   ISCC.exe packaging\installer.iss
; (run from the repo root, so the relative ..\dist\ path below resolves).

#define MyAppName "parfum-finder"
; Sürüm CI'dan geliyor: ISCC /DMyAppVersion=0.2.0. Buradaki yedek yalnızca
; elle derlemeler için, tek doğru kaynak src/parfum_finder/__init__.py.
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppExeName "parfum-finder.exe"

[Setup]
AppId={{2F6C3B9E-6C9E-4C9F-9E1A-8D0B5E9F4A2E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Utku Metin
VersionInfoVersion={#MyAppVersion}
; Uygulama açıkken kurulum yapılmasını engeller: gui.py aynı adlı mutex'i
; açılışta oluşturuyor, kurulum da onu görünce üzerine yazmadan duruyor.
AppMutex=parfum-finder-running
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
SetupIconFile=icon.ico
; No admin prompt and no Program Files write: the install lives entirely
; under the current user's own LOCALAPPDATA, matching where the app itself
; keeps its writable data (see paths.user_data_dir()).
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=parfum-finder-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\parfum-finder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
