"""Governed body-read safety plan for S751-S764.

This is a planning layer only. Body reads are still blocked. The module creates
risk classifications and extraction scopes so the cockpit can show what would be
required before Claire is allowed to read page bodies.
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

RISK_RULES: Dict[str, Dict[str, Any]] = {
    "official_docs": {"risk": "low", "body_read_default": "blocked_until_manual_gate", "max_scope": "single_page"},
    "primary_market_or_regulatory": {"risk": "low_medium", "body_read_default": "blocked_until_manual_gate", "max_scope": "single_page"},
    "reputable_secondary": {"risk": "medium", "body_read_default": "blocked_until_manual_gate", "max_scope": "single_page_with_citation_review"},
    "open_web": {"risk": "medium_high", "body_read_default": "blocked_until_manual_gate", "max_scope": "single_page_metadata_first"},
    "unknown_or_user_supplied": {"risk": "high", "body_read_default": "blocked", "max_scope": "none_until_source_review"},
    "denied_or_unsafe": {"risk": "denied", "body_read_default": "denied", "max_scope": "none"},
}

_SAMPLE_CANDIDATES: List[Dict[str, Any]] = [
    {"candidate_id": "body-read-plan-official-001", "title": "Official docs candidate", "source_family": "official_docs", "url": "https://docs.example.invalid/release-notes"},
    {"candidate_id": "body-read-plan-open-002", "title": "Open web candidate", "source_family": "open_web", "url": "https://example.invalid/result"},
    {"candidate_id": "body-read-plan-unknown-003", "title": "Unknown user supplied candidate", "source_family": "unknown_or_user_supplied", "url": ""},
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def classify_body_read_candidate(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    source_family = str(candidate.get("source_family") or "unknown_or_user_supplied")
    rule = RISK_RULES.get(source_family, RISK_RULES["unknown_or_user_supplied"])
    denied = rule["risk"] == "denied"
    return {
        "candidate_id": str(candidate.get("candidate_id") or candidate.get("result_id") or "body-read-candidate"),
        "title": str(candidate.get("title") or "Body read candidate"),
        "url": str(candidate.get("url") or ""),
        "source_family": source_family,
        "risk_level": rule["risk"],
        "body_read_allowed": False,
        "body_read_performed": False,
        "network_request_performed": False,
        "requires_manual_preflight": not denied,
        "requires_source_review": source_family in {"unknown_or_user_supplied", "open_web"},
        "extraction_scope": rule["max_scope"],
        "blocked_reason": "body_read_gate_not_enabled" if not denied else "source_denied",
        "created_at": _now_iso(),
    }


def build_body_read_safety_plan(candidates: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    raw_candidates = list(candidates) if candidates is not None else deepcopy(_SAMPLE_CANDIDATES)
    classified = [classify_body_read_candidate(item) for item in raw_candidates]
    return {
        "stage_range": "S751-S764",
        "name": "Governed Body-Read Safety Plan + Risk Classifier",
        "terminal_state": "body_read_planning_ready_body_reads_blocked",
        "authority": "planning_only",
        "plan_id": "governed-body-read-safety-plan-s751-s764",
        "summary": {
            "candidate_total": len(classified),
            "body_read_allowed_total": 0,
            "body_read_performed_total": 0,
            "manual_preflight_required_total": sum(1 for item in classified if item["requires_manual_preflight"]),
            "denied_total": sum(1 for item in classified if item["risk_level"] == "denied"),
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "risk_rules": deepcopy(RISK_RULES),
        "candidates": classified,
        "required_unlocks_before_body_read": [
            "operator_selected_single_candidate",
            "source_policy_allows_manual_body_read_request",
            "rate_limit_policy_present",
            "robots_or_terms_review_recorded_where_applicable",
            "body_extraction_scope_locked",
            "quarantine_store_target_locked",
            "runtime_truth_auto_promotion_remains_disabled",
        ],
    }


def build_body_read_safety_cards(candidates: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    payload = build_body_read_safety_plan(candidates)
    cards: List[Dict[str, Any]] = []
    for item in payload["candidates"]:
        cards.append(
            {
                "card_id": f"body-read-plan-{item['candidate_id']}",
                "title": item["title"],
                "subtitle": f"{item['source_family']} / risk {item['risk_level']}",
                "state": "blocked_body_read_plan",
                "summary": f"Body read remains blocked. Proposed extraction scope: {item['extraction_scope']}.",
                "url": item["url"],
                "badges": ["body-read-blocked", "manual-preflight-required", "no-network", "quarantine-only"],
                "actions": ["review_body_read_plan", "reject_candidate", "prepare_manual_request_packet"],
                "execution_enabled": False,
            }
        )
    return cards


def build_status() -> Dict[str, Any]:
    return {
        "stage_range": "S751-S764",
        "status": "body_read_planning_ready",
        "body_read_allowed": False,
        "blocked_capabilities": get_blocked_capabilities(),
    }
