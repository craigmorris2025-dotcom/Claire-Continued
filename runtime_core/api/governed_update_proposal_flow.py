from __future__ import annotations

from typing import Dict, List


def get_update_proposal_flow() -> Dict[str, object]:
    steps: List[Dict[str, object]] = [
        {
            "step_id": "detect_update_need",
            "label": "Detect Update Need",
            "authority": "analysis_only",
            "writes_runtime_truth": False,
        },
        {
            "step_id": "create_update_proposal",
            "label": "Create Update Proposal",
            "authority": "proposal_only",
            "writes_runtime_truth": False,
        },
        {
            "step_id": "attach_evidence_basket",
            "label": "Attach Evidence Basket",
            "authority": "quarantine_only",
            "writes_runtime_truth": False,
        },
        {
            "step_id": "operator_review",
            "label": "Operator Review",
            "authority": "manual_review",
            "writes_runtime_truth": False,
        },
        {
            "step_id": "approve_for_future_execution",
            "label": "Approve For Future Execution",
            "authority": "approval_record_only",
            "writes_runtime_truth": False,
        },
        {
            "step_id": "execute_runtime_update",
            "label": "Execute Runtime Update",
            "authority": "blocked",
            "writes_runtime_truth": False,
            "blocked_reason": "automatic_updates_and_runtime_mutation_blocked",
        },
    ]
    return {
        "version": "v19.89.8-S205-S211",
        "stage_range": "S205-S211",
        "flow": steps,
        "automatic_update_execution_enabled": False,
        "runtime_mutation_enabled": False,
        "operator_review_required": True,
    }
