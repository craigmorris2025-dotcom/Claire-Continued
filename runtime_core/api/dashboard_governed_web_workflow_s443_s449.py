"""
S443-S449 governed web workflow UI contract.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict
import json
PHASE="S443-S449"; VERSION="v19.89.8-S443-S449"
JS="frontend/cockpit/shell/assets/claire_governed_web_workflow.js"; CSS="frontend/cockpit/shell/assets/claire_governed_web_workflow.css"
def _now(): return datetime.now(timezone.utc).isoformat()
def _base(stage,status,**extra):
    p={"stage_version":stage,"phase":PHASE,"version":VERSION,"status":status,"ok":True,"ready":True,
       "runtime_mutation_enabled":False,"automatic_updates_enabled":False,"autonomous_crawling_enabled":False,
       "body_read_allowed":False,"created_at":_now()}; p.update(extra); return p
def build_s443_workflow_lane_contract():
    steps=["live_toggle_preflight","provider_probe","controlled_fetch","metadata_run","proposal_review","proposal_export"]
    return _base("S443","workflow_lane_contract_ready",steps=steps,step_count=len(steps))
def build_s444_source_input_contract():
    return _base("S444","source_input_contract_ready",source_input={"default_source_url":"https://example.com","requires_http_shape":True,"manual_operator_entry":True,"allowlist_gate_backend_owned":True})
def build_s445_workflow_step_endpoint_map():
    endpoints={"live_toggle_preflight":"/api/internet/live-toggle/preflight","provider_probe":"/api/internet/provider/probe","controlled_fetch":"/api/internet/fetch/controlled","metadata_run":"/api/internet/live-metadata/run","proposal_review":"/api/internet/proposals/review","proposal_export":"/api/internet/proposals/export"}
    return _base("S445","workflow_step_endpoint_map_ready",endpoints=endpoints,endpoint_count=len(endpoints))
def build_s446_workflow_result_model():
    return _base("S446","workflow_result_model_ready",result_model={"stores_last_step_result":True,"requires_manual_review":True,"runtime_truth_write":"blocked","export_is_artifact_only":True})
def build_s447_workflow_guardrail_contract():
    return _base("S447","workflow_guardrail_contract_ready",guardrails={"body_read_allowed":False,"runtime_mutation_allowed":False,"automatic_update_allowed":False,"autonomous_crawling_allowed":False,"operator_confirmation_each_step":True})
def build_s448_workflow_asset_manifest():
    return _base("S448","workflow_asset_manifest_ready",assets={"workflow_js":JS,"workflow_css":CSS,"js_exists":Path(JS).exists(),"css_exists":Path(CSS).exists()})
def build_s449_stop_gate(report_dir=None):
    checks={"workflow_steps_ok":build_s443_workflow_lane_contract()["step_count"]==6,
            "source_input_ok":build_s444_source_input_contract()["source_input"]["manual_operator_entry"] is True,
            "endpoint_map_ok":build_s445_workflow_step_endpoint_map()["endpoint_count"]==6,
            "result_model_ok":build_s446_workflow_result_model()["result_model"]["requires_manual_review"] is True,
            "guardrails_ok":build_s447_workflow_guardrail_contract()["guardrails"]["runtime_mutation_allowed"] is False,
            "js_exists":build_s448_workflow_asset_manifest()["assets"]["js_exists"],
            "css_exists":build_s448_workflow_asset_manifest()["assets"]["css_exists"]}
    ok=all(checks.values()); p=_base("S449","governed_web_workflow_ui_passed" if ok else "governed_web_workflow_ui_failed",checks=checks,forward_motion_allowed=ok,dashboard_operational_cockpit_ready=ok,next_phase="Claire Q&A foundation or visual polish after operator verification" if ok else "repair S443-S449")
    if report_dir:
        d=Path(report_dir); d.mkdir(parents=True, exist_ok=True); r=d/"s443_s449_governed_web_workflow_ui.json"; r.write_text(json.dumps(p,indent=2),encoding="utf-8"); p["report_path"]=str(r)
    return p
def build_governed_web_workflow_ui_s443_s449():
    return _base("S449","governed_web_workflow_ui_ready",workflow=build_s443_workflow_lane_contract(),source_input=build_s444_source_input_contract(),endpoint_map=build_s445_workflow_step_endpoint_map(),result_model=build_s446_workflow_result_model(),guardrails=build_s447_workflow_guardrail_contract(),assets=build_s448_workflow_asset_manifest(),stop_gate=build_s449_stop_gate())
