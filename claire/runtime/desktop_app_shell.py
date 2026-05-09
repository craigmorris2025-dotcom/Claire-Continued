"""App-like desktop shell metadata for Claire."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class DesktopAppShell:
    """Report app-shell readiness for browser-backed desktop launches."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def status(self) -> Dict[str, Any]:
        launcher = self.project_root / "START_CLAIRE_DESKTOP.bat"
        unified = self.project_root / "START_CLAIRE.bat"
        return {
            "status": "success" if launcher.exists() and unified.exists() else "partial",
            "shell_version": "v5.69",
            "shell_type": "local_browser_app_shell",
            "launcher": str(launcher),
            "unified_launcher": str(unified),
            "app_mode_env": "CLAIRE_APP_SHELL=1",
            "desktop_live_env": "CLAIRE_DESKTOP_LIVE=1",
            "ready": launcher.exists() and unified.exists(),
            "notes": [
                "This is an app-like local shell using Claire's local dashboard server.",
                "It does not bundle Electron or native installers yet.",
                "It keeps the portable folder model intact for flash-drive use.",
            ],
        }
