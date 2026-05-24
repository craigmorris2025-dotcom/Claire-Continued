"""Normalize quarantined metadata results into evidence-review cockpit cards for S716-S722."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional

from runtime_core.governance.governed_search_result_quarantine import (
    BLOCKED_CAPABILITIES,
    build_quarantine_store,
)


def build_evidence_card_from_result(result: Mapping[str, Any]) -> Dict[str, Any]:
    source_family = str(result.get("source_family") or "unknown_or_user_supplied")
    trust_tier = str(result.get("trust_tier") or "unknown")
    denied = result.get("quarantine_state") == "denied"
    return {
        "evidence_card_id": f"evidence-card-{result.get('result_id', 'unknown')}",
        "source_result_id": result.get("result_id"),
        "title": result.get("title") or "Untitled evidence card",
        "url": result.get("url") or "",
        "source_family": source_family,
        "trust_tier": trust_tier,
        "evidence_state": "denied_by_source_policy" if denied else "review_card_ready",
        "review_state": result.get("review_state") or "pending_operator_review",
        "confidence_inputs": {
            "source_family_known": source_family not in {"unknown_or_user_supplied", "denied_or_unsafe"},
            "metadata_only": bool(result.get("metadata_only")),
            "body_read": False,
            "network_request_performed": False,
            "runtime_truth_mutated": False,
        },
        "claim_preview": {
            "headline": result.get("title") or "Untitled metadata result",
            "snippet": result.get("snippet") or "Metadata-only result; body not read.",
            "claim_status": "candidate_only_not_runtime_truth",
        },
        "lineage": {
            "provider": result.get("provider") or "unexecuted_provider_boundary",
            "rank": result.get("rank"),
            "captured_at": result.get("captured_at"),
            "quarantine_state": result.get("quarantine_state"),
        },
        "badges": [
            "candidate-evidence",
            "metadata-only",
            "operator-review-required" if not denied else "denied-source-policy",
            "not-runtime-truth",
        ],
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }


def build_result_evidence_payload(results: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    store = build_quarantine_store(results)
    cards = [build_evidence_card_from_result(item) for item in store["results"]]
    return {
        "stage_range": "S716-S722",
        "name": "Result-to-Evidence Card Normalizer",
        "terminal_state": "evidence_cards_ready_for_review",
        "source_store_id": store["store_id"],
        "summary": {
            "metadata_result_total": store["summary"]["result_total"],
            "evidence_card_total": len(cards),
            "review_card_total": sum(1 for card in cards if card["evidence_state"] == "review_card_ready"),
            "denied_card_total": sum(1 for card in cards if card["evidence_state"] == "denied_by_source_policy"),
            "runtime_truth_mutations": 0,
            "body_reads": 0,
            "network_requests": 0,
        },
        "cards": cards,
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }


def build_result_evidence_cards(results: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    return build_result_evidence_payload(results)["cards"]


def build_result_evidence_status() -> Dict[str, Any]:
    payload = build_result_evidence_payload()
    return {
        "stage_range": "S716-S722",
        "status": "ready",
        "stop_gate": "result_evidence_cards_ready",
        "summary": payload["summary"],
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }
