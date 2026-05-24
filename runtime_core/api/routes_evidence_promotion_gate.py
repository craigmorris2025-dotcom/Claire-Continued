
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from runtime_core.internet.evidence_promotion_gate import (
    build_evidence_promotion_gate,
    evidence_promotion_summary,
    promote_approved_evidence,
)

router = APIRouter(tags=["Internet Evidence"])


@router.get("/internet/evidence-promotion")
def get_evidence_promotion_gate():
    return build_evidence_promotion_gate()


@router.get("/internet/evidence-promotion/summary")
def get_evidence_promotion_summary():
    return evidence_promotion_summary()


@router.post("/internet/evidence-promotion/rebuild")
def rebuild_evidence_promotion_gate():
    return build_evidence_promotion_gate()


@router.post("/internet/evidence-promotion/promote-approved")
def post_promote_approved_evidence(payload: Dict[str, Any]):
    return promote_approved_evidence(confirm_text=str(payload.get("confirm_text", "")))


@router.get("/internet/evidence-promotion/status")
def get_evidence_promotion_status():
    return evidence_promotion_summary()
