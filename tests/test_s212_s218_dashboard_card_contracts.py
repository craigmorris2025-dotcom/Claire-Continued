from __future__ import annotations

from runtime_core.api.governed_dashboard_card_contracts import get_dashboard_card_contracts


def test_s212_s218_dashboard_cards_cover_core_operational_sections_without_unsafe_execution():
    payload = get_dashboard_card_contracts()

    assert payload["unsafe_execution_allowed"] is False
    cards = {card["card_id"]: card for card in payload["cards"]}

    for required in [
        "bounded_jobs",
        "evidence_intake",
        "quarantine",
        "update_proposals",
        "review_queue",
        "promotion_candidates",
        "export_ready",
        "authority_locks",
        "blocked_capabilities",
        "payload_health",
        "web_job_state",
    ]:
        assert required in cards
        assert cards[required]["unsafe_execution_allowed"] is False

    assert cards["bounded_jobs"]["action_surface"] == "request_only"
    assert cards["update_proposals"]["action_surface"] == "proposal_only"
    assert cards["promotion_candidates"]["action_surface"] == "manual_approve_reject"
