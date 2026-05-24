from __future__ import annotations
from runtime_core.api.dashboard_real_cockpit_shell_s429_s435 import *

def test_s429_shell_contract_replaces_surface_wall():
    p=build_s429_real_cockpit_shell_contract()
    assert p["stage_version"]=="S429"
    assert p["shell_contract"]["old_surface_wall_allowed"] is False
    assert p["shell_contract"]["repeated_live_bubbles_allowed"] is False

def test_s430_status_header_hides_legacy_label():
    assert build_s430_status_header_contract()["status_header"]["legacy_s43_label_hidden_from_primary_header"] is True

def test_s431_command_bar_requires_confirmation():
    b=build_s431_command_bar_contract()["command_bar"]
    assert b["freeform_ai_answer_enabled"] is False
    assert b["action_confirmation_required"] is True

def test_s432_navigation_has_five_sections():
    p=build_s432_navigation_workspace_contract()
    assert p["section_count"]==5 and "web" in p["sections"]

def test_s433_debug_drawer_hides_raw_payload_by_default():
    assert build_s433_debug_drawer_contract()["debug_drawer"]["raw_payload_visible_by_default"] is False

def test_s434_assets_exist():
    a=build_s434_shell_asset_manifest()["assets"]
    assert a["shell_exists"] and a["css_exists"] and a["js_exists"]

def test_s435_stop_gate_passes(tmp_path):
    p=build_s435_stop_gate(report_dir=tmp_path)
    assert p["forward_motion_allowed"] is True and "report_path" in p

def test_s429_s435_rollup_ready():
    assert build_real_cockpit_shell_replacement_s429_s435()["stop_gate"]["forward_motion_allowed"] is True
