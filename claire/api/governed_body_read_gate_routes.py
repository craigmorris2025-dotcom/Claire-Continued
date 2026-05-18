"""FastAPI routes for S779-S834 governed body-read gate and extraction safety."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Body

from claire.governance.governed_body_read_authorization import (
    build_authorization_actions,
    build_authorization_cards,
    build_authorization_payload,
)
from claire.governance.governed_content_safety_sanitizer import (
    build_sanitizer_actions,
    build_sanitizer_cards,
    build_sanitizer_payload,
    classify_content_risk,
)
from claire.governance.governed_extraction_scope_contract import (
    build_extraction_scope_actions,
    build_extraction_scope_cards,
    build_extraction_scope_contract,
)
from claire.governance.governed_manual_body_read_gate import (
    build_manual_body_read_gate_actions,
    build_manual_body_read_gate_cards,
    build_manual_body_read_gate_payload,
    build_manual_body_read_status,
    build_manual_body_read_stop_gate,
)

router = APIRouter(tags=["Claire Governed Body Read Gate"])


@router.get("/api/web/body-read/authorization/payload")
def get_body_read_authorization_payload() -> Dict[str, Any]:
    return build_authorization_payload()


@router.get("/api/web/body-read/authorization/cards")
def get_body_read_authorization_cards() -> Any:
    return build_authorization_cards()


@router.get("/api/web/body-read/authorization/actions")
def get_body_read_authorization_actions() -> Any:
    return build_authorization_actions()


@router.post("/api/web/body-read/authorization/payload")
def post_body_read_authorization_payload(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    requests = payload.get("requests") if isinstance(payload, dict) else None
    return build_authorization_payload(requests)


@router.get("/api/web/body-read/extraction-scope/contract")
def get_extraction_scope_contract() -> Dict[str, Any]:
    return build_extraction_scope_contract()


@router.get("/api/web/body-read/extraction-scope/cards")
def get_extraction_scope_cards() -> Any:
    return build_extraction_scope_cards()


@router.get("/api/web/body-read/extraction-scope/actions")
def get_extraction_scope_actions() -> Any:
    return build_extraction_scope_actions()


@router.get("/api/web/body-read/sanitizer/payload")
def get_sanitizer_payload() -> Dict[str, Any]:
    return build_sanitizer_payload()


@router.get("/api/web/body-read/sanitizer/cards")
def get_sanitizer_cards() -> Any:
    return build_sanitizer_cards()


@router.get("/api/web/body-read/sanitizer/actions")
def get_sanitizer_actions() -> Any:
    return build_sanitizer_actions()


@router.post("/api/web/body-read/sanitizer/classify")
def post_sanitizer_classify(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    return classify_content_risk(payload.get("content_type"), payload.get("source_family"))


@router.get("/api/web/body-read/manual-gate/preflight")
def get_manual_gate_preflight() -> Dict[str, Any]:
    return build_manual_body_read_gate_payload()


@router.get("/api/web/body-read/manual-gate/payload")
def get_manual_gate_payload() -> Dict[str, Any]:
    return build_manual_body_read_gate_payload()


@router.get("/api/web/body-read/manual-gate/cards")
def get_manual_gate_cards() -> Any:
    return build_manual_body_read_gate_cards()


@router.get("/api/web/body-read/manual-gate/actions")
def get_manual_gate_actions() -> Any:
    return build_manual_body_read_gate_actions()


@router.get("/api/web/body-read/manual-gate/status")
def get_manual_gate_status() -> Dict[str, Any]:
    return build_manual_body_read_status()


@router.get("/api/web/body-read/manual-gate/stop-gate")
def get_manual_gate_stop_gate() -> Dict[str, Any]:
    return build_manual_body_read_stop_gate()


@router.get("/api/cockpit/body-read-gate/payload")
def get_cockpit_body_read_gate_payload() -> Dict[str, Any]:
    return build_manual_body_read_gate_payload()


@router.get("/api/cockpit/body-read-gate/cards")
def get_cockpit_body_read_gate_cards() -> Any:
    return build_manual_body_read_gate_cards()


@router.get("/api/cockpit/body-read-gate/actions")
def get_cockpit_body_read_gate_actions() -> Any:
    return build_manual_body_read_gate_actions()


@router.get("/api/cockpit/body-read-gate/status")
def get_cockpit_body_read_gate_status() -> Dict[str, Any]:
    return build_manual_body_read_status()


@router.get("/api/cockpit/body-read-gate/stop-gate")
def get_cockpit_body_read_gate_stop_gate() -> Dict[str, Any]:
    return build_manual_body_read_stop_gate()


@router.get("/api/internet/body-read-gate/payload")
def get_internet_body_read_gate_payload() -> Dict[str, Any]:
    return build_manual_body_read_gate_payload()
