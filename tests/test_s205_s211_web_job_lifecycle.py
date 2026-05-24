from __future__ import annotations

from runtime_core.api.governed_web_job_lifecycle import get_web_job_lifecycle_contract


def test_s205_s211_web_job_lifecycle_is_visible_bounded_and_not_continuous():
    payload = get_web_job_lifecycle_contract()
    states = {state["state_id"]: state for state in payload["states"]}

    assert payload["version"] == "v19.89.8-S205-S211"
    assert payload["continuous_crawling_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
    assert payload["operator_approval_required"] is True

    assert states["approved_bounded_probe"]["allows_network_action"] is True
    assert states["approved_bounded_probe"]["requires_manual_approval"] is True
    assert states["result_quarantined"]["allows_network_action"] is False
    assert states["blocked_by_governance"]["terminal"] is True
