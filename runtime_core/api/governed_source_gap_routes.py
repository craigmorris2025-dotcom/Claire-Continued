"""FastAPI routes for governed source gap matrix S604-S610."""
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.governance.governed_source_gap_matrix import (
    build_stop_gate,
    governed_source_gap_payload,
    search_scope_cards,
    search_scope_plans,
    source_gap_actions,
    source_gap_cards,
    source_gap_matrix,
    source_gap_policy,
    source_gap_status,
)

router = APIRouter(tags=["governed-source-gap-matrix"])


@router.get("/api/sources/gaps/matrix")
def get_source_gap_matrix():
    return source_gap_matrix()


@router.get("/api/sources/gaps/cards")
def get_source_gap_cards():
    return source_gap_cards()


@router.get("/api/sources/gaps/actions")
def get_source_gap_actions():
    return source_gap_actions()


@router.get("/api/sources/gaps/policy")
def get_source_gap_policy():
    return source_gap_policy()


@router.get("/api/sources/gaps/status")
def get_source_gap_status():
    return source_gap_status()


@router.get("/api/sources/gaps/payload")
def get_source_gap_payload():
    return governed_source_gap_payload()


@router.get("/api/sources/gaps/stop-gate")
def get_source_gap_stop_gate():
    return build_stop_gate()


@router.get("/api/search/scope/plans")
def get_search_scope_plans():
    return search_scope_plans()


@router.get("/api/search/scope/cards")
def get_search_scope_cards():
    return search_scope_cards()


@router.get("/api/search/scope/actions")
def get_search_scope_actions():
    return source_gap_actions()


@router.get("/api/search/scope/status")
def get_search_scope_status():
    return source_gap_status()


@router.get("/api/search/scope/payload")
def get_search_scope_payload():
    return governed_source_gap_payload()
