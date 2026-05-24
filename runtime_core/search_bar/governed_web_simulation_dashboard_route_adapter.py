from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

try:
    from .governed_web_simulation_dashboard_api import (
        assert_dashboard_api_response_non_executing,
        build_dashboard_api_response,
    )
except Exception:
    assert_dashboard_api_response_non_executing = None
    build_dashboard_api_response = None


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


DEFAULT_ROUTE_PATH = "/search/governed-web/simulation/dashboard"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


def _fallback_dashboard_response(payload: Mapping[str, Any]) -> Dict[str, Any]:
    response = {
        "api": "search_bar_governed_web_simulation_dashboard",
        "version": "v18.09",
        "created_at": _utc_now(),
        "request_id": str(payload.get("request_id") or "route-adapter-fallback"),
        "ok": True,
        "mode": "governed_web_simulation_review",
        "route_adapter": True,
        "route_path": DEFAULT_ROUTE_PATH,
        "dashboard_rewired": False,
        "execution_state": _false_execution_state(),
        "summary": {
            "total": 0,
            "eligible_for_simulation_review": 0,
            "blocked_or_incomplete": 0,
            **_false_execution_state(),
        },
        "cards": [],
        "safety_state": {
            "approval_equals_execution": False,
            "review_gated": True,
            "execution_enabled": False,
            "live_web_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
            "dashboard_rewired": False,
        },
        "messages": [
            "route_adapter_ready",
            "dashboard_api_fallback_used",
            "simulation_review_only",
            "no_execution_performed",
        ],
    }
    return response


def assert_route_response_non_executing(response: Mapping[str, Any]) -> bool:
    execution_state = dict(response.get("execution_state") or {})
    summary = dict(response.get("summary") or {})
    safety_state = dict(response.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")
        if bool(summary.get(field_name)):
            raise AssertionError(f"summary.{field_name} must remain false")
        for card in response.get("cards") or []:
            if bool(card.get(field_name)):
                raise AssertionError(f"card.{field_name} must remain false")

    if bool(response.get("dashboard_rewired")):
        raise AssertionError("dashboard_rewired must remain false in v18.09")
    if bool(safety_state.get("execution_enabled")):
        raise AssertionError("execution_enabled must remain false")
    if bool(safety_state.get("live_web_enabled")):
        raise AssertionError("live_web_enabled must remain false")
    if bool(safety_state.get("runtime_truth_mutation_enabled")):
        raise AssertionError("runtime_truth_mutation_enabled must remain false")
    if bool(safety_state.get("ai_agent_execution_enabled")):
        raise AssertionError("ai_agent_execution_enabled must remain false")
    if bool(safety_state.get("automatic_updates_enabled")):
        raise AssertionError("automatic_updates_enabled must remain false")

    return True


def handle_governed_web_simulation_dashboard_route(
    payload: Optional[Mapping[str, Any]] = None,
    *,
    route_path: str = DEFAULT_ROUTE_PATH,
) -> Dict[str, Any]:
    safe_payload = dict(payload or {})
    viewer_result = dict(safe_payload.get("viewer_result") or safe_payload.get("result") or {})
    request_id = str(safe_payload.get("request_id") or viewer_result.get("request_id") or "route-adapter-request")

    if build_dashboard_api_response is not None:
        response = build_dashboard_api_response(viewer_result, request_id=request_id)
    else:
        response = _fallback_dashboard_response({"request_id": request_id})

    response["version"] = "v18.09"
    response["route_adapter"] = True
    response["route_path"] = route_path
    response["dashboard_rewired"] = False
    response.setdefault("messages", [])
    if "route_adapter_ready" not in response["messages"]:
        response["messages"].append("route_adapter_ready")
    if "dashboard_route_not_mounted_yet" not in response["messages"]:
        response["messages"].append("dashboard_route_not_mounted_yet")

    response["execution_state"] = _false_execution_state()
    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        response.setdefault("summary", {})[field_name] = False
        for card in response.get("cards") or []:
            card[field_name] = False

    response.setdefault("safety_state", {})
    response["safety_state"].update(
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

    assert_route_response_non_executing(response)
    if assert_dashboard_api_response_non_executing is not None:
        assert_dashboard_api_response_non_executing(response)
    return response


def describe_governed_web_simulation_dashboard_route() -> Dict[str, Any]:
    return {
        "route_path": DEFAULT_ROUTE_PATH,
        "method": "POST",
        "handler": "handle_governed_web_simulation_dashboard_route",
        "mounted": False,
        "dashboard_rewired": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
        "purpose": "dashboard-safe governed web simulation result viewing",
    }
