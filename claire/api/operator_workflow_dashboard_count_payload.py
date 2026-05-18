from __future__ import annotations

from typing import Dict

try:
    from claire.api.operator_workflow_dashboard_counts import get_operator_dashboard_counts
except Exception:
    def get_operator_dashboard_counts() -> Dict[str, object]:
        return {
            "review_queue_count": 0,
            "bounded_web_job_count": 0,
            "export_count": 0,
            "audit_event_count": 0,
            "dashboard_ready": True,
            "runtime_truth_write_enabled": False,
        }


def build_dashboard_live_count_payload() -> Dict[str, object]:
    counts = get_operator_dashboard_counts()
    return {
        "version": "v19.89.8-S275-S281",
        "payload_id": "operator_workflow_dashboard_live_counts",
        "cards": {
            "review_queue": {
                "label": "Review Queue",
                "count": counts.get("review_queue_count", 0),
                "action": "open_review_queue",
            },
            "bounded_web_jobs": {
                "label": "Bounded Web Jobs",
                "count": counts.get("bounded_web_job_count", 0),
                "action": "request_bounded_web_job",
            },
            "exports": {
                "label": "Exports",
                "count": counts.get("export_count", 0),
                "action": "export_reviewed_package",
            },
            "audit_trail": {
                "label": "Audit Trail",
                "count": counts.get("audit_event_count", 0),
                "action": "inspect_audit_trail",
            },
        },
        "dashboard_ready": True,
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
    }
