from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

from .governed_web_simulation_fastapi_route import (
    describe_fastapi_route_registration,
    register_governed_web_simulation_route,
)


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


class RouteMountProbeApp:
    def __init__(self) -> None:
        self.routers: List[Any] = []

    def include_router(self, router: Any) -> None:
        self.routers.append(router)


def assert_mount_verification_non_executing(report: Mapping[str, Any]) -> bool:
    execution_state = dict(report.get("execution_state") or {})
    safety_state = dict(report.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")

    if bool(report.get("dashboard_rewired")):
        raise AssertionError("dashboard_rewired must remain false")
    if bool(report.get("production_app_mutated")):
        raise AssertionError("production_app_mutated must remain false")
    if bool(report.get("live_web_enabled")):
        raise AssertionError("live_web_enabled must remain false")
    if bool(report.get("runtime_truth_mutation_enabled")):
        raise AssertionError("runtime_truth_mutation_enabled must remain false")
    if bool(report.get("ai_agent_execution_enabled")):
        raise AssertionError("ai_agent_execution_enabled must remain false")
    if bool(report.get("automatic_updates_enabled")):
        raise AssertionError("automatic_updates_enabled must remain false")

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

    return True


def verify_governed_web_simulation_route_mount(
    app: Optional[Any] = None,
    *,
    mutate_supplied_app: bool = False,
) -> Dict[str, Any]:
    """
    Verify route mount behavior safely.

    v18.11.1 repair:
    - Never mutates a supplied/production app.
    - Always uses RouteMountProbeApp for mountability proof.
    - Keeps mutate_supplied_app only as an observed request flag for audit clarity.
    """
    route_description = describe_fastapi_route_registration()

    probe_app = RouteMountProbeApp()
    registration = register_governed_web_simulation_route(probe_app)
    routers_count = len(probe_app.routers)

    report = {
        "build": "v18.11.1",
        "created_at": _utc_now(),
        "verifier": "governed_web_simulation_route_mount_verifier",
        "route_path": route_description.get("route_path"),
        "method": route_description.get("method"),
        "probe_app_used": True,
        "supplied_app_present": app is not None,
        "mutate_supplied_app_requested": bool(mutate_supplied_app),
        "mutate_supplied_app_honored": False,
        "production_app_mutated": False,
        "mount_verified": bool(registration.get("registered")),
        "registration": registration,
        "routers_count": routers_count,
        "dashboard_rewired": False,
        "live_web_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
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
            "production_app_mutation_enabled": False,
        },
        "messages": [
            "mount_verification_complete",
            "probe_app_only",
            "production_app_not_mutated",
            "simulation_route_only",
            "no_live_web_enabled",
            "no_runtime_truth_mutation",
            "no_ai_agent_execution",
            "no_automatic_updates",
        ],
    }

    assert_mount_verification_non_executing(report)
    return report


def describe_route_mount_verifier() -> Dict[str, Any]:
    return {
        "build": "v18.11.1",
        "name": "Search Bar Governed Web Simulation Route Mount Verifier Repair",
        "auto_mounts_production_app": False,
        "mutates_supplied_app": False,
        "uses_probe_app_only": True,
        "dashboard_rewired": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
