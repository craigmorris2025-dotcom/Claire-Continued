"""Manual body-read request packet and preflight cockpit cards for S765-S778.

The packet is a non-executable governance artifact. It documents what Claire
would need before any future manual body-read gate can be considered.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

from claire.governance.governed_body_read_safety_plan import (
    build_body_read_safety_cards,
    build_body_read_safety_plan,
    get_blocked_capabilities,
)
from claire.governance.governed_evidence_basket_promotion_preview import (
    build_promotion_actions,
    build_promotion_cards,
    build_promotion_preview,
)
from claire.governance.governed_metadata_search_stop_gate import (
    build_metadata_search_actions,
    build_metadata_search_cards,
    build_metadata_search_proof,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_body_read_request_packet(candidate: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    candidate_data = dict(candidate or {})
    source_family = str(candidate_data.get("source_family") or "official_docs")
    title = str(candidate_data.get("title") or "Manual body-read request candidate")
    url = str(candidate_data.get("url") or "https://docs.example.invalid/manual-body-read-candidate")
    safety_plan = build_body_read_safety_plan([
        {
            "candidate_id": str(candidate_data.get("candidate_id") or "manual-body-read-request-001"),
            "title": title,
            "source_family": source_family,
            "url": url,
        }
    ])
    planned_candidate = safety_plan["candidates"][0]
    return {
        "stage_range": "S765-S771",
        "name": "Manual Body-Read Request Packet",
        "terminal_state": "manual_body_read_request_packet_ready_body_reads_blocked",
        "authority": "request_packet_only",
        "packet_id": "manual-body-read-request-packet-s765-s771",
        "created_at": _now_iso(),
        "candidate": planned_candidate,
        "summary": {
            "packet_ready": True,
            "body_read_allowed": False,
            "body_read_performed": False,
            "network_requests": 0,
            "runtime_truth_mutations": 0,
        },
        "required_operator_confirmations": [
            "single_url_scope_confirmed",
            "source_policy_reviewed",
            "body_read_risk_accepted",
            "quarantine_destination_confirmed",
            "runtime_truth_auto_promotion_disabled_confirmed",
        ],
        "blocked_capabilities": get_blocked_capabilities(),
        "execution_enabled": False,
    }


def build_body_read_preflight_payload() -> Dict[str, Any]:
    promotion = build_promotion_preview()
    metadata_proof = build_metadata_search_proof()
    safety_plan = build_body_read_safety_plan()
    packet = build_body_read_request_packet()
    cards = build_body_read_preflight_cards()
    actions = build_body_read_preflight_actions()
    return {
        "stage_range": "S737-S778",
        "name": "Controlled Metadata Proof + Body-Read Planning",
        "terminal_state": "metadata_proof_complete_body_read_planning_ready",
        "authority": "cockpit_visible_planning_only",
        "payload_id": "controlled-metadata-proof-and-body-read-planning-s737-s778",
        "created_at": _now_iso(),
        "summary": {
            "promotion_preview_ready": True,
            "metadata_search_stop_gate_ready": True,
            "body_read_safety_plan_ready": True,
            "manual_body_read_packet_ready": True,
            "cards_total": len(cards),
            "actions_total": len(actions),
            "executable_actions": 0,
            "body_reads": 0,
            "network_requests": 0,
            "runtime_truth_mutations": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "sections": {
            "evidence_basket_promotion_preview": promotion,
            "controlled_metadata_search_stop_gate": metadata_proof,
            "body_read_safety_plan": safety_plan,
            "manual_body_read_request_packet": packet,
        },
        "cards": cards,
        "actions": actions,
        "stop_gate": build_body_read_preflight_stop_gate(),
    }


def build_body_read_preflight_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    cards.extend(build_promotion_cards())
    cards.extend(build_metadata_search_cards())
    cards.extend(build_body_read_safety_cards())
    cards.append(
        {
            "card_id": "manual-body-read-request-packet-card",
            "title": "Manual body-read request packet",
            "subtitle": "Planning only / body reads blocked",
            "state": "packet_ready_non_executable",
            "summary": "A future manual body-read request can be described, but this build cannot execute it.",
            "badges": ["request-packet", "non-executable", "body-read-blocked", "operator-gated"],
            "execution_enabled": False,
        }
    )
    return cards


def build_body_read_preflight_actions() -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    actions.extend(build_promotion_actions())
    actions.extend(build_metadata_search_actions())
    actions.extend(
        [
            {
                "action_id": "prepare_manual_body_read_request_packet",
                "label": "Prepare manual body-read request packet",
                "description": "Builds a governance packet only. Body reading remains blocked.",
                "execution_enabled": False,
                "body_read_allowed": False,
                "requires_operator_approval": True,
            },
            {
                "action_id": "open_body_read_safety_plan",
                "label": "Open body-read safety plan",
                "description": "Displays risk, scope, and required unlocks before any future body-read gate.",
                "execution_enabled": False,
                "body_read_allowed": False,
                "requires_operator_approval": True,
            },
        ]
    )
    return actions


def build_body_read_preflight_stop_gate() -> Dict[str, Any]:
    return {
        "stage_range": "S772-S778",
        "gate_id": "S778_BODY_READ_PREFLIGHT_STOP_GATE",
        "passed": True,
        "terminal_state": "body_read_preflight_visible_body_reads_blocked",
        "meaning": "Claire can show the body-read governance plan, request packet, and cockpit cards without reading page bodies.",
        "allowed_next_phase": "governed_body_read_gate_design",
        "blocked_next_phase": "body_read_execution_or_crawling",
        "blocked_capabilities": get_blocked_capabilities(),
    }


def build_status() -> Dict[str, Any]:
    return {
        "stage_range": "S737-S778",
        "status": "metadata_proof_and_body_read_planning_ready",
        "terminal_state": "metadata_proof_complete_body_read_planning_ready",
        "blocked_capabilities": get_blocked_capabilities(),
    }
