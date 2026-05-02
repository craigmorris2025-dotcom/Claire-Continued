"""Desktop live service readiness for Claire."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import os


class DesktopServiceStatus:
    """Summarize the services that should work in desktop/live mode."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def status(
        self,
        mode_status: Dict[str, Any],
        feed_status: Dict[str, Any],
        live_scan_status: Dict[str, Any],
        live_source_catalog_status: Dict[str, Any] | None,
        updater_status: Dict[str, Any],
        baseline_available: bool,
    ) -> Dict[str, Any]:
        live_source_catalog_status = live_source_catalog_status or {}
        services = [
            self._service("dashboard", "Dashboard Server", True, "current export dashboard server"),
            self._service("portable_launcher", "Portable Launcher", (self.project_root / "tools" / "portable_launcher.py").exists(), "plug-and-use local launcher"),
            self._service("baseline_runner", "Baseline Runner", baseline_available, "single-command validation"),
            self._service("mode_governance", "Mode Governance", mode_status.get("status") == "success", mode_status.get("controller")),
            self._service("feed_registry", "Feed Registry", feed_status.get("status") == "success", feed_status.get("feed_layer")),
            self._service("live_source_catalog", "Live Source Catalog", live_source_catalog_status.get("status") == "success", f"{live_source_catalog_status.get('active_source_count', 0)} active sources"),
            self._service("live_metadata_fetcher", "Live Metadata Fetcher", live_scan_status.get("status") == "success", "enabled" if live_scan_status.get("live_enabled") else "installed_disabled"),
            self._service("updater", "Self-Updater", updater_status.get("readiness") == "self_update_ready", updater_status.get("readiness")),
            self._service("exports", "Export Browser", (self.project_root / "exports").exists(), "local export artifacts"),
            self._service("venv", "Bundled Python Environment", (self.project_root / ".venv" / "Scripts" / "python.exe").exists(), ".venv portable runtime"),
        ]
        ready = len([item for item in services if item["ready"]])
        live_enabled = os.environ.get("CLAIRE_ENABLE_LIVE_FEEDS", "").strip() == "1"
        return {
            "status": "success" if ready == len(services) else "partial",
            "desktop_state": "live_connected" if live_enabled else "portable_local",
            "live_connected_enabled": live_enabled,
            "service_count": len(services),
            "ready_service_count": ready,
            "services": services,
            "notes": [
                "Live metadata scans are public URL metadata only.",
                "Governance and deterministic fallback remain active.",
                "Use START_CLAIRE_LIVE.bat for live connected desktop state.",
            ],
        }

    def _service(self, key: str, name: str, ready: bool, detail: Any) -> Dict[str, Any]:
        return {"key": key, "name": name, "ready": bool(ready), "detail": str(detail or "")}


__all__ = ["DesktopServiceStatus"]
