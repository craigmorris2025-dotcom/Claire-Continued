from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from runtime_core.governance.governed_evidence_cards import get_governed_evidence_payload

router = APIRouter(prefix="/api/evidence/governed", tags=["Governed Evidence Cards"])


@router.get("/cards")
def read_governed_evidence_cards() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "policy": payload["policy"],
        "blocked_capabilities": payload["blocked_capabilities"],
        "evidence_cards": payload["evidence_cards"],
    }


@router.get("/review")
def read_governed_evidence_review() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "review_queue": payload["review_queue"],
        "cockpit_panel": payload["cockpit_panels"]["evidence_review"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


@router.get("/actions")
def read_governed_evidence_actions() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "governed_actions": payload["governed_actions"],
        "cockpit_panel": payload["cockpit_panels"]["actions"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


@router.get("/policy")
def read_governed_evidence_policy() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return {
        "version": payload["version"],
        "policy": payload["policy"],
        "blocked_capabilities": payload["blocked_capabilities"],
        "review_states": {
            card["review_state"]: card["review_label"] for card in payload["evidence_cards"]
        },
    }


@router.get("/status")
def read_governed_evidence_status() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return {
        "version": payload["version"],
        "generated_at": payload["generated_at"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "upstream_surfaces": payload["upstream_surfaces"],
        "stop_gate": payload["stop_gate"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


@router.get("/payload")
def read_governed_evidence_payload() -> dict[str, Any]:
    return get_governed_evidence_payload()

