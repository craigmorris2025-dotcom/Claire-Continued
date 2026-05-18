from __future__ import annotations

from typing import Any, Dict, Mapping

from claire.api.governed_payload_bridge_adapter_s109r1 import (
    build_runtime_spine_payload_bridge,
    build_payload_bridge_adapter_report,
)

REQUIRED_PREVIEW_PANELS = [
    "governed_runtime_spine",
    "operator_review_queue",
    "operator_export_manifest",
    "governed_search_control",
    "system_proof_status",
]

def _panel(
    panel_id: str,
    title: str,
    status: str = "preview_ready",
    data: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "panel_id": panel_id,
        "title": title,
        "status": status,
        "version": "S110R1",
        "read_only": True,
        "backend_owned": True,
        "cockpit_presentation_only": True,
        "preview_only": True,
        "data": dict(data or {}),
    }

def build_unified_cockpit_payload_preview() -> Dict[str, Any]:
    bridge = build_runtime_spine_payload_bridge()
    fragment = bridge.get("canonical_payload_fragment", {})
    runtime_spine_panel = fragment.get("governed_runtime_spine", {}) if isinstance(fragment, Mapping) else {}

    panels = {
        "governed_runtime_spine": runtime_spine_panel,
        "operator_review_queue": _panel(
            "operator_review_queue",
            "Operator Review Queue",
            data={
                "source": "S109R1 runtime spine read model",
                "action_authority": "manual_operator_only",
                "runtime_truth_write": "blocked",
            },
        ),
        "operator_export_manifest": _panel(
            "operator_export_manifest",
            "Reviewed Export Manifest",
            data={
                "source": "derived artifact manifest",
                "exports_are_runtime_truth": False,
                "runtime_truth_write": "blocked",
            },
        ),
        "governed_search_control": _panel(
            "governed_search_control",
            "Governed Search Control",
            data={
                "manual_probe_required": True,
                "quarantine_required": True,
                "continuous_crawling": "blocked",
                "automatic_updates": "blocked",
            },
        ),
        "system_proof_status": _panel(
            "system_proof_status",
            "System Proof Status",
            data={
                "last_stop_gate": "S105-CHECK",
                "runtime_spine_contract": "S106R1",
                "registry_discovery": "S107R1",
                "payload_compatibility": "S108R1",
                "payload_bridge_adapter": "S109R1",
            },
        ),
    }

    return {
        "preview_version": "S110R1",
        "status": "unified_cockpit_payload_preview_ready",
        "preview_only": True,
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "panel_order": list(REQUIRED_PREVIEW_PANELS),
        "panels": panels,
        "locks": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_truth_write_blocked": True,
            "runtime_truth_mutation_blocked": True,
            "automatic_updates_blocked": True,
            "autonomous_execution_blocked": True,
        },
    }

def validate_unified_cockpit_payload_preview(
    payload: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = payload or build_unified_cockpit_payload_preview()
    panels = payload.get("panels", {}) if isinstance(payload.get("panels"), Mapping) else {}

    panels_present = all(panel_id in panels for panel_id in REQUIRED_PREVIEW_PANELS)
    panels_read_only = all(
        isinstance(panels.get(panel_id), Mapping)
        and panels[panel_id].get("read_only") is True
        and panels[panel_id].get("cockpit_presentation_only") is True
        for panel_id in REQUIRED_PREVIEW_PANELS
    )
    no_live_rewire = (
        payload.get("preview_only") is True
        and payload.get("live_dashboard_rewire_performed") is False
        and payload.get("app_patch_performed") is False
        and payload.get("route_registration_performed") is False
    )
    locks = payload.get("locks", {}) if isinstance(payload.get("locks"), Mapping) else {}
    locks_ok = (
        locks.get("runtime_truth_write_blocked") is True
        and locks.get("runtime_truth_mutation_blocked") is True
        and locks.get("automatic_updates_blocked") is True
        and locks.get("autonomous_execution_blocked") is True
    )

    return {
        "validation_version": "S110R1",
        "status": "passed" if panels_present and panels_read_only and no_live_rewire and locks_ok else "failed",
        "ok": panels_present and panels_read_only and no_live_rewire and locks_ok,
        "panels_present": panels_present,
        "panels_read_only": panels_read_only,
        "no_live_rewire": no_live_rewire,
        "locks_ok": locks_ok,
    }

def build_unified_cockpit_preview_report() -> Dict[str, Any]:
    adapter = build_payload_bridge_adapter_report()
    preview = build_unified_cockpit_payload_preview()
    validation = validate_unified_cockpit_payload_preview(preview)
    ok = adapter.get("ok") is True and validation.get("ok") is True

    return {
        "preview_report_version": "S110R1",
        "status": "unified_cockpit_preview_report_passed" if ok else "unified_cockpit_preview_report_failed",
        "ok": ok,
        "adapter_ok": adapter.get("ok"),
        "validation": validation,
        "preview": preview,
        "next_safe_step": "S111R1 cockpit preview export artifact without live rewiring",
    }
