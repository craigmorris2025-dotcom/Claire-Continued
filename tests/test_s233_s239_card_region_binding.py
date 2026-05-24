from __future__ import annotations

from runtime_core.api.cockpit_card_region_binding import get_card_region_binding_contract


def test_s233_s239_card_region_binding_maps_required_cards_to_correct_regions():
    payload = get_card_region_binding_contract()
    bindings = {item["card_id"]: item for item in payload["bindings"]}

    assert payload["frontend_can_reassign_required_cards"] is False
    assert bindings["command_surface"]["region_id"] == "top_command_bar"
    assert bindings["next_action"]["region_id"] == "primary_runtime_panel"
    assert bindings["bounded_jobs"]["region_id"] == "operations_strip"
    assert bindings["payload_health"]["region_id"] == "monitoring_column"
    assert bindings["raw_payload"]["region_id"] == "diagnostics_drawer"
    assert bindings["raw_payload"]["required"] is False
