"""Small in-memory mode state helper for dashboard sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class ModeStateManager:
    """Keeps recent mode decisions inspectable without becoming persistent state."""

    def __init__(self, limit: int = 100) -> None:
        self.limit = limit
        self._events: List[Dict[str, Any]] = []

    def record(self, event_type: str, decision: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "requested_mode": decision.get("requested_mode"),
            "effective_mode": decision.get("effective_mode"),
            "status": decision.get("status"),
            "mode_decision_id": decision.get("mode_decision_id"),
            "warnings": decision.get("warnings", []),
            "context": context or {},
        }
        self._events.append(event)
        self._events = self._events[-self.limit :]
        return event

    def recent(self, limit: int = 20) -> Dict[str, Any]:
        return {
            "status": "success",
            "event_count": len(self._events),
            "events": list(reversed(self._events[-limit:])),
        }
