from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body

from claire.governance.governed_manual_body_read_execution_envelope import build_execution_envelope_actions, build_execution_envelope_cards, build_execution_envelope_payload
from claire.governance.governed_runtime_truth_promotion_preview import build_cockpit_source_ingestion_actions, build_cockpit_source_ingestion_cards, build_cockpit_source_ingestion_payload, build_runtime_truth_promotion_preview, build_s900_stop_gate
from claire.governance.governed_sanitized_extraction_preview import build_sanitized_extraction_cards, build_sanitized_extraction_preview_payload
from claire.governance.governed_source_update_ingestion import build_operator_ingestion_actions, build_source_ingestion_cards, build_source_ingestion_payload, build_source_lineage_payload, build_update_proposal_payload

router = APIRouter(tags=["Governed Body Read Source Ingestion S835-S900"])

@router.get("/api/web/body-read/execution-envelope/payload")
def get_body_read_execution_envelope_payload() -> Dict[str, Any]:
    return build_execution_envelope_payload()

@router.post("/api/web/body-read/execution-envelope/payload")
def post_body_read_execution_envelope_payload(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    return build_execution_envelope_payload(payload.get("envelopes"))

@router.get("/api/web/body-read/execution-envelope/cards")
def get_body_read_execution_envelope_cards() -> Any:
    return build_execution_envelope_cards()

@router.get("/api/web/body-read/execution-envelope/actions")
def get_body_read_execution_envelope_actions() -> Any:
    return build_execution_envelope_actions()

@router.get("/api/web/body-read/extraction-preview/payload")
def get_sanitized_extraction_preview_payload() -> Dict[str, Any]:
    return build_sanitized_extraction_preview_payload()

@router.post("/api/web/body-read/extraction-preview/payload")
def post_sanitized_extraction_preview_payload(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    return build_sanitized_extraction_preview_payload(payload.get("previews"))

@router.get("/api/web/body-read/extraction-preview/cards")
def get_sanitized_extraction_preview_cards() -> Any:
    return build_sanitized_extraction_cards()

@router.get("/api/web/source-ingestion/draft")
def get_source_ingestion_draft() -> Dict[str, Any]:
    return build_source_ingestion_payload()

@router.post("/api/web/source-ingestion/draft")
def post_source_ingestion_draft(payload: Dict[str, Any] = Body(default_factory=dict)) -> Dict[str, Any]:
    return build_source_ingestion_payload(payload.get("drafts"))

@router.get("/api/web/source-ingestion/cards")
def get_source_ingestion_cards() -> Any:
    return build_source_ingestion_cards()

@router.get("/api/web/source-ingestion/lineage")
def get_source_ingestion_lineage() -> Dict[str, Any]:
    return build_source_lineage_payload()

@router.get("/api/web/source-ingestion/validate")
def get_source_ingestion_validate() -> Dict[str, Any]:
    payload = build_source_ingestion_payload()
    return {"stage_range": "S856-S869", "status": "ready", "terminal_state": "source_ingestion_validation_ready_review_required", "valid": True, "summary": payload["summary"], "blocked_capabilities": payload["blocked_capabilities"]}

@router.get("/api/web/update-proposal/payload")
def get_update_proposal_payload() -> Dict[str, Any]:
    return build_update_proposal_payload()

@router.get("/api/web/operator-ingestion/actions")
def get_operator_ingestion_actions() -> Any:
    return build_operator_ingestion_actions()

@router.get("/api/web/runtime-truth/promotion-preview")
def get_runtime_truth_promotion_preview() -> Dict[str, Any]:
    return build_runtime_truth_promotion_preview()

@router.get("/api/cockpit/source-ingestion/payload")
def get_cockpit_source_ingestion_payload() -> Dict[str, Any]:
    return build_cockpit_source_ingestion_payload()

@router.get("/api/cockpit/source-ingestion/cards")
def get_cockpit_source_ingestion_cards() -> Any:
    return build_cockpit_source_ingestion_cards()

@router.get("/api/cockpit/source-ingestion/actions")
def get_cockpit_source_ingestion_actions() -> Any:
    return build_cockpit_source_ingestion_actions()

@router.get("/api/cockpit/source-ingestion/status")
def get_cockpit_source_ingestion_status() -> Dict[str, Any]:
    payload = build_cockpit_source_ingestion_payload()
    return {"status": "ready", "stage_range": payload["stage_range"], "terminal_state": payload["terminal_state"], "executable_actions": 0, "body_read_allowed": False, "runtime_mutation_enabled": False, "automatic_updates_enabled": False}

@router.get("/api/cockpit/source-ingestion/stop-gate")
def get_cockpit_source_ingestion_stop_gate() -> Dict[str, Any]:
    return build_s900_stop_gate()

@router.get("/api/internet/source-ingestion/payload")
def get_internet_source_ingestion_payload() -> Dict[str, Any]:
    return build_cockpit_source_ingestion_payload()

@router.get("/api/internet/s900-stop-gate")
def get_internet_s900_stop_gate() -> Dict[str, Any]:
    return build_s900_stop_gate()
