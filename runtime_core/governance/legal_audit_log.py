"""
Legal Audit Log — local audit trail for governance/legal events.

v5.42:
- Logs allow/review/block governance decisions.
- Does not externally report by default.
- External reporting should occur only if required by law, contract, policy, or authorized compliance workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import json


class LegalAuditLog:
    """JSONL audit log for governance decisions."""

    def __init__(self, path: str = "data/governance/legal_audit_log.jsonl") -> None:
        self.path = Path(path)

    def log(self, event_type: str, decision: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "decision_id": decision.get("decision_id"),
            "decision": decision.get("decision"),
            "severity": decision.get("severity"),
            "defense_classification": decision.get("defense_classification"),
            "legal_status": decision.get("legal_status"),
            "reason_summary": decision.get("reason_summary"),
            "triggered_terms": decision.get("triggered_terms", []),
            "recommended_action": decision.get("recommended_action"),
            "context": context or {},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")
        return event

    def recent(self, limit: int = 25) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "status": "success",
                "path": str(self.path),
                "event_count": 0,
                "events": [],
            }

        lines = self.path.read_text(encoding="utf-8").splitlines()
        events: List[Dict[str, Any]] = []
        for line in lines[-max(1, limit):]:
            try:
                events.append(json.loads(line))
            except Exception:
                continue

        return {
            "status": "success",
            "path": str(self.path),
            "event_count": len(events),
            "events": list(reversed(events)),
        }
