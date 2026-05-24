from __future__ import annotations

from typing import Dict, List


class SignalConflictReconciler:
    def reconcile(self, evidence_packets: List[Dict[str, object]]) -> Dict[str, object]:
        supporting = [item for item in evidence_packets if item.get("stance") == "supporting"]
        conflicting = [item for item in evidence_packets if item.get("stance") == "conflicting"]
        neutral = [item for item in evidence_packets if item.get("stance") not in {"supporting", "conflicting"}]

        support_score = sum(float(item.get("confidence", 0.5)) for item in supporting)
        conflict_score = sum(float(item.get("confidence", 0.5)) for item in conflicting)

        if conflict_score > support_score:
            status = "conflict_dominant"
        elif support_score > conflict_score:
            status = "support_dominant"
        else:
            status = "balanced_or_insufficient"

        return {
            "status": status,
            "supporting_count": len(supporting),
            "conflicting_count": len(conflicting),
            "neutral_count": len(neutral),
            "support_score": round(support_score, 4),
            "conflict_score": round(conflict_score, 4),
            "recommendation": "escalate_for_review" if conflict_score > 0 else "continue_monitoring",
        }
