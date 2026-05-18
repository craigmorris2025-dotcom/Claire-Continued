from __future__ import annotations

from typing import Dict, List


def get_bounded_web_job_record_contract() -> Dict[str, object]:
    states = ["draft", "preflight", "approved", "running_bounded", "quarantined", "review_pending", "complete", "blocked"]
    fields: List[Dict[str, object]] = [
        {"field": "job_id", "required": True, "mutable": False},
        {"field": "query", "required": True, "mutable": False},
        {"field": "bounds", "required": True, "mutable": False},
        {"field": "operator_approved", "required": True, "mutable": True},
        {"field": "state", "required": True, "mutable": True, "allowed": states},
        {"field": "quarantine_location", "required": True, "mutable": False},
        {"field": "created_at", "required": True, "mutable": False},
        {"field": "completed_at", "required": False, "mutable": True},
    ]
    return {
        "version": "v19.89.8-S261-S267",
        "contract_id": "bounded_web_job_record_contract",
        "fields": fields,
        "allowed_states": states,
        "continuous_crawling_enabled": False,
        "operator_approval_required": True,
        "persistence_ready": True,
    }
