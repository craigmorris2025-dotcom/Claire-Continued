from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover
    APIRouter = None

from .governed_web_simulation_dashboard_route_adapter import (
    DEFAULT_ROUTE_PATH,
    handle_governed_web_simulation_dashboard_route,
)


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


def assert_fastapi_route_response_non_executing(response: Mapping[str, Any]) -> bool:
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
        raise AssertionError("dashboard_rewired must remain false in v18.10")
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


def governed_web_simulation_dashboard_endpoint(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    response = handle_governed_web_simulation_dashboard_route(payload or {}, route_path=DEFAULT_ROUTE_PATH)
    response["version"] = "v18.10"
    response["fastapi_route_shim"] = True
    response["dashboard_rewired"] = False
    response["execution_state"] = _false_execution_state()
    response.setdefault("messages", [])
    if "fastapi_route_shim_ready" not in response["messages"]:
        response["messages"].append("fastapi_route_shim_ready")
    if "explicit_registration_required" not in response["messages"]:
        response["messages"].append("explicit_registration_required")
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
    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        response.setdefault("summary", {})[field_name] = False
        for card in response.get("cards") or []:
            card[field_name] = False
    assert_fastapi_route_response_non_executing(response)
    return response


def create_governed_web_simulation_router():
    """Create a FastAPI APIRouter only when FastAPI is available."""
    if APIRouter is None:
        return None

    router = APIRouter(prefix="", tags=["search-bar-governed-web-simulation"])

    @router.post(DEFAULT_ROUTE_PATH)
    def _post_governed_web_simulation_dashboard(payload: Dict[str, Any]) -> Dict[str, Any]:
        return governed_web_simulation_dashboard_endpoint(payload)

    return router


def register_governed_web_simulation_route(app: Any) -> Dict[str, Any]:
    """
    Explicit registration helper.

    This does not run automatically. Call it from the main app only when the
    operator wants this route mounted.
    """
    router = create_governed_web_simulation_router()
    registered = False
    reason = None

    if router is None:
        reason = "fastapi_not_available"
    elif app is None or not hasattr(app, "include_router"):
        reason = "app_missing_include_router"
    else:
        app.include_router(router)
        registered = True

    result = {
        "build": "v18.10",
        "route_path": DEFAULT_ROUTE_PATH,
        "registered": registered,
        "reason": reason,
        "dashboard_rewired": False,
        "execution_state": _false_execution_state(),
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
    }
    assert_fastapi_route_response_non_executing(
        {
            "execution_state": result["execution_state"],
            "summary": _false_execution_state(),
            "cards": [],
            "safety_state": result["safety_state"],
            "dashboard_rewired": False,
        }
    )
    return result


def describe_fastapi_route_registration() -> Dict[str, Any]:
    return {
        "build": "v18.10",
        "route_path": DEFAULT_ROUTE_PATH,
        "method": "POST",
        "fastapi_router_factory": "create_governed_web_simulation_router",
        "explicit_registration_helper": "register_governed_web_simulation_route",
        "auto_registered": False,
        "dashboard_rewired": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
