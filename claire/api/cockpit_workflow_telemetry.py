from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class WorkflowSignal:
    signal_id: str
    label: str
    source_surface: str
    dashboard_zone: str
    severity: str
    requires_operator_attention: bool
    execution_authority: str


WORKFLOW_SIGNALS: List[WorkflowSignal] = [
    WorkflowSignal("payload_health", "Payload Health", "dashboard_payload", "monitoring_column", "info", False, "read_only"),
    WorkflowSignal("review_queue_count", "Review Queue Count", "review_queue", "monitoring_column", "attention", True, "operator_review"),
    WorkflowSignal("quarantine_pending", "Quarantine Pending", "evidence_quarantine", "monitoring_column", "attention", True, "manual_review_only"),
    WorkflowSignal("web_job_status", "Web Job Status", "bounded_web_jobs", "operations_strip", "info", False, "proposal_only"),
    WorkflowSignal("export_ready", "Export Ready", "export_queue", "operations_strip", "attention", True, "operator_approved"),
    WorkflowSignal("governance_lock_state", "Governance Lock State", "authority_locks", "top_command_bar", "critical", False, "read_only"),
    WorkflowSignal("mutation_proposal_waiting", "Mutation Proposal Waiting", "proposal_queue", "review_workspace", "attention", True, "proposal_only"),
]


def get_workflow_telemetry_contract() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S198-S204",
        "stage_range": "S198-S204",
        "signals": [asdict(signal) for signal in WORKFLOW_SIGNALS],
        "dashboard_ready": True,
        "unsafe_execution_enabled": False,
    }
