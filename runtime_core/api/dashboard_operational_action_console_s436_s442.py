"""
S436-S442 operational action console contract.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict
import json
PHASE="S436-S442"; VERSION="v19.89.8-S436-S442"
JS="frontend/cockpit/shell/assets/claire_action_console.js"; CSS="frontend/cockpit/shell/assets/claire_action_console.css"
def _now(): return datetime.now(timezone.utc).isoformat()
def _base(stage,status,**extra):
    p={"stage_version":stage,"phase":PHASE,"version":VERSION,"status":status,"ok":True,"ready":True,
       "runtime_mutation_enabled":False,"automatic_updates_enabled":False,"autonomous_crawling_enabled":False,
       "body_read_allowed":False,"created_at":_now()}; p.update(extra); return p
def build_s436_action_console_contract():
    return _base("S436","action_console_contract_ready", console={"source":"/dashboard/actions/registry","summary":"/dashboard/actions/summary","result_drawer":True,"toast_status":True,"operator_confirmation_default":True,"raw_json_default_visible":False})
def build_s437_action_endpoint_binding_contract():
    b={"provider_probe":"/api/internet/provider/probe","controlled_fetch":"/api/internet/fetch/controlled","proposal_review":"/api/internet/proposals/review","proposal_export":"/api/internet/proposals/export","live_toggle_preflight":"/api/internet/live-toggle/preflight","first_metadata_probe":"/api/internet/live-metadata/run"}
    return _base("S437","action_endpoint_binding_contract_ready",bindings=b,binding_count=len(b))
def build_s438_action_result_drawer_contract():
    return _base("S438","action_result_drawer_contract_ready", result_drawer={"shows_last_action":True,"shows_success_or_error":True,"shows_backend_response":True,"runtime_truth_write_warning":"blocked"})
def build_s439_action_event_log_contract():
    return _base("S439","action_event_log_contract_ready", event_log={"client_side_log":True,"records":["action_name","endpoint","timestamp","status"],"mutation_events_allowed":False})
def build_s440_operator_confirmation_contract():
    return _base("S440","operator_confirmation_contract_ready", confirmation={"operator_confirmed_in_body":True,"default_confirmed":True,"runtime_mutation_actions_available":False})
def build_s441_action_console_asset_manifest():
    return _base("S441","action_console_asset_manifest_ready", assets={"console_js":JS,"console_css":CSS,"js_exists":Path(JS).exists(),"css_exists":Path(CSS).exists()})
def build_s442_stop_gate(report_dir=None):
    checks={"console_contract_ok":build_s436_action_console_contract()["console"]["result_drawer"] is True,
            "bindings_complete":build_s437_action_endpoint_binding_contract()["binding_count"]>=6,
            "result_drawer_ok":build_s438_action_result_drawer_contract()["result_drawer"]["shows_backend_response"] is True,
            "event_log_ok":build_s439_action_event_log_contract()["event_log"]["mutation_events_allowed"] is False,
            "confirmation_ok":build_s440_operator_confirmation_contract()["confirmation"]["runtime_mutation_actions_available"] is False,
            "js_exists":build_s441_action_console_asset_manifest()["assets"]["js_exists"],
            "css_exists":build_s441_action_console_asset_manifest()["assets"]["css_exists"]}
    ok=all(checks.values()); p=_base("S442","operational_action_console_passed" if ok else "operational_action_console_failed",checks=checks,forward_motion_allowed=ok,next_phase="S443-S449 governed web workflow UI" if ok else "repair S436-S442")
    if report_dir:
        d=Path(report_dir); d.mkdir(parents=True, exist_ok=True); r=d/"s436_s442_operational_action_console.json"; r.write_text(json.dumps(p,indent=2),encoding="utf-8"); p["report_path"]=str(r)
    return p
def build_operational_action_console_s436_s442():
    return _base("S442","operational_action_console_ready",console=build_s436_action_console_contract(),bindings=build_s437_action_endpoint_binding_contract(),result_drawer=build_s438_action_result_drawer_contract(),event_log=build_s439_action_event_log_contract(),confirmation=build_s440_operator_confirmation_contract(),assets=build_s441_action_console_asset_manifest(),stop_gate=build_s442_stop_gate())
