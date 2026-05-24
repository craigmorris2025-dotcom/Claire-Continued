"""Evidence basket promotion preview for S737-S743.

This module previews how reviewed metadata evidence could be promoted into an
approved evidence basket. It does not promote evidence to runtime truth and does
not execute network requests, body reads, package installation, commands, or
runtime mutation.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

BLOCKED_CAPABILITIES: Dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "body_read_performed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

_SAMPLE_REVIEWED_EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "reviewed-meta-official-001",
        "title": "Official documentation metadata candidate",
        "source_family": "official_docs",
        "trust_tier": "tier_1_official",
        "review_state": "operator_review_preview",
        "confidence": 0.87,
        "metadata_only": True,
        "body_read": False,
        "runtime_truth_mutated": False,
    },
    {
        "evidence_id": "reviewed-meta-primary-002",
        "title": "Primary market or regulatory metadata candidate",
        "source_family": "primary_market_or_regulatory",
        "trust_tier": "tier_1_primary",
        "review_state": "operator_review_preview",
        "confidence": 0.83,
        "metadata_only": True,
        "body_read": False,
        "runtime_truth_mutated": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def normalize_reviewed_evidence(items: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    raw_items = list(items) if items is not None else deepcopy(_SAMPLE_REVIEWED_EVIDENCE)
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(raw_items):
        confidence = float(item.get("confidence", 0.5))
        body_read = bool(item.get("body_read", False))
        normalized.append(
            {
                "evidence_id": str(item.get("evidence_id") or f"reviewed-metadata-evidence-{index + 1:03d}"),
                "title": str(item.get("title") or "Reviewed metadata evidence"),
                "source_family": str(item.get("source_family") or "unknown_or_user_supplied"),
                "trust_tier": str(item.get("trust_tier") or "tier_4_unknown"),
                "review_state": str(item.get("review_state") or "operator_review_preview"),
                "confidence": max(0.0, min(1.0, confidence)),
                "metadata_only": True,
                "body_read": False if body_read else False,
                "network_request_performed": False,
                "runtime_truth_mutated": False,
                "eligible_for_runtime_truth": False,
                "eligible_for_evidence_basket_preview": bool(confidence >= 0.65 and not body_read),
                "created_at": str(item.get("created_at") or _now_iso()),
            }
        )
    return normalized


def build_promotion_preview(items: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    evidence = normalize_reviewed_evidence(items)
    eligible = [item for item in evidence if item["eligible_for_evidence_basket_preview"]]
    return {
        "stage_range": "S737-S743",
        "name": "Evidence Basket Promotion Preview",
        "terminal_state": "evidence_basket_promotion_preview_ready",
        "authority": "preview_only_no_runtime_truth_mutation",
        "preview_id": "evidence-basket-promotion-preview-s737-s743",
        "summary": {
            "reviewed_evidence_total": len(evidence),
            "preview_eligible_total": len(eligible),
            "runtime_truth_mutations": 0,
            "body_reads": 0,
            "network_requests": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "evidence": evidence,
        "promotion_preview": {
            "basket_id": "preview-basket-metadata-only-s737-s743",
            "would_create_basket": bool(eligible),
            "would_promote_to_runtime_truth": False,
            "would_trigger_updates": False,
            "requires_operator_approval": True,
            "allowed_next_step": "manual_review_only",
        },
    }


def build_promotion_cards(items: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    payload = build_promotion_preview(items)
    cards: List[Dict[str, Any]] = []
    for item in payload["evidence"]:
        cards.append(
            {
                "card_id": f"promotion-preview-{item['evidence_id']}",
                "title": item["title"],
                "subtitle": f"{item['source_family']} / {item['trust_tier']}",
                "state": "preview_eligible" if item["eligible_for_evidence_basket_preview"] else "review_required",
                "summary": "Metadata-only reviewed evidence can be previewed for basket inclusion; runtime truth remains unchanged.",
                "confidence": item["confidence"],
                "badges": ["metadata-only", "preview-only", "runtime-truth-blocked", "body-read-blocked"],
                "actions": ["review_preview", "reject_preview", "prepare_basket_draft"],
                "execution_enabled": False,
            }
        )
    return cards


def build_promotion_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "preview_evidence_basket_draft",
            "label": "Preview evidence basket draft",
            "description": "Display how reviewed metadata evidence would be grouped, without promotion.",
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "requires_operator_approval": True,
        },
        {
            "action_id": "reject_metadata_evidence_preview",
            "label": "Reject metadata evidence preview",
            "description": "Operator-visible action descriptor only; no destructive action is executed by this build.",
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "requires_operator_approval": True,
        },
    ]


def build_status() -> Dict[str, Any]:
    return {
        "stage_range": "S737-S743",
        "status": "ready",
        "authority": "preview_only",
        "blocked_capabilities": get_blocked_capabilities(),
    }
