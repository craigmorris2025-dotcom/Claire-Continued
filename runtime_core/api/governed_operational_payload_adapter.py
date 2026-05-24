from __future__ import annotations

from typing import Dict, List


def get_governed_operational_payload() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S212-S218",
        "payload_contract": "governed_operational_payload_adapter",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority_locks": {
            "runtime_truth_write": False,
            "runtime_mutation": False,
            "automatic_updates": False,
            "autonomous_execution": False,
            "continuous_crawling": False,
        },
        "dashboard_sections": [
            {
                "section_id": "internet_operations",
                "label": "Internet Operations",
                "state": "governed_ready",
                "cards": ["bounded_jobs", "evidence_intake", "quarantine", "update_proposals"],
            },
            {
                "section_id": "operator_review",
                "label": "Operator Review",
                "state": "manual_required",
                "cards": ["review_queue", "promotion_candidates", "export_ready"],
            },
            {
                "section_id": "governance",
                "label": "Governance",
                "state": "locked",
                "cards": ["authority_locks", "blocked_capabilities", "manual_promotion"],
            },
            {
                "section_id": "monitoring",
                "label": "Monitoring",
                "state": "contract_ready",
                "cards": ["payload_health", "web_job_state", "queue_state", "warnings"],
            },
        ],
    }


def list_dashboard_section_ids() -> List[str]:
    return [section["section_id"] for section in get_governed_operational_payload()["dashboard_sections"]]
