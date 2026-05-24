"""Governed non-executable operator review actions for S730-S736."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional

from runtime_core.governance.governed_source_confidence_builder import build_source_confidence_cards
from runtime_core.governance.governed_search_result_quarantine import BLOCKED_CAPABILITIES

_ACTION_POLICY = {
    "actions_are_descriptors_only": True,
    "executes_commands": False,
    "performs_network_requests": False,
    "reads_bodies": False,
    "mutates_runtime_truth": False,
    "installs_packages": False,
    "requires_future_operator_gate": True,
}


def build_review_action_for_confidence_card(card: Mapping[str, Any]) -> Dict[str, Any]:
    citation_candidate = bool(card.get("citation_candidate"))
    confidence_band = str(card.get("confidence_band") or "low")
    if confidence_band == "denied":
        action_type = "reject_denied_source"
        action_state = "blocked_by_source_policy"
    elif citation_candidate:
        action_type = "review_citation_candidate"
        action_state = "operator_review_available_non_executable"
    else:
        action_type = "review_low_confidence_candidate"
        action_state = "operator_review_available_non_executable"
    return {
        "action_id": f"review-action-{card.get('confidence_card_id', 'unknown')}",
        "action_type": action_type,
        "action_state": action_state,
        "title": card.get("title") or "Review candidate",
        "source_family": card.get("source_family"),
        "trust_tier": card.get("trust_tier"),
        "confidence_score": card.get("confidence_score"),
        "confidence_band": confidence_band,
        "citation_candidate": citation_candidate,
        "operator_visible": True,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "body_read_enabled": False,
        "network_request_enabled": False,
        "allowed_future_decisions": [
            "approve_for_evidence_basket_preview",
            "reject_candidate",
            "request_more_metadata",
        ] if confidence_band != "denied" else ["reject_candidate"],
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
        "policy": deepcopy(_ACTION_POLICY),
    }


def build_operator_review_payload(cards: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    confidence_cards = list(cards) if cards is not None else build_source_confidence_cards()
    actions = [build_review_action_for_confidence_card(card) for card in confidence_cards]
    return {
        "stage_range": "S730-S736",
        "name": "Operator Review Actions",
        "terminal_state": "operator_review_actions_ready_non_executable",
        "summary": {
            "confidence_card_total": len(confidence_cards),
            "operator_action_total": len(actions),
            "review_available_total": sum(1 for action in actions if action["action_state"].startswith("operator_review")),
            "blocked_policy_total": sum(1 for action in actions if action["action_state"] == "blocked_by_source_policy"),
            "executable_actions": 0,
            "runtime_truth_mutations": 0,
            "body_reads": 0,
            "network_requests": 0,
        },
        "actions": actions,
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
        "policy": deepcopy(_ACTION_POLICY),
    }


def build_operator_review_actions(cards: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    return build_operator_review_payload(cards)["actions"]


def build_operator_review_status() -> Dict[str, Any]:
    payload = build_operator_review_payload()
    return {
        "stage_range": "S730-S736",
        "status": "ready",
        "stop_gate": "operator_review_actions_ready",
        "summary": payload["summary"],
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }
