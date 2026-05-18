"""Manual update approval workflow contract.

S33R18 prepares approval flow for update candidates.
It does not approve, apply, or execute updates.
"""

from __future__ import annotations

from typing import Any, Dict, List


APPROVAL_STATES: List[str] = [
    "candidate_created",
    "operator_review_required",
    "approved_for_staged_apply",
    "rejected",
    "expired",
]

REQUIRED_APPROVAL_FIELDS: List[str] = [
    "candidate_id",
    "candidate_type",
    "evidence_reference",
    "operator_id",
    "approval_decision",
    "approval_timestamp_utc",
    "rollback_plan",
]


def get_manual_update_approval_workflow_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R18",
        "status": "manual_update_approval_workflow_contract_visible",
        "approval_workflow_enabled": False,
        "apply_enabled": False,
        "auto_approval_allowed": False,
        "automatic_updates": "blocked",
        "runtime_truth_write_allowed": False,
        "approval_states": APPROVAL_STATES,
        "required_approval_fields": REQUIRED_APPROVAL_FIELDS,
        "pending_approvals": [],
        "operator_approval_required": True,
        "rollback_required_before_apply": True,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "next_safe_step": "first guarded live update path contract, non-autonomous",
    }
