from __future__ import annotations

import hashlib
from typing import Dict

from .models import EscalationDecision


class EventDrivenEscalationEngine:
    def evaluate(self, topic: str, priority: int, conflict_status: str, confidence: float) -> EscalationDecision:
        if conflict_status == "conflict_dominant":
            route = "human_review"
            reason = "Conflicting evidence dominates supporting evidence."
        elif priority >= 8 and confidence >= 0.7:
            route = "strategic_decision_layer"
            reason = "High-priority, high-confidence signal qualifies for decisioning."
        elif priority >= 6:
            route = "continued_monitoring"
            reason = "Signal is meaningful but requires more evidence."
        else:
            route = "archive_observation"
            reason = "Signal does not currently justify escalation."

        escalation_id = "escalation_" + hashlib.sha256(f"{topic}|{route}|{reason}".encode("utf-8")).hexdigest()[:12]

        return EscalationDecision(
            escalation_id=escalation_id,
            topic=topic,
            route=route,
            reason=reason,
            confidence=max(0.0, min(1.0, confidence)),
            status="requires_review" if route in {"human_review", "strategic_decision_layer"} else "bounded",
        )
