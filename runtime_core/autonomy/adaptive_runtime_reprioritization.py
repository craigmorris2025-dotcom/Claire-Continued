
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime_core.orchestration.strategic_priority_engine import build_strategic_priority_state
from runtime_core.memory.operator_reinforcement_feedback import list_operator_feedback


ADAPTIVE_PRIORITY_PATH = Path("data/autonomy/adaptive_runtime_reprioritization.json")


def build_adaptive_runtime_reprioritization() -> Dict[str, Any]:
    priority_state = build_strategic_priority_state()
    feedback = list_operator_feedback()

    feedback_adjustment = 0.0
    for item in feedback[-25:]:
        feedback_adjustment += float(item.get("confidence_delta", 0.0))

    feedback_adjustment = max(-0.2, min(0.2, feedback_adjustment))

    adjusted_items: List[Dict[str, Any]] = []
    for item in priority_state.get("ranked_tasks", []) + priority_state.get("ranked_memories", []):
        base_score = float(item.get("score", 0.0))
        adjusted_score = max(0.0, min(1.0, base_score + feedback_adjustment))
        adjusted_items.append({
            **item,
            "base_score": round(base_score, 4),
            "feedback_adjustment": round(feedback_adjustment, 4),
            "adjusted_score": round(adjusted_score, 4),
        })

    adjusted_items = sorted(adjusted_items, key=lambda i: i["adjusted_score"], reverse=True)

    state = {
        "version": "16.89",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "feedback_record_count": len(feedback),
        "feedback_adjustment": round(feedback_adjustment, 4),
        "adjusted_priorities": adjusted_items,
        "top_adjusted_priority": adjusted_items[:1],
        "governance_note": "Adaptive reprioritization is bounded and explainable; it does not bypass operator review.",
    }

    ADAPTIVE_PRIORITY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADAPTIVE_PRIORITY_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
