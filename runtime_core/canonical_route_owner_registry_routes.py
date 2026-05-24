from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(tags=["Claire Canonical Route Owner Registry"])

VERSION = "v19.89.8-A1"
BUILD_NAME = "Canonical Route Owner Registry"

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def _registry_path() -> Path:
    return _project_root() / "data" / "authority" / "canonical_route_owner_registry.json"

def _safe_read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": str(exc), "path": str(path)}
    return fallback

def _registry() -> Dict[str, Any]:
    payload = _safe_read_json(_registry_path(), {})
    if isinstance(payload, dict) and payload.get('surface') == 'canonical_route_owner_registry':
        return payload
    return {
        "surface": "canonical_route_owner_registry",
        "version": VERSION,
        "missing": True,
        "reason": "Registry file was not found. Re-run v19.89.8-A1 installer.",
        "checked_at": _utc_now(),
    }

@router.get("/system/route-owner-registry")
def route_owner_registry() -> Dict[str, Any]:
    return _registry()

@router.get("/system/route-owner-registry/summary")
def route_owner_registry_summary() -> Dict[str, Any]:
    registry = _registry()
    authority = registry.get('authority_status', {}) if isinstance(registry.get('authority_status'), dict) else {}
    return {
        "surface": registry.get("surface"),
        "version": registry.get("version"),
        "build": registry.get("build"),
        "backend_owns_truth": registry.get("backend_owns_truth"),
        "cockpit_presentation_only": registry.get("cockpit_presentation_only"),
        "critical_route_count": len(registry.get("critical_route_owners", {})),
        "discovered_route_count": registry.get("discovered_route_count"),
        "duplicate_route_count": registry.get("duplicate_route_count"),
        "safe_to_expand_runtime_authority": authority.get("safe_to_expand_runtime_authority"),
        "reason": authority.get("reason"),
        "checked_at": _utc_now(),
    }

@router.get("/system/route-owner-registry/critical")
def route_owner_registry_critical() -> Dict[str, Any]:
    registry = _registry()
    return {
        "surface": "critical_route_owner_registry",
        "version": registry.get("version"),
        "critical_route_owners": registry.get("critical_route_owners", {}),
        "checked_at": _utc_now(),
    }

@router.get("/system/route-owner-registry/duplicates")
def route_owner_registry_duplicates() -> Dict[str, Any]:
    registry = _registry()
    duplicates = registry.get('duplicates_detected', {})
    return {
        "surface": "route_owner_duplicates",
        "version": registry.get("version"),
        "duplicate_route_count": len(duplicates) if isinstance(duplicates, dict) else 0,
        "duplicates": duplicates,
        "checked_at": _utc_now(),
    }

@router.get("/system/route-owner-registry/registration-proof")
def route_owner_registry_registration_proof() -> Dict[str, Any]:
    return {
        "surface": "route_owner_registry_registration_proof",
        "version": VERSION,
        "registered": True,
        "routes": [
            "/system/route-owner-registry",
            "/system/route-owner-registry/summary",
            "/system/route-owner-registry/critical",
            "/system/route-owner-registry/duplicates",
            "/system/route-owner-registry/registration-proof",
        ],
        "checked_at": _utc_now(),
    }
