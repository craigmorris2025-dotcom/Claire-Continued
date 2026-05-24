"""
S345-S351 — Frontend Cockpit Renderer Integration.

This pack creates the frontend renderer contract and static renderer assets that
consume the integrated /dashboard/payload from S338-S344. It safely injects the
renderer into the cockpit shell when that shell exists.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from runtime_core.api.dashboard_payload_live_integration_s338_s344 import (
    get_s338_s344_integrated_dashboard_payload,
)
from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks


PHASE = "S345-S351"
VERSION = "v19.89.8-S345-S351"
PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"
RENDERER_JS = "frontend/cockpit/consolidated/s345_s351_cockpit_renderer.js"
RENDERER_CSS = "frontend/cockpit/consolidated/s345_s351_cockpit_renderer.css"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "stage_version": stage_version,
        "phase": PHASE,
        "version": VERSION,
        "status": status,
        "ok": True,
        "ready": True,
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "status_endpoint": STATUS_ENDPOINT,
        "authority_locks": authority_locks(),
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "proposal_only": True,
        "runtime_truth_modified": False,
        "created_at": _timestamp(),
    }
    payload.update(extra)
    return payload


def build_s345_frontend_state_object_contract() -> Dict[str, Any]:
    return _base(
        "S345",
        "frontend_state_object_contract_ready",
        state_object={
            "name": "ClaireCockpitState",
            "source": PAYLOAD_ENDPOINT,
            "required_keys": [
                "internet_update_readiness",
                "internet_evidence",
                "internet_update_proposals",
                "cockpit_panel_registry",
                "dashboard_renderer_states",
            ],
            "read_only": True,
            "invent_state_allowed": False,
        },
    )


def build_s346_renderer_asset_manifest() -> Dict[str, Any]:
    return _base(
        "S346",
        "renderer_asset_manifest_ready",
        renderer_assets={
            "javascript": RENDERER_JS,
            "stylesheet": RENDERER_CSS,
            "mount_target_id": "claire-consolidated-cockpit",
            "auto_create_mount_if_missing": True,
            "fetch_endpoint": PAYLOAD_ENDPOINT,
        },
    )


def build_s347_panel_dom_binding_contract() -> Dict[str, Any]:
    bindings = {
        "internet_update_readiness": {"selector": "[data-claire-panel='internet_update_readiness']", "payload_key": "internet_update_readiness"},
        "internet_evidence": {"selector": "[data-claire-panel='internet_evidence']", "payload_key": "internet_evidence"},
        "internet_update_proposals": {"selector": "[data-claire-panel='internet_update_proposals']", "payload_key": "internet_update_proposals"},
        "blocked_authority_modes": {"selector": "[data-claire-panel='blocked_authority_modes']", "payload_key": "authority_locks"},
    }
    return _base("S347", "panel_dom_binding_contract_ready", dom_bindings=bindings, binding_count=len(bindings))


def build_s348_renderer_state_behavior_contract() -> Dict[str, Any]:
    return _base(
        "S348",
        "renderer_state_behavior_contract_ready",
        renderer_behaviors={
            "loading": "show loading message while fetching payload",
            "missing": "show missing payload key message",
            "blocked": "show blocked authority reason",
            "error": "show payload fetch or parse error",
            "ready": "show backend-provided payload",
        },
        hide_missing_data_allowed=False,
        fake_connected_labels_allowed=False,
    )


def build_s349_command_bar_visual_integration_contract() -> Dict[str, Any]:
    return _base(
        "S349",
        "command_bar_visual_integration_contract_ready",
        command_bar={
            "selector": "#claire-consolidated-command-bar",
            "placeholder": "Ask Claire or prepare a governed web check...",
            "question_answer_enabled": False,
            "agent_action_enabled": False,
            "visible": True,
            "position": "top",
        },
    )


def build_s350_frontend_visual_smoke_contract() -> Dict[str, Any]:
    payload = get_s338_s344_integrated_dashboard_payload()
    checks = {
        "payload_has_readiness": "internet_update_readiness" in payload,
        "payload_has_evidence": "internet_evidence" in payload,
        "payload_has_proposals": "internet_update_proposals" in payload,
        "payload_has_renderer_states": "dashboard_renderer_states" in payload,
        "payload_has_panel_registry": "cockpit_panel_registry" in payload,
    }
    return _base(
        "S350",
        "frontend_visual_smoke_contract_passed" if all(checks.values()) else "frontend_visual_smoke_contract_failed",
        checks=checks,
        smoke_ok=all(checks.values()),
    )


def build_s351_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    checks = {
        "state_object_contract_ok": build_s345_frontend_state_object_contract()["ok"],
        "renderer_asset_manifest_ok": build_s346_renderer_asset_manifest()["ok"],
        "panel_dom_binding_ok": build_s347_panel_dom_binding_contract()["ok"],
        "renderer_state_behavior_ok": build_s348_renderer_state_behavior_contract()["ok"],
        "command_bar_contract_ok": build_s349_command_bar_visual_integration_contract()["ok"],
        "frontend_visual_smoke_ok": build_s350_frontend_visual_smoke_contract()["smoke_ok"],
        "runtime_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S351",
        "frontend_cockpit_renderer_integration_passed" if ok else "frontend_cockpit_renderer_integration_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S352-S358 live dashboard visibility smoke proof" if ok else "repair S345-S351 frontend renderer",
        remaining_packs_to_live_dashboard_visibility=1,
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s345_s351_frontend_cockpit_renderer_integration.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_frontend_cockpit_renderer_integration_s345_s351() -> Dict[str, Any]:
    return _base(
        "S351",
        "frontend_cockpit_renderer_integration_ready",
        state_object=build_s345_frontend_state_object_contract(),
        renderer_assets=build_s346_renderer_asset_manifest(),
        dom_bindings=build_s347_panel_dom_binding_contract(),
        renderer_states=build_s348_renderer_state_behavior_contract(),
        command_bar=build_s349_command_bar_visual_integration_contract(),
        visual_smoke=build_s350_frontend_visual_smoke_contract(),
        stop_gate=build_s351_stop_gate(),
    )


__all__ = [
    "build_s345_frontend_state_object_contract",
    "build_s346_renderer_asset_manifest",
    "build_s347_panel_dom_binding_contract",
    "build_s348_renderer_state_behavior_contract",
    "build_s349_command_bar_visual_integration_contract",
    "build_s350_frontend_visual_smoke_contract",
    "build_s351_stop_gate",
    "build_frontend_cockpit_renderer_integration_s345_s351",
]
