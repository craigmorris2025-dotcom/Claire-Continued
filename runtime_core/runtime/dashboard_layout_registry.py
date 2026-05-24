"""Dashboard panel grouping registry for the plateau UI."""

from __future__ import annotations

from typing import Any, Dict, List


class DashboardLayoutRegistry:
    """Describes a consolidated dashboard structure without removing panels."""

    def payload(self) -> Dict[str, Any]:
        groups = [
            self._group("launch", "Launch", ["Opportunity Discovery", "Mode Governance", "Live Run Events"]),
            self._group("system", "System", ["System Status", "Lifecycle / Thresholds", "Run History"]),
            self._group("feeds", "Feeds", ["Public Company Live Scan v1", "Normalized Signals", "Feed Activation Governance", "Feed Status"]),
            self._group("sources", "Sources", ["Offline Universe Resolver", "Public Company Source Catalog"]),
            self._group("outputs", "Outputs", ["Export Browser", "Files", "Preview", "Run JSON"]),
        ]
        return {
            "status": "success",
            "layout_version": "v5.59_dashboard_ux_consolidation",
            "group_count": len(groups),
            "groups": groups,
            "principles": [
                "preserve current controls",
                "group panels by user workflow",
                "keep protected discovery construction hidden",
                "favor status summaries over panel sprawl",
            ],
        }

    def _group(self, key: str, name: str, panels: List[str]) -> Dict[str, Any]:
        return {"key": key, "name": name, "panels": panels, "panel_count": len(panels)}


__all__ = ["DashboardLayoutRegistry"]
