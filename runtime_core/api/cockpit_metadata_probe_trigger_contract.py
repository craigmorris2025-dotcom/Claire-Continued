"""Cockpit metadata probe trigger contract.

S34R11 exposes the trigger state for the cockpit. It remains disabled unless
endpoint registration is proven and gates pass.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.guarded_endpoint_registration_audit import (
    get_guarded_endpoint_registration_audit,
)
from runtime_core.api.governed_provider_readiness_validator import (
    get_governed_provider_readiness_validator,
)


def get_cockpit_metadata_probe_trigger_contract() -> Dict[str, Any]:
    audit = get_guarded_endpoint_registration_audit()
    readiness = get_governed_provider_readiness_validator()

    endpoint_registered = audit.get("endpoint_registered") is True
    provider_ready = readiness.get("readiness_passed") is True
    trigger_enabled = endpoint_registered and provider_ready

    return {
        "version": "v19.89.8-S34R11",
        "status": "trigger_enabled" if trigger_enabled else "trigger_visible_disabled",
        "trigger_visible": True,
        "trigger_enabled": trigger_enabled,
        "endpoint_registered": endpoint_registered,
        "provider_ready": provider_ready,
        "operator_trigger_required": True,
        "manual_review_required": True,
        "evidence_quarantine_required": True,
        "execution_mode": "metadata_only_head",
        "network_request": "blocked_until_operator_trigger" if trigger_enabled else "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
