"""Live update candidate generation contract.

S33R17 defines how update candidates may be proposed later.
It does not fetch, execute, apply, or mutate runtime truth.
"""

from __future__ import annotations

from typing import Any, Dict, List


CANDIDATE_TYPES: List[Dict[str, Any]] = [
    {
        "id": "provider_configuration_update",
        "description": "Suggest provider configuration changes after governed validation.",
        "auto_apply_allowed": False,
    },
    {
        "id": "allowlist_policy_update",
        "description": "Suggest allowlist additions after metadata-only evidence review.",
        "auto_apply_allowed": False,
    },
    {
        "id": "rate_limit_policy_update",
        "description": "Suggest rate-limit adjustments after operator-reviewed evidence.",
        "auto_apply_allowed": False,
    },
    {
        "id": "evidence_promotion_candidate",
        "description": "Suggest quarantined metadata promotion into governed evidence basket.",
        "auto_apply_allowed": False,
    },
]


def get_live_update_candidate_generation_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R17",
        "status": "live_update_candidate_generation_contract_visible",
        "candidate_generation_enabled": False,
        "auto_apply_enabled": False,
        "runtime_truth_write_allowed": False,
        "manual_review_required": True,
        "operator_approval_required": True,
        "candidate_types": CANDIDATE_TYPES,
        "current_candidates": [],
        "candidate_store_enabled": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": "manual update approval workflow contract",
    }
