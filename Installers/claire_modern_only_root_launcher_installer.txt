#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

INSTALLER_NAME = "Claire Modern-Only Root Launcher Installer"
INSTALLER_VERSION = "11.42"
DEFAULT_TARGET = Path.home() / "OneDrive" / "Desktop" / "Claire"

LAUNCHER_CONTENT = '@echo off\nsetlocal EnableExtensions\n\nREM ============================================================\nREM Claire Modern Root Launcher\nREM File: LAUNCH_CLAIRE.bat\nREM Purpose:\nREM   One clean root launcher.\nREM   Opens the modern dashboard only.\nREM   Does NOT call tools\\portable_launcher.py --live --app because that can\nREM   open the old dashboard shell.\nREM ============================================================\n\ncd /d "%~dp0"\n\nset "CLAIRE_ROOT=%~dp0"\nset "CLAIRE_APP_SHELL=0"\nset "CLAIRE_LAUNCH_MODE=modern_dashboard_root"\nset "CLAIRE_DASHBOARD_PATH=src\\frontend\\command_center\\modern\\index.html"\nset "CLAIRE_LOG_DIR=logs"\n\nif not exist "%CLAIRE_LOG_DIR%" mkdir "%CLAIRE_LOG_DIR%"\n\necho.\necho ============================================================\necho Claire Syntalion - Modern Dashboard Root Launcher\necho Root: %CLAIRE_ROOT%\necho ============================================================\necho.\n\nif exist ".venv\\Scripts\\python.exe" (\n    set "CLAIRE_PYTHON=.venv\\Scripts\\python.exe"\n) else (\n    set "CLAIRE_PYTHON=python"\n)\n\necho Using Python: %CLAIRE_PYTHON%\necho.\n\nREM Sync dashboard/version state if available.\nif exist "tools\\desktop_version_sync.py" (\n    echo Syncing desktop/version state...\n    "%CLAIRE_PYTHON%" "tools\\desktop_version_sync.py" --root "%CLAIRE_ROOT%" --mode modern_dashboard_root > "%CLAIRE_LOG_DIR%\\desktop_version_sync.out.log" 2> "%CLAIRE_LOG_DIR%\\desktop_version_sync.err.log"\n)\n\nREM Open modern dashboard only.\nif exist "%CLAIRE_DASHBOARD_PATH%" (\n    echo Opening modern dashboard:\n    echo   %CLAIRE_DASHBOARD_PATH%\n    echo.\n    start "" "%CLAIRE_DASHBOARD_PATH%"\n    goto :done\n)\n\necho.\necho [Claire Launcher Error]\necho Modern dashboard not found:\necho   %CLAIRE_DASHBOARD_PATH%\necho.\necho Run the modern dashboard installer first:\necho   python claire_modern_dashboard_web_ui_installer.py --install\necho.\npause\n\n:done\necho.\necho Modern dashboard launch complete.\nendlocal\n'

OLD_LAUNCHERS = [
    "START_CLAIRE.bat",
    "START_CLAIRE_DESKTOP.bat",
    "START_CLAIRE_LIVE.bat",
    "START_CLAIRE_LIVE_SAFE.bat",
    "START_CLAIRE_PORTABLE.bat",
    "START_CLAIRE_PORTABLE_SAFE.bat",
]

def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def main():
    p = argparse.ArgumentParser(description=INSTALLER_NAME)
    p.add_argument("--target", default=str(DEFAULT_TARGET))
    p.add_argument("--install", action="store_true")
    p.add_argument("--archive-old-launchers", action="store_true", help="Move old START_CLAIRE*.bat files into backups/old_launchers")
    args = p.parse_args()

    root = Path(args.target).expanduser().resolve()
    install = bool(args.install)

    print(f"{INSTALLER_NAME} {INSTALLER_VERSION}")
    print(f"Target: {root}")
    print("Mode:", "INSTALL" if install else "DRY RUN")

    if not root.exists():
        print(f"[ERROR] Target does not exist: {root}")
        return 2

    actions = []
    launcher_path = root / "LAUNCH_CLAIRE.bat"

    if install:
        backup = None
        if launcher_path.exists():
            backup_path = launcher_path.with_name(launcher_path.name + ".bak_" + stamp())
            shutil.copy2(launcher_path, backup_path)
            backup = str(backup_path)

        launcher_path.write_text(LAUNCHER_CONTENT, encoding="utf-8", newline="\r\n")
        actions.append({"action": "write_modern_only_root_launcher", "path": str(launcher_path), "backup": backup})

        if args.archive_old_launchers:
            archive_dir = root / "backups" / "old_launchers" / stamp()
            archive_dir.mkdir(parents=True, exist_ok=True)
            for name in OLD_LAUNCHERS:
                pth = root / name
                if pth.exists():
                    dest = archive_dir / name
                    shutil.move(str(pth), str(dest))
                    actions.append({"action": "archive_old_launcher", "from": str(pth), "to": str(dest)})

        report_dir = root / ".claire_install" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "installer": INSTALLER_NAME,
            "installer_version": INSTALLER_VERSION,
            "installed_at_utc": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "launcher": "LAUNCH_CLAIRE.bat",
            "modern_dashboard_only": True,
            "does_not_call_portable_launcher": True,
            "old_launcher_archive_requested": bool(args.archive_old_launchers),
            "actions": actions,
            "safety_contract": {
                "does_not_modify_runtime": True,
                "does_not_modify_scoring": True,
                "does_not_modify_routing": True,
                "opens_only_modern_dashboard": True
            }
        }
        report_path = report_dir / ("modern_only_root_launcher_" + stamp() + ".json")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[OK] Updated: {launcher_path}")
        print(f"[OK] Report: {report_path}")
    else:
        print("[DRY RUN] No files changed.")
        print(f"Would update: {launcher_path}")

    print()
    print("Use this command after install:")
    print("  LAUNCH_CLAIRE.bat")
    print()
    print("To also move old START_CLAIRE*.bat files out of the root:")
    print("  python claire_modern_only_root_launcher_installer.py --install --archive-old-launchers")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
