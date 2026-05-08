#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

INSTALLER_NAME = "Claire Consolidation, Version Lock, and Cleanup Installer"
INSTALLER_VERSION = "11.42-consolidation"
LOCK_VERSION = "11.42"
DEFAULT_TARGET = Path.home() / "OneDrive" / "Desktop" / "Claire"

ROOT_LAUNCHER = "@echo off\nsetlocal EnableExtensions\n\nREM ============================================================\nREM Claire Root Launcher\nREM Version: 11.42\nREM Active Dashboard: src\\frontend\\command_center\\modern\\index.html\nREM Purpose:\nREM   One clean project-root launcher.\nREM   Opens modern command center only.\nREM   Does not call old dashboard shell.\nREM ============================================================\n\ncd /d \"%~dp0\"\n\nset \"CLAIRE_ROOT=%~dp0\"\nset \"CLAIRE_APP_SHELL=0\"\nset \"CLAIRE_LAUNCH_MODE=modern_dashboard_root\"\nset \"CLAIRE_DASHBOARD_PATH=src\\frontend\\command_center\\modern\\index.html\"\nset \"CLAIRE_LOG_DIR=logs\"\n\nif not exist \"%CLAIRE_LOG_DIR%\" mkdir \"%CLAIRE_LOG_DIR%\"\n\necho.\necho ============================================================\necho Claire Syntalion - Root Launcher v11.42\necho Root: %CLAIRE_ROOT%\necho Dashboard: %CLAIRE_DASHBOARD_PATH%\necho ============================================================\necho.\n\nif exist \".venv\\Scripts\\python.exe\" (\n    set \"CLAIRE_PYTHON=.venv\\Scripts\\python.exe\"\n) else (\n    set \"CLAIRE_PYTHON=python\"\n)\n\necho Using Python: %CLAIRE_PYTHON%\necho.\n\nif exist \"tools\\desktop_version_sync.py\" (\n    echo Syncing desktop/version state...\n    \"%CLAIRE_PYTHON%\" \"tools\\desktop_version_sync.py\" --root \"%CLAIRE_ROOT%\" --mode consolidated_root > \"%CLAIRE_LOG_DIR%\\desktop_version_sync.out.log\" 2> \"%CLAIRE_LOG_DIR%\\desktop_version_sync.err.log\"\n)\n\nif exist \"%CLAIRE_DASHBOARD_PATH%\" (\n    echo Opening modern Claire dashboard...\n    start \"\" \"%CLAIRE_DASHBOARD_PATH%\"\n    goto :done\n)\n\necho.\necho [Claire Launcher Error]\necho Modern dashboard not found:\necho   %CLAIRE_DASHBOARD_PATH%\necho.\necho Install the modern dashboard package first, or verify this folder exists:\necho   src\\frontend\\command_center\\modern\necho.\npause\n\n:done\necho.\necho Claire modern dashboard launch complete.\nendlocal\n"
README_TEXT = "# Claire v11.42 Consolidation Lock\n\n## Active launcher\n\nUse only:\n\n```bat\nLAUNCH_CLAIRE.bat\n```\n\n## Active dashboard\n\n```text\nsrc/frontend/command_center/modern/index.html\n```\n\n## Archived launchers\n\nLegacy launchers are moved to:\n\n```text\nbackups/legacy_launchers/<timestamp>/\n```\n\n## Version state\n\n```text\n.claire_version\nversion_11_42_locked.json\n```\n\n## Safety\n\nThis consolidation pass does not modify runtime, lifecycle routing, scoring, live permissions, or `core_run_output.json`.\n\n## Resume later from\n\n- operational evidence accumulation\n- data readiness improvement\n- benchmark/replay validation\n- telemetry accumulation\n- governance hardening\n- controlled pilot operations\n"

OLD_LAUNCHERS = [
    "START_CLAIRE.bat",
    "START_CLAIRE_DESKTOP.bat",
    "START_CLAIRE_LIVE.bat",
    "START_CLAIRE_LIVE_SAFE.bat",
    "START_CLAIRE_PORTABLE.bat",
    "START_CLAIRE_PORTABLE_SAFE.bat",
    "LAUNCH_CLAIRE_MODERN_ONLY.bat",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def ensure_dir(path: Path, install: bool, actions: List[Dict[str, Any]]) -> None:
    existed = path.exists()
    if install:
        path.mkdir(parents=True, exist_ok=True)
    actions.append({"action": "ensure_dir", "path": str(path), "installed": install, "existed": existed})

def write_text(path: Path, text: str, install: bool, actions: List[Dict[str, Any]], newline: str = "\n") -> None:
    existed = path.exists()
    backup = None
    if install:
        path.parent.mkdir(parents=True, exist_ok=True)
        if existed:
            backup_path = path.with_name(path.name + ".bak_" + stamp())
            shutil.copy2(path, backup_path)
            backup = str(backup_path)
        path.write_text(text, encoding="utf-8", newline=newline)
    actions.append({"action": "write_text", "path": str(path), "installed": install, "existed": existed, "backup": backup})

def write_json(path: Path, payload: Dict[str, Any], install: bool, actions: List[Dict[str, Any]]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True), install, actions)

def archive_file(src: Path, dest_dir: Path, install: bool, actions: List[Dict[str, Any]]) -> None:
    if not src.exists():
        actions.append({"action": "archive_file", "path": str(src), "installed": False, "reason": "missing"})
        return

    dest = dest_dir / src.name
    if install:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest = dest_dir / (src.stem + "_" + stamp() + src.suffix)
        shutil.move(str(src), str(dest))

    actions.append({"action": "archive_file", "from": str(src), "to": str(dest), "installed": install})

