from __future__ import annotations

from runtime_core.api.cockpit_operator_next_actions import get_operator_next_actions


def test_s198_s204_operator_next_actions_enable_safe_actions_and_block_unsafe_actions():
    payload = get_operator_next_actions()
    actions = {action["action_id"]: action for action in payload["actions"]}

    assert actions["inspect_current_payload"]["enabled"] is True
    assert actions["review_quarantined_evidence"]["enabled"] is True
    assert actions["approve_evidence_promotion"]["authority"] == "manual_promotion_only"
    assert actions["request_bounded_web_job"]["authority"] == "proposal_only"

    assert actions["run_autonomous_update"]["enabled"] is False
    assert actions["run_autonomous_update"]["blocked_reason"] == "automatic_updates_blocked"
    assert actions["execute_runtime_mutation"]["enabled"] is False
    assert actions["execute_runtime_mutation"]["blocked_reason"] == "runtime_mutation_blocked"

    assert payload["manual_promotion_mandatory"] is True
    assert payload["quarantine_mandatory"] is True
