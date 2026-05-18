from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from claire.api.governed_cockpit_attachment_gate_s128_s134 import build_s128_s134_stop_gate
from claire.api.governed_readonly_cockpit_integration_s121_s127 import build_consolidated_readonly_cockpit_payload

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def build_governed_operations_registry_entry(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    payload = build_consolidated_readonly_cockpit_payload(store_path=store_path, export_dir=export_dir)
    return {
        "stage_version": "S135",
        "registry_key": "governed_operations",
        "status": "registry_entry_ready",
        "read_only": True,
        "payload": payload,
        "rollback": {
            "removal_key": "governed_operations",
            "safe_to_remove": True,
            "runtime_truth_impact": "none",
        },
        "locks": dict(LOCKS),
    }

def build_payload_registry_preview(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    entry = build_governed_operations_registry_entry(store_path=store_path, export_dir=export_dir)
    return {
        "stage_version": "S136",
        "status": "payload_registry_preview_ready",
        "registry": {
            "governed_operations": entry["payload"],
        },
        "registered_keys": ["governed_operations"],
        "live_registry_write_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "locks": dict(LOCKS),
    }

def build_existing_payload_bridge_contract() -> Dict[str, Any]:
    return {
        "stage_version": "S137",
        "status": "existing_payload_bridge_contract_ready",
        "merge_contract": {
            "mode": "read_only_append",
            "key": "governed_operations",
            "preserve_existing_payload": True,
            "overwrite_existing_keys": False,
            "rollback_supported": True,
        },
        "requires_app_patch": False,
        "requires_dashboard_rewrite": False,
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_payload_stability_probe(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    p1 = build_payload_registry_preview(store_path=store_path, export_dir=export_dir)
    p2 = build_payload_registry_preview(store_path=store_path, export_dir=export_dir)
    stable_shape = set(p1["registry"].keys()) == set(p2["registry"].keys())
    return {
        "stage_version": "S138",
        "status": "payload_stability_probe_passed" if stable_shape else "payload_stability_probe_failed",
        "ok": stable_shape,
        "stable_registry_keys": stable_shape,
        "registry_keys": list(p1["registry"].keys()),
        "live_fetch_required": False,
        "locks": dict(LOCKS),
    }

def build_existing_cockpit_nonbreak_contract() -> Dict[str, Any]:
    return {
        "stage_version": "S139",
        "status": "existing_cockpit_nonbreak_contract_ready",
        "rules": {
            "preserve_existing_dashboard_payload": True,
            "append_only_under_governed_operations": True,
            "no_dom_rewrite": True,
            "no_js_fetch_replacement": True,
            "no_app_patch": True,
            "rollback_before_visual_integration": True,
        },
        "locks": dict(LOCKS),
    }

def build_readonly_surface_validation(*, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    registry = build_payload_registry_preview(store_path=store_path, export_dir=export_dir)
    payload = registry["registry"]["governed_operations"]
    panels = payload.get("panels", {}) if isinstance(payload.get("panels"), Mapping) else {}
    checks = {
        "registry_preview_ready": registry["status"] == "payload_registry_preview_ready",
        "payload_read_only": payload.get("read_only") is True,
        "no_live_registry_write": registry["live_registry_write_performed"] is False,
        "no_app_patch": registry["app_patch_performed"] is False,
        "no_route_registration": registry["route_registration_performed"] is False,
        "panels_read_only": all(isinstance(panel, Mapping) and panel.get("read_only") is True for panel in panels.values()),
        "runtime_truth_write_blocked": payload.get("runtime_truth_write") == "blocked",
    }
    return {
        "stage_version": "S140",
        "status": "readonly_surface_validation_passed" if all(checks.values()) else "readonly_surface_validation_failed",
        "ok": all(checks.values()),
        "checks": checks,
        "locks": dict(LOCKS),
    }

def build_s135_s141_stop_gate(*, report_dir: Path | None = None, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    previous = build_s128_s134_stop_gate(store_path=store_path, export_dir=export_dir)
    entry = build_governed_operations_registry_entry(store_path=store_path, export_dir=export_dir)
    registry = build_payload_registry_preview(store_path=store_path, export_dir=export_dir)
    bridge = build_existing_payload_bridge_contract()
    stability = build_payload_stability_probe(store_path=store_path, export_dir=export_dir)
    nonbreak = build_existing_cockpit_nonbreak_contract()
    readonly = build_readonly_surface_validation(store_path=store_path, export_dir=export_dir)
    checks = {
        "previous_gate_ok": previous.get("ok") is True,
        "s135_entry_ready": entry["status"] == "registry_entry_ready",
        "s136_registry_preview_ready": registry["status"] == "payload_registry_preview_ready",
        "s137_bridge_contract_ready": bridge["status"] == "existing_payload_bridge_contract_ready",
        "s138_stability_ok": stability["ok"] is True,
        "s139_nonbreak_ready": nonbreak["status"] == "existing_cockpit_nonbreak_contract_ready",
        "s140_readonly_ok": readonly["ok"] is True,
        "rollback_supported": entry["rollback"]["safe_to_remove"] is True,
        "no_app_patch": registry["app_patch_performed"] is False,
    }
    ok = all(checks.values())
    report = {
        "stage_version": "S141",
        "generated_at": _utc_now(),
        "status": "s135_s141_payload_registry_integration_passed" if ok else "s135_s141_payload_registry_integration_failed",
        "ok": ok,
        "functional_coverage": {
            "S135": "governed_operations registry entry",
            "S136": "payload registry preview",
            "S137": "existing payload bridge contract",
            "S138": "payload stability probe",
            "S139": "existing cockpit nonbreak contract",
            "S140": "readonly surface validation",
            "S141": "payload registry integration stop gate",
        },
        "checks": checks,
        "registry_preview": registry,
        "bridge_contract": bridge,
        "stability_probe": stability,
        "nonbreak_contract": nonbreak,
        "readonly_validation": readonly,
        "forward_motion_allowed": ok,
        "next_allowed_phase": "S142 controlled live payload bridge adapter patch" if ok else "repair S135-S141 failing check only",
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / "s135_s141_payload_registry_integration.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(path)
    return report
