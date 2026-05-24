from __future__ import annotations

from runtime_core.api.cockpit_card_state_normalizer import get_card_state_normalizer_contract
from runtime_core.api.cockpit_render_safety_contract import get_render_safety_contract


def test_s226_s232_render_safety_prevents_blank_or_unsafe_cockpit_states():
    payload = get_render_safety_contract()
    safety = payload["render_safety"]

    assert safety["blank_main_result_allowed"] is False
    assert safety["missing_payload_fallback_required"] is True
    assert safety["blocked_action_explanation_required"] is True
    assert safety["diagnostics_hidden_by_default"] is True
    assert safety["unsafe_button_disable_required"] is True
    assert safety["backend_state_required_for_enabled_buttons"] is True

    fallbacks = {state["state_id"]: state for state in payload["fallback_states"]}
    assert fallbacks["payload_unavailable"]["allows_operator_action"] is False
    assert fallbacks["insufficient_data"]["allows_operator_action"] is True
    assert fallbacks["blocked_by_governance"]["allows_operator_action"] is False


def test_s226_s232_card_state_normalizer_blocks_unsafe_status_invention():
    payload = get_card_state_normalizer_contract()
    states = {state["state"]: state for state in payload["normalized_states"]}

    assert states["ready"]["operator_action_allowed"] is True
    assert states["pending_review"]["operator_action_allowed"] is True
    assert states["proposal_only"]["operator_action_allowed"] is True
    assert states["blocked"]["operator_action_allowed"] is False
    assert states["read_only"]["operator_action_allowed"] is False
    assert states["unavailable"]["operator_action_allowed"] is False
