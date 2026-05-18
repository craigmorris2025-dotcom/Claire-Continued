"""FastAPI routes for S639-S645 governed quarantine evidence store."""
from __future__ import annotations

from fastapi import APIRouter

from claire.governance.governed_quarantine_evidence_store import (
    build_quarantine_actions,
    build_quarantine_cards,
    build_quarantine_payload,
    build_quarantine_status,
    build_quarantine_stop_gate,
    build_review_queue,
    get_quarantine_policy,
    get_quarantine_store,
)

router = APIRouter(tags=["governed-quarantine-evidence"])


@router.get("/api/evidence/quarantine/store")
def evidence_quarantine_store():
    return get_quarantine_store()


@router.get("/api/evidence/quarantine/cards")
def evidence_quarantine_cards():
    return {"cards": build_quarantine_cards()}


@router.get("/api/evidence/quarantine/review-queue")
def evidence_quarantine_review_queue():
    return build_review_queue()


@router.get("/api/evidence/quarantine/actions")
def evidence_quarantine_actions():
    return {"actions": build_quarantine_actions()}


@router.get("/api/evidence/quarantine/policy")
def evidence_quarantine_policy():
    return get_quarantine_policy()


@router.get("/api/evidence/quarantine/status")
def evidence_quarantine_status():
    return build_quarantine_status()


@router.get("/api/evidence/quarantine/payload")
def evidence_quarantine_payload():
    return build_quarantine_payload()


@router.get("/api/evidence/quarantine/stop-gate")
def evidence_quarantine_stop_gate():
    return build_quarantine_stop_gate()


@router.get("/api/sources/evidence/quarantine/payload")
def sources_evidence_quarantine_payload():
    return build_quarantine_payload()


@router.get("/api/search/evidence/quarantine/cards")
def search_evidence_quarantine_cards():
    return {"cards": build_quarantine_cards()}
