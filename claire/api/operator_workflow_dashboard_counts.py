from __future__ import annotations

from typing import Dict

from claire.api.operator_workflow_storage_adapter import get_workflow_counts


def get_operator_dashboard_counts() -> Dict[str, object]:
    counts_payload = get_workflow_counts()
    counts = counts_payload["counts"]

    return {
        "version": "v19.89.8-S268-S274",
        "review_queue_count": counts.get("review_queue", 0),
        "bounded_web_job_count": counts.get("bounded_web_jobs", 0),
        "export_count": counts.get("exports", 0),
        "audit_event_count": counts.get("audit_trail", 0),
        "dashboard_ready": True,
        "runtime_truth_write_enabled": False,
    }
