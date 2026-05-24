from __future__ import annotations

from runtime_core.api.cockpit_action_intent_contract import get_action_intent_contract
from runtime_core.api.cockpit_workflow_card_payloads import get_workflow_card_payloads


def test_s254_s260_action_intents_are_safe_and_non_mutating():
    payload = get_action_intent_contract()
    intents = {intent["intent_id"]: intent for intent in payload["intents"]}

    assert payload["frontend_may_execute_without_backend_contract"] is False
    assert payload["runtime_truth_write_enabled"] is False

    assert intents["request_bounded_web_job"]["authority"] == "proposal_only"
    assert intents["create_update_proposal"]["writes_runtime_truth"] is False
    assert intents["run_autonomous_update"]["enabled_by_default"] is False
    assert intents["run_autonomous_update"]["blocked_reason"] == "automatic_updates_blocked"
    assert intents["execute_runtime_mutation"]["authority"] == "blocked"


def test_s254_s260_workflow_cards_are_safe_for_presentation():
    payload = get_workflow_card_payloads()
    cards = {card["card_id"]: card for card in payload["cards"]}

    assert payload["all_cards_safe_for_presentation"] is True
    assert payload["unsafe_execution_enabled"] is False

    assert cards["review_queue"]["operator_action"] == "open_review_queue"
    assert cards["promotion_candidates"]["state"] == "manual_promotion_required"
    assert cards["export_ready"]["operator_action"] == "export_reviewed_package"
    assert cards["update_proposals"]["state"] == "proposal_only"
    assert cards["bounded_jobs"]["operator_action"] == "request_bounded_web_job"
