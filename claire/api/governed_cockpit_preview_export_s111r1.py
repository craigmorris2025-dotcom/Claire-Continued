from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from claire.api.governed_unified_cockpit_preview_s110r1 import (
    build_unified_cockpit_preview_report,
)

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def export_cockpit_preview_artifact(
    *,
    export_dir: Path | None = None,
    filename: str = "s111r1_unified_cockpit_preview.json",
) -> Dict[str, Any]:
    report = build_unified_cockpit_preview_report()
    out_dir = export_dir or Path.cwd() / "exports" / "cockpit_preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename

    artifact = {
        "artifact_version": "S111R1",
        "created_at": _utc_now(),
        "status": "cockpit_preview_artifact_ready" if report.get("ok") else "cockpit_preview_artifact_blocked",
        "derived_artifact_only": True,
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "runtime_truth_write": "blocked",
        "runtime_truth_mutation": "blocked",
        "automatic_updates": "blocked",
        "autonomous_execution": "blocked",
        "preview_report": report,
    }

    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "export_version": "S111R1",
        "status": artifact["status"],
        "ok": report.get("ok") is True and path.exists(),
        "path": str(path),
        "derived_artifact_only": True,
        "live_dashboard_rewire_performed": False,
        "app_patch_performed": False,
        "route_registration_performed": False,
        "runtime_truth_write": "blocked",
        "next_safe_step": "S112R1 cockpit artifact validation and stop gate",
    }

def validate_cockpit_preview_artifact(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"validation_version": "S111R1", "ok": False, "error": repr(exc)}

    checks = {
        "artifact_version_ok": payload.get("artifact_version") == "S111R1",
        "derived_artifact_only": payload.get("derived_artifact_only") is True,
        "no_live_rewire": payload.get("live_dashboard_rewire_performed") is False,
        "no_app_patch": payload.get("app_patch_performed") is False,
        "no_route_registration": payload.get("route_registration_performed") is False,
        "runtime_truth_write_blocked": payload.get("runtime_truth_write") == "blocked",
        "runtime_truth_mutation_blocked": payload.get("runtime_truth_mutation") == "blocked",
        "automatic_updates_blocked": payload.get("automatic_updates") == "blocked",
        "autonomous_execution_blocked": payload.get("autonomous_execution") == "blocked",
        "preview_report_ok": (payload.get("preview_report") or {}).get("ok") is True,
    }

    return {
        "validation_version": "S111R1",
        "status": "passed" if all(checks.values()) else "failed",
        "ok": all(checks.values()),
        "checks": checks,
        "path": str(path),
    }

def build_cockpit_preview_export_report(export_dir: Path | None = None) -> Dict[str, Any]:
    export = export_cockpit_preview_artifact(export_dir=export_dir)
    validation = validate_cockpit_preview_artifact(Path(export["path"]))
    ok = export.get("ok") is True and validation.get("ok") is True
    return {
        "export_report_version": "S111R1",
        "status": "cockpit_preview_export_report_passed" if ok else "cockpit_preview_export_report_failed",
        "ok": ok,
        "export": export,
        "validation": validation,
        "next_safe_step": "S112R1 cockpit artifact validation and stop gate",
    }
