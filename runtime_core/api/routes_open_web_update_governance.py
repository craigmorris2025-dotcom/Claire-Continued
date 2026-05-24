from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from runtime_core.platform.update_governance.open_web_update_governance import (
    apply_governed_update,
    build_dashboard_update_panel,
    build_install_readiness,
    build_open_web_readiness_report,
    build_self_analysis,
    create_update_request,
    record_user_approval,
    stage_update_install,
)


router = APIRouter(tags=["open-web-update-governance"])


def _safe_error(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        {
            "ok": False,
            "status": "invalid_request",
            "reason": message,
            "install_allowed": False,
            "install_performed": False,
            "runtime_mutation_allowed": False,
            "runtime_mutation_performed": False,
            "automatic_update_allowed": False,
            "automatic_update_performed": False,
        },
        status_code=status_code,
    )


async def _json_body(request: Request) -> dict[str, Any] | None:
    try:
        payload = await request.json()
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else None


@router.get("/api/update-governance/open-web/readiness")
def open_web_update_governance_readiness() -> dict[str, Any]:
    return build_open_web_readiness_report()


@router.get("/api/update-governance/open-web/panel")
def open_web_update_governance_panel() -> dict[str, Any]:
    return build_dashboard_update_panel()


@router.get("/dashboard/update-governance/panel")
def dashboard_open_web_update_governance_panel() -> dict[str, Any]:
    return build_dashboard_update_panel()


@router.get("/api/update-governance/open-web/install/status/{update_id}")
def open_web_update_install_status(update_id: str) -> dict[str, Any]:
    return build_install_readiness(update_id)


@router.post("/api/update-governance/open-web/self-analysis")
async def open_web_update_self_analysis(request: Request) -> dict[str, Any]:
    body = await _json_body(request)
    if body is None:
        return _safe_error("request body must be a JSON object")
    required = body.get("required_capabilities") if isinstance(body.get("required_capabilities"), list) else None
    available = body.get("available_capabilities") if isinstance(body.get("available_capabilities"), list) else None
    return build_self_analysis(required_capabilities=required, available_capabilities=available)


@router.post("/api/update-governance/open-web/request")
async def open_web_update_request(request: Request):
    body = await _json_body(request)
    if body is None:
        return _safe_error("request body must be a JSON object")
    if not body.get("update_id"):
        return _safe_error("update_id is required")
    if not body.get("provider_id"):
        return _safe_error("provider_id is required")
    result = create_update_request(body)
    status_code = 202 if result["status"] == "approval_required" else 409
    return JSONResponse(result, status_code=status_code)


@router.post("/api/update-governance/open-web/approve")
async def open_web_update_approve(request: Request):
    body = await _json_body(request)
    if body is None:
        return _safe_error("request body must be a JSON object")
    update_id = str(body.get("update_id") or "").strip()
    if not update_id:
        return _safe_error("update_id is required")
    phrase = str(body.get("approval_phrase") or "").strip()
    result = record_user_approval(update_id, phrase, actor=str(body.get("actor") or "owner"))
    status_code = 202 if result["user_approved"] else 403
    return JSONResponse(result, status_code=status_code)


@router.post("/api/update-governance/open-web/install/stage")
async def open_web_update_install_stage(request: Request):
    body = await _json_body(request)
    if body is None:
        return _safe_error("request body must be a JSON object")
    update_id = str(body.get("update_id") or "").strip()
    if not update_id:
        return _safe_error("update_id is required")
    result = stage_update_install(update_id, actor=str(body.get("actor") or "owner"))
    status_code = 202 if result["install_allowed"] else 409
    return JSONResponse(result, status_code=status_code)


@router.post("/api/update-governance/open-web/install/apply")
async def open_web_update_install_apply(request: Request):
    body = await _json_body(request)
    if body is None:
        return _safe_error("request body must be a JSON object")
    update_id = str(body.get("update_id") or "").strip()
    if not update_id:
        return _safe_error("update_id is required")
    result = apply_governed_update(
        update_id,
        str(body.get("approval_phrase") or ""),
        actor=str(body.get("actor") or "owner"),
    )
    status_code = 202 if result["install_performed"] else 409
    return JSONResponse(result, status_code=status_code)


@router.post("/api/update-governance/open-web/rollback/plan")
async def open_web_update_rollback_plan(request: Request):
    body = await _json_body(request)
    if body is None:
        return _safe_error("request body must be a JSON object")
    result = create_update_request({**body, "update_id": body.get("update_id") or "rollback_plan_preview"})
    rollback = {
        "schema_version": result["schema_version"],
        "status": "rollback_plan_ready",
        "update_id": result["update_id"],
        "rollback": result["rollback"],
        "install_allowed": False,
        "install_performed": False,
        "runtime_mutation_allowed": False,
        "runtime_mutation_performed": False,
    }
    return JSONResponse(rollback, status_code=202)
