from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from runtime_core.api.governed_s92_s98_cockpit_contracts import (
    build_canonical_s85_s91_panel,
    build_review_queue_status,
    build_export_manifest,
    build_cockpit_evidence_output_card,
    perform_operator_review_action,
    build_route_demo_selector,
    build_end_to_end_cockpit_demo_proof,
)

router = APIRouter(prefix="/api/governed/operator", tags=["governed-operator-s99-s105"])

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_mutation_blocked": True,
    "runtime_truth_write_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
}

DEFAULT_EVIDENCE = {
    "basket_id": "api_demo_basket_s99_s105",
    "trust_score": 0.78,
    "evidence_items": [
        {
            "evidence_id": "api_ev_s99_001",
            "title": "Governed operator API demo signal",
            "trust_score": 0.78,
        }
    ],
}

DEFAULT_EXTRACTION = {
    "extraction_id": "api_extract_s99_s105",
    "signals": [
        {"label": "portfolio operator API signal", "type": "portfolio", "confidence": 0.79},
        {"label": "design implication signal", "type": "design", "confidence": 0.65},
    ],
}

STORE_PATH = Path.cwd() / "data" / "governed_review_queue.json"
EXPORT_DIR = Path.cwd() / "exports" / "governed_outputs"


class ReviewActionRequest(BaseModel):
    review_item_id: str = Field(..., min_length=1)
    action: Literal["approve", "reject", "archive", "export_only", "export-only"]
    operator: str = "operator"
    note: str = ""


class RouteDemoRequest(BaseModel):
    route: Literal["portfolio", "breakthrough", "design"]
    approve: bool = False
    evidence_basket: Dict[str, Any] | None = None
    extraction: Dict[str, Any] | None = None


@router.get("/proof-panel")
def get_governed_proof_panel() -> Dict[str, Any]:
    payload = build_canonical_s85_s91_panel(
        DEFAULT_EVIDENCE,
        DEFAULT_EXTRACTION,
        store_path=STORE_PATH,
        export_dir=EXPORT_DIR,
    )
    payload["endpoint_contract_version"] = "S99"
    return payload


@router.get("/review-queue")
def get_review_queue_status() -> Dict[str, Any]:
    payload = build_review_queue_status(store_path=STORE_PATH)
    payload["endpoint_contract_version"] = "S99-S93"
    return payload


@router.post("/review-action")
def post_review_action(request: ReviewActionRequest) -> Dict[str, Any]:
    try:
        payload = perform_operator_review_action(
            request.review_item_id,
            request.action,
            store_path=STORE_PATH,
            export_dir=EXPORT_DIR,
            operator=request.operator,
            note=request.note,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payload["endpoint_contract_version"] = "S100"
    return payload


@router.post("/route-demo")
def post_route_demo(request: RouteDemoRequest) -> Dict[str, Any]:
    try:
        payload = build_route_demo_selector(
            request.route,
            request.evidence_basket or DEFAULT_EVIDENCE,
            request.extraction or DEFAULT_EXTRACTION,
            store_path=STORE_PATH,
            export_dir=EXPORT_DIR,
            approve=request.approve,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payload["endpoint_contract_version"] = "S101"
    return payload


@router.get("/export-manifest")
def get_export_manifest() -> Dict[str, Any]:
    payload = build_export_manifest(export_dir=EXPORT_DIR)
    payload["endpoint_contract_version"] = "S102"
    return payload


@router.get("/cockpit-card")
def get_cockpit_card() -> Dict[str, Any]:
    payload = build_cockpit_evidence_output_card(
        DEFAULT_EVIDENCE,
        DEFAULT_EXTRACTION,
        store_path=STORE_PATH,
        export_dir=EXPORT_DIR,
    )
    payload["endpoint_contract_version"] = "S103"
    return payload


@router.get("/fetch-map")
def get_cockpit_fetch_map() -> Dict[str, Any]:
    return {
        "endpoint_contract_version": "S103",
        "status": "fetch_map_available",
        "read_only": True,
        "cockpit_fetch_map": {
            "proof_panel": "/api/governed/operator/proof-panel",
            "review_queue": "/api/governed/operator/review-queue",
            "review_action": "/api/governed/operator/review-action",
            "route_demo": "/api/governed/operator/route-demo",
            "export_manifest": "/api/governed/operator/export-manifest",
            "cockpit_card": "/api/governed/operator/cockpit-card",
            "api_demo_proof": "/api/governed/operator/api-demo-proof",
        },
        "locks": dict(LOCKS),
    }


@router.get("/swagger-proof")
def get_swagger_visibility_proof() -> Dict[str, Any]:
    return {
        "endpoint_contract_version": "S104",
        "status": "swagger_visible",
        "tag": "governed-operator-s99-s105",
        "routes": [
            "GET /api/governed/operator/proof-panel",
            "GET /api/governed/operator/review-queue",
            "POST /api/governed/operator/review-action",
            "POST /api/governed/operator/route-demo",
            "GET /api/governed/operator/export-manifest",
            "GET /api/governed/operator/cockpit-card",
            "GET /api/governed/operator/fetch-map",
            "GET /api/governed/operator/api-demo-proof",
        ],
        "locks": dict(LOCKS),
    }


@router.get("/api-demo-proof")
def get_end_to_end_operator_api_demo_proof() -> Dict[str, Any]:
    proof = build_end_to_end_cockpit_demo_proof(
        DEFAULT_EVIDENCE,
        DEFAULT_EXTRACTION,
        store_path=STORE_PATH,
        export_dir=EXPORT_DIR,
    )
    proof["endpoint_contract_version"] = "S105"
    proof["api_demo_path"] = [
        "GET proof-panel",
        "GET review-queue",
        "POST route-demo",
        "POST review-action",
        "GET export-manifest",
        "GET cockpit-card",
    ]
    proof["locks"] = dict(LOCKS)
    return proof


def include_governed_s99_s105_routes(app: Any) -> Any:
    marker = "governed_operator_s99_s105_routes_included"
    if getattr(app.state, marker, False):
        return app
    app.include_router(router)
    setattr(app.state, marker, True)
    return app
