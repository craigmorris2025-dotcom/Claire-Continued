from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from .runtime_truth_contract import ROUTE_REQUIRED_STAGES, ROUTE_TERMINALS, coerce_list, first_present, normalize_route, normalize_terminal


@dataclass
class RouteTruth:
    route_selected: str
    route_confidence: float | None
    route_reason: str
    routes_rejected: List[Any]
    route_gate_stage: int
    route_started_at: str
    route_terminal_state: str
    route_required_stages: List[int]
    route_completed_stages: List[int]
    route_missing_stages: List[int]
    route_blocked_stages: List[int]
    route_terminal_fit: bool
    raw: Any


def _confidence(value: Any) -> float | None:
    if isinstance(value, Mapping):
        value = first_present(value, ["route_confidence", "confidence", "score"], None)
    try:
        if value is None or value == "":
            return None
        score = float(value)
        return max(0.0, min(1.0, score if score <= 1 else score / 100.0))
    except Exception:
        return None


def build_route_truth(raw: Mapping[str, Any], stage_truth: List[Dict[str, Any]]) -> Dict[str, Any]:
    route_obj = raw.get("route_decision") if isinstance(raw.get("route_decision"), Mapping) else raw.get("routing") if isinstance(raw.get("routing"), Mapping) else {}
    selected = normalize_route(first_present(raw, ["route_selected", "selected_route", "route", "route_type", "core_lifecycle_summary.route_selected"], None) or first_present(route_obj, ["route_selected", "selected_route", "route"], "")) or "not_reported"
    terminal = normalize_terminal(first_present(raw, ["terminal_state", "status_terminal", "core_lifecycle_summary.terminal_state"], "")) or "not_reported"
    required = ROUTE_REQUIRED_STAGES.get(selected, [])
    completed = sorted([s["stage_number"] for s in stage_truth if s.get("status") == "completed" and s.get("stage_number") in required])
    blocked = sorted([s["stage_number"] for s in stage_truth if s.get("status") in {"blocked", "failed"} and s.get("stage_number") in required])
    missing = sorted([n for n in required if n not in completed and n not in [s["stage_number"] for s in stage_truth if s.get("status") in {"skipped_by_route", "not_applicable"}]])
    rejected = first_present(raw, ["routes_rejected", "rejected_routes"], None) or first_present(route_obj, ["routes_rejected", "rejected_routes"], [])
    truth = RouteTruth(
        route_selected=selected,
        route_confidence=_confidence(first_present(raw, ["route_confidence"], None) or route_obj),
        route_reason=str(first_present(raw, ["route_reason", "route_decision.reason", "route_decision.route_reason"], "not_reported")),
        routes_rejected=coerce_list(rejected),
        route_gate_stage=10,
        route_started_at=str(first_present(raw, ["route_started_at", "stage_10.completed_at", "started_at", "timestamp"], "not_reported")),
        route_terminal_state=terminal,
        route_required_stages=list(required),
        route_completed_stages=completed,
        route_missing_stages=missing,
        route_blocked_stages=blocked,
        route_terminal_fit=terminal in ROUTE_TERMINALS.get(selected, set()),
        raw=route_obj,
    )
    return asdict(truth)
