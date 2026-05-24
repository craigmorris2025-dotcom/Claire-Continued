from __future__ import annotations

from runtime_core.api.cockpit_frontend_presentation_schema import (
    get_frontend_presentation_schema,
    get_region_order,
)


def test_s219_s225_frontend_schema_has_precise_required_regions_in_order():
    payload = get_frontend_presentation_schema()

    assert payload["schema_id"] == "cockpit_frontend_presentation_schema"
    assert payload["backend_owns_truth"] is True
    assert payload["frontend_owns_layout_only"] is True

    assert get_region_order() == [
        "top_command_bar",
        "primary_runtime_panel",
        "operations_strip",
        "monitoring_column",
        "lifecycle_evidence_workspace",
        "diagnostics_drawer",
    ]


def test_s219_s225_frontend_schema_keeps_command_and_governance_visible():
    regions = {region["region_id"]: region for region in get_frontend_presentation_schema()["required_regions"]}

    assert regions["top_command_bar"]["sticky"] is True
    assert "command_surface" in regions["top_command_bar"]["required_cards"]
    assert "governance_locks" in regions["top_command_bar"]["required_cards"]
    assert "next_action" in regions["primary_runtime_panel"]["required_cards"]
