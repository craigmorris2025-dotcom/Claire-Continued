"""First metadata probe dry-run simulator.

S34R15 simulates the decision path without executing a network request.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.provider_gate_diagnostic import get_provider_gate_diagnostic
from runtime_core.api.guarded_endpoint_registration_audit import (
    get_guarded_endpoint_registration_audit,
)
from runtime_core.api.guarded_metadata_probe_request_policy import (
    validate_guarded_metadata_probe_request,
)


def get_first_metadata_probe_dry_run_simulator() -> Dict[str, Any]:
    diagnostic = get_provider_gate_diagnostic()
    audit = get_guarded_endpoint_registration_audit()

    sample_policy = validate_guarded_metadata_probe_request(
        target_url="https://www.googleapis.com",
        operator_trigger_id="dry_run_only",
        method="HEAD",
    )

    endpoint_registered = audit.get("endpoint_registered") is True
    gates_ready = diagnostic.get("ready_for_operator_probe_after_endpoint_registration") is True
    request_policy_passed = sample_policy.get("accepted_for_future_execution") is True

    dry_run_passed = endpoint_registered and gates_ready and request_policy_passed

    return {
        "version": "v19.89.8-S34R15",
        "status": "dry_run_passed" if dry_run_passed else "dry_run_blocked",
        "dry_run_only": True,
        "network_request_performed": False,
        "endpoint_registered": endpoint_registered,
        "provider_gates_ready": gates_ready,
        "request_policy_passed": request_policy_passed,
        "sample_policy": sample_policy,
        "ready_for_real_operator_probe": dry_run_passed,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": (
            "If dry-run passes, perform one operator-triggered metadata-only HEAD "
            "probe through registered guarded endpoint."
        ),
    }
