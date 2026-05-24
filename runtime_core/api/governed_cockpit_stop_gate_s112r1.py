from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from runtime_core.api.governed_cockpit_preview_export_s111r1 import (
    build_cockpit_preview_export_report,
)
from runtime_core.api.governed_unified_cockpit_preview_s110r1 import (
    validate_unified_cockpit_payload_preview,
)
from runtime_core.api.governed_payload_bridge_adapter_s109r1 import (
    validate_runtime_spine_payload_bridge,
)
from runtime_core.api.governed_dashboard_payload_spine_compat_s108r1 import (
    build_dashboard_payload_compatibility_report,
)
from runtime_core.api.governed_runtime_registry_discovery_s107r1 import (
    build_registry_discovery_report,
)
from runtime_core.api.governed_runtime_spine_s106r1 import (
    build_runtime_spine_contract_report,
)

LOCK_KEYS = [
    "runtime_truth_write_blocked",
    "runtime_truth_mutation_blocked",
    "automatic_updates_blocked",
    "autonomous_execution_blocked",
]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _extract_locks(payload: Mapping[str, Any]) -> Dict[str, Any]:
    locks = {}
    if isinstance(payload.get("locks"), Mapping):
        locks.update(payload["locks"])
    preview = payload.get("preview")
    if isinstance(preview, Mapping) and isinstance(preview.get("locks"), Mapping):
        locks.update(preview["locks"])
    bridge = payload.get("bridge")
    if isinstance(bridge, Mapping) and isinstance(bridge.get("locks"), Mapping):
        locks.update(bridge["locks"])
    return locks

def build_cockpit_artifact_stop_gate(export_dir: Path | None = None) -> Dict[str, Any]:
    runtime_spine = build_runtime_spine_contract_report()
    registry = build_registry_discovery_report()
    compatibility = build_dashboard_payload_compatibility_report()
    bridge_validation = validate_runtime_spine_payload_bridge()
    preview_validation = validate_unified_cockpit_payload_preview()
    export_report = build_cockpit_preview_export_report(export_dir=export_dir)

    export_path = Path(export_report["export"]["path"])
    artifact_payload = json.loads(export_path.read_text(encoding="utf-8"))
    locks = _extract_locks(artifact_payload.get("preview_report", {}))
    locks_ok = all(locks.get(key) is True for key in LOCK_KEYS)

    no_rewire_ok = (
        artifact_payload.get("live_dashboard_rewire_performed") is False
        and artifact_payload.get("app_patch_performed") is False
        and artifact_payload.get("route_registration_performed") is False
    )

    artifact_ok = (
        artifact_payload.get("artifact_version") == "S111R1"
        and artifact_payload.get("derived_artifact_only") is True
        and artifact_payload.get("preview_report", {}).get("ok") is True
    )

    checks = {
        "runtime_spine_ok": runtime_spine.get("ok") is True,
        "registry_discovery_ok": registry.get("ok") is True,
        "payload_compatibility_ok": compatibility.get("ok") is True,
        "payload_bridge_validation_ok": bridge_validation.get("ok") is True,
        "cockpit_preview_validation_ok": preview_validation.get("ok") is True,
        "export_report_ok": export_report.get("ok") is True,
        "artifact_ok": artifact_ok,
        "locks_ok": locks_ok,
        "no_rewire_ok": no_rewire_ok,
    }
    ok = all(checks.values())

    return {
        "stop_gate_version": "S112R1",
        "generated_at": _utc_now(),
        "status": "cockpit_artifact_stop_gate_passed" if ok else "cockpit_artifact_stop_gate_failed",
        "ok": ok,
        "forward_motion_allowed": ok,
        "next_allowed_phase": "S113R1 controlled live cockpit integration plan" if ok else "repair S112R1 failing check only",
        "checks": checks,
        "artifact_path": str(export_path),
        "no_live_dashboard_rewire": True,
        "no_app_patch": True,
        "no_route_registration": True,
        "governance_locks_checked": LOCK_KEYS,
        "reports": {
            "runtime_spine": runtime_spine,
            "registry": registry,
            "compatibility": compatibility,
            "bridge_validation": bridge_validation,
            "preview_validation": preview_validation,
            "export_report": export_report,
        },
    }

def write_cockpit_artifact_stop_gate_report(
    *,
    report_dir: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    report = build_cockpit_artifact_stop_gate(export_dir=export_dir)
    out_dir = report_dir or Path.cwd() / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "s112r1_cockpit_artifact_stop_gate.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "writer_version": "S112R1",
        "ok": report["ok"] and path.exists(),
        "status": report["status"],
        "path": str(path),
        "forward_motion_allowed": report["forward_motion_allowed"],
        "next_allowed_phase": report["next_allowed_phase"],
    }
