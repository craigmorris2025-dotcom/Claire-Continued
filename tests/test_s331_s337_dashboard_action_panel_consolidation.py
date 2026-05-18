from __future__ import annotations

from claire.api.dashboard_action_panel_consolidation_s331_s337 import (
    build_dashboard_action_panel_consolidation_s331_s337,
    build_s331_operator_action_registry,
    build_s332_evidence_panel_contract,
    build_s333_update_proposal_panel_contract,
    build_s334_blocked_state_ui_contract,
    build_s335_dashboard_readiness_summary_card,
    build_s336_frontend_binding_manifest,
    build_s337_stop_gate,
    write_frontend_binding_manifest,
)


def test_s331_action_registry_is_visible_but_disabled():
    payload = build_s331_operator_action_registry()
    assert payload["stage_version"] == "S331"
    assert payload["live_action_execution_enabled"] is False
    assert payload["action_registry"]["provider_probe"]["visible"] is True
    assert payload["action_registry"]["provider_probe"]["enabled"] is False


def test_s332_evidence_panel_has_detail_drawer_without_raw_body():
    payload = build_s332_evidence_panel_contract()
    panel = payload["evidence_panel"]
    assert payload["stage_version"] == "S332"
    assert panel["detail_drawer"]["enabled"] is True
    assert panel["detail_drawer"]["raw_body_visible"] is False


def test_s333_update_panel_shows_review_actions_disabled():
    payload = build_s333_update_proposal_panel_contract()
    panel = payload["update_proposal_panel"]
    assert payload["stage_version"] == "S333"
    assert panel["review_actions_visible"] is True
    assert panel["review_actions_enabled"] is False


def test_s334_blocked_state_banners_are_visible():
    payload = build_s334_blocked_state_ui_contract()
    assert payload["stage_version"] == "S334"
    assert payload["all_locked_banners_visible"] is True
    assert payload["blocked_banners"]["automatic_updates"]["visible"] is True


def test_s335_dashboard_summary_reads_consolidated_payload():
    payload = build_s335_dashboard_readiness_summary_card()
    summary = payload["summary_card"]
    assert payload["stage_version"] == "S335"
    assert summary["internet_update_readiness"] == "governed_internet_update_ready"
    assert summary["proposal_count"] == 1


def test_s336_frontend_binding_manifest_lists_required_payload_keys():
    payload = build_s336_frontend_binding_manifest()
    manifest = payload["frontend_binding_manifest"]
    assert payload["stage_version"] == "S336"
    assert "internet_update_proposals" in manifest["required_payload_keys"]
    assert manifest["live_action_execution_enabled"] is False


def test_s336_write_frontend_binding_manifest(tmp_path):
    target = tmp_path / "binding_manifest.json"
    payload = write_frontend_binding_manifest(target)
    assert payload["stage_version"] == "S336"
    assert target.exists()


def test_s337_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s337_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S337"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["live_action_execution_disabled"] is True
    assert payload["checks"]["runtime_mutation_blocked"] is True
    assert payload["dashboard_consolidation_state"] == "contract_consolidated"
    assert "report_path" in payload


def test_s331_s337_rollup_ready():
    payload = build_dashboard_action_panel_consolidation_s331_s337()
    assert payload["stage_version"] == "S337"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
