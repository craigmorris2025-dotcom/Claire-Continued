from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class GovernanceDeploymentLock:
    """Creates governance deployment lock records for controlled scaling."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_lock(self, version: str, status: str = "governance_locked", notes: str = "") -> Dict[str, Any]:
        return {
            "record_type": "governance_deployment_lock",
            "version": version,
            "status": status,
            "notes": notes,
            "locked_at_utc": datetime.now(timezone.utc).isoformat(),
            "controls": {
                "source_allowlist_required": True,
                "lineage_required": True,
                "operator_review_required": True,
                "benchmark_replay_required": True,
                "false_positive_tracking_required": True,
                "live_activation_gated": True,
            },
        }

    def export_lock(self, lock: Dict[str, Any]) -> Path:
        out = self.root / "data" / "operational_proof" / "governance_locks" / f"governance_lock_{lock['version'].replace('.','_')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(lock, indent=2, sort_keys=True), encoding="utf-8")
        return out
