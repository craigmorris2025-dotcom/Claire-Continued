from __future__ import annotations

from typing import Any, Dict, Mapping

from claire.api.governed_dashboard_payload_spine_compat_s108r1 import (
    build_dashboard_payload_compatibility_report,
    build_spine_dashboard_read_model,
)

CANONICAL_PANEL_KEYS = [
    "panel_id",
    "title",
    "status",
    "version",
    "read_only",
    "backend_owned",
    "cockpit_presentation_only",
    "summary",
    "data",
]

def build_runtime_spine_payload_panel(
    read_model: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    read_model = read_model or build_spine_dashboard_read_model()
    return {
        "panel_id": "runtime_spine",
        "title": "Runtime Spine",
        "status": read_model.get("status"),
        "version": "S109R1",
        "read_only": True,
        "backend_owned": True,
        "cockpit_presentation_only": True,
        "summary": {
            "spine_version": read_model.get("spine_version"),
            "stage_count": read_model.get("stage_count"),
            "route_count": read_model.get("route_count"),
            "review_queue_total": read_model.get("review_queue_total", 0),
            "export_count": read_model.get("export_count", 0),
        },
        "data": dict(read_model),
    }

def build_runtime_spine_payload_bridge(
    read_model: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    read_model = read_model or build_spine_dashboard_read_model()
    panel = build_runtime_spine_payload_panel(read_model)
    return {
        "bridge_adapter_version": "S109R1",
        "status": "payload_bridge_adapter_ready",
        "patch_performed": False,
        "route_registration_performed": False,
        "dashboard_rewire_performed": False,
        "canonical_payload_fragment": {
            "governed_runtime_spine": panel,
        },
        "panel_order_hint": ["governed_runtime_spine"],
        "locks": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_truth_write_blocked": True,
            "runtime_truth_mutation_blocked": True,
            "automatic_updates_blocked": True,
            "autonomous_execution_blocked": True,
        },
    }

def validate_runtime_spine_payload_bridge(
    bridge: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    bridge = bridge or build_runtime_spine_payload_bridge()
    fragment = bridge.get("canonical_payload_fragment", {})
    panel = fragment.get("governed_runtime_spine", {}) if isinstance(fragment, Mapping) else {}

    panel_keys_ok = all(key in panel for key in CANONICAL_PANEL_KEYS)
    flags_ok = (
        bridge.get("patch_performed") is False
        and bridge.get("route_registration_performed") is False
        and bridge.get("dashboard_rewire_performed") is False
        and panel.get("read_only") is True
        and panel.get("backend_owned") is True
        and panel.get("cockpit_presentation_only") is True
    )
    locks = bridge.get("locks", {}) if isinstance(bridge.get("locks"), Mapping) else {}
    locks_ok = (
        locks.get("runtime_truth_write_blocked") is True
        and locks.get("runtime_truth_mutation_blocked") is True
        and locks.get("automatic_updates_blocked") is True
        and locks.get("autonomous_execution_blocked") is True
    )

    return {
        "validation_version": "S109R1",
        "status": "passed" if panel_keys_ok and flags_ok and locks_ok else "failed",
        "ok": panel_keys_ok and flags_ok and locks_ok,
        "panel_keys_ok": panel_keys_ok,
        "flags_ok": flags_ok,
        "locks_ok": locks_ok,
        "panel_id": panel.get("panel_id"),
    }

def build_payload_bridge_adapter_report() -> Dict[str, Any]:
    compatibility = build_dashboard_payload_compatibility_report()
    read_model = build_spine_dashboard_read_model(review_queue_total=3, export_count=6)
    bridge = build_runtime_spine_payload_bridge(read_model)
    validation = validate_runtime_spine_payload_bridge(bridge)
    ok = compatibility.get("ok") is True and validation.get("ok") is True
    return {
        "adapter_report_version": "S109R1",
        "status": "payload_bridge_adapter_report_passed" if ok else "payload_bridge_adapter_report_failed",
        "ok": ok,
        "compatibility_ok": compatibility.get("ok"),
        "validation": validation,
        "bridge": bridge,
        "next_safe_step": "S110R1 unified cockpit payload preview without live rewiring",
    }
