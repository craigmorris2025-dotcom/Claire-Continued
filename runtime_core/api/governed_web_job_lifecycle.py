from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class WebJobLifecycleState:
    state_id: str
    label: str
    operator_visible: bool
    allows_network_action: bool
    requires_manual_approval: bool
    terminal: bool


WEB_JOB_STATES: List[WebJobLifecycleState] = [
    WebJobLifecycleState("draft_request", "Draft Request", True, False, True, False),
    WebJobLifecycleState("preflight_pending", "Preflight Pending", True, False, True, False),
    WebJobLifecycleState("approved_bounded_probe", "Approved Bounded Probe", True, True, True, False),
    WebJobLifecycleState("result_quarantined", "Result Quarantined", True, False, True, False),
    WebJobLifecycleState("review_pending", "Review Pending", True, False, True, False),
    WebJobLifecycleState("promotion_candidate", "Promotion Candidate", True, False, True, False),
    WebJobLifecycleState("operator_export_ready", "Operator Export Ready", True, False, True, True),
    WebJobLifecycleState("blocked_by_governance", "Blocked By Governance", True, False, False, True),
]


def get_web_job_lifecycle_contract() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S205-S211",
        "stage_range": "S205-S211",
        "states": [asdict(state) for state in WEB_JOB_STATES],
        "continuous_crawling_enabled": False,
        "automatic_updates_enabled": False,
        "operator_approval_required": True,
    }
