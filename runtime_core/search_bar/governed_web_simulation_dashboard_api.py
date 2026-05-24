from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_bool_false_map() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


def _coerce_card(card: Mapping[str, Any]) -> Dict[str, Any]:
    coerced = dict(card)
    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        coerced[field_name] = False
    coerced.setdefault("card_id", f"simulation-card-{coerced.get('request_id', 'unknown')}")
    coerced.setdefault("title", "Governed web simulation review")
    coerced.setdefault("status", "blocked_or_incomplete_simulation_review")
    coerced.setdefault("decision", "not_eligible_for_simulation_review")
    coerced.setdefault("safety_badges", [])
    coerced.setdefault("reasons", ["execution_blocked_by_policy"])
    return coerced


def build_dashboard_api_response(
    viewer_result: Mapping[str, Any],
    *,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a dashboard-safe API response from a governed web simulation viewer result.

    This adapter intentionally does not execute web actions, mutate runtime truth,
    activate AI-agent execution, or perform automatic updates.
    """
    raw_cards = list(viewer_result.get("cards") or [])
    cards = [_coerce_card(card) for card in raw_cards]

    summary = dict(viewer_result.get("summary") or {})
    summary.setdefault("total", len(cards))
    summary.setdefault(
        "eligible_for_simulation_review",
        sum(1 for card in cards if bool(card.get("eligible_for_simulation_review"))),
    )
    summary.setdefault(
        "blocked_or_incomplete",
        summary.get("total", len(cards)) - summary.get("eligible_for_simulation_review", 0),
    )
    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        summary[field_name] = False

    safety_state = dict(viewer_result.get("safety_state") or {})
    safety_state.update(
        {
            "approval_equals_execution": False,
            "review_gated": True,
            "execution_enabled": False,
            "live_web_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
            "dashboard_rewired": False,
        }
    )

    response = {
        "api": "search_bar_governed_web_simulation_dashboard",
        "version": "v18.08",
        "created_at": _utc_now(),
        "request_id": request_id or str(viewer_result.get("request_id") or "dashboard-simulation-view"),
        "ok": True,
        "mode": "governed_web_simulation_review",
        "dashboard_rewired": False,
        "execution_state": _safe_bool_false_map(),
        "summary": summary,
        "cards": cards,
        "safety_state": safety_state,
        "messages": [
            "dashboard_api_contract_ready",
            "simulation_review_only",
            "no_execution_performed",
            "dashboard_rewiring_not_performed",
        ],
    }

    assert_dashboard_api_response_non_executing(response)
    return response


def assert_dashboard_api_response_non_executing(response: Mapping[str, Any]) -> bool:
    execution_state = dict(response.get("execution_state") or {})
    summary = dict(response.get("summary") or {})
    safety_state = dict(response.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")
        if bool(summary.get(field_name)):
            raise AssertionError(f"summary.{field_name} must remain false")

    if bool(safety_state.get("execution_enabled")):
        raise AssertionError("safety_state.execution_enabled must remain false")
    if bool(safety_state.get("live_web_enabled")):
        raise AssertionError("safety_state.live_web_enabled must remain false")
    if bool(safety_state.get("runtime_truth_mutation_enabled")):
        raise AssertionError("safety_state.runtime_truth_mutation_enabled must remain false")
    if bool(safety_state.get("ai_agent_execution_enabled")):
        raise AssertionError("safety_state.ai_agent_execution_enabled must remain false")
    if bool(safety_state.get("automatic_updates_enabled")):
        raise AssertionError("safety_state.automatic_updates_enabled must remain false")
    if bool(response.get("dashboard_rewired")):
        raise AssertionError("dashboard_rewired must remain false for v18.08")

    for card in response.get("cards") or []:
        for field_name in FORBIDDEN_EXECUTION_FIELDS:
            if bool(card.get(field_name)):
                raise AssertionError(f"card.{field_name} must remain false")

    return True
