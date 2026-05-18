from __future__ import annotations

from typing import Dict, List


def get_workflow_card_payloads() -> Dict[str, object]:
    cards: List[Dict[str, object]] = [
        {
            "card_id": "review_queue",
            "title": "Review Queue",
            "state": "manual_required",
            "empty_message": "No review items are currently queued.",
            "operator_action": "open_review_queue",
        },
        {
            "card_id": "promotion_candidates",
            "title": "Promotion Candidates",
            "state": "manual_promotion_required",
            "empty_message": "No promotion candidates are currently waiting.",
            "operator_action": "approve_promotion_candidate",
        },
        {
            "card_id": "export_ready",
            "title": "Export Ready",
            "state": "operator_approved_export",
            "empty_message": "No reviewed packages are ready for export.",
            "operator_action": "export_reviewed_package",
        },
        {
            "card_id": "update_proposals",
            "title": "Update Proposals",
            "state": "proposal_only",
            "empty_message": "No update proposals are currently drafted.",
            "operator_action": "create_update_proposal",
        },
        {
            "card_id": "bounded_jobs",
            "title": "Bounded Web Jobs",
            "state": "operator_requested_only",
            "empty_message": "No bounded web jobs are currently active.",
            "operator_action": "request_bounded_web_job",
        },
    ]
    return {
        "version": "v19.89.8-S254-S260",
        "cards": cards,
        "all_cards_safe_for_presentation": True,
        "unsafe_execution_enabled": False,
    }
