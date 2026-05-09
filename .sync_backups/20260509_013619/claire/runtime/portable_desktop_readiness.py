"""Portable desktop readiness checks."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


class PortableDesktopReadiness:
    """Validate Claire can run from a moved folder or flash drive."""

    REQUIRED_PATHS = [
        "main.py",
        "tools/portable_launcher.py",
        "tools/serve_export_dashboard.py",
        "tools/run_claire_baseline.py",
        "src/claire",
        "src/frontend/export_dashboard/index.html",
        "data/live_sources/public_company_source_packs.json",
        "data/update_sources/allowed_sources.json",
    ]

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def status(self) -> Dict[str, Any]:
        checks = [self._path_check(rel) for rel in self.REQUIRED_PATHS]
        python_path = self.project_root / ".venv" / "Scripts" / "python.exe"
        launchers = {
            "unified": (self.project_root / "START_CLAIRE.bat").exists(),
            "portable": (self.project_root / "START_CLAIRE_PORTABLE.bat").exists(),
            "live": (self.project_root / "START_CLAIRE_LIVE.bat").exists(),
            "desktop_app": (self.project_root / "START_CLAIRE_DESKTOP.bat").exists(),
        }
        portable_drive_hint = self._drive_hint()
        ready = all(item["exists"] for item in checks) and python_path.exists() and launchers["unified"]
        return {
            "status": "success" if ready else "partial",
            "readiness_version": "v5.67",
            "project_root": str(self.project_root),
            "selected_python": str(python_path) if python_path.exists() else "",
            "path_checks": checks,
            "launcher_checks": launchers,
            "portable_drive_hint": portable_drive_hint,
            "ready_for_flash_drive_use": ready,
            "recommended_launcher": "START_CLAIRE.bat",
            "notes": [
                "Paths are resolved from the current project root at runtime.",
                "Use the unified launcher after moving the folder to another drive.",
                "Keep .venv with the project for true plug-and-use behavior.",
            ],
        }

    def _path_check(self, rel: str) -> Dict[str, Any]:
        path = self.project_root / rel
        return {"path": rel, "exists": path.exists()}

    def _drive_hint(self) -> Dict[str, Any]:
        drive = self.project_root.drive
        removable_guess = drive.upper() not in {"C:"}
        return {
            "drive": drive,
            "portable_drive_likely": removable_guess,
            "onedrive_path": "OneDrive" in str(self.project_root),
            "cwd": os.getcwd(),
        }
