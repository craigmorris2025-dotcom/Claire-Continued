from __future__ import annotations

from typing import Dict, List


def get_warning_banner_contracts() -> Dict[str, object]:
    banners: List[Dict[str, object]] = [
        {
            "banner_id": "runtime_mutation_blocked",
            "severity": "critical",
            "visible_when": "runtime_mutation_requested",
            "message": "Runtime mutation is blocked. Only mutation proposals may be created.",
            "operator_action": "review_proposal_only",
        },
        {
            "banner_id": "automatic_updates_blocked",
            "severity": "critical",
            "visible_when": "automatic_update_requested",
            "message": "Automatic updates are blocked. Create an update proposal instead.",
            "operator_action": "create_update_proposal",
        },
        {
            "banner_id": "quarantine_required",
            "severity": "warning",
            "visible_when": "new_external_evidence_detected",
            "message": "External evidence must remain quarantined until manual review.",
            "operator_action": "review_quarantine",
        },
        {
            "banner_id": "manual_promotion_required",
            "severity": "warning",
            "visible_when": "promotion_candidate_ready",
            "message": "Manual promotion is required before evidence can influence runtime truth.",
            "operator_action": "approve_or_reject_candidate",
        },
        {
            "banner_id": "continuous_crawling_blocked",
            "severity": "critical",
            "visible_when": "continuous_crawl_requested",
            "message": "Continuous crawling is blocked. Use bounded operator-approved jobs only.",
            "operator_action": "request_bounded_job",
        },
    ]
    return {
        "version": "v19.89.8-S219-S225",
        "banners": banners,
        "unsafe_actions_redirected": True,
    }
