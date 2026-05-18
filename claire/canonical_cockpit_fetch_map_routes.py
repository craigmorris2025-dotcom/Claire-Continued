from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(tags=["Claire Canonical Cockpit Fetch Map"])

VERSION = "v19.89.8-A3"

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def _map_path() -> Path:
    return _project_root() / "data" / "authority" / "canonical_cockpit_fetch_map.json"

def _safe_read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": str(exc), "path": str(path)}
    return fallback

def _map() -> Dict[str, Any]:
    payload = _safe_read_json(_map_path(), {})
    if isinstance(payload, dict) and payload.get("surface") == "canonical_cockpit_fetch_map":
        return payload
    return {"surface": "canonical_cockpit_fetch_map", "version": VERSION, "missing": True, "reason": "Fetch map missing. Re-run installer.", "checked_at": _utc_now()}

@router.get("/system/cockpit-fetch-map")
def cockpit_fetch_map() -> Dict[str, Any]:
    return _map()

@router.get("/system/cockpit-fetch-map/summary")
def cockpit_fetch_map_summary() -> Dict[str, Any]:
    payload = _map()
    audit = payload.get("frontend_fetch_audit", {}) if isinstance(payload.get("frontend_fetch_audit"), dict) else {}
    authority = payload.get("authority_status", {}) if isinstance(payload.get("authority_status"), dict) else {}
    return {
        "surface": payload.get("surface"),
        "version": payload.get("version"),
        "build": payload.get("build"),
        "backend_owns_truth": payload.get("backend_owns_truth"),
        "cockpit_presentation_only": payload.get("cockpit_presentation_only"),
        "frontend_truth_allowed": payload.get("frontend_truth_allowed"),
        "approved_route_count": len(payload.get("approved_fetch_routes", [])),
        "fetch_route_count": audit.get("fetch_route_count"),
        "approved_found_count": audit.get("approved_found_count"),
        "unauthorized_count": audit.get("unauthorized_count"),
        "required_missing_count": audit.get("required_missing_count"),
        "safe_to_expand_runtime_authority": authority.get("safe_to_expand_runtime_authority"),
        "safe_to_retire_compatibility_routes": authority.get("safe_to_retire_compatibility_routes"),
        "reason": authority.get("reason"),
        "checked_at": _utc_now(),
    }

@router.get("/system/cockpit-fetch-map/audit")
def cockpit_fetch_map_audit() -> Dict[str, Any]:
    payload = _map()
    return {"surface": "cockpit_fetch_map_audit", "version": payload.get("version"), "frontend_fetch_audit": payload.get("frontend_fetch_audit", {}), "checked_at": _utc_now()}

@router.get("/system/cockpit-fetch-map/approved")
def cockpit_fetch_map_approved() -> Dict[str, Any]:
    payload = _map()
    return {"surface": "cockpit_fetch_map_approved_routes", "version": payload.get("version"), "approved_fetch_routes": payload.get("approved_fetch_routes", []), "canonical_fetch_map": payload.get("canonical_fetch_map", {}), "checked_at": _utc_now()}

from claire.api.routes import governed_live_probe
@router.get("/system/cockpit-fetch-map/registration-proof")
def cockpit_fetch_map_registration_proof() -> Dict[str, Any]:
    return {
        "surface": "cockpit_fetch_map_registration_proof",
        "version": VERSION,
        "registered": True,
        "routes": ["/system/cockpit-fetch-map", "/system/cockpit-fetch-map/summary", "/system/cockpit-fetch-map/audit", "/system/cockpit-fetch-map/approved", "/system/cockpit-fetch-map/registration-proof"],
        "checked_at": _utc_now(),
    }

# S36 governed live metadata probe graft: mounted through existing clean router only.
router.include_router(governed_live_probe.router)
