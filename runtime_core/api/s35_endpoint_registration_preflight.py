"""S35 endpoint registration preflight.

This module checks whether S35 can proceed to endpoint registration. It does not
register the endpoint and does not patch app.py.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.s35_provider_activation_verifier import get_s35_provider_activation_verifier
from runtime_core.api.guarded_endpoint_registration_decision_gate import (
    get_guarded_endpoint_registration_decision_gate,
)
from runtime_core.api.guarded_route_rollback_proof_validator import (
    get_guarded_route_rollback_proof_validator,
)


def get_s35_endpoint_registration_preflight() -> Dict[str, Any]:
    provider = get_s35_provider_activation_verifier()
    decision = get_guarded_endpoint_registration_decision_gate()
    rollback = get_guarded_route_rollback_proof_validator()

    failures = []
    if provider.get("ready") is not True:
        failures.append("provider_activation_not_ready")
    if decision.get("registration_allowed") is not True:
        failures.append("registration_decision_gate_blocked")
    if rollback.get("rollback_ready") is not True:
        failures.append("rollback_not_ready")

    allowed = len(failures) == 0

    return {
        "version": "v19.89.8-S35R2",
        "status": "registration_preflight_passed" if allowed else "registration_preflight_blocked",
        "registration_allowed": allowed,
        "registration_performed": False,
        "failures": failures,
        "provider_activation": provider,
        "registration_decision": decision,
        "rollback_validator": {
            "rollback_ready": rollback.get("rollback_ready"),
            "endpoint_registered": rollback.get("endpoint_registered"),
            "adapter_defined": rollback.get("adapter_defined"),
        },
        "app_py_patch_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
