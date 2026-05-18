"""FastAPI routes for S737-S778 controlled metadata proof and body-read planning."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from claire.governance.governed_body_read_preflight import (
    build_body_read_preflight_actions,
    build_body_read_preflight_cards,
    build_body_read_preflight_payload,
    build_body_read_preflight_stop_gate,
    build_body_read_request_packet,
    build_status as build_body_read_preflight_status,
)
from claire.governance.governed_body_read_safety_plan import (
    build_body_read_safety_cards,
    build_body_read_safety_plan,
    build_status as build_body_read_safety_status,
)
from claire.governance.governed_evidence_basket_promotion_preview import (
    build_promotion_actions,
    build_promotion_cards,
    build_promotion_preview,
    build_status as build_promotion_status,
)
from claire.governance.governed_metadata_search_stop_gate import (
    build_metadata_search_actions,
    build_metadata_search_cards,
    build_metadata_search_proof,
    build_status as build_metadata_search_status,
)

router = APIRouter(tags=["Claire Governed Web Search Body Read Planning"])


@router.get("/api/evidence/basket/promotion-preview")
def get_evidence_basket_promotion_preview() -> Dict[str, Any]:
    return build_promotion_preview()


@router.get("/api/evidence/basket/promotion-preview/cards")
def get_evidence_basket_promotion_preview_cards() -> Any:
    return build_promotion_cards()


@router.get("/api/evidence/basket/promotion-preview/actions")
def get_evidence_basket_promotion_preview_actions() -> Any:
    return build_promotion_actions()


@router.get("/api/evidence/basket/promotion-preview/status")
def get_evidence_basket_promotion_preview_status() -> Dict[str, Any]:
    return build_promotion_status()


@router.get("/api/search/metadata/controlled-proof/payload")
def get_controlled_metadata_search_proof_payload() -> Dict[str, Any]:
    return build_metadata_search_proof()


@router.get("/api/search/metadata/controlled-proof/cards")
def get_controlled_metadata_search_proof_cards() -> Any:
    return build_metadata_search_cards()


@router.get("/api/search/metadata/controlled-proof/actions")
def get_controlled_metadata_search_proof_actions() -> Any:
    return build_metadata_search_actions()


@router.get("/api/search/metadata/controlled-proof/status")
def get_controlled_metadata_search_proof_status() -> Dict[str, Any]:
    return build_metadata_search_status()


@router.get("/api/search/metadata/controlled-proof/stop-gate")
def get_controlled_metadata_search_proof_stop_gate() -> Dict[str, Any]:
    return build_metadata_search_proof()["stop_gate"]


@router.get("/api/web/body-read/safety-plan")
def get_body_read_safety_plan() -> Dict[str, Any]:
    return build_body_read_safety_plan()


@router.get("/api/web/body-read/safety/cards")
def get_body_read_safety_cards() -> Any:
    return build_body_read_safety_cards()


@router.get("/api/web/body-read/safety/status")
def get_body_read_safety_status() -> Dict[str, Any]:
    return build_body_read_safety_status()


@router.post("/api/web/body-read/risk-classifier")
def post_body_read_risk_classifier(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidates = payload.get("candidates") if isinstance(payload, dict) else None
    return build_body_read_safety_plan(candidates)


@router.get("/api/web/body-read/request-packet")
def get_body_read_request_packet() -> Dict[str, Any]:
    return build_body_read_request_packet()


@router.post("/api/web/body-read/request-packet")
def post_body_read_request_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = payload.get("candidate") if isinstance(payload, dict) else None
    return build_body_read_request_packet(candidate)


@router.get("/api/web/body-read/preflight/payload")
def get_body_read_preflight_payload() -> Dict[str, Any]:
    return build_body_read_preflight_payload()


@router.get("/api/web/body-read/preflight/cards")
def get_body_read_preflight_cards() -> Any:
    return build_body_read_preflight_cards()


@router.get("/api/web/body-read/preflight/actions")
def get_body_read_preflight_actions() -> Any:
    return build_body_read_preflight_actions()


@router.get("/api/web/body-read/preflight/status")
def get_body_read_preflight_status() -> Dict[str, Any]:
    return build_body_read_preflight_status()


@router.get("/api/web/body-read/preflight/stop-gate")
def get_body_read_preflight_stop_gate() -> Dict[str, Any]:
    return build_body_read_preflight_stop_gate()


@router.get("/api/cockpit/web-search/payload")
def get_cockpit_web_search_payload() -> Dict[str, Any]:
    return build_body_read_preflight_payload()


@router.get("/api/cockpit/web-search/cards")
def get_cockpit_web_search_cards() -> Any:
    return build_body_read_preflight_cards()


@router.get("/api/cockpit/web-search/actions")
def get_cockpit_web_search_actions() -> Any:
    return build_body_read_preflight_actions()


@router.get("/api/cockpit/web-search/status")
def get_cockpit_web_search_status() -> Dict[str, Any]:
    return build_body_read_preflight_status()


@router.get("/api/cockpit/web-search/stop-gate")
def get_cockpit_web_search_stop_gate() -> Dict[str, Any]:
    return build_body_read_preflight_stop_gate()


@router.get("/api/internet/controlled-metadata-proof/payload")
def get_internet_controlled_metadata_proof_payload() -> Dict[str, Any]:
    return build_body_read_preflight_payload()
