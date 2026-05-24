"""Controlled guarded endpoint registration attempt.

S34R10 is fail-closed by default. It does not patch claire/app.py.
It only reports what would be required for safe router-module registration.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.guarded_endpoint_registration_decision_gate import (
    get_guarded_endpoint_registration_decision_gate,
)
from runtime_core.api.guarded_endpoint_non_mutating_registration_plan import (
    get_guarded_endpoint_non_mutating_registration_plan,
)


def get_controlled_guarded_endpoint_registration_attempt() -> Dict[str, Any]:
    decision = get_guarded_endpoint_registration_decision_gate()
    plan = get_guarded_endpoint_non_mutating_registration_plan()

    allowed = (
        decision.get("registration_allowed") is True
        and plan.get("registration_allowed_by_gate") is True
        and plan.get("selected_strategy") == "existing_safe_router_module_include"
    )

    return {
        "version": "v19.89.8-S34R10",
        "status": "registration_attempt_ready" if allowed else "registration_attempt_blocked",
        "registration_allowed": allowed,
        "registration_performed": False,
        "app_py_patch_allowed": False,
        "selected_strategy": plan.get("selected_strategy"),
        "decision_failures": decision.get("failures", []),
        "required_next_if_blocked": [
            "provider readiness must pass",
            "safe mounted router must be explicitly approved",
            "allowlist policy must be present",
            "rate-limit policy must be present",
        ],
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
