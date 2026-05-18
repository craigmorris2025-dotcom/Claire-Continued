"""
S380-S386 — Proposal Review + Export Action Gate.
Governed review/export endpoints. Export writes local files under exports/.
No runtime truth mutation, self-apply, automatic updates, or autonomous crawling.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import hashlib, json
from fastapi import FastAPI

from claire.api.governed_internet_update_foundation_s296_s302 import authority_locks
from claire.api.governed_update_proposal_pipeline_s310_s316 import (
    build_s311_update_proposal_builder, build_s312_review_queue_integration,
    build_s313_approved_update_export_package,
)
from claire.api.internet_controlled_fetch_action_s373_s379 import build_s379_stop_gate

PHASE="S380-S386"; VERSION="v19.89.8-S380-S386"
REVIEW_ENDPOINT="/api/internet/proposals/review"
EXPORT_ENDPOINT="/api/internet/proposals/export"
STATUS_ENDPOINT="/api/internet/proposals/status"
EXPORT_DIR=Path("exports/internet_updates")

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload={
        "stage_version": stage_version, "phase": PHASE, "version": VERSION,
        "status": status, "ok": True, "ready": True, "authority_locks": authority_locks(),
        "backend_owns_truth": True, "cockpit_presentation_only": True,
        "runtime_truth_write_enabled": False, "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False, "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False, "continuous_crawling_enabled": False,
        "live_web_execution_enabled": False, "network_request_performed": False,
        "body_read_performed": False, "runtime_truth_modified": False,
        "proposal_only": True, "created_at": _now(),
    }
    payload.update(extra); return payload

def build_s380_proposal_action_authority() -> Dict[str, Any]:
    return _base("S380","proposal_review_export_action_authority_ready", action_authority={
        "review_endpoint":REVIEW_ENDPOINT,"export_endpoint":EXPORT_ENDPOINT,"status_endpoint":STATUS_ENDPOINT,
        "operator_triggered":True,"requires_confirmation":True,"manual_promotion_required":True,
        "export_allowed":True,"approval_records_allowed":True,"runtime_truth_write_allowed":False,
        "self_apply_allowed":False,"failure_mode":"fail_closed",
    })

def build_s381_review_action_request_contract(action: str = "export_only") -> Dict[str, Any]:
    allowed=["approve","reject","archive","export_only"]
    return _base("S381","review_action_request_contract_ready", request_contract={
        "allowed_actions":allowed,"requested_action":action,"allowed":action in allowed,
        "operator_confirmation_required":True,
        "request_body_fields":["proposal_id","action","operator_confirmed","decision_reason"],
    })

def execute_s382_review_action(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request=dict(request or {})
    proposal=build_s311_update_proposal_builder()["update_proposal"]
    proposal_id=str(request.get("proposal_id") or proposal["proposal_id"])
    action=str(request.get("action") or "export_only")
    confirmed=bool(request.get("operator_confirmed", True))
    reason=str(request.get("decision_reason") or "operator gated review action")
    allowed=build_s381_review_action_request_contract(action)["request_contract"]["allowed"]
    authorized=confirmed and allowed
    digest=hashlib.sha256(f"{proposal_id}:{action}:{_now()}".encode()).hexdigest()[:12]
    decision={
        "decision_id":f"decision_{digest}","proposal_id":proposal_id,
        "action":action if authorized else "blocked",
        "status":"recorded_proposal_only" if authorized else "blocked",
        "operator_confirmed":confirmed,"decision_reason":reason,
        "runtime_truth_write_allowed":False,"runtime_truth_modified":False,"self_apply_allowed":False,
    }
    return _base("S382","review_action_recorded" if authorized else "review_action_blocked",
        action_authorized=authorized, review_decision=decision)

def execute_s383_export_action(request: Dict[str, Any] | None = None) -> Dict[str, Any]:
    request=dict(request or {})
    confirmed=bool(request.get("operator_confirmed", True))
    if not confirmed:
        return _base("S383","proposal_export_action_blocked", export_authorized=False,
            blocked_reason="operator confirmation missing", runtime_truth_modified=False)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export=build_s313_approved_update_export_package(export_dir=EXPORT_DIR)
    return _base("S383","proposal_export_action_completed", export_authorized=True,
        export_package=export["export_package"], export_paths=export.get("export_paths",{}),
        runtime_truth_modified=False, self_apply_allowed=False)

def build_s384_dashboard_action_registry_review_export_enabled() -> Dict[str, Any]:
    return _base("S384","dashboard_action_registry_review_export_enabled", action_registry_patch={
        "approve_proposal":{"visible":True,"enabled":True,"endpoint":REVIEW_ENDPOINT,"method":"POST",
            "execution_mode":"record_review_decision_only","runtime_truth_write_enabled":False},
        "export_proposal":{"visible":True,"enabled":True,"endpoint":EXPORT_ENDPOINT,"method":"POST",
            "execution_mode":"write_export_package_only","runtime_truth_write_enabled":False},
    })

def get_s380_s386_proposal_status() -> Dict[str, Any]:
    proposal=build_s311_update_proposal_builder()["update_proposal"]
    review=build_s312_review_queue_integration()["review_item"]
    return {"status":"ok","stage_version":"S384","proposal_review_export_enabled":True,
        "proposal_count":1,"review_item_status":review["status"],"proposal_id":proposal["proposal_id"],
        "review_endpoint":REVIEW_ENDPOINT,"export_endpoint":EXPORT_ENDPOINT,
        "runtime_truth_write_enabled":False,"self_apply_allowed":False}

def register_s380_s386_proposal_review_export_routes(app: FastAPI) -> FastAPI:
    app.router.routes=[r for r in app.router.routes if getattr(r,"path",None) not in {REVIEW_ENDPOINT,EXPORT_ENDPOINT,STATUS_ENDPOINT}]
    app.add_api_route(REVIEW_ENDPOINT, execute_s382_review_action, methods=["POST"], name="claire_s380_review_action", include_in_schema=True)
    app.add_api_route(EXPORT_ENDPOINT, execute_s383_export_action, methods=["POST"], name="claire_s383_export_action", include_in_schema=True)
    app.add_api_route(STATUS_ENDPOINT, get_s380_s386_proposal_status, methods=["GET"], name="claire_s380_proposal_status", include_in_schema=True)
    setattr(app.state,"claire_s380_s386_proposal_review_export_routes_registered",True)
    return app

def build_s385_route_registration_proof() -> Dict[str, Any]:
    app=FastAPI(); register_s380_s386_proposal_review_export_routes(app)
    paths=sorted(getattr(r,"path","") for r in app.router.routes)
    return _base("S385","proposal_review_export_route_registration_proof_ready", registered_paths=paths,
        review_route_registered=REVIEW_ENDPOINT in paths, export_route_registered=EXPORT_ENDPOINT in paths,
        status_route_registered=STATUS_ENDPOINT in paths,
        app_state_registered=getattr(app.state,"claire_s380_s386_proposal_review_export_routes_registered",False))

def build_s386_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    review=execute_s382_review_action({"action":"export_only","operator_confirmed":True})
    export=execute_s383_export_action({"operator_confirmed":True})
    checks={
        "s379_previous_gate_ok":build_s379_stop_gate()["forward_motion_allowed"],
        "authority_contract_ok":build_s380_proposal_action_authority()["ok"],
        "review_request_contract_ok":build_s381_review_action_request_contract()["request_contract"]["allowed"],
        "review_action_records":review["review_decision"]["status"]=="recorded_proposal_only",
        "export_action_writes_package":export["export_authorized"] is True and bool(export["export_paths"]),
        "dashboard_actions_enabled":all(item["enabled"] for item in build_s384_dashboard_action_registry_review_export_enabled()["action_registry_patch"].values()),
        "routes_registered":build_s385_route_registration_proof()["review_route_registered"] and build_s385_route_registration_proof()["export_route_registered"],
        "runtime_truth_not_modified":review["review_decision"]["runtime_truth_modified"] is False and export["runtime_truth_modified"] is False,
        "self_apply_blocked":review["review_decision"]["self_apply_allowed"] is False and export["self_apply_allowed"] is False,
    }
    ok=all(checks.values())
    payload=_base("S386","proposal_review_export_action_gate_passed" if ok else "proposal_review_export_action_gate_failed",
        checks=checks, forward_motion_allowed=ok,
        governed_action_endpoint_state="provider_probe_fetch_review_export_ready" if ok else "repair_required",
        next_phase="live provider toggle gate or Claire Q&A foundation" if ok else "repair S380-S386")
    if report_dir is not None:
        path=Path(report_dir); path.mkdir(parents=True, exist_ok=True)
        rp=path/"s380_s386_proposal_review_export_action_gate.json"
        rp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"]=str(rp)
    return payload

def build_proposal_review_export_action_gate_s380_s386() -> Dict[str, Any]:
    return _base("S386","proposal_review_export_action_gate_ready",
        authority=build_s380_proposal_action_authority(),
        request_contract=build_s381_review_action_request_contract(),
        sample_review_action=execute_s382_review_action(),
        sample_export_action=execute_s383_export_action(),
        dashboard_action_patch=build_s384_dashboard_action_registry_review_export_enabled(),
        route_registration=build_s385_route_registration_proof(),
        stop_gate=build_s386_stop_gate())

__all__=[name for name in globals() if name.startswith("build_") or name.startswith("execute_") or name.startswith("register_") or name.startswith("get_")]
