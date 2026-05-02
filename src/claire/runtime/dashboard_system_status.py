"""Dashboard-level system status rollup for Claire."""

from __future__ import annotations

from typing import Any, Dict, List


class DashboardSystemStatus:
    """Builds a compact status payload from subsystem snapshots."""

    def build(
        self,
        mode_status: Dict[str, Any],
        feed_status: Dict[str, Any],
        signal_status: Dict[str, Any],
        enrichment_status: Dict[str, Any],
        fusion_status: Dict[str, Any],
        lifecycle_status: Dict[str, Any],
        export_summary: Dict[str, Any],
        updater_status: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        subsystems = [
            self._item("mode_governance", "Mode Governance", "ready", mode_status.get("controller")),
            self._item("feed_governance", "Feed Governance", feed_status.get("activation_layer", feed_status.get("status")), "connected feeds governed"),
            self._item("normalized_signals", "Normalized Signals", signal_status.get("status"), f"{signal_status.get('signal_count', signal_status.get('count', 0))} signal(s)"),
            self._item("connected_enrichment", "Connected Enrichment", enrichment_status.get("status"), f"{enrichment_status.get('safe_to_enrich_count', 0)} safe signal(s)"),
            self._item("hybrid_fusion", "Hybrid Fusion", fusion_status.get("status"), fusion_status.get("fusion_engine")),
            self._item("lifecycle_spine", "Lifecycle Spine", lifecycle_status.get("status"), f"{lifecycle_status.get('stage_count', 0)} stage(s)"),
            self._item("exports", "Exports", export_summary.get("status", "available"), f"{export_summary.get('run_count', export_summary.get('total_runs', 0))} run(s)"),
            self._item("updater", "Updater", (updater_status or {}).get("status", "bootstrap_ready"), "local/web package path available"),
        ]
        ready_count = len([item for item in subsystems if item["state"] in {"ready", "success", "available", "bootstrap_ready"}])
        return {
            "status": "success",
            "dashboard_rollup": "v5.54",
            "subsystem_count": len(subsystems),
            "ready_subsystem_count": ready_count,
            "completion_posture": self._completion_posture(ready_count, len(subsystems)),
            "subsystems": subsystems,
            "next_focus": self._next_focus(subsystems),
            "speed_levers": [
                "keep new capabilities behind stable contracts before UI polish",
                "run compile and smoke checks after each package",
                "use the updater path for future package installation",
                "defer hard folder restructuring until the plateau pass",
            ],
        }

    def _item(self, key: str, name: str, state: Any, detail: Any) -> Dict[str, Any]:
        return {
            "key": key,
            "name": name,
            "state": str(state or "unknown"),
            "detail": str(detail or ""),
        }

    def _completion_posture(self, ready_count: int, total: int) -> str:
        if not total:
            return "unknown"
        ratio = ready_count / total
        if ratio >= 0.85:
            return "plateau_candidate"
        if ratio >= 0.65:
            return "major_capability_buildout"
        return "foundation_buildout"

    def _next_focus(self, subsystems: List[Dict[str, Any]]) -> Dict[str, Any]:
        for item in subsystems:
            if item["state"] not in {"ready", "success", "available", "bootstrap_ready"}:
                return {
                    "key": item["key"],
                    "name": item["name"],
                    "reason": f"{item['name']} is currently {item['state']}.",
                }
        return {
            "key": "optimization",
            "name": "System-wide optimization",
            "reason": "Core dashboard subsystems report ready/available status.",
        }
