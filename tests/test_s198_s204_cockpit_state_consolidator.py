from __future__ import annotations

from runtime_core.api.cockpit_state_consolidator import get_consolidated_cockpit_state


def test_s198_s204_consolidated_cockpit_has_required_layout_zones():
    payload = get_consolidated_cockpit_state()

    zones = {zone["zone_id"]: zone for zone in payload["zones"]}
    required = {
        "top_command_bar",
        "primary_runtime_panel",
        "operations_strip",
        "monitoring_column",
        "lifecycle_evidence_workspace",
        "diagnostics_drawer",
    }

    assert payload["layout_contract"] == "precision_consolidated_cockpit"
    assert required.issubset(zones)
    assert zones["diagnostics_drawer"]["must_remain_visible"] is False

    for zone in zones.values():
        assert zone["backend_owned"] is True


def test_s198_s204_consolidated_cockpit_preserves_unsafe_authority_locks():
    payload = get_consolidated_cockpit_state()
    locks = payload["unsafe_authority"]

    assert locks["runtime_truth_write"] is False
    assert locks["runtime_mutation"] is False
    assert locks["automatic_updates"] is False
    assert locks["autonomous_execution"] is False
    assert locks["continuous_crawling"] is False
