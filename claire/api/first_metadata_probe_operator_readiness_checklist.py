"""Operator readiness checklist for first metadata-only probe.

S34R6 is presentation/checklist only.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.api.guarded_endpoint_registration_decision_gate import (
    get_guarded_endpoint_registration_decision_gate,
)


CHECKS: List[Dict[str, Any]] = [
    {
        "id": "provider_configured",
        "label": "Provider configuration present",
        "required": True,
    },
    {
        "id": "safe_router_approved",
        "label": "Safe mounted router approved",
        "required": True,
    },
    {
        "id": "allowlist_ready",
        "label": "Allowlist policy ready",
        "required": True,
    },
    {
        "id": "rate_limit_ready",
        "label": "Rate-limit policy ready",
        "required": True,
    },
    {
        "id": "quarantine_ready",
        "label": "Metadata quarantine path ready",
        "required": True,
    },
    {
        "id": "manual_review_ready",
        "label": "Manual review gate visible",
        "required": True,
    },
]


def get_first_metadata_probe_operator_readiness_checklist() -> Dict[str, Any]:
    decision = get_guarded_endpoint_registration_decision_gate()
    ready = decision.get("registration_allowed") is True

    return {
        "version": "v19.89.8-S34R6",
        "status": "ready_for_registration_review" if ready else "blocked_registration_review_required",
        "ready_for_first_probe": False,
        "registration_allowed_by_gate": ready,
        "operator_checks": CHECKS,
        "execution_button_enabled": False,
        "operator_trigger_required": True,
        "manual_review_required": True,
        "evidence_quarantine_required": True,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": (
            "Only after endpoint registration is proven and provider gates pass "
            "should the cockpit expose a one-shot metadata probe trigger."
        ),
    }
