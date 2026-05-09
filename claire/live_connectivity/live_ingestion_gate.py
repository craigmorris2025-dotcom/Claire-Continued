from __future__ import annotations
from typing import Any, Dict

class LiveIngestionGate:
    REQUIRED = ["source_allowed", "rights_confirmed", "lineage_created", "audit_logged", "quarantine_supported"]

    def evaluate(self, checks: Dict[str, bool]) -> Dict[str, Any]:
        missing = [key for key in self.REQUIRED if not checks.get(key, False)]
        return {
            "record_type": "live_ingestion_gate",
            "status": "pass" if not missing else "blocked",
            "missing": missing,
            "rule": "Live internet data must be allowlisted, rights-aware, lineage-tracked, audited, and quarantine-capable."
        }
