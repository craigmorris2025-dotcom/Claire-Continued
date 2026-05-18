"""Guarded endpoint non-mutating registration plan.

S34R7 defines exactly how registration may happen later without blind app.py patching.
It does not perform registration.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.api.guarded_endpoint_registration_decision_gate import (
    get_guarded_endpoint_registration_decision_gate,
)


REGISTRATION_STRATEGIES: List[Dict[str, Any]] = [
    {
        "id": "existing_safe_router_module_include",
        "allowed": True,
        "description": (
            "Attach guarded metadata probe router only through an already-mounted "
            "router module that is explicitly approved by allowlist proof."
        ),
        "forbidden": [
            "blind_app_py_patch",
            "new_unmounted_router_assumption",
            "runtime_truth_mutation",
            "automatic_execution",
        ],
    },
    {
        "id": "app_py_patch",
        "allowed": False,
        "description": "Direct claire/app.py patching remains forbidden after S33R4 rollback.",
    },
]


def get_guarded_endpoint_non_mutating_registration_plan() -> Dict[str, Any]:
    decision = get_guarded_endpoint_registration_decision_gate()
    registration_allowed = decision.get("registration_allowed") is True

    return {
        "version": "v19.89.8-S34R7",
        "status": "registration_plan_ready" if registration_allowed else "registration_plan_blocked",
        "registration_allowed_by_gate": registration_allowed,
        "registration_performed": False,
        "strategies": REGISTRATION_STRATEGIES,
        "selected_strategy": (
            "existing_safe_router_module_include" if registration_allowed else None
        ),
        "required_before_apply": [
            "safe_mounted_router_approved",
            "provider_readiness_passed",
            "allowlist_policy_present",
            "rate_limit_policy_present",
            "rollback_plan_present",
            "compile_changed_modules_only",
        ],
        "app_py_patch_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
