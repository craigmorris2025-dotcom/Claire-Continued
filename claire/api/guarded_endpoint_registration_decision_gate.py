"""Guarded endpoint registration decision gate.

S34R5 produces the final registration decision for this plateau.
It does not perform registration.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.api.safe_mounted_router_comparator import get_safe_mounted_router_comparator
from claire.api.governed_provider_readiness_validator import get_governed_provider_readiness_validator
from claire.api.allowlist_rate_limit_enforcement_proof import (
    get_allowlist_rate_limit_enforcement_proof,
)


def get_guarded_endpoint_registration_decision_gate() -> Dict[str, Any]:
    router = get_safe_mounted_router_comparator()
    readiness = get_governed_provider_readiness_validator()
    policy = get_allowlist_rate_limit_enforcement_proof()

    failures = []
    if router.get("safe_router_approved") is not True:
        failures.append("safe_mounted_router_not_approved")
    if readiness.get("readiness_passed") is not True:
        failures.append("provider_readiness_not_passed")
    if policy.get("allowlist_policy_present") is not True:
        failures.append("allowlist_policy_missing")
    if policy.get("rate_limit_policy_present") is not True:
        failures.append("rate_limit_policy_missing")

    registration_allowed = len(failures) == 0

    return {
        "version": "v19.89.8-S34R5",
        "status": "registration_allowed" if registration_allowed else "registration_blocked",
        "registration_allowed": registration_allowed,
        "registration_performed": False,
        "failures": failures,
        "decision_inputs": {
            "safe_router_approved": router.get("safe_router_approved"),
            "provider_readiness_passed": readiness.get("readiness_passed"),
            "allowlist_policy_present": policy.get("allowlist_policy_present"),
            "rate_limit_policy_present": policy.get("rate_limit_policy_present"),
        },
        "endpoint_candidate": "/api/governed-web/metadata-probe",
        "method": "POST",
        "app_py_patch_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": (
            "If registration_allowed is true in a future audited state, register via "
            "an existing safe router module only, never by blind app.py patching."
        ),
    }
