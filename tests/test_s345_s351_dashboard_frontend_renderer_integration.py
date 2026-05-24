from __future__ import annotations

from pathlib import Path

from runtime_core.api.dashboard_frontend_renderer_integration_s345_s351 import (
    build_frontend_cockpit_renderer_integration_s345_s351,
    build_s345_frontend_state_object_contract,
    build_s346_renderer_asset_manifest,
    build_s347_panel_dom_binding_contract,
    build_s348_renderer_state_behavior_contract,
    build_s349_command_bar_visual_integration_contract,
    build_s350_frontend_visual_smoke_contract,
    build_s351_stop_gate,
)


def test_s345_frontend_state_object_uses_payload_truth():
    payload = build_s345_frontend_state_object_contract()
    state = payload["state_object"]
    assert payload["stage_version"] == "S345"
    assert state["source"] == "/dashboard/payload"
    assert state["invent_state_allowed"] is False


def test_s346_renderer_assets_exist_after_installer():
    payload = build_s346_renderer_asset_manifest()
    assets = payload["renderer_assets"]
    assert payload["stage_version"] == "S346"
    assert Path(assets["javascript"]).exists()
    assert Path(assets["stylesheet"]).exists()


def test_s347_panel_dom_binding_has_required_panels():
    payload = build_s347_panel_dom_binding_contract()
    bindings = payload["dom_bindings"]
    assert payload["stage_version"] == "S347"
    assert "internet_update_readiness" in bindings
    assert "internet_evidence" in bindings
    assert "internet_update_proposals" in bindings


def test_s348_renderer_state_behavior_forbids_fake_connected_labels():
    payload = build_s348_renderer_state_behavior_contract()
    assert payload["stage_version"] == "S348"
    assert payload["hide_missing_data_allowed"] is False
    assert payload["fake_connected_labels_allowed"] is False


def test_s349_command_bar_visible_but_not_ai_enabled_yet():
    payload = build_s349_command_bar_visual_integration_contract()
    bar = payload["command_bar"]
    assert payload["stage_version"] == "S349"
    assert bar["visible"] is True
    assert bar["question_answer_enabled"] is False
    assert bar["agent_action_enabled"] is False


def test_s350_frontend_visual_smoke_passes():
    payload = build_s350_frontend_visual_smoke_contract()
    assert payload["stage_version"] == "S350"
    assert payload["smoke_ok"] is True
    assert all(payload["checks"].values())


def test_s351_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s351_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S351"
    assert payload["forward_motion_allowed"] is True
    assert "report_path" in payload


def test_s345_s351_rollup_ready():
    payload = build_frontend_cockpit_renderer_integration_s345_s351()
    assert payload["stage_version"] == "S351"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
