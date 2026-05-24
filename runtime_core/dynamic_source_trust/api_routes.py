from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .service import DynamicSourceTrustService


router = APIRouter(prefix="/internet/source-trust", tags=["Dynamic Source Trust"])


class TrustEventRequest(BaseModel):
    domain: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    evidence_id: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""


class WeightEvidenceRequest(BaseModel):
    evidence: Dict[str, Any]


class WeightEvidenceBatchRequest(BaseModel):
    evidence: List[Dict[str, Any]]


@router.post("/events")
def record_event(request: TrustEventRequest):
    service = DynamicSourceTrustService()
    return service.record_event(
        domain=request.domain,
        event_type=request.event_type,
        evidence_id=request.evidence_id,
        confidence=request.confidence,
        reason=request.reason,
    )


@router.post("/weight")
def weight_evidence(request: WeightEvidenceRequest):
    service = DynamicSourceTrustService()
    return service.weight_evidence(request.evidence)


@router.post("/weight-batch")
def weight_evidence_batch(request: WeightEvidenceBatchRequest):
    service = DynamicSourceTrustService()
    return service.weight_evidence_batch(request.evidence)


@router.post("/quarantine/{domain}")
def quarantine_source(domain: str, reason: str = "Manual quarantine"):
    service = DynamicSourceTrustService()
    return service.quarantine_source(domain, reason=reason)


@router.post("/release/{domain}")
def release_source(domain: str, reason: str = "Manual release"):
    service = DynamicSourceTrustService()
    return service.release_source(domain, reason=reason)


@router.get("/profiles")
def list_profiles():
    service = DynamicSourceTrustService()
    return {"profiles": service.list_profiles()}


@router.get("/events")
def list_events(domain: Optional[str] = None, limit: int = 100):
    service = DynamicSourceTrustService()
    return {"events": service.list_events(domain=domain, limit=limit)}
