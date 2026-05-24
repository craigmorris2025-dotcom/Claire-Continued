from __future__ import annotations

from typing import Dict, List


def get_action_intent_contract() -> Dict[str, object]:
    intents: List[Dict[str, object]] = [
        {
            "intent_id": "request_bounded_web_job",
            "label": "Request Bounded Web Job",
            "authority": "proposal_only",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": True,
        },
        {
            "intent_id": "open_review_queue",
            "label": "Open Review Queue",
            "authority": "read_only",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": True,
        },
        {
            "intent_id": "approve_promotion_candidate",
            "label": "Approve Promotion Candidate",
            "authority": "manual_promotion_only",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": True,
        },
        {
            "intent_id": "export_reviewed_package",
            "label": "Export Reviewed Package",
            "authority": "operator_approved_export",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": True,
        },
        {
            "intent_id": "create_update_proposal",
            "label": "Create Update Proposal",
            "authority": "proposal_only",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": True,
        },
        {
            "intent_id": "run_autonomous_update",
            "label": "Run Autonomous Update",
            "authority": "blocked",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": False,
            "blocked_reason": "automatic_updates_blocked",
        },
        {
            "intent_id": "execute_runtime_mutation",
            "label": "Execute Runtime Mutation",
            "authority": "blocked",
            "requires_operator": True,
            "writes_runtime_truth": False,
            "enabled_by_default": False,
            "blocked_reason": "runtime_mutation_blocked",
        },
    ]
    return {
        "version": "v19.89.8-S254-S260",
        "intents": intents,
        "frontend_may_execute_without_backend_contract": False,
        "runtime_truth_write_enabled": False,
    }
