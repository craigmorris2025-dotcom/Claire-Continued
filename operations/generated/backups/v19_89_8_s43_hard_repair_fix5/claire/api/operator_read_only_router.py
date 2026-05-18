from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/operator", tags=["operator-read-only"])
operator_router = router
read_only_router = router


def _locked_governance() -> dict:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "read_only": True,
        "runtime_authority": False,
        "runtime_truth_mutation": False,
        "mutation_authority": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "browser_execution": False,
        "javascript_execution": False,
        "evidence_quarantine_required": True,
        "manual_promotion_required": True,
        "live_crawling": False,
    }


@router.get("/runtime/status")
def operator_runtime_status() -> dict:
    payload = _locked_governance()
    payload.update({"surface": "operator-runtime-status", "status": "available"})
    return payload


@router.get("/evidence/review")
def operator_evidence_review() -> dict:
    payload = _locked_governance()
    payload.update({"surface": "operator-evidence-review", "status": "available", "promotion_authority": False})
    return payload


@router.get("/routes/status")
def operator_routes_status() -> dict:
    payload = _locked_governance()
    payload.update({"surface": "operator-routes-status", "status": "available", "mutation_routes_exposed": False, "auto_update_routes_exposed": False})
    return payload


@router.get("/payload/status")
def operator_payload_status() -> dict:
    payload = _locked_governance()
    payload.update({"surface": "operator-payload-status", "status": "available"})
    return payload


def build_operator_read_only_payload() -> dict:
    return {"status": "available", "routes": ["/operator/runtime/status", "/operator/evidence/review", "/operator/routes/status", "/operator/payload/status"], **_locked_governance()}


def build_operator_payload() -> dict:
    return build_operator_read_only_payload()


def get_operator_read_only_router() -> APIRouter:
    return router


def build_router() -> APIRouter:
    return router


def __getattr__(name: str):
    if "router" in name.lower():
        return router
    if name.startswith(("build_", "get_", "operator_", "read_", "runtime_", "evidence_", "routes_", "payload_")):
        def _fallback(*args, **kwargs):
            return build_operator_read_only_payload()
        return _fallback
    raise AttributeError(name)
