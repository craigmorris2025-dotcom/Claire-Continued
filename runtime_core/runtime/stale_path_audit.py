"""Non-destructive stale path audit for Claire optimization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class StalePathAudit:
    """Find known stale or legacy paths without deleting anything."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def run(self) -> Dict[str, Any]:
        checks = [
            self._check("legacy_frontend_entry", "src/frontend/index.html", "legacy frontend path; active dashboard is src/frontend/export_dashboard/index.html"),
            self._check("legacy_launch_bat", "LAUNCH.bat", "legacy launcher may not reflect current dashboard server path"),
            self._check("empty_mode_placeholders", "src/claire/mode", "mode placeholders should now be real controller files"),
        ]
        return {
            "status": "success",
            "audit_version": "v5.60_stale_path_cleanup",
            "destructive_actions": False,
            "stale_count": len([item for item in checks if item.get("exists")]),
            "checks": checks,
            "recommendation": "Do not delete automatically; review after plateau candidate passes baseline.",
        }

    def _check(self, key: str, rel: str, note: str) -> Dict[str, Any]:
        path = self.project_root / rel
        return {"key": key, "path": rel, "exists": path.exists(), "note": note}


__all__ = ["StalePathAudit"]
