from __future__ import annotations

from typing import Dict, List


def get_blocked_capability_matrix() -> Dict[str, object]:
    blocked: List[Dict[str, object]] = [
        {
            "capability": "automatic_updates",
            "blocked": True,
            "reason": "requires operator review, rollback certainty, and promotion proof",
            "allowed_substitute": "update_proposal_flow",
        },
        {
            "capability": "runtime_mutation",
            "blocked": True,
            "reason": "runtime truth mutation authority not granted",
            "allowed_substitute": "mutation_proposal_review",
        },
        {
            "capability": "continuous_crawling",
            "blocked": True,
            "reason": "continuous web reach requires scheduling, rate-limit, and governance hardening",
            "allowed_substitute": "bounded_operator_approved_web_job",
        },
        {
            "capability": "autonomous_execution",
            "blocked": True,
            "reason": "operator cockpit remains presentation/control layer only",
            "allowed_substitute": "manual_operator_action",
        },
        {
            "capability": "runtime_truth_write",
            "blocked": True,
            "reason": "manual promotion gate remains mandatory",
            "allowed_substitute": "promotion_candidate_record",
        },
    ]
    return {
        "version": "v19.89.8-S212-S218",
        "blocked": blocked,
        "all_unsafe_capabilities_blocked": True,
    }
