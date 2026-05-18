"""Guarded route rollback and proof validator.

S34R9 exposes rollback requirements and route proof state.
It does not modify files, register endpoints, or execute probes.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.api.guarded_endpoint_registration_audit import (
    get_guarded_endpoint_registration_audit,
)
from claire.api.router_integration_adapter_contract import (
    get_router_integration_adapter_contract,
)


def get_guarded_route_rollback_proof_validator() -> Dict[str, Any]:
    audit = get_guarded_endpoint_registration_audit()
    adapter = get_router_integration_adapter_contract()

    endpoint_registered = audit.get("endpoint_registered") is True
    rollback_ready = True

    return {
        "version": "v19.89.8-S34R9",
        "status": "rollback_proof_ready_endpoint_registered" if endpoint_registered else "rollback_proof_ready_endpoint_not_registered",
        "rollback_ready": rollback_ready,
        "endpoint_registered": endpoint_registered,
        "adapter_defined": adapter.get("router_available") is True,
        "required_rollback_assets": [
            "backup of changed router module",
            "backup of governed_payload_reconciliation.py",
            "install report",
            "compile result",
            "payload health result",
        ],
        "route_proof": audit,
        "registration_allowed_next": False,
        "reason": (
            "S34R9 is proof/rollback preparation only. Actual route include remains "
            "blocked until an approved mounted router exists."
        ),
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
