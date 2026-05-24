from __future__ import annotations

from runtime_core.api.cockpit_live_governance_banners import get_live_governance_banners
from runtime_core.api.cockpit_workflow_binding_readiness import get_workflow_binding_readiness


def test_s254_s260_live_governance_banners_surface_core_locks():
    payload = get_live_governance_banners()
    banners = {banner["banner_id"]: banner for banner in payload["banners"]}

    assert payload["unsafe_actions_redirected"] is True
    assert banners["backend_owns_truth"]["always_visible"] is True
    assert banners["manual_promotion_required"]["severity"] == "warning"
    assert banners["quarantine_required"]["always_visible"] is True
    assert banners["automatic_updates_blocked"]["severity"] == "critical"
    assert banners["runtime_mutation_blocked"]["severity"] == "critical"


def test_s254_s260_workflow_binding_readiness_marks_visual_workflow_ready_not_daily_use_complete():
    payload = get_workflow_binding_readiness()

    assert payload["workflow_cards_ready"] is True
    assert payload["action_intents_ready"] is True
    assert payload["governance_banners_ready"] is True
    assert payload["shell_binding_ready"] is True
    assert payload["operator_workflow_visualization_ready"] is True
    assert payload["authority_locks_preserved"] is True

    remaining = set(payload["remaining_before_daily_use"])
    assert "real queue persistence" in remaining
    assert "real bounded web job records" in remaining
    assert "review approval persistence" in remaining
