from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from claire.api.governed_functional_slice_s114_s120 import (
    build_evidence_to_lifecycle_bridge,
    build_approved_evidence_run_contract,
    build_dashboard_operations_fetch_map,
    build_review_export_control_backend,
    build_governed_search_control_backend,
    build_dashboard_managed_demo_backend,
    build_s114_s120_stop_gate,
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

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _panel(panel_id: str, title: str, status: str, data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "panel_id": panel_id,
        "title": title,
        "status": status,
        "read_only": True,
        "backend_owned": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write": "blocked",
        "data": dict(data),
    }

def build_runtime_spine_cockpit_panel(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    demo = build_dashboard_managed_demo_backend(store_path=store_path, export_dir=export_dir)
    spine = demo["runtime_spine"]
    return _panel(
        "runtime_spine",
        "Runtime Spine",
        "ready",
        {
            "spine_version": spine.get("spine_version"),
            "stage_count": spine.get("stage_count"),
            "route_count": spine.get("route_count"),
            "proof_status": spine.get("proof_status"),
            "authority_model": spine.get("authority_model"),
        },
    )

def build_review_export_cockpit_panel(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    control = build_review_export_control_backend(store_path=store_path, export_dir=export_dir)
    return _panel(
        "review_export",
        "Review / Export",
        "ready",
        {
            "available_actions": control.get("available_actions"),
            "manual_operator_only": control.get("manual_operator_only"),
            "queue_total": control.get("queue_total"),
            "decision_total": control.get("decision_total"),
            "latest_export": control.get("latest_export"),
        },
    )

def build_governed_search_cockpit_panel() -> Dict[str, Any]:
    control = build_governed_search_control_backend()
    return _panel(
        "governed_search",
        "Governed Search Control",
        "ready",
        {
            "manual_probe_required": control.get("manual_probe_required"),
            "quarantine_required": control.get("quarantine_required"),
            "operator_review_required": control.get("operator_review_required"),
            "manual_promotion_required": control.get("manual_promotion_required"),
            "continuous_crawling": control.get("continuous_crawling"),
            "automatic_updates": control.get("automatic_updates"),
            "live_web_execution": control.get("live_web_execution"),
        },
    )

def build_evidence_demo_cockpit_panel(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    bridge = build_evidence_to_lifecycle_bridge()
    approved = build_approved_evidence_run_contract(store_path=store_path, export_dir=export_dir)
    return _panel(
        "evidence_demo",
        "Evidence To Output Demo",
        "ready",
        {
            "bridge_status": bridge.get("status"),
            "approved_run_status": approved.get("status"),
            "discovery_candidate_id": bridge.get("discovery_candidate", {}).get("candidate_id"),
            "output_candidate_id": bridge.get("useful_output_candidate", {}).get("output_candidate_id"),
            "export_status": approved.get("export", {}).get("status"),
            "export_path": approved.get("export", {}).get("path"),
        },
    )

def build_consolidated_readonly_cockpit_payload(
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    panels = {
        "runtime_spine": build_runtime_spine_cockpit_panel(store_path=store_path, export_dir=export_dir),
        "review_export": build_review_export_cockpit_panel(store_path=store_path, export_dir=export_dir),
        "governed_search": build_governed_search_cockpit_panel(),
        "evidence_demo": build_evidence_demo_cockpit_panel(store_path=store_path, export_dir=export_dir),
    }
    fetch_map = build_dashboard_operations_fetch_map()
    stop_gate = build_s114_s120_stop_gate(store_path=store_path, export_dir=export_dir)

    return {
        "cockpit_payload_version": "S121-S127",
        "generated_at": _utc_now(),
        "status": "readonly_cockpit_payload_ready",
        "read_only": True,
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "runtime_truth_write": "blocked",
        "panels": panels,
        "panel_order": ["runtime_spine", "review_export", "governed_search", "evidence_demo"],
        "fetch_map": fetch_map,
        "stop_gate": {
            "status": stop_gate.get("status"),
            "ok": stop_gate.get("ok"),
            "forward_motion_allowed": stop_gate.get("forward_motion_allowed"),
        },
        "locks": dict(LOCKS),
    }

def validate_consolidated_readonly_cockpit_payload(payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or build_consolidated_readonly_cockpit_payload()
    panels = payload.get("panels", {}) if isinstance(payload.get("panels"), Mapping) else {}
    required = ["runtime_spine", "review_export", "governed_search", "evidence_demo"]
    checks = {
        "payload_ready": payload.get("status") == "readonly_cockpit_payload_ready",
        "read_only": payload.get("read_only") is True,
        "no_live_rewire": payload.get("live_dashboard_rewire_performed") is False,
        "no_app_patch": payload.get("app_patch_performed") is False,
        "no_route_registration": payload.get("route_registration_performed") is False,
        "runtime_truth_write_blocked": payload.get("runtime_truth_write") == "blocked",
        "required_panels_present": all(panel in panels for panel in required),
        "panels_read_only": all(isinstance(panels.get(panel), Mapping) and panels[panel].get("read_only") is True for panel in required),
        "stop_gate_ok": payload.get("stop_gate", {}).get("ok") is True,
        "governance_locks_ok": all(payload.get("locks", {}).get(key) is True for key in [
            "backend_owns_truth",
            "cockpit_presentation_only",
            "runtime_truth_write_blocked",
            "runtime_truth_mutation_blocked",
            "automatic_updates_blocked",
            "autonomous_execution_blocked",
        ]),
    }
    return {
        "validation_version": "S127",
        "status": "readonly_cockpit_integration_validation_passed" if all(checks.values()) else "readonly_cockpit_integration_validation_failed",
        "ok": all(checks.values()),
        "checks": checks,
        "next_allowed_phase": "S128 controlled live cockpit attachment gate" if all(checks.values()) else "repair S121-S127 failing check only",
    }

def build_s121_s127_stop_gate(
    *,
    report_dir: Path | None = None,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    payload = build_consolidated_readonly_cockpit_payload(store_path=store_path, export_dir=export_dir)
    validation = validate_consolidated_readonly_cockpit_payload(payload)
    report = {
        "stop_gate_version": "S121-S127",
        "generated_at": _utc_now(),
        "status": "s121_s127_readonly_cockpit_integration_passed" if validation["ok"] else "s121_s127_readonly_cockpit_integration_failed",
        "ok": validation["ok"],
        "functional_coverage": {
            "S121": "runtime spine into read-only cockpit payload",
            "S122": "review/export state into cockpit payload",
            "S123": "governed search state into cockpit payload",
            "S124": "evidence/demo status into cockpit payload",
            "S125": "fragmented payload consolidation",
            "S126": "single operational cockpit payload preview",
            "S127": "fail-closed stop-gate validation",
        },
        "payload": payload,
        "validation": validation,
        "forward_motion_allowed": validation["ok"],
        "next_allowed_phase": validation["next_allowed_phase"],
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s121_s127_readonly_cockpit_integration.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report
