from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

from runtime_core.api.governed_runtime_spine_s106r1 import build_runtime_spine_state
from runtime_core.api.governed_runtime_registry_discovery_s107r1 import build_registry_discovery_report

ROOT = Path.cwd()

DASHBOARD_PAYLOAD_CANDIDATES = [
    "runtime_core/api/dashboard_payload_bridge.py",
    "runtime_core/api/dashboard_payload.py",
    "runtime_core/api/governed_s92_s98_cockpit_contracts.py",
    "runtime_core/api/governed_s99_s105_routes.py",
]

READ_MODEL_KEYS = [
    "spine_version",
    "spine_id",
    "status",
    "stage_count",
    "route_count",
    "stage_state",
    "route_state",
    "review_queue_total",
    "export_count",
    "authority_model",
    "locks",
]

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

def discover_dashboard_payload_surfaces(root: Path | None = None) -> Dict[str, Any]:
    base = root or ROOT
    surfaces = []
    for rel in DASHBOARD_PAYLOAD_CANDIDATES:
        path = base / rel
        text = _read_text(path)
        surfaces.append({
            "path": rel,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "mentions_dashboard": "dashboard" in text.lower(),
            "mentions_payload": "payload" in text.lower(),
            "mentions_cockpit": "cockpit" in text.lower(),
            "safe_read_model_candidate": path.exists() and ("payload" in text.lower() or "cockpit" in text.lower()),
            "patched_by_s108r1": False,
        })
    return {
        "surface_discovery_version": "S108R1",
        "status": "dashboard_payload_surface_discovery_complete",
        "surfaces": surfaces,
        "patch_performed": False,
    }

def build_spine_dashboard_read_model(
    *,
    review_queue_total: int = 0,
    export_count: int = 0,
) -> Dict[str, Any]:
    spine = build_runtime_spine_state(
        proof_status="ready",
        review_queue_total=review_queue_total,
        export_count=export_count,
    )
    read_model = {key: spine.get(key) for key in READ_MODEL_KEYS}
    read_model.update({
        "read_model_version": "S108R1",
        "status": "dashboard_spine_read_model_ready",
        "backend_owned": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_mutation": "blocked",
        "automatic_updates": "blocked",
        "autonomous_execution": "blocked",
        "patch_performed": False,
        "route_registration_performed": False,
    })
    return read_model

def build_dashboard_payload_compatibility_report(root: Path | None = None) -> Dict[str, Any]:
    registry = build_registry_discovery_report(root)
    discovery = discover_dashboard_payload_surfaces(root)
    read_model = build_spine_dashboard_read_model(review_queue_total=3, export_count=6)

    candidate_count = sum(1 for item in discovery["surfaces"] if item["safe_read_model_candidate"])
    required_keys_present = all(key in read_model for key in READ_MODEL_KEYS)
    locks_ok = (
        read_model["runtime_truth_write"] == "blocked"
        and read_model["runtime_truth_mutation"] == "blocked"
        and read_model["automatic_updates"] == "blocked"
        and read_model["autonomous_execution"] == "blocked"
    )

    ok = (
        registry["ok"] is True
        and candidate_count >= 1
        and required_keys_present
        and locks_ok
        and discovery["patch_performed"] is False
        and read_model["patch_performed"] is False
        and read_model["route_registration_performed"] is False
    )

    return {
        "compatibility_report_version": "S108R1",
        "status": "dashboard_payload_compatibility_ready" if ok else "dashboard_payload_compatibility_blocked",
        "ok": ok,
        "purpose": "Prove runtime spine can become a dashboard payload read model without patching app.py or registering routes.",
        "candidate_surface_count": candidate_count,
        "required_keys_present": required_keys_present,
        "locks_ok": locks_ok,
        "registry_report": registry,
        "surface_discovery": discovery,
        "spine_dashboard_read_model": read_model,
        "next_safe_step": "S109R1 payload bridge adapter module without app patching",
    }
