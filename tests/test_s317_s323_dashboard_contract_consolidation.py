from __future__ import annotations

from claire.api.dashboard_contract_consolidation_s317_s323 import (
    apply_s317_s323_extension_to_payload,
    build_dashboard_contract_consolidation_s317_s323,
    build_s317_canonical_payload_extension_registry,
    build_s318_internet_readiness_payload_extension,
    build_s319_dashboard_fetch_map_lock,
    build_s320_cockpit_panel_registry,
    build_s321_missing_data_blocked_state_contract,
    build_s322_dashboard_schema_validation,
    build_s323_stop_gate,
)


def test_s317_extension_registry_targets_existing_dashboard_payload():
    payload = build_s317_canonical_payload_extension_registry()
    assert payload["stage_version"] == "S317"
    assert payload["endpoint_strategy"] == "extend_existing_dashboard_payload"
    assert payload["random_endpoint_sprawl_allowed"] is False
    assert payload["extension_count"] == 3


def test_s318_payload_extension_exposes_internet_readiness_sections():
    payload = build_s318_internet_readiness_payload_extension()
    extension = payload["dashboard_payload_extension"]
    assert payload["stage_version"] == "S318"
    assert "internet_update_readiness" in extension
    assert "internet_evidence" in extension
    assert "internet_update_proposals" in extension
    assert extension["internet_update_readiness"]["readiness_state"] == "governed_internet_update_ready"


def test_s319_fetch_map_uses_single_boot_payload():
    payload = build_s319_dashboard_fetch_map_lock()
    assert payload["stage_version"] == "S319"
    assert payload["single_boot_payload"] is True
    assert payload["random_panel_fetches_allowed"] is False
    assert set(payload["fetch_map"].values()) == {"/dashboard/payload", "/dashboard/payload/status"}


def test_s320_panel_registry_points_panels_to_payload_keys():
    payload = build_s320_cockpit_panel_registry()
    panels = payload["panel_registry"]
    assert payload["stage_version"] == "S320"
    assert panels["internet_evidence"]["payload_key"] == "internet_evidence"
    assert panels["internet_update_proposals"]["truth_source"] == "/dashboard/payload"


def test_s321_missing_state_contract_forbids_fake_connected_labels():
    payload = build_s321_missing_data_blocked_state_contract()
    assert payload["stage_version"] == "S321"
    assert payload["fake_connected_labels_allowed"] is False
    assert "blocked" in payload["renderer_states"]


def test_s322_schema_validation_passes_for_internet_sections():
    payload = build_s322_dashboard_schema_validation()
    assert payload["stage_version"] == "S322"
    assert payload["validation_ok"] is True
    assert all(payload["checks"].values())


def test_s323_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s323_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S323"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["schema_validation_ok"] is True
    assert "report_path" in payload


def test_s317_s323_payload_merge_does_not_mutate_input():
    original = {"existing": True}
    merged = apply_s317_s323_extension_to_payload(original)
    assert original == {"existing": True}
    assert merged["existing"] is True
    assert "internet_update_readiness" in merged
    assert "cockpit_panel_registry" in merged


def test_s317_s323_rollup_ready():
    payload = build_dashboard_contract_consolidation_s317_s323()
    assert payload["stage_version"] == "S323"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
