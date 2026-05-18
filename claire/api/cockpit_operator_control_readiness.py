from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class OperatorControlReadiness:
    control_id: str
    label: str
    backend_contract_required: bool
    visual_state_required: bool
    monitoring_signal_required: bool
    operator_review_required: bool
    execution_authority: str


CONTROLS: List[OperatorControlReadiness] = [
    OperatorControlReadiness("bounded_web_job_request", "Request Bounded Web Job", True, True, True, True, "proposal_only"),
    OperatorControlReadiness("review_evidence_basket", "Review Evidence Basket", True, True, True, True, "operator_review"),
    OperatorControlReadiness("export_reviewed_package", "Export Reviewed Package", True, True, True, True, "operator_approved"),
    OperatorControlReadiness("inspect_source_lineage", "Inspect Source Lineage", True, True, True, False, "read_only"),
    OperatorControlReadiness("approve_promotion_candidate", "Approve Promotion Candidate", True, True, True, True, "manual_promotion_only"),
    OperatorControlReadiness("request_mutation_proposal", "Request Mutation Proposal", True, True, True, True, "proposal_only"),
    OperatorControlReadiness("view_runtime_lock_state", "View Runtime Lock State", True, True, True, False, "read_only"),
]


def get_operator_control_readiness() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S191-S197",
        "stage_range": "S191-S197",
        "controls": [asdict(item) for item in CONTROLS],
        "unsafe_authority_enabled": False,
        "blocked_capabilities": [
            "runtime_truth_write",
            "runtime_mutation",
            "automatic_updates",
            "autonomous_execution",
            "continuous_crawling",
        ],
    }
