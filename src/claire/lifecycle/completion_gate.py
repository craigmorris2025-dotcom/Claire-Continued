"""Final completion gate for Claire core lifecycle runs."""

from __future__ import annotations

from typing import Any, Dict, List

from .stage_status import BLOCKED, COMPLETE, FAILED, INSUFFICIENT_DATA, SKIPPED_BY_ROUTE


class CompletionGate:
    """Classifies a route-aware lifecycle run without forcing invention."""

    def evaluate(self, lifecycle_payload: Dict[str, Any]) -> Dict[str, Any]:
        stages = lifecycle_payload.get("stages", [])
        if not stages:
            return {"status": "blocked", "reason": "no lifecycle stages were provided", "blocking_stage_count": 0}

        blocking: List[Dict[str, Any]] = []
        insufficient: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []
        complete = 0

        for stage in stages:
            status = stage.get("status")
            if status == COMPLETE:
                complete += 1
            elif status in {FAILED, BLOCKED}:
                blocking.append(stage)
            elif status == INSUFFICIENT_DATA:
                insufficient.append(stage)
            elif status == SKIPPED_BY_ROUTE:
                skipped.append(stage)

        if blocking:
            gate_status = "blocked"
        elif insufficient:
            gate_status = "insufficient_data"
        elif complete + len(skipped) == len(stages):
            gate_status = "complete"
        else:
            gate_status = "incomplete"

        return {
            "status": gate_status,
            "route": lifecycle_payload.get("route"),
            "stage_count": len(stages),
            "complete_stage_count": complete,
            "skipped_by_route_stage_count": len(skipped),
            "blocking_stage_count": len(blocking),
            "insufficient_data_stage_count": len(insufficient),
            "blocked_stages": [{"stage_id": item.get("id"), "name": item.get("name")} for item in blocking],
            "insufficient_data_stages": [{"stage_id": item.get("id"), "name": item.get("name"), "missing_outputs": item.get("missing_outputs", [])} for item in insufficient],
        }
