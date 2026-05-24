"""S779-S792 governed body-read authorization model.

This module builds authorization packets and cockpit cards for body-read review.
It never authorizes or performs a body read. It keeps all execution flags false.
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

DEFAULT_REQUESTS: List[Dict[str, Any]] = [
    {
        "request_id": "body-read-auth-official-docs-001",
        "title": "Official documentation body-read candidate",
        "source_family": "official_docs",
        "trust_tier": "tier_1_official",
        "requested_scope": "metadata_to_body_read_review",
        "reason": "Would allow a future operator-approved read of a single official documentation page.",
    },
    {
        "request_id": "body-read-auth-primary-market-002",
        "title": "Primary market/regulatory body-read candidate",
        "source_family": "primary_market_or_regulatory",
        "trust_tier": "tier_1_primary",
        "requested_scope": "metadata_to_body_read_review",
        "reason": "Would allow a future operator-approved read of a single primary-source page.",
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def normalize_authorization_requests(requests: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    raw = list(requests) if requests is not None else deepcopy(DEFAULT_REQUESTS)
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(raw):
        source_family = str(item.get("source_family") or "unknown_or_user_supplied")
        trust_tier = str(item.get("trust_tier") or "tier_4_unknown")
        high_risk = source_family in {"open_web_unknown", "denied_source_family", "untrusted_forum"} or trust_tier.startswith("tier_4")
        normalized.append(
            {
                "request_id": str(item.get("request_id") or f"body-read-auth-request-{index + 1:03d}"),
                "title": str(item.get("title") or "Body-read authorization candidate"),
                "source_family": source_family,
                "trust_tier": trust_tier,
                "requested_scope": str(item.get("requested_scope") or "single_url_metadata_to_body_review"),
                "reason": str(item.get("reason") or "Operator review candidate only."),
                "risk_level": "high" if high_risk else "controlled",
                "authorization_state": "authorization_planned_not_granted",
                "operator_approval_required": True,
                "body_read_allowed": False,
                "body_read_performed": False,
                "network_request_performed": False,
                "runtime_truth_mutated": False,
                "created_at": str(item.get("created_at") or _now_iso()),
            }
        )
    return normalized


def build_authorization_payload(requests: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    normalized = normalize_authorization_requests(requests)
    return {
        "stage_range": "S779-S792",
        "name": "Governed Body-Read Authorization",
        "terminal_state": "body_read_authorization_model_ready_body_reads_blocked",
        "authority": "authorization_model_only_no_body_read_execution",
        "summary": {
            "authorization_requests": len(normalized),
            "authorizations_granted": 0,
            "body_reads_allowed": 0,
            "body_reads_performed": 0,
            "network_requests": 0,
            "runtime_truth_mutations": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "requests": normalized,
        "policy": {
            "single_url_only": True,
            "operator_approval_required": True,
            "deny_unknown_source_family_by_default": True,
            "body_read_execution_enabled": False,
            "crawl_expansion_enabled": False,
        },
    }


def build_authorization_cards(requests: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    payload = build_authorization_payload(requests)
    cards: List[Dict[str, Any]] = []
    for item in payload["requests"]:
        cards.append(
            {
                "card_id": f"body-read-auth-{item['request_id']}",
                "title": item["title"],
                "subtitle": f"{item['source_family']} / {item['trust_tier']}",
                "state": item["authorization_state"],
                "summary": "Body-read request is modeled for operator review only; no read can execute in this build.",
                "risk_level": item["risk_level"],
                "badges": ["authorization-model", "manual-review", "body-read-blocked", "crawl-blocked"],
                "actions": ["review_request_packet", "reject_request_packet", "prepare_extraction_scope"],
                "execution_enabled": False,
            }
        )
    return cards


def build_authorization_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "review_body_read_authorization_packet",
            "label": "Review body-read authorization packet",
            "description": "Review a modeled request; this does not grant execution authority.",
            "execution_enabled": False,
            "body_read_allowed": False,
            "requires_operator_approval": True,
        },
        {
            "action_id": "deny_body_read_authorization_packet",
            "label": "Deny body-read authorization packet",
            "description": "Non-executable action descriptor for future cockpit control wiring.",
            "execution_enabled": False,
            "body_read_allowed": False,
            "requires_operator_approval": True,
        },
    ]
