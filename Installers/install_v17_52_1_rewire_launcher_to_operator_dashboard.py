#!/usr/bin/env python3
"""
Claire Syntalion v17.52.1 — Rewire Launcher to Modern Operator Dashboard

Single-file installer.
Run from the project root.

This updates LAUNCH_CLAIRE.bat so the launcher opens:
  src\frontend\command_center\modern\index.html

It also creates a backup of the existing launcher.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import shutil


ROOT = Path.cwd()
VERSION = "v17.52.1"
DASHBOARD_PATH = Path("src") / "frontend" / "command_center" / "modern" / "index.html"
LAUNCHER = ROOT / "LAUNCH_CLAIRE.bat"
BACKUP_DIR = ROOT / "backups" / "v17_52_1_launcher_rewire"
MANIFEST_DIR = ROOT / "manifests"
TESTS_DIR = ROOT / "tests"


LAUNCHER_CONTENT = """@echo off
setlocal EnableExtensions

REM ============================================================
REM Claire Root Launcher
REM Version: 17.52.1
REM Active Dashboard: src\\frontend\\command_center\\modern\\index.html
REM Purpose:
REM   Opens the modern Claire Operator Dashboard.
REM   Uses the v17.52 dashboard as the primary launcher surface.
REM   Does not open old build-layer shells.
REM ============================================================

cd /d "%~dp0"

set "CLAIRE_ROOT=%~dp0"
set "CLAIRE_APP_SHELL=0"
set "CLAIRE_LAUNCH_MODE=modern_operator_dashboard"
set "CLAIRE_DASHBOARD_PATH=src\\frontend\\command_center\\modern\\index.html"
set "CLAIRE_LOG_DIR=logs"

if not exist "%CLAIRE_LOG_DIR%" mkdir "%CLAIRE_LOG_DIR%"

echo.
echo ============================================================
echo Claire Syntalion - Root Launcher v17.52.1
echo Root: %CLAIRE_ROOT%
echo Dashboard: %CLAIRE_DASHBOARD_PATH%
echo ============================================================
echo.

if exist ".venv\\Scripts\\python.exe" (
    set "CLAIRE_PYTHON=.venv\\Scripts\\python.exe"
) else (
    set "CLAIRE_PYTHON=python"
)

echo Using Python: %CLAIRE_PYTHON%
echo.

if exist "tools\\desktop_version_sync.py" (
    echo Syncing desktop/version state...
    "%CLAIRE_PYTHON%" "tools\\desktop_version_sync.py" --root "%CLAIRE_ROOT%" --mode modern_operator_dashboard > "%CLAIRE_LOG_DIR%\\desktop_version_sync.out.log" 2> "%CLAIRE_LOG_DIR%\\desktop_version_sync.err.log"
)

if exist "%CLAIRE_DASHBOARD_PATH%" (
    echo Opening modern Claire Operator Dashboard...
    start "" "%CLAIRE_DASHBOARD_PATH%"
    goto :done
)

echo.
echo [Claire Launcher Error]
echo Modern Operator Dashboard not found:
echo   %CLAIRE_DASHBOARD_PATH%
echo.
echo Expected file:
echo   src\\frontend\\command_center\\modern\\index.html
echo.
echo Install or rerun:
echo   python .\\install_v17_52_modern_operator_dashboard.py
echo.
pause

:done
echo.
echo Claire Operator Dashboard launch complete.
endlocal
"""


TEST_CONTENT = """from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v17_52_1_launcher_points_to_operator_dashboard():
    launcher = ROOT / "LAUNCH_CLAIRE.bat"
    assert launcher.exists()
    text = launcher.read_text(encoding="utf-8")
    assert "Version: 17.52.1" in text
    assert "modern_operator_dashboard" in text
    assert "src\\\\frontend\\\\command_center\\\\modern\\\\index.html" in text or "src\\frontend\\command_center\\modern\\index.html" in text
    assert "Opening modern Claire Operator Dashboard" in text


def test_v17_52_1_operator_dashboard_exists():
    dashboard = ROOT / "src" / "frontend" / "command_center" / "modern" / "index.html"
    assert dashboard.exists()
    text = dashboard.read_text(encoding="utf-8")
    assert "Claire Syntalion Operator Dashboard" in text
    assert "Modern Operator Dashboard" in text
"""


def main() -> None:
    dashboard = ROOT / DASHBOARD_PATH
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)

    if LAUNCHER.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(LAUNCHER, BACKUP_DIR / f"LAUNCH_CLAIRE_{timestamp}.bat")

    LAUNCHER.write_text(LAUNCHER_CONTENT, encoding="utf-8", newline="\r\n")
    (TESTS_DIR / "test_v17_52_1_launcher_rewire.py").write_text(TEST_CONTENT, encoding="utf-8", newline="\n")

    manifest = {
        "version": VERSION,
        "name": "Rewire Launcher to Modern Operator Dashboard",
        "active_dashboard": str(DASHBOARD_PATH),
        "launcher": "LAUNCH_CLAIRE.bat",
        "backup_dir": str(BACKUP_DIR.relative_to(ROOT)),
        "dashboard_exists_at_install": dashboard.exists(),
        "purpose": "Make the user's normal launcher open the new v17.52 operator dashboard directly.",
    }
    (MANIFEST_DIR / "v17_52_1_launcher_rewire.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("v17.52.1 launcher rewire installed.")
    print("Launcher now opens:", DASHBOARD_PATH)
    if dashboard.exists():
        print("Dashboard file found.")
    else:
        print("WARNING: Dashboard file not found. Rerun v17.52 installer first.")
    print("Run:")
    print("  python -m pytest tests\\test_v17_52_1_launcher_rewire.py")


if __name__ == "__main__":
    main()
