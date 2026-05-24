"""Plateau candidate report for Claire."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from runtime_core.runtime.production_readiness import ProductionReadiness
from runtime_core.runtime.stale_path_audit import StalePathAudit
from runtime_core.updater.update_health import UpdaterHealth


class PlateauCandidateReport:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def build(self, baseline_status: str = "not_run") -> Dict[str, Any]:
        production = ProductionReadiness(self.project_root).status()
        updater = UpdaterHealth(self.project_root).status()
        stale = StalePathAudit(self.project_root).run()
        blockers = []
        if baseline_status not in {"success", "passed"}:
            blockers.append("baseline runner has not been confirmed in this report")
        if updater.get("readiness") != "self_update_ready":
            blockers.append("updater is not fully self_update_ready")
        return {
            "status": "success",
            "plateau_version": "v5.62",
            "plateau_posture": "candidate" if not blockers else "candidate_with_notes",
            "baseline_status": baseline_status,
            "production": production,
            "updater": updater,
            "stale_path_audit": stale,
            "blockers": blockers,
            "next_phase": "optimization and desktop packaging",
        }


__all__ = ["PlateauCandidateReport"]
