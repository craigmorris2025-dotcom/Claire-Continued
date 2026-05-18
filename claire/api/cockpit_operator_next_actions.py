from __future__ import annotations

from typing import Dict, List


def get_operator_next_actions() -> Dict[str, object]:
    actions: List[Dict[str, object]] = [
        {
            "action_id": "inspect_current_payload",
            "label": "Inspect Current Payload",
            "enabled": True,
            "authority": "read_only",
            "blocked_reason": None,
        },
        {
            "action_id": "review_quarantined_evidence",
            "label": "Review Quarantined Evidence",
            "enabled": True,
            "authority": "operator_review",
            "blocked_reason": None,
        },
        {
            "action_id": "approve_evidence_promotion",
            "label": "Approve Evidence Promotion",
            "enabled": True,
            "authority": "manual_promotion_only",
            "blocked_reason": None,
        },
        {
            "action_id": "request_bounded_web_job",
            "label": "Request Bounded Web Job",
            "enabled": True,
            "authority": "proposal_only",
            "blocked_reason": None,
        },
        {
            "action_id": "run_autonomous_update",
            "label": "Run Autonomous Update",
            "enabled": False,
            "authority": "blocked",
            "blocked_reason": "automatic_updates_blocked",
        },
        {
            "action_id": "execute_runtime_mutation",
            "label": "Execute Runtime Mutation",
            "enabled": False,
            "authority": "blocked",
            "blocked_reason": "runtime_mutation_blocked",
        },
    ]
    return {
        "version": "v19.89.8-S198-S204",
        "actions": actions,
        "manual_promotion_mandatory": True,
        "quarantine_mandatory": True,
    }
