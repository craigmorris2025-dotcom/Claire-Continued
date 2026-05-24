"""
S331-S337 — Dashboard Action Cards, Evidence Panels, Update Panels, Blocked-State UI.

This pack defines the visible operator controls and panel contracts that should
sit on top of the consolidated dashboard payload. Actions are visible and
contracted, but live execution remains disabled until later explicit action
endpoint gates are installed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from runtime_core.api.dashboard_contract_consolidation_s317_s323 import (
    apply_s317_s323_extension_to_payload,
)
from runtime_core.api.dashboard_operator_cockpit_layout_s324_s330 import (
    build_s330_stop_gate,
)
from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks


PHASE = "S331-S337"
VERSION = "v19.89.8-S331-S337"
PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"


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


def build_s331_operator_action_registry() -> Dict[str, Any]:
    actions = {
        "provider_probe": {
            "label": "Run Provider Probe",
            "method": "POST",
            "endpoint": "/api/internet/provider/probe",
            "visible": True,
            "enabled": False,
            "blocked_reason": "action endpoint gate not installed",
            "requires_confirmation": True,
        },
        "controlled_fetch": {
            "label": "Prepare Controlled Fetch",
            "method": "POST",
            "endpoint": "/api/internet/fetch/controlled",
            "visible": True,
            "enabled": False,
            "blocked_reason": "live fetch gate not installed",
            "requires_confirmation": True,
        },
        "approve_proposal": {
            "label": "Approve Proposal",
            "method": "POST",
            "endpoint": "/api/internet/proposals/approve",
            "visible": True,
            "enabled": False,
            "blocked_reason": "manual approval persistence gate not installed",
            "requires_confirmation": True,
        },
        "export_proposal": {
            "label": "Export Proposal",
            "method": "POST",
            "endpoint": "/api/internet/proposals/export",
            "visible": True,
            "enabled": False,
            "blocked_reason": "export action endpoint deferred",
            "requires_confirmation": True,
        },
    }
    return _base(
        "S331",
        "operator_action_registry_ready",
        action_registry=actions,
        action_count=len(actions),
        live_action_execution_enabled=False,
    )


def build_s332_evidence_panel_contract() -> Dict[str, Any]:
    panel = {
        "panel_key": "internet_evidence",
        "cards": [
            "latest_evidence_capsules",
            "latest_quarantine_items",
            "source_trust_summary",
            "review_needed_count",
        ],
        "detail_drawer": {
            "enabled": True,
            "payload_source": "internet_evidence",
            "raw_body_visible": False,
            "quarantine_visible": True,
        },
        "empty_state": "No governed evidence capsules are waiting.",
    }
    return _base("S332", "evidence_panel_contract_ready", evidence_panel=panel)


def build_s333_update_proposal_panel_contract() -> Dict[str, Any]:
    panel = {
        "panel_key": "internet_update_proposals",
        "cards": [
            "candidate_list",
            "proposal_list",
            "review_queue_status",
            "approved_exports",
            "runtime_mutation_blocked_banner",
        ],
        "review_actions_visible": True,
        "review_actions_enabled": False,
        "empty_state": "No internet update proposals are waiting.",
    }
    return _base("S333", "update_proposal_panel_contract_ready", update_proposal_panel=panel)


def build_s334_blocked_state_ui_contract() -> Dict[str, Any]:
    locks = authority_locks()
    banners = {
        "runtime_mutation": {
            "visible": locks["runtime_mutation_allowed"] is False,
            "severity": "locked",
            "message": "Runtime mutation is blocked.",
        },
        "automatic_updates": {
            "visible": locks["automatic_updates_allowed"] is False,
            "severity": "locked",
            "message": "Automatic internet updates are blocked.",
        },
        "autonomous_crawling": {
            "visible": locks["autonomous_crawling_allowed"] is False,
            "severity": "locked",
            "message": "Autonomous crawling is blocked.",
        },
    }
    return _base(
        "S334",
        "blocked_state_ui_contract_ready",
        blocked_banners=banners,
        all_locked_banners_visible=all(item["visible"] for item in banners.values()),
    )


def build_s335_dashboard_readiness_summary_card() -> Dict[str, Any]:
    payload = apply_s317_s323_extension_to_payload({})
    summary = {
        "card_key": "dashboard_readiness_summary",
        "internet_update_readiness": payload["internet_update_readiness"]["readiness_state"],
        "evidence_review_needed": payload["internet_evidence"]["review_needed_count"],
        "proposal_count": len(payload["internet_update_proposals"]["internet_update_proposals"]),
        "runtime_mutation_status": payload["internet_update_proposals"]["runtime_mutation_status"],
    }
    return _base("S335", "dashboard_readiness_summary_card_ready", summary_card=summary)


def build_s336_frontend_binding_manifest() -> Dict[str, Any]:
    manifest = {
        "manifest_id": "frontend_action_panel_binding_manifest_s331_s337",
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "required_payload_keys": [
            "internet_update_readiness",
            "internet_evidence",
            "internet_update_proposals",
            "cockpit_panel_registry",
            "dashboard_fetch_map_lock",
            "dashboard_renderer_states",
        ],
        "panels": [
            "internet_update_readiness",
            "internet_evidence",
            "internet_update_proposals",
            "blocked_authority_modes",
            "dashboard_readiness_summary",
        ],
        "actions": list(build_s331_operator_action_registry()["action_registry"].keys()),
        "live_action_execution_enabled": False,
    }
    return _base("S336", "frontend_binding_manifest_ready", frontend_binding_manifest=manifest)


def build_s337_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    previous = build_s330_stop_gate()
    action_registry = build_s331_operator_action_registry()
    checks = {
        "previous_gate_ok": previous["ok"],
        "operator_action_registry_ok": action_registry["ok"],
        "evidence_panel_ok": build_s332_evidence_panel_contract()["ok"],
        "proposal_panel_ok": build_s333_update_proposal_panel_contract()["ok"],
        "blocked_state_ui_ok": build_s334_blocked_state_ui_contract()["ok"],
        "readiness_summary_ok": build_s335_dashboard_readiness_summary_card()["ok"],
        "frontend_binding_manifest_ok": build_s336_frontend_binding_manifest()["ok"],
        "live_action_execution_disabled": action_registry["live_action_execution_enabled"] is False,
        "runtime_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S337",
        "dashboard_action_panel_blocked_state_consolidation_passed" if ok else "dashboard_action_panel_blocked_state_consolidation_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="dashboard visual shell integration or action endpoint gates" if ok else "repair S331-S337 dashboard action panels",
        dashboard_consolidation_state="contract_consolidated" if ok else "repair_required",
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s331_s337_dashboard_action_panel_blocked_state.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_dashboard_action_panel_consolidation_s331_s337() -> Dict[str, Any]:
    return _base(
        "S337",
        "dashboard_action_panel_consolidation_ready",
        actions=build_s331_operator_action_registry(),
        evidence_panel=build_s332_evidence_panel_contract(),
        proposal_panel=build_s333_update_proposal_panel_contract(),
        blocked_ui=build_s334_blocked_state_ui_contract(),
        readiness_summary=build_s335_dashboard_readiness_summary_card(),
        frontend_binding_manifest=build_s336_frontend_binding_manifest(),
        stop_gate=build_s337_stop_gate(),
    )


def write_frontend_binding_manifest(path: str | Path) -> Dict[str, Any]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_s336_frontend_binding_manifest()["frontend_binding_manifest"]
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return _base("S336", "frontend_binding_manifest_written", written_path=str(target), frontend_binding_manifest=manifest)


__all__ = [
    "build_s331_operator_action_registry",
    "build_s332_evidence_panel_contract",
    "build_s333_update_proposal_panel_contract",
    "build_s334_blocked_state_ui_contract",
    "build_s335_dashboard_readiness_summary_card",
    "build_s336_frontend_binding_manifest",
    "build_s337_stop_gate",
    "build_dashboard_action_panel_consolidation_s331_s337",
    "write_frontend_binding_manifest",
]
