from __future__ import annotations

from runtime_core.api.dashboard_operator_cockpit_layout_s324_s330 import (
    build_operator_cockpit_layout_consolidation_s324_s330,
    build_s324_single_cockpit_layout_contract,
    build_s325_top_command_search_bar_contract,
    build_s326_internet_update_zone_contract,
    build_s327_evidence_review_zone_contract,
    build_s328_proposal_review_zone_contract,
    build_s329_visual_state_manifest,
    build_s330_stop_gate,
    write_frontend_manifest,
)


def test_s324_single_cockpit_layout_has_required_zones():
    payload = build_s324_single_cockpit_layout_contract()
    zones = payload["zones"]
    assert payload["stage_version"] == "S324"
    assert "top_command" in zones
    assert "evidence_review" in zones
    assert "proposal_review" in zones
    assert payload["old_scattered_layout_allowed"] is False


def test_s325_top_command_bar_is_persistent_but_not_agent_execution():
    payload = build_s325_top_command_search_bar_contract()
    bar = payload["command_bar"]
    assert payload["stage_version"] == "S325"
    assert bar["placement"] == "top_persistent"
    assert bar["ai_agent_execution_enabled"] is False
    assert bar["operator_confirmation_required"] is True


def test_s326_internet_update_zone_requires_blocked_modes():
    payload = build_s326_internet_update_zone_contract()
    zone = payload["zone"]
    assert payload["stage_version"] == "S326"
    assert zone["zone_id"] == "internet_update_zone"
    assert zone["must_show_blocked_modes"] is True


def test_s327_evidence_review_zone_uses_internet_evidence_payload_key():
    payload = build_s327_evidence_review_zone_contract()
    zone = payload["zone"]
    assert payload["stage_version"] == "S327"
    assert "internet_evidence" in zone["payload_keys"]


def test_s328_proposal_zone_shows_actions_but_does_not_execute_live():
    payload = build_s328_proposal_review_zone_contract()
    zone = payload["zone"]
    assert payload["stage_version"] == "S328"
    assert zone["operator_actions_visible"] is True
    assert zone["operator_actions_execute_live"] is False


def test_s329_visual_manifest_forbids_fake_connected_state():
    payload = build_s329_visual_state_manifest()
    manifest = payload["frontend_manifest"]
    assert payload["stage_version"] == "S329"
    assert "do_not_show_fake_connected_state" in manifest["renderer_requirements"]


def test_s329_write_frontend_manifest(tmp_path):
    target = tmp_path / "manifest.json"
    payload = write_frontend_manifest(target)
    assert payload["stage_version"] == "S329"
    assert target.exists()


def test_s330_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s330_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S330"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["merged_payload_has_internet_readiness"] is True
    assert "report_path" in payload


def test_s324_s330_rollup_ready():
    payload = build_operator_cockpit_layout_consolidation_s324_s330()
    assert payload["stage_version"] == "S330"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
