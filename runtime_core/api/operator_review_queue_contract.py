from __future__ import annotations

from typing import Dict, List


def get_review_queue_contract() -> Dict[str, object]:
    fields: List[Dict[str, object]] = [
        {"field": "review_id", "required": True, "mutable": False},
        {"field": "source_type", "required": True, "mutable": False},
        {"field": "evidence_basket_id", "required": True, "mutable": False},
        {"field": "created_at", "required": True, "mutable": False},
        {"field": "status", "required": True, "mutable": True, "allowed": ["pending", "approved", "rejected", "needs_more_evidence"]},
        {"field": "operator_note", "required": False, "mutable": True},
        {"field": "promotion_candidate", "required": True, "mutable": False},
    ]
    return {
        "version": "v19.89.8-S261-S267",
        "contract_id": "operator_review_queue_contract",
        "fields": fields,
        "runtime_truth_write_enabled": False,
        "manual_review_required": True,
        "persistence_ready": True,
    }
