"""
Feed Audit Log — local audit trail for feed activation decisions.

v5.43:
- Logs feed activation decisions locally.
- Does not externally report.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import json


class FeedAuditLog:
    """JSONL audit log for feed activation decisions."""

    def __init__(self, path: str = "data/governance/feed_audit_log.jsonl") -> None:
        self.path = Path(path)

    def log(self, event_type: str, activation_decision: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "activation_id": activation_decision.get("activation_id"),
            "decision": activation_decision.get("decision"),
            "feed_status": activation_decision.get("feed_status"),
            "severity": activation_decision.get("severity"),
            "execution_mode": activation_decision.get("execution_mode"),
            "market_universe": activation_decision.get("market_universe"),
            "source_category": activation_decision.get("source_category"),
            "connected_ingestion_allowed": activation_decision.get("connected_ingestion_allowed"),
            "deterministic_fallback_allowed": activation_decision.get("deterministic_fallback_allowed"),
            "reason": activation_decision.get("reason"),
            "context": context or {},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")
        return event

    def recent(self, limit: int = 25) -> Dict[str, Any]:
        if not self.path.exists():
            return {"status": "success", "path": str(self.path), "event_count": 0, "events": []}
        lines = self.path.read_text(encoding="utf-8").splitlines()
        events: List[Dict[str, Any]] = []
        for line in lines[-max(1, limit):]:
            try:
                events.append(json.loads(line))
            except Exception:
                continue
        return {"status": "success", "path": str(self.path), "event_count": len(events), "events": list(reversed(events))}
