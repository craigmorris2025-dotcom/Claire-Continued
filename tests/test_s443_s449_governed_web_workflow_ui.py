from __future__ import annotations
from claire.api.dashboard_governed_web_workflow_s443_s449 import *
def test_s443_workflow_has_six_steps(): assert build_s443_workflow_lane_contract()["step_count"]==6
def test_s444_source_input_manual(): assert build_s444_source_input_contract()["source_input"]["manual_operator_entry"] is True
def test_s445_endpoint_map_complete(): 
    p=build_s445_workflow_step_endpoint_map(); assert p["endpoint_count"]==6 and p["endpoints"]["metadata_run"]=="/api/internet/live-metadata/run"
def test_s446_result_model_requires_review(): assert build_s446_workflow_result_model()["result_model"]["requires_manual_review"] is True
def test_s447_guardrails_block_mutation(): 
    g=build_s447_workflow_guardrail_contract()["guardrails"]; assert g["body_read_allowed"] is False and g["runtime_mutation_allowed"] is False
def test_s448_assets_exist(): 
    a=build_s448_workflow_asset_manifest()["assets"]; assert a["js_exists"] and a["css_exists"]
def test_s449_stop_gate_passes(tmp_path): 
    p=build_s449_stop_gate(report_dir=tmp_path); assert p["forward_motion_allowed"] is True and p["dashboard_operational_cockpit_ready"] is True and "report_path" in p
def test_s443_s449_rollup_ready(): assert build_governed_web_workflow_ui_s443_s449()["stop_gate"]["forward_motion_allowed"] is True
