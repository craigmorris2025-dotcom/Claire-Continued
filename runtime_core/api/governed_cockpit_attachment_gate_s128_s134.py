from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from runtime_core.api.governed_readonly_cockpit_integration_s121_s127 import (
    build_consolidated_readonly_cockpit_payload,
    validate_consolidated_readonly_cockpit_payload,
    build_s121_s127_stop_gate,
)

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
    "continuous_crawling_blocked": True,
}

ATTACHMENT_TARGETS = {
    "canonical_payload_fragment": {"allowed": True, "mode": "read_only_payload_merge", "patches_app": False, "runtime_truth_write": False},
    "dashboard_fetch_map": {"allowed": True, "mode": "read_only_fetch_contract", "patches_app": False, "runtime_truth_write": False},
    "live_dashboard_dom_rewire": {"allowed": False, "mode": "blocked_until_operator_visual_gate", "patches_app": False, "runtime_truth_write": False},
    "direct_app_py_patch": {"allowed": False, "mode": "blocked", "patches_app": True, "runtime_truth_write": False},
}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def build_attachment_eligibility_matrix() -> Dict[str, Any]:
    return {
        "stage_version": "S128",
        "status": "attachment_eligibility_matrix_ready",
        "targets": ATTACHMENT_TARGETS,
        "allowed_targets": [key for key, value in ATTACHMENT_TARGETS.items() if value["allowed"]],
        "blocked_targets": [key for key, value in ATTACHMENT_TARGETS.items() if not value["allowed"]],
        "locks": dict(LOCKS),
    }

def build_readonly_attachment_contract(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    payload = build_consolidated_readonly_cockpit_payload(store_path=store_path, export_dir=export_dir)
    validation = validate_consolidated_readonly_cockpit_payload(payload)
    return {
        "stage_version": "S129",
        "status": "readonly_attachment_contract_ready" if validation["ok"] else "readonly_attachment_contract_blocked",
        "payload": payload,
        "validation": validation,
        "attachment_mode": "read_only_payload_merge",
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_cockpit_payload_merge_preview(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    contract = build_readonly_attachment_contract(store_path=store_path, export_dir=export_dir)
    payload = contract["payload"]
    return {
        "stage_version": "S130",
        "status": "cockpit_payload_merge_preview_ready" if contract["validation"]["ok"] else "cockpit_payload_merge_preview_blocked",
        "merge_strategy": "append_readonly_governed_payload_under_governed_operations_key",
        "canonical_key": "governed_operations",
        "merged_payload_preview": {"governed_operations": payload},
        "source_payload_version": payload.get("cockpit_payload_version"),
        "panel_count": len(payload.get("panels", {})),
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "locks": dict(LOCKS),
    }

def build_fetch_contract_for_cockpit_attachment() -> Dict[str, Any]:
    return {
        "stage_version": "S131",
        "status": "cockpit_fetch_contract_ready",
        "read_only": True,
        "fetch_contract": {
            "governed_operations_payload_key": "governed_operations",
            "runtime_spine_panel_key": "runtime_spine",
            "review_export_panel_key": "review_export",
            "governed_search_panel_key": "governed_search",
            "evidence_demo_panel_key": "evidence_demo",
        },
        "operator_actions_visible": ["approve", "reject", "archive", "export_only"],
        "operator_actions_execute_runtime_truth_write": False,
        "locks": dict(LOCKS),
    }

def build_visual_attachment_gate() -> Dict[str, Any]:
    return {
        "stage_version": "S132",
        "status": "visual_attachment_gate_blocked_pending_operator_review",
        "allowed_now": False,
        "reason": "Live visual cockpit rewiring requires separate operator-visible UI gate after payload merge contract passes.",
        "required_before_live_rewire": [
            "payload merge preview passes",
            "fetch contract passes",
            "existing cockpit target file identified",
            "rollback file prepared",
            "operator confirms UI attachment target",
        ],
        "direct_app_patch_allowed": False,
        "live_dashboard_rewire_performed": False,
        "locks": dict(LOCKS),
    }

def build_attachment_governance_validation(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    matrix = build_attachment_eligibility_matrix()
    contract = build_readonly_attachment_contract(store_path=store_path, export_dir=export_dir)
    merge = build_cockpit_payload_merge_preview(store_path=store_path, export_dir=export_dir)
    fetch = build_fetch_contract_for_cockpit_attachment()
    visual = build_visual_attachment_gate()
    checks = {
        "matrix_ready": matrix["status"] == "attachment_eligibility_matrix_ready",
        "contract_ready": contract["status"] == "readonly_attachment_contract_ready",
        "merge_preview_ready": merge["status"] == "cockpit_payload_merge_preview_ready",
        "fetch_contract_ready": fetch["status"] == "cockpit_fetch_contract_ready",
        "visual_rewire_blocked": visual["allowed_now"] is False,
        "no_app_patch": contract["app_patch_performed"] is False and merge["app_patch_performed"] is False,
        "no_route_registration": contract["route_registration_performed"] is False and merge["route_registration_performed"] is False,
        "runtime_truth_write_blocked": contract["runtime_truth_write"] == "blocked",
        "locks_ok": all(contract["locks"].get(key) is True for key in [
            "backend_owns_truth",
            "cockpit_presentation_only",
            "runtime_truth_write_blocked",
            "runtime_truth_mutation_blocked",
            "automatic_updates_blocked",
            "autonomous_execution_blocked",
        ]),
    }
    return {
        "stage_version": "S133",
        "status": "attachment_governance_validation_passed" if all(checks.values()) else "attachment_governance_validation_failed",
        "ok": all(checks.values()),
        "checks": checks,
        "matrix": matrix,
        "contract": contract,
        "merge_preview": merge,
        "fetch_contract": fetch,
        "visual_gate": visual,
        "locks": dict(LOCKS),
    }

def build_s128_s134_stop_gate(*, report_dir: Path | None = None, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    previous_gate = build_s121_s127_stop_gate(store_path=store_path, export_dir=export_dir)
    validation = build_attachment_governance_validation(store_path=store_path, export_dir=export_dir)
    checks = {
        "previous_gate_ok": previous_gate.get("ok") is True,
        "attachment_validation_ok": validation.get("ok") is True,
        "read_only_payload_merge_allowed": "canonical_payload_fragment" in validation["matrix"]["allowed_targets"],
        "live_visual_rewire_blocked": validation["visual_gate"]["allowed_now"] is False,
        "direct_app_patch_blocked": "direct_app_py_patch" in validation["matrix"]["blocked_targets"],
        "no_runtime_truth_write": validation["checks"]["runtime_truth_write_blocked"] is True,
    }
    ok = all(checks.values())
    report = {
        "stage_version": "S134",
        "generated_at": _utc_now(),
        "status": "s128_s134_attachment_gate_passed" if ok else "s128_s134_attachment_gate_failed",
        "ok": ok,
        "functional_coverage": {
            "S128": "attachment eligibility matrix",
            "S129": "read-only attachment contract",
            "S130": "cockpit payload merge preview",
            "S131": "cockpit fetch contract",
            "S132": "visual attachment gate",
            "S133": "attachment governance validation",
            "S134": "controlled attachment stop gate",
        },
        "checks": checks,
        "attachment_validation": validation,
        "forward_motion_allowed": ok,
        "next_allowed_phase": "S135 controlled payload registry integration without app.py patching" if ok else "repair S128-S134 failing check only",
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s128_s134_cockpit_attachment_gate.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report
