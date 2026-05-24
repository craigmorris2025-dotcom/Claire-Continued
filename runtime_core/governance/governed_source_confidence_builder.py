"""Source confidence and citation candidate builder for S723-S729."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional

from runtime_core.governance.governed_result_evidence_normalizer import build_result_evidence_cards
from runtime_core.governance.governed_search_result_quarantine import BLOCKED_CAPABILITIES

TRUST_TIER_BASE_SCORES: Dict[str, float] = {
    "tier_1_official": 0.92,
    "tier_1_primary": 0.88,
    "tier_2_secondary": 0.72,
    "tier_3_open_web": 0.52,
    "tier_4_unknown": 0.30,
    "denied": 0.0,
}


def score_evidence_card(card: Mapping[str, Any]) -> Dict[str, Any]:
    trust_tier = str(card.get("trust_tier") or "tier_4_unknown")
    base_score = TRUST_TIER_BASE_SCORES.get(trust_tier, 0.25)
    inputs = dict(card.get("confidence_inputs") or {})
    if inputs.get("body_read"):
        base_score -= 0.20
    if inputs.get("network_request_performed"):
        base_score -= 0.10
    if card.get("evidence_state") == "denied_by_source_policy":
        base_score = 0.0
    score = max(0.0, min(1.0, round(base_score, 2)))
    citation_candidate = score >= 0.5 and card.get("evidence_state") == "review_card_ready"
    return {
        "confidence_card_id": f"confidence-{card.get('evidence_card_id', 'unknown')}",
        "evidence_card_id": card.get("evidence_card_id"),
        "title": card.get("title"),
        "url": card.get("url"),
        "source_family": card.get("source_family"),
        "trust_tier": trust_tier,
        "confidence_score": score,
        "confidence_band": "high" if score >= 0.85 else "medium" if score >= 0.65 else "low" if score > 0 else "denied",
        "citation_candidate": citation_candidate,
        "citation_state": "candidate_needs_operator_review" if citation_candidate else "not_citation_ready",
        "runtime_truth_state": "not_promoted",
        "scoring_inputs": inputs,
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }


def build_source_confidence_payload(cards: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    evidence_cards = list(cards) if cards is not None else build_result_evidence_cards()
    confidence_cards = [score_evidence_card(card) for card in evidence_cards]
    return {
        "stage_range": "S723-S729",
        "name": "Source Confidence + Citation Candidate Builder",
        "terminal_state": "citation_candidates_ready_for_operator_review",
        "summary": {
            "evidence_card_total": len(evidence_cards),
            "confidence_card_total": len(confidence_cards),
            "citation_candidate_total": sum(1 for item in confidence_cards if item["citation_candidate"]),
            "high_confidence_total": sum(1 for item in confidence_cards if item["confidence_band"] == "high"),
            "denied_total": sum(1 for item in confidence_cards if item["confidence_band"] == "denied"),
            "runtime_truth_mutations": 0,
            "body_reads": 0,
            "network_requests": 0,
        },
        "trust_tier_base_scores": deepcopy(TRUST_TIER_BASE_SCORES),
        "cards": confidence_cards,
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }


def build_source_confidence_cards(cards: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    return build_source_confidence_payload(cards)["cards"]


def build_source_confidence_status() -> Dict[str, Any]:
    payload = build_source_confidence_payload()
    return {
        "stage_range": "S723-S729",
        "status": "ready",
        "stop_gate": "source_confidence_ready",
        "summary": payload["summary"],
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }
