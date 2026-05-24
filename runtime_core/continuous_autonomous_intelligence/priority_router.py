from __future__ import annotations

from typing import Dict


class IngestionPriorityRouter:
    def score(self, signal: Dict[str, object]) -> int:
        confidence = float(signal.get("confidence", 0.5))
        novelty = float(signal.get("novelty", 0.5))
        urgency = float(signal.get("urgency", 0.5))
        contradiction = float(signal.get("contradiction", 0.0))

        raw = (confidence * 3.0) + (novelty * 2.0) + (urgency * 3.0) + (contradiction * 2.0)
        return max(1, min(10, round(raw)))

    def route(self, signal: Dict[str, object]) -> Dict[str, object]:
        priority = self.score(signal)

        if priority >= 8:
            route = "immediate_review_queue"
        elif priority >= 5:
            route = "standard_ingestion_queue"
        else:
            route = "low_priority_observation_queue"

        return {
            "priority": priority,
            "route": route,
            "reason": "Priority combines confidence, novelty, urgency, and contradiction pressure.",
        }
