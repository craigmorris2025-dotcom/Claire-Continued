
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime_core.autonomy.autonomous_escalation_engine import evaluate_autonomous_escalations
from runtime_core.orchestration.intelligence_task_registry import register_intelligence_task


RECURSION_STATE_PATH = Path("data/autonomy/recursive_orchestration_state.json")

ALLOWED_RECURSIVE_ROUTES = {
    "thesis_update",
    "evidence_review",
    "portfolio_review",
    "buyer_readiness_review",
    "operator_review",
}


def run_recursive_orchestration_controller(
    threshold: float = 0.75,
    max_follow_on_tasks: int = 5,
    operator_approved: bool = True,
) -> Dict[str, Any]:
    max_follow_on_tasks = max(0, min(10, int(max_follow_on_tasks)))

    if not operator_approved:
        state = {
            "version": "16.88",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "blocked",
            "reason": "Operator approval required for recursive follow-on task generation.",
            "created_task_count": 0,
            "created_tasks": [],
        }
        RECURSION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECURSION_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    escalations = evaluate_autonomous_escalations(threshold=threshold).get("escalations", [])
    pending = [e for e in escalations if e.get("status") == "pending_operator_review"]

    created_tasks: List[Dict[str, Any]] = []

    for escalation in pending[:max_follow_on_tasks]:
        route = escalation.get("recommended_route", "operator_review")
        if route not in ALLOWED_RECURSIVE_ROUTES:
            route = "operator_review"

        task_type = route if route != "operator_review" else "evidence_review"
        if task_type == "buyer_readiness_review":
            task_type = "buyer_readiness_review"

        task = register_intelligence_task(
            task_type=task_type,
            title=f"Follow-on task from escalation: {escalation.get('title')}",
            payload={
                "source_escalation_id": escalation.get("escalation_id"),
                "source_id": escalation.get("source_id"),
                "recommended_route": route,
                "score": escalation.get("score"),
            },
            priority=8,
            owner="recursive_orchestration_controller",
        )
        created_tasks.append(task)

    state = {
        "version": "16.88",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "threshold": threshold,
        "max_follow_on_tasks": max_follow_on_tasks,
        "created_task_count": len(created_tasks),
        "created_tasks": created_tasks,
        "governance_note": "Follow-on generation is bounded and route-limited.",
    }

    RECURSION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECURSION_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
