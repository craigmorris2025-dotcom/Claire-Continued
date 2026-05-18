from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/operator", tags=["operator-read-only"])


@router.get("/runtime/status")
def operator_runtime_status() -> dict:
    return {
        "surface": "operator-runtime-status",
        "status": "available",
        "read_only": True,
        "runtime_authority": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "browser_execution": False,
        "javascript_execution": False,
        "evidence_quarantine_required": True,
        "manual_promotion_required": True,
    }


@router.get("/evidence/review")
def operator_evidence_review() -> dict:
    return {
        "surface": "operator-evidence-review",
        "status": "available",
        "read_only": True,
        "evidence_quarantine_required": True,
        "manual_promotion_required": True,
        "promotion_authority": False,
    }


@router.get("/routes/status")
def operator_routes_status() -> dict:
    return {
        "surface": "operator-routes-status",
        "status": "available",
        "read_only": True,
        "mutation_routes_exposed": False,
        "auto_update_routes_exposed": False,
    }


@router.get("/payload/status")
def operator_payload_status() -> dict:
    return {
        "surface": "operator-payload-status",
        "status": "available",
        "read_only": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
    }
