from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class DashboardCardContract:
    card_id: str
    section_id: str
    title: str
    source_contract: str
    action_surface: str
    unsafe_execution_allowed: bool


CARDS: List[DashboardCardContract] = [
    DashboardCardContract("bounded_jobs", "internet_operations", "Bounded Jobs", "governed_web_job_lifecycle", "request_only", False),
    DashboardCardContract("evidence_intake", "internet_operations", "Evidence Intake", "governed_evidence_intake_checkpoints", "read_only", False),
    DashboardCardContract("quarantine", "internet_operations", "Quarantine", "governed_evidence_intake_checkpoints", "review_only", False),
    DashboardCardContract("update_proposals", "internet_operations", "Update Proposals", "governed_update_proposal_flow", "proposal_only", False),
    DashboardCardContract("review_queue", "operator_review", "Review Queue", "operator_review_queue", "operator_review", False),
    DashboardCardContract("promotion_candidates", "operator_review", "Promotion Candidates", "manual_promotion", "manual_approve_reject", False),
    DashboardCardContract("export_ready", "operator_review", "Export Ready", "export_queue", "operator_approved_export", False),
    DashboardCardContract("authority_locks", "governance", "Authority Locks", "authority_lock_contract", "read_only", False),
    DashboardCardContract("blocked_capabilities", "governance", "Blocked Capabilities", "authority_lock_contract", "read_only", False),
    DashboardCardContract("manual_promotion", "governance", "Manual Promotion", "promotion_governance", "read_only", False),
    DashboardCardContract("payload_health", "monitoring", "Payload Health", "monitoring_backend", "read_only", False),
    DashboardCardContract("web_job_state", "monitoring", "Web Job State", "governed_web_job_lifecycle", "read_only", False),
    DashboardCardContract("queue_state", "monitoring", "Queue State", "monitoring_backend", "read_only", False),
    DashboardCardContract("warnings", "monitoring", "Warnings", "operator_notifications", "read_only", False),
]


def get_dashboard_card_contracts() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S212-S218",
        "cards": [asdict(card) for card in CARDS],
        "unsafe_execution_allowed": False,
    }
