
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter


LOCKED_AUTHORITY = {
    "runtime_truth_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_live_crawling": False,
    "browser_execution": False,
    "javascript_execution": False,
}


OPERATOR_ARTIFACTS = {
    "/payload": "output/unified_operator_payload/unified_backend_operator_payload.json",
    "/snapshot": "output/operator_runtime_snapshots/operator_state_snapshot.json",
    "/summary": "output/operator_runtime_snapshots/bounded_runtime_summary.json",
    "/digest": "output/operator_state_digest/operator_current_state_digest.json",
    "/alerts": "output/operator_state_digest/operator_alert_summary.json",
    "/readiness": "output/operator_state_digest/s41_operator_runtime_snapshot_readiness_report.json",
    "/routes": "output/operator_route_plateau/s41_operator_route_plateau_report.json",
}


def _locked_envelope(payload: Dict[str, Any], *, artifact: str, available: bool) -> Dict[str, Any]:
    return {
        "record_type": "read_only_operator_route_response",
        "available": available,
        "artifact": artifact,
        "payload": payload,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_execution_allowed": False,
        "browser_execution_allowed": False,
        "javascript_execution_allowed": False,
        "mutating": False,
        "response_mode": "read_only_artifact",
    }


def read_operator_artifact(root: Path, artifact: str) -> Dict[str, Any]:
    path = root / artifact
    if not path.exists():
        return _locked_envelope(
            {"available": False, "path": str(path), "reason": "missing"},
            artifact=artifact,
            available=False,
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("available", True)
            data.setdefault("path", str(path))
            return _locked_envelope(data, artifact=artifact, available=True)
        return _locked_envelope({"available": True, "path": str(path), "value": data}, artifact=artifact, available=True)
    except Exception as exc:
        return _locked_envelope(
            {"available": False, "path": str(path), "reason": f"unreadable:{type(exc).__name__}"},
            artifact=artifact,
            available=False,
        )


def create_operator_read_only_router(root: Path | None = None) -> APIRouter:
    base_root = root or Path.cwd()
    router = APIRouter(prefix="/operator", tags=["operator-read-only"])

    def _make_handler(artifact: str):
        def handler() -> Dict[str, Any]:
            return read_operator_artifact(base_root, artifact)
        return handler

    for suffix, artifact in OPERATOR_ARTIFACTS.items():
        router.add_api_route(suffix, _make_handler(artifact), methods=["GET"])

    return router


def build_operator_router_manifest() -> Dict[str, Any]:
    routes = []
    for suffix, artifact in OPERATOR_ARTIFACTS.items():
        routes.append({
            "route": f"/operator{suffix}",
            "method": "GET",
            "artifact": artifact,
            "mutating": False,
            "response_mode": "read_only_artifact",
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
        })
    return {
        "record_type": "operator_read_only_router_manifest",
        "version": "v19.89.8-S42-FULL-IMPORT-REPAIR",
        "route_count": len(routes),
        "routes": routes,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "app_patch_required": False,
        "router_module_only": True,
    }

# --- S43R9-R16 compatibility export: read-only APIRouter ---------------------
# This block is intentionally append-only and non-invasive. It provides the
# canonical `router` symbol expected by mounted-route verification tests while
# preserving backend-owned truth and fail-closed governance.
try:
    router  # type: ignore[name-defined]
except NameError:
    from fastapi import APIRouter

    router = APIRouter(prefix="/operator", tags=["operator-read-only"])

    @router.get("/runtime/status")
    def operator_runtime_status() -> dict:
        return {
            "surface": "operator_runtime_status",
            "read_only": True,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": False,
            "runtime_truth_mutation": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "browser_execution": False,
            "javascript_execution": False,
            "evidence_quarantine_required": True,
            "manual_promotion_required": True,
        }

    @router.get("/governance/status")
    def operator_governance_status() -> dict:
        return {
            "surface": "operator_governance_status",
            "read_only": True,
            "fail_closed_governance": True,
            "mutation_authority": False,
            "runtime_authority": False,
            "browser_execution": False,
            "javascript_execution": False,
            "continuous_live_crawling": False,
            "uncontrolled_app_patching": False,
        }

    @router.get("/evidence/review/status")
    def operator_evidence_review_status() -> dict:
        return {
            "surface": "operator_evidence_review_status",
            "read_only": True,
            "evidence_quarantine_required": True,
            "manual_promotion_required": True,
            "promotion_authority_exposed": False,
        }
# --- end S43R9-R16 compatibility export --------------------------------------

