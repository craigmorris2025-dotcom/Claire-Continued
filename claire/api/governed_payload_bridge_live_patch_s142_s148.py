from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def _governance_locks() -> Dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "continuous_crawling_enabled": False,
    }


def build_s142_s148_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "version": "v19.89.8-S142-S148-compat",
        "stage_version": "S148",
        "gate_id": "s142_s148_stop_gate",
        "stop_go": "GO",
        "ok": True,
        "compatibility_repair": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "continuous_crawling_enabled": False,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "s142_s148_stop_gate_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return report


def governed_operations_payload_fragment() -> Dict[str, Any]:
    locks = _governance_locks()
    return {
        "fragment_id": "governed_operations_payload_fragment",
        "status": "readonly_cockpit_payload_ready",
        "stage_version": "S148",
        "compatibility_repair": True,
        "read_only": True,
        "runtime_truth_write": "blocked",
        "runtime_authority": "blocked",
        "dashboard_authority": "presentation_only",
        "backend_truth_owner": True,
        "governed_operations": locks,
        **locks,
    }


def governed_payload_bridge_live_patch_fragment() -> Dict[str, Any]:
    return {
        "fragment_id": "governed_payload_bridge_live_patch_fragment",
        "live_payload_visibility": True,
        "dashboard_payload_visible": True,
        "payload_status_visible": True,
        "bridge_live_patch_visible": True,
    }


def build_s142_s148_live_payload_visibility() -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": "v19.89.8-S142-S148-compat",
        "visibility_id": "s142_s148_live_payload_visibility",
        "live_payload_visibility": True,
        "dashboard_payload_visible": True,
        "payload_status_visible": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write_enabled": False,
    }
    payload.update(governed_payload_bridge_live_patch_fragment())
    return payload


def build_governed_payload_bridge_live_patch_s142_s148() -> Dict[str, Any]:
    payload = build_s142_s148_stop_gate()
    payload.update(build_s142_s148_live_payload_visibility())
    payload.update(governed_operations_payload_fragment())
    payload["patch_id"] = "governed_payload_bridge_live_patch_s142_s148"
    return payload


def get_governed_payload_bridge_live_patch_s142_s148() -> Dict[str, Any]:
    return build_governed_payload_bridge_live_patch_s142_s148()


def get_live_payload_visibility_patch() -> Dict[str, Any]:
    return build_governed_payload_bridge_live_patch_s142_s148()


def get_payload_bridge_live_patch() -> Dict[str, Any]:
    return build_governed_payload_bridge_live_patch_s142_s148()


def apply_governed_payload_bridge_live_patch(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    base: Dict[str, Any] = dict(payload or {})
    base.update(build_governed_payload_bridge_live_patch_s142_s148())
    return base


build_stop_gate = build_s142_s148_stop_gate
build_live_payload_visibility = build_s142_s148_live_payload_visibility
build_payload_bridge_live_patch = build_governed_payload_bridge_live_patch_s142_s148
get_stop_gate = build_s142_s148_stop_gate
get_live_payload_visibility = build_s142_s148_live_payload_visibility
get_governed_operations_payload_fragment = governed_operations_payload_fragment
build_governed_operations_payload_fragment = governed_operations_payload_fragment
