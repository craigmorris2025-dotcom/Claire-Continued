"""
S324-S330 — Operator Cockpit Layout Consolidation.

This pack defines the single cockpit layout contract that should render the
S317-S323 payload extension. It still does not mutate runtime truth and does not
replace the launcher. It creates the layout blueprint and a frontend manifest
the next visual pass can consume.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from runtime_core.api.dashboard_contract_consolidation_s317_s323 import (
    apply_s317_s323_extension_to_payload,
    build_s323_stop_gate,
)
from runtime_core.api.governed_internet_update_foundation_s296_s302 import authority_locks


PHASE = "S324-S330"
VERSION = "v19.89.8-S324-S330"
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


def build_s324_single_cockpit_layout_contract() -> Dict[str, Any]:
    zones = {
        "top_command": ["search_command_bar", "provider_state", "blocked_authority_banner"],
        "primary_status": ["internet_update_readiness", "system_health", "latest_job"],
        "evidence_review": ["internet_evidence", "quarantine", "source_trust"],
        "proposal_review": ["internet_update_proposals", "review_queue", "approved_exports"],
        "system_governance": ["blocked_authority_modes", "fetch_map", "panel_registry"],
    }
    return _base(
        "S324",
        "single_cockpit_layout_contract_ready",
        layout_id="operator_cockpit_single_payload_layout",
        zones=zones,
        zone_count=len(zones),
        dashboard_truth_policy="backend_payload_only",
        old_scattered_layout_allowed=False,
    )


def build_s325_top_command_search_bar_contract() -> Dict[str, Any]:
    return _base(
        "S325",
        "top_command_search_bar_contract_ready",
        command_bar={
            "component_id": "claire_top_command_bar",
            "placement": "top_persistent",
            "modes": ["dashboard_search", "runtime_question", "governed_provider_probe_intent"],
            "ai_agent_execution_enabled": False,
            "operator_confirmation_required": True,
            "placeholder": "Ask Claire, search system state, or prepare a governed web check...",
        },
    )


def build_s326_internet_update_zone_contract() -> Dict[str, Any]:
    return _base(
        "S326",
        "internet_update_zone_contract_ready",
        zone={
            "zone_id": "internet_update_zone",
            "cards": [
                "internet_update_readiness",
                "provider_status",
                "source_policy",
                "latest_governed_update_run",
            ],
            "payload_keys": ["internet_update_readiness", "governed_internet_contracts"],
            "must_show_blocked_modes": True,
        },
    )


def build_s327_evidence_review_zone_contract() -> Dict[str, Any]:
    return _base(
        "S327",
        "evidence_review_zone_contract_ready",
        zone={
            "zone_id": "evidence_review_zone",
            "cards": [
                "internet_evidence",
                "quarantine_summary",
                "source_trust_summary",
                "review_needed_evidence",
            ],
            "payload_keys": ["internet_evidence"],
            "empty_state": "No governed evidence capsules are waiting for review.",
        },
    )


def build_s328_proposal_review_zone_contract() -> Dict[str, Any]:
    return _base(
        "S328",
        "proposal_review_zone_contract_ready",
        zone={
            "zone_id": "proposal_review_zone",
            "cards": [
                "internet_update_proposals",
                "review_queue_status",
                "approved_exports",
                "runtime_mutation_blocked_banner",
            ],
            "payload_keys": ["internet_update_proposals"],
            "operator_actions_visible": True,
            "operator_actions_execute_live": False,
        },
    )


def build_s329_visual_state_manifest() -> Dict[str, Any]:
    manifest = {
        "manifest_id": "frontend_cockpit_consolidated_manifest_s324_s330",
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "state_object_name": "ClaireCockpitState",
        "layout_contract": "operator_cockpit_single_payload_layout",
        "zones": [
            "top_command",
            "primary_status",
            "evidence_review",
            "proposal_review",
            "system_governance",
        ],
        "renderer_requirements": [
            "show_loading_state",
            "show_missing_payload_state",
            "show_blocked_state",
            "show_error_state",
            "do_not_show_fake_connected_state",
        ],
    }
    return _base(
        "S329",
        "visual_state_manifest_ready",
        frontend_manifest=manifest,
    )


def build_s330_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    previous = build_s323_stop_gate()
    merged_payload = apply_s317_s323_extension_to_payload({"base_payload": True})
    checks = {
        "previous_gate_ok": previous["ok"],
        "single_layout_contract_ok": build_s324_single_cockpit_layout_contract()["ok"],
        "top_command_contract_ok": build_s325_top_command_search_bar_contract()["ok"],
        "internet_zone_ok": build_s326_internet_update_zone_contract()["ok"],
        "evidence_zone_ok": build_s327_evidence_review_zone_contract()["ok"],
        "proposal_zone_ok": build_s328_proposal_review_zone_contract()["ok"],
        "visual_state_manifest_ok": build_s329_visual_state_manifest()["ok"],
        "merged_payload_has_internet_readiness": "internet_update_readiness" in merged_payload,
        "merged_payload_has_evidence": "internet_evidence" in merged_payload,
        "merged_payload_has_proposals": "internet_update_proposals" in merged_payload,
    }
    ok = all(checks.values())
    payload = _base(
        "S330",
        "operator_cockpit_layout_consolidation_passed" if ok else "operator_cockpit_layout_consolidation_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S331-S337 action cards evidence panels update panels blocked state UI" if ok else "repair S324-S330 cockpit layout",
        remaining_packs_to_dashboard_consolidation=1,
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s324_s330_operator_cockpit_layout_consolidation.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_operator_cockpit_layout_consolidation_s324_s330() -> Dict[str, Any]:
    return _base(
        "S330",
        "operator_cockpit_layout_consolidation_ready",
        layout=build_s324_single_cockpit_layout_contract(),
        command_bar=build_s325_top_command_search_bar_contract(),
        internet_zone=build_s326_internet_update_zone_contract(),
        evidence_zone=build_s327_evidence_review_zone_contract(),
        proposal_zone=build_s328_proposal_review_zone_contract(),
        frontend_manifest=build_s329_visual_state_manifest(),
        stop_gate=build_s330_stop_gate(),
    )


def write_frontend_manifest(path: str | Path) -> Dict[str, Any]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_s329_visual_state_manifest()["frontend_manifest"]
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return _base("S329", "frontend_manifest_written", written_path=str(target), frontend_manifest=manifest)


__all__ = [
    "build_s324_single_cockpit_layout_contract",
    "build_s325_top_command_search_bar_contract",
    "build_s326_internet_update_zone_contract",
    "build_s327_evidence_review_zone_contract",
    "build_s328_proposal_review_zone_contract",
    "build_s329_visual_state_manifest",
    "build_s330_stop_gate",
    "build_operator_cockpit_layout_consolidation_s324_s330",
    "write_frontend_manifest",
]
