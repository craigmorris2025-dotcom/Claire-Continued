
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime_core.memory.strategic_memory_registry import add_strategic_memory


OPERATOR_FEEDBACK_PATH = Path("data/memory/operator_reinforcement_feedback.json")

VALID_FEEDBACK = {
    "approved",
    "rejected",
    "needs_review",
    "false_positive",
    "useful_signal",
    "weak_signal",
}


def _load_feedback() -> List[Dict[str, Any]]:
    if not OPERATOR_FEEDBACK_PATH.exists():
        return []
    try:
        data = json.loads(OPERATOR_FEEDBACK_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def record_operator_feedback(
    target_id: str,
    feedback: str,
    rationale: str,
    operator: str = "system",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if feedback not in VALID_FEEDBACK:
        raise ValueError(f"Invalid feedback type: {feedback}")

    confidence_delta = {
        "approved": 0.10,
        "useful_signal": 0.06,
        "needs_review": 0.0,
        "weak_signal": -0.04,
        "rejected": -0.10,
        "false_positive": -0.15,
    }[feedback]

    record = {
        "version": "16.69",
        "feedback_id": f"feedback_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target_id": target_id,
        "feedback": feedback,
        "rationale": rationale,
        "operator": operator,
        "confidence_delta": confidence_delta,
        "metadata": metadata or {},
    }

    OPERATOR_FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    feedback_records = _load_feedback()
    feedback_records.append(record)
    OPERATOR_FEEDBACK_PATH.write_text(json.dumps(feedback_records, indent=2), encoding="utf-8")

    add_strategic_memory(
        memory_type="operator_decision",
        title=f"Operator feedback: {feedback}",
        payload=record,
        confidence=max(0.0, min(1.0, 0.5 + confidence_delta)),
        tags=["operator_feedback", feedback],
    )

    return record


def list_operator_feedback() -> List[Dict[str, Any]]:
    return _load_feedback()
