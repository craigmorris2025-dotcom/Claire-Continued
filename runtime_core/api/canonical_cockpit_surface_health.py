from __future__ import annotations

from typing import Any, Dict, List


SURFACE_HEALTH_VERSION = "v19.89.8-S18"


def _surface_issue(surface: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    surface_id = surface.get("surface_id", "unknown")

    required_fields = [
        "surface_id",
        "label",
        "payload_owner",
        "route_owner",
        "sidebar_owner",
        "telemetry_owner",
        "visibility",
        "sync_state",
        "runtime_authority",
    ]

    for field in required_fields:
        if not surface.get(field):
            issues.append({
                "surface_id": surface_id,
                "issue": "missing_required_field",
                "field": field,
                "severity": "warning",
                "runtime_authority": "blocked",
            })

    if surface.get("runtime_authority") != "blocked":
        issues.append({
            "surface_id": surface_id,
            "issue": "runtime_authority_drift",
            "field": "runtime_authority",
            "severity": "critical",
            "runtime_authority": "blocked",
        })

    if surface.get("sync_state") not in {"canonical", "pending", "available"}:
        issues.append({
            "surface_id": surface_id,
            "issue": "noncanonical_sync_state",
            "field": "sync_state",
            "severity": "warning",
            "runtime_authority": "blocked",
        })

    if surface.get("visibility") not in {"active", "available", "pending", "hidden"}:
        issues.append({
            "surface_id": surface_id,
            "issue": "unknown_visibility_state",
            "field": "visibility",
            "severity": "warning",
            "runtime_authority": "blocked",
        })

    return issues


def evaluate_surface_registry_health(registry: Dict[str, Any]) -> Dict[str, Any]:
    registry = dict(registry) if isinstance(registry, dict) else {}
    surfaces = registry.get("surfaces") if isinstance(registry.get("surfaces"), list) else []

    ids = [surface.get("surface_id") for surface in surfaces if isinstance(surface, dict)]
    duplicates = sorted({surface_id for surface_id in ids if surface_id and ids.count(surface_id) > 1})

    issues: List[Dict[str, Any]] = []
    for surface in surfaces:
        if isinstance(surface, dict):
            issues.extend(_surface_issue(surface))

    for duplicate in duplicates:
        issues.append({
            "surface_id": duplicate,
            "issue": "duplicate_surface_id",
            "field": "surface_id",
            "severity": "critical",
            "runtime_authority": "blocked",
        })

    critical_count = sum(1 for issue in issues if issue.get("severity") == "critical")
    warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")

    health = "healthy"
    if critical_count:
        health = "blocked"
    elif warning_count:
        health = "degraded"

    return {
        "version": SURFACE_HEALTH_VERSION,
        "status": "active",
        "health": health,
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
        },
        "summary": {
            "surface_total": len(surfaces),
            "issue_total": len(issues),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "duplicate_surface_ids": duplicates,
        },
        "issues": issues,
    }


def attach_surface_health(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    registry = payload.get("canonical_cockpit_surface_registry")
    if isinstance(registry, dict):
        payload["canonical_cockpit_surface_health"] = evaluate_surface_registry_health(registry)
    else:
        payload["canonical_cockpit_surface_health"] = evaluate_surface_registry_health({"surfaces": []})
    return payload


def register_surface_health_routes(app: Any) -> None:
    try:
        from fastapi import APIRouter
        from runtime_core.api.canonical_cockpit_surface_registry import build_cockpit_surface_registry
    except Exception:
        return

    router = APIRouter(prefix="/api/cockpit", tags=["Canonical Cockpit Surface Health"])

    @router.get("/surface-health")
    def get_surface_health() -> Dict[str, Any]:
        return evaluate_surface_registry_health(build_cockpit_surface_registry())

    @router.get("/surface-health/status")
    def get_surface_health_status() -> Dict[str, Any]:
        health = evaluate_surface_registry_health(build_cockpit_surface_registry())
        return {
            "version": health["version"],
            "status": health["status"],
            "health": health["health"],
            "surface_total": health["summary"]["surface_total"],
            "issue_total": health["summary"]["issue_total"],
            "runtime_authority": "blocked",
            "presentation_only": True,
        }

    app.include_router(router)
