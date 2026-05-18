from __future__ import annotations

from typing import Dict, List


def get_operator_audit_trail_contract() -> Dict[str, object]:
    events: List[Dict[str, object]] = [
        {"event_type": "bounded_job_requested", "requires_operator": True, "writes_runtime_truth": False},
        {"event_type": "evidence_quarantined", "requires_operator": False, "writes_runtime_truth": False},
        {"event_type": "review_opened", "requires_operator": True, "writes_runtime_truth": False},
        {"event_type": "promotion_candidate_approved", "requires_operator": True, "writes_runtime_truth": False},
        {"event_type": "promotion_candidate_rejected", "requires_operator": True, "writes_runtime_truth": False},
        {"event_type": "export_created", "requires_operator": True, "writes_runtime_truth": False},
        {"event_type": "blocked_action_attempted", "requires_operator": True, "writes_runtime_truth": False},
    ]
    return {
        "version": "v19.89.8-S261-S267",
        "contract_id": "operator_audit_trail_contract",
        "events": events,
        "append_only": True,
        "runtime_truth_write_enabled": False,
        "persistence_ready": True,
    }
