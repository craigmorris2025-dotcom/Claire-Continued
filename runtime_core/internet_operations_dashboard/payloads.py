from __future__ import annotations

from typing import Any, Dict, List

from .models import DashboardPanelStatus, DashboardSnapshot


class DashboardPayloadBuilder:
    def build(
        self,
        campaigns: List[Dict[str, Any]],
        schedules: List[Dict[str, Any]],
        scheduler_reports: List[Dict[str, Any]],
        stability: Dict[str, Any],
        source_trust_profiles: List[Dict[str, Any]],
        source_trust_events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        panels = [
            self._panel("campaigns", campaigns),
            self._panel("schedules", schedules),
            self._panel("scheduler_reports", scheduler_reports),
            self._health_panel(stability),
            self._panel("source_trust_profiles", source_trust_profiles),
            self._panel("source_trust_events", source_trust_events),
        ]

        overall = "healthy"
        if any(panel["status"] == "error" for panel in panels):
            overall = "error"
        elif any(panel["status"] in {"degraded", "warning"} for panel in panels):
            overall = "degraded"

        snapshot = DashboardSnapshot(
            status=overall,
            panels=panels,
            campaigns=campaigns,
            schedules=schedules,
            scheduler_reports=scheduler_reports,
            stability=stability,
            source_trust_profiles=source_trust_profiles,
            source_trust_events=source_trust_events,
            recommendations=self._recommendations(campaigns, schedules, stability, source_trust_profiles),
        )
        return snapshot.to_dict()

    def _panel(self, name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        return DashboardPanelStatus(panel=name, status="healthy", count=len(items)).to_dict()

    def _health_panel(self, stability: Dict[str, Any]) -> Dict[str, Any]:
        status = str(stability.get("status", "unknown"))
        panel_status = "healthy" if status == "healthy" else ("degraded" if status in {"degraded", "not_ready"} else "warning")
        return DashboardPanelStatus(
            panel="internet_runtime_health",
            status=panel_status,
            count=1 if stability else 0,
            warnings=stability.get("missing_data_paths", []) if isinstance(stability, dict) else [],
            errors=stability.get("missing_required_paths", []) if isinstance(stability, dict) else [],
        ).to_dict()

    def _recommendations(
        self,
        campaigns: List[Dict[str, Any]],
        schedules: List[Dict[str, Any]],
        stability: Dict[str, Any],
        source_trust_profiles: List[Dict[str, Any]],
    ) -> List[str]:
        recs = []
        if campaigns and not schedules:
            recs.append("Create schedules for active internet campaigns.")
        if stability.get("status") == "not_ready":
            recs.append("Resolve missing required internet runtime modules before launch.")
        if any(item.get("status") == "quarantined" for item in source_trust_profiles):
            recs.append("Review quarantined sources before relying on their evidence.")
        if not campaigns:
            recs.append("Create at least one persistent campaign before launch validation.")
        return recs
