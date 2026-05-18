from __future__ import annotations

from fastapi import APIRouter, Query

from claire.governance.governed_source_evidence_intake import (
    build_source_evidence_cards,
    build_source_evidence_intake_payload,
    build_source_intake_actions,
    blocked_authority,
    source_family_policy,
)


router = APIRouter(tags=["Claire Governed Source Evidence Intake"])


@router.get("/api/evidence/source/intake")
def get_source_evidence_intake(
    query: str = Query(default="", description="Operator/user query descriptor. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return build_source_evidence_intake_payload(query=query, route_context=route_context)


@router.get("/api/evidence/source/intake/cards")
def get_source_evidence_intake_cards(
    query: str = Query(default="", description="Operator/user query descriptor. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return {"cards": build_source_evidence_cards(query=query, route_context=route_context)}


@router.get("/api/evidence/source/intake/actions")
def get_source_evidence_intake_actions(
    query: str = Query(default="", description="Operator/user query descriptor. Not executed."),
    route_context: str = Query(default="web_source_search"),
):
    return {"actions": build_source_intake_actions(query=query, route_context=route_context)}


@router.get("/api/evidence/source/intake/policy")
def get_source_evidence_intake_policy():
    return {
        "source_families": source_family_policy(),
        "authority": blocked_authority(),
        "body_reads": "blocked",
        "network_requests": "not_performed",
        "runtime_truth_mutation": "blocked",
    }


@router.get("/api/evidence/source/intake/status")
def get_source_evidence_intake_status():
    return {
        "phase": "S611-S617",
        "status": "ready",
        "execution": "blocked",
        "body_reads": "blocked",
        "network_requests": "not_performed",
        "runtime_truth_mutation": "blocked",
        "authority": blocked_authority(),
    }


@router.get("/api/evidence/source/intake/stop-gate")
def get_source_evidence_intake_stop_gate():
    return {
        "gate_id": "S617",
        "state": "pass_ready",
        "forward_motion_allowed": True,
        "next": "S618-S624 governed query builder and search scope compiler",
        "blocked_authorities_preserved": True,
    }

