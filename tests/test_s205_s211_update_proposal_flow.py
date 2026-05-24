from __future__ import annotations

from runtime_core.api.governed_update_proposal_flow import get_update_proposal_flow


def test_s205_s211_update_proposal_flow_blocks_runtime_update_execution():
    payload = get_update_proposal_flow()
    steps = {step["step_id"]: step for step in payload["flow"]}

    assert payload["automatic_update_execution_enabled"] is False
    assert payload["runtime_mutation_enabled"] is False
    assert payload["operator_review_required"] is True

    assert steps["create_update_proposal"]["authority"] == "proposal_only"
    assert steps["attach_evidence_basket"]["authority"] == "quarantine_only"
    assert steps["execute_runtime_update"]["authority"] == "blocked"
    assert steps["execute_runtime_update"]["writes_runtime_truth"] is False
