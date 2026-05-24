"""First guarded live update path contract.

S33R19 defines the first non-autonomous live update path.
It does not enable or apply live updates.
"""

from __future__ import annotations

from typing import Any, Dict, List


GUARDED_UPDATE_PATH_STEPS: List[Dict[str, Any]] = [
    {
        "step": 1,
        "name": "metadata_probe_result_quarantined",
        "required": True,
        "automatic": False,
    },
    {
        "step": 2,
        "name": "operator_reviews_quarantine_record",
        "required": True,
        "automatic": False,
    },
    {
        "step": 3,
        "name": "operator_promotes_evidence",
        "required": True,
        "automatic": False,
    },
    {
        "step": 4,
        "name": "candidate_generated_from_promoted_evidence",
        "required": True,
        "automatic": False,
    },
    {
        "step": 5,
        "name": "operator_approves_candidate",
        "required": True,
        "automatic": False,
    },
    {
        "step": 6,
        "name": "staged_update_written_to_review_area",
        "required": True,
        "automatic": False,
    },
    {
        "step": 7,
        "name": "runtime_truth_update_requires_separate_future_gate",
        "required": True,
        "automatic": False,
    },
]


def get_first_guarded_live_update_path_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R19",
        "status": "first_guarded_live_update_path_contract_visible_non_autonomous",
        "live_update_path_defined": True,
        "live_update_apply_enabled": False,
        "automatic_updates": "blocked",
        "autonomous_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "runtime_truth_write_allowed": False,
        "operator_approval_required": True,
        "manual_promotion_required": True,
        "staged_review_area_required": True,
        "rollback_plan_required": True,
        "path_steps": GUARDED_UPDATE_PATH_STEPS,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "next_safe_step": (
            "endpoint registration may be attempted only after safe mounted router "
            "proof is explicitly approved and provider gates pass"
        ),
    }
