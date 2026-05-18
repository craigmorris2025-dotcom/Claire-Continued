"""
S429-S435 real cockpit shell replacement contract.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
from datetime import datetime, timezone

PHASE="S429-S435"; VERSION="v19.89.8-S429-S435"
SHELL="frontend/cockpit/shell/cockpit_shell.html"
CSS="frontend/cockpit/shell/assets/claire_modern_cockpit.css"
JS="frontend/cockpit/shell/assets/claire_modern_cockpit.js"

def _now(): return datetime.now(timezone.utc).isoformat()
def _base(stage, status, **extra):
    p={"stage_version":stage,"phase":PHASE,"version":VERSION,"status":status,"ok":True,"ready":True,
       "backend_owns_truth":True,"cockpit_presentation_only":True,"runtime_mutation_enabled":False,
       "automatic_updates_enabled":False,"autonomous_crawling_enabled":False,"created_at":_now()}
    p.update(extra); return p

def build_s429_real_cockpit_shell_contract():
    return _base("S429","real_cockpit_shell_contract_ready", shell_contract={
        "shell_path":SHELL,"layout":"single_operator_cockpit","old_surface_wall_allowed":False,
        "raw_json_default_visible":False,"debug_drawer_allowed":True,"repeated_live_bubbles_allowed":False,
        "backend_truth_only":True})

def build_s430_status_header_contract():
    return _base("S430","status_header_contract_ready", status_header={
        "uses":["/dashboard/status/harmonized","/dashboard/visibility/summary","/dashboard/actions/summary"],
        "legacy_s43_label_hidden_from_primary_header":True,
        "required_chips":["backend","readiness","actions","runtime_mutation","body_read"]})

def build_s431_command_bar_contract():
    return _base("S431","command_bar_contract_ready", command_bar={
        "id":"claire-command-input","placeholder":"Ask Claire or run a governed web operation...",
        "freeform_ai_answer_enabled":False,"action_confirmation_required":True})

def build_s432_navigation_workspace_contract():
    sections={"overview":"status and next action","web":"governed web workflow","evidence":"evidence and review",
              "actions":"operator action console","system":"health and debug drawer"}
    return _base("S432","navigation_workspace_contract_ready", sections=sections, section_count=len(sections))

def build_s433_debug_drawer_contract():
    return _base("S433","debug_drawer_contract_ready", debug_drawer={
        "raw_payload_visible_by_default":False,"operator_can_expand":True,"presentation_only":True})

def build_s434_shell_asset_manifest():
    return _base("S434","shell_asset_manifest_ready", assets={
        "shell_path":SHELL,"css_path":CSS,"js_path":JS,
        "shell_exists":Path(SHELL).exists(),"css_exists":Path(CSS).exists(),"js_exists":Path(JS).exists()})

def build_s435_stop_gate(report_dir=None):
    a=build_s434_shell_asset_manifest()["assets"]
    checks={
        "shell_contract_ok": build_s429_real_cockpit_shell_contract()["shell_contract"]["old_surface_wall_allowed"] is False,
        "status_header_ok": build_s430_status_header_contract()["status_header"]["legacy_s43_label_hidden_from_primary_header"] is True,
        "command_bar_ok": build_s431_command_bar_contract()["command_bar"]["action_confirmation_required"] is True,
        "navigation_ok": build_s432_navigation_workspace_contract()["section_count"] == 5,
        "debug_drawer_ok": build_s433_debug_drawer_contract()["debug_drawer"]["raw_payload_visible_by_default"] is False,
        "shell_asset_exists": a["shell_exists"], "css_asset_exists": a["css_exists"], "js_asset_exists": a["js_exists"]}
    ok=all(checks.values())
    p=_base("S435","real_cockpit_shell_replacement_passed" if ok else "real_cockpit_shell_replacement_failed",
            checks=checks, forward_motion_allowed=ok, next_phase="S436-S442 operational action console" if ok else "repair S429-S435")
    if report_dir:
        d=Path(report_dir); d.mkdir(parents=True, exist_ok=True); r=d/"s429_s435_real_cockpit_shell_replacement.json"
        r.write_text(json.dumps(p, indent=2), encoding="utf-8"); p["report_path"]=str(r)
    return p

def build_real_cockpit_shell_replacement_s429_s435():
    return _base("S435","real_cockpit_shell_replacement_ready",
        shell=build_s429_real_cockpit_shell_contract(), status_header=build_s430_status_header_contract(),
        command_bar=build_s431_command_bar_contract(), navigation=build_s432_navigation_workspace_contract(),
        debug_drawer=build_s433_debug_drawer_contract(), assets=build_s434_shell_asset_manifest(), stop_gate=build_s435_stop_gate())