def build_version_lock() -> Dict[str, Any]:
    return {
        "version": LOCK_VERSION,
        "state": "locked",
        "phase": "operational_maturity",
        "locked_at_utc": now_iso(),
        "dashboard": "modern_command_center",
        "launcher": "LAUNCH_CLAIRE.bat",
        "frontend": "src/frontend/command_center/modern",
        "runtime_entry": "main.py",
        "status": "stable_checkpoint",
        "notes": [
            "single root launcher consolidation complete",
            "modern dashboard active",
            "legacy launchers archived",
            "governance-first maturity phase active",
            "runtime, routing, scoring, and core_run_output.json intentionally untouched"
        ],
        "active_paths": {
            "root_launcher": "LAUNCH_CLAIRE.bat",
            "modern_dashboard": "src/frontend/command_center/modern/index.html",
            "dashboard_css": "src/frontend/command_center/modern/modern_dashboard.css",
            "dashboard_js": "src/frontend/command_center/modern/modern_dashboard.js",
            "dashboard_guide": "docs/dashboard/modern_dashboard_use_guide.md",
            "version_file": ".claire_version",
            "version_lock": "version_11_42_locked.json"
        },
        "safety_contract": {
            "does_not_modify_runtime": True,
            "does_not_modify_routing": True,
            "does_not_modify_scoring": True,
            "does_not_modify_core_run_output": True,
            "archives_legacy_launchers_instead_of_deleting": True,
            "single_active_launcher": True
        }
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=INSTALLER_NAME)
    parser.add_argument("--target", default=str(DEFAULT_TARGET), help="Claire project root")
    parser.add_argument("--install", action="store_true", help="Apply changes. Without this, dry run only.")
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    install = bool(args.install)

    print(f"{INSTALLER_NAME} {INSTALLER_VERSION}")
    print(f"Target: {root}")
    print("Mode:", "INSTALL" if install else "DRY RUN")

    if not root.exists():
        print(f"[ERROR] Target does not exist: {root}")
        return 2

    sanity = {
        "root_exists": root.exists(),
        "main_py_exists": (root / "main.py").exists(),
        "src_exists": (root / "src").exists(),
        "modern_dashboard_exists": (root / "src" / "frontend" / "command_center" / "modern" / "index.html").exists(),
        "current_root_launcher_exists": (root / "LAUNCH_CLAIRE.bat").exists()
    }

    if not sanity["main_py_exists"] and not sanity["src_exists"]:
        print("[ERROR] This does not look like the Claire project root.")
        return 3

    actions: List[Dict[str, Any]] = []
    archive_dir = root / "backups" / "legacy_launchers" / stamp()

    for rel in ["backups/legacy_launchers", "docs/consolidation", "data/consolidation", ".claire_install/reports", "logs"]:
        ensure_dir(root / rel, install, actions)

    for name in OLD_LAUNCHERS:
        archive_file(root / name, archive_dir, install, actions)

    write_text(root / "LAUNCH_CLAIRE.bat", ROOT_LAUNCHER, install, actions, newline="\r\n")
    write_text(root / ".claire_version", LOCK_VERSION + "\n", install, actions)

    version_lock = build_version_lock()
    write_json(root / "version_11_42_locked.json", version_lock, install, actions)
    write_text(root / "docs" / "consolidation" / "v11_42_consolidation_lock.md", README_TEXT, install, actions)

    consolidation_state = {
        "status": "stable_checkpoint",
        "version": LOCK_VERSION,
        "phase": "operational_maturity",
        "created_at_utc": now_iso(),
        "active_launcher": "LAUNCH_CLAIRE.bat",
        "active_dashboard": "src/frontend/command_center/modern/index.html",
        "legacy_launcher_archive": str(archive_dir),
        "sanity": sanity,
        "resume_focus": [
            "operational evidence accumulation",
            "data readiness improvement",
            "benchmark replay validation",
            "telemetry accumulation",
            "governance hardening",
            "controlled pilot operations"
        ]
    }
    write_json(root / "data" / "consolidation" / "v11_42_consolidation_state.json", consolidation_state, install, actions)

    report = {
        "installer": INSTALLER_NAME,
        "installer_version": INSTALLER_VERSION,
        "installed": install,
        "installed_at_utc": now_iso(),
        "target": str(root),
        "sanity": sanity,
        "actions": actions,
        "final_active_files": [
            "LAUNCH_CLAIRE.bat",
            ".claire_version",
            "version_11_42_locked.json",
            "src/frontend/command_center/modern/index.html",
            "docs/consolidation/v11_42_consolidation_lock.md",
            "data/consolidation/v11_42_consolidation_state.json"
        ],
        "post_install_checks": [
            "Double-click LAUNCH_CLAIRE.bat from the project root.",
            "Confirm the modern dashboard opens.",
            "Confirm old START_CLAIRE*.bat launchers are no longer in the root.",
            "Run pytest later when rested."
        ],
        "safety_contract": version_lock["safety_contract"]
    }

    if install:
        report_path = root / ".claire_install" / "reports" / ("v11_42_consolidation_cleanup_" + stamp() + ".json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[OK] Consolidation report written: {report_path}")
        print("[OK] Active launcher: LAUNCH_CLAIRE.bat")
        print("[OK] Version locked: 11.42")
    else:
        print("[DRY RUN] No files changed. Re-run with --install to apply.")

    print(json.dumps({
        "installed": install,
        "target": str(root),
        "active_launcher": "LAUNCH_CLAIRE.bat",
        "version": LOCK_VERSION,
        "modern_dashboard_exists": sanity["modern_dashboard_exists"],
        "will_archive": OLD_LAUNCHERS
    }, indent=2))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
