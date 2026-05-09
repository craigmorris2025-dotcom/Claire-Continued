from __future__ import annotations

from typing import Any, Dict, List, Optional

from .memory_record import utc_now


FEEDBACK_ELIGIBLE_ROUTES = {
    "portfolio",
    "portfolio_optimization",
    "breakthrough",
    "autodesign",
    "design",
    "system_design",
    "acquisition",
    "package",
}


class RecursiveFeedbackGate:
    """Decide whether a verified output may be fed back into future Claire runs."""

    contract_version = "claire.recursive_feedback_gate.v17.61"

    def evaluate(self, memory_gate_report: Dict[str, Any]) -> Dict[str, Any]:
        route = str(memory_gate_report.get("route_selected") or "unknown").lower()
        memory_eligible = bool(memory_gate_report.get("memory_eligible"))
        validation_passed = bool(memory_gate_report.get("validation_passed"))
        memory_record = memory_gate_report.get("memory_record") if isinstance(memory_gate_report.get("memory_record"), dict) else None

        blockers: List[str] = []
        reasons: List[str] = []

        if not validation_passed:
            blockers.append("validation_not_passed")
            reasons.append("Recursive feedback is blocked because validation did not pass.")

        if not memory_eligible:
            blockers.append("memory_not_eligible")
            reasons.append("Recursive feedback is blocked because verified memory eligibility failed.")

        if not memory_record:
            blockers.append("missing_memory_record")
            reasons.append("Recursive feedback is blocked because no verified memory record payload exists.")

        if route not in FEEDBACK_ELIGIBLE_ROUTES:
            blockers.append("route_not_feedback_eligible")
            reasons.append(f"Route '{route}' is not currently approved for recursive feedback.")

        allowed = len(blockers) == 0

        return {
            "schema": "claire.recursive_feedback_gate_report.v1",
            "contract_version": self.contract_version,
            "generated_at": utc_now(),
            "run_id": memory_gate_report.get("run_id", "unknown"),
            "route_selected": memory_gate_report.get("route_selected", "unknown"),
            "terminal_state": memory_gate_report.get("terminal_state", "missing"),
            "recursive_feedback_allowed": allowed,
            "feedback_status": "allowed" if allowed else "blocked",
            "feedback_blockers": blockers,
            "feedback_reasons": reasons or ["Validated output is memory-eligible and may be used as governed recursive feedback."],
            "feedback_payload": {
                "memory_id": memory_record.get("memory_id") if memory_record else None,
                "run_id": memory_gate_report.get("run_id", "unknown"),
                "route_selected": memory_gate_report.get("route_selected", "unknown"),
                "terminal_state": memory_gate_report.get("terminal_state", "missing"),
                "allowed_uses": [
                    "future_context_reference",
                    "architecture_gap_analysis",
                    "validated_output_replay",
                    "route_quality_learning",
                ] if allowed else [],
            },
            "safety_note": "v17.61 permits recursive feedback only as a governed status/payload. It does not autonomously mutate the runtime or retrain models.",
        }


def build_recursive_feedback_report(memory_gate_report: Dict[str, Any]) -> Dict[str, Any]:
    return RecursiveFeedbackGate().evaluate(memory_gate_report)
