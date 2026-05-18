"""Cockpit manual review gate for metadata probe evidence.

S33R14 is passive review governance only.
"""

from __future__ import annotations

from typing import Any, Dict, List


REVIEW_ACTIONS: List[Dict[str, Any]] = [
    {
        "id": "view_quarantine",
        "label": "View quarantined metadata",
        "enabled": True,
        "execution": "read_only_presentation",
    },
    {
        "id": "approve_promotion",
        "label": "Approve evidence promotion",
        "enabled": False,
        "execution": "blocked_until_quarantine_record_exists",
    },
    {
        "id": "reject_promotion",
        "label": "Reject evidence promotion",
        "enabled": False,
        "execution": "blocked_until_quarantine_record_exists",
    },
    {
        "id": "execute_live_probe",
        "label": "Execute live probe",
        "enabled": False,
        "execution": "blocked",
    },
]


def get_cockpit_manual_review_gate() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R14",
        "status": "manual_review_gate_visible",
        "review_required": True,
        "promotion_enabled": False,
        "live_execution_enabled": False,
        "actions": REVIEW_ACTIONS,
        "quarantine_record_required": True,
        "operator_approval_required": True,
        "runtime_truth_write_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
