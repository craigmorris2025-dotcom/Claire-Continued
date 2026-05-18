"""FastAPI routes for S709-S736 governed search result review."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from claire.governance.governed_operator_review_actions import (
    build_operator_review_actions,
    build_operator_review_payload,
    build_operator_review_status,
)
from claire.governance.governed_result_evidence_normalizer import (
    build_result_evidence_cards,
    build_result_evidence_payload,
    build_result_evidence_status,
)
from claire.governance.governed_search_result_quarantine import (
    build_quarantine_cards,
    build_quarantine_status,
    build_quarantine_store,
    get_blocked_capabilities,
)
from claire.governance.governed_source_confidence_builder import (
    build_source_confidence_cards,
    build_source_confidence_payload,
    build_source_confidence_status,
)

router = APIRouter(tags=["Governed Search Result Review"])


class MetadataResultIn(BaseModel):
    title: str = Field(default="Untitled metadata result")
    url: str = Field(default="")
    source_family: Optional[str] = Field(default=None)
    provider: str = Field(default="manual_metadata_probe_preview")
    snippet: str = Field(default="Metadata-only result; body not read.")
    rank: int = Field(default=1)


class MetadataResultsIn(BaseModel):
    results: List[MetadataResultIn] = Field(default_factory=list)


def _as_dicts(payload: MetadataResultsIn) -> List[Dict[str, Any]]:
    return [item.model_dump() if hasattr(item, "model_dump") else item.dict() for item in payload.results]


@router.get("/api/search/results/quarantine/store")
def get_search_result_quarantine_store() -> Dict[str, Any]:
    return build_quarantine_store()


@router.post("/api/search/results/quarantine/store")
def post_search_result_quarantine_store(payload: MetadataResultsIn) -> Dict[str, Any]:
    return build_quarantine_store(_as_dicts(payload))


@router.get("/api/search/results/quarantine/cards")
def get_search_result_quarantine_cards() -> List[Dict[str, Any]]:
    return build_quarantine_cards()


@router.get("/api/search/results/quarantine/status")
def get_search_result_quarantine_status() -> Dict[str, Any]:
    return build_quarantine_status()


@router.get("/api/search/results/quarantine/payload")
def get_search_result_quarantine_payload() -> Dict[str, Any]:
    return build_quarantine_store()


@router.get("/api/search/results/normalize/cards")
def get_result_evidence_cards() -> List[Dict[str, Any]]:
    return build_result_evidence_cards()


@router.get("/api/search/results/normalize/payload")
def get_result_evidence_payload() -> Dict[str, Any]:
    return build_result_evidence_payload()


@router.get("/api/search/results/normalize/status")
def get_result_evidence_status() -> Dict[str, Any]:
    return build_result_evidence_status()


@router.get("/api/search/source-confidence/cards")
def get_source_confidence_cards() -> List[Dict[str, Any]]:
    return build_source_confidence_cards()


@router.get("/api/search/source-confidence/payload")
def get_source_confidence_payload() -> Dict[str, Any]:
    return build_source_confidence_payload()


@router.get("/api/search/source-confidence/status")
def get_source_confidence_status() -> Dict[str, Any]:
    return build_source_confidence_status()


@router.get("/api/search/operator-review/actions")
def get_operator_review_actions() -> List[Dict[str, Any]]:
    return build_operator_review_actions()


@router.get("/api/search/operator-review/payload")
def get_operator_review_payload() -> Dict[str, Any]:
    return build_operator_review_payload()


@router.get("/api/search/operator-review/status")
def get_operator_review_status() -> Dict[str, Any]:
    return build_operator_review_status()


@router.get("/api/cockpit/search-results/payload")
def get_cockpit_search_results_payload() -> Dict[str, Any]:
    return {
        "stage_range": "S709-S736",
        "name": "Cockpit Search Result Review Payload",
        "terminal_state": "search_result_review_ready",
        "quarantine": build_quarantine_store(),
        "evidence": build_result_evidence_payload(),
        "confidence": build_source_confidence_payload(),
        "operator_review": build_operator_review_payload(),
        "blocked_capabilities": get_blocked_capabilities(),
    }


@router.get("/api/cockpit/search-results/cards")
def get_cockpit_search_results_cards() -> Dict[str, Any]:
    return {
        "quarantine_cards": build_quarantine_cards(),
        "evidence_cards": build_result_evidence_cards(),
        "confidence_cards": build_source_confidence_cards(),
    }


@router.get("/api/cockpit/search-results/actions")
def get_cockpit_search_results_actions() -> List[Dict[str, Any]]:
    return build_operator_review_actions()


@router.get("/api/cockpit/search-results/status")
def get_cockpit_search_results_status() -> Dict[str, Any]:
    return {
        "stage_range": "S709-S736",
        "status": "ready",
        "stop_gate": "search_result_review_ready",
        "blocked_capabilities": get_blocked_capabilities(),
    }


@router.get("/api/cockpit/search-results/stop-gate")
def get_cockpit_search_results_stop_gate() -> Dict[str, Any]:
    return {
        "stage_range": "S709-S736",
        "stop_gate": "pass",
        "forward_motion_allowed": True,
        "reason": "metadata-only search result quarantine, evidence normalization, confidence scoring, and non-executable operator actions are available",
        "blocked_capabilities": get_blocked_capabilities(),
    }


@router.get("/api/internet/search-results/payload")
def get_internet_search_results_payload_alias() -> Dict[str, Any]:
    return get_cockpit_search_results_payload()
