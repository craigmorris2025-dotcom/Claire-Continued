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

DEFAULT_ENVELOPES: List[Dict[str, Any]] = [
    {"envelope_id": "manual-body-read-envelope-official-docs-001", "title": "Official documentation body-read envelope", "source_family": "official_docs", "trust_tier": "tier_1_official", "target_kind": "single_url", "review_reason": "Future operator-approved read of one official documentation page."},
    {"envelope_id": "manual-body-read-envelope-regulatory-002", "title": "Primary/regulatory body-read envelope", "source_family": "primary_market_or_regulatory", "trust_tier": "tier_1_primary", "target_kind": "single_url", "review_reason": "Future operator-approved read of one primary-source page."},
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def normalize_body_read_envelopes(envelopes: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    raw = list(envelopes) if envelopes is not None else deepcopy(DEFAULT_ENVELOPES)
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(raw):
        source_family = str(item.get("source_family") or "unknown_or_user_supplied")
        trust_tier = str(item.get("trust_tier") or "tier_4_unknown")
        high_risk = source_family in {"open_web_unknown", "denied_source_family", "untrusted_forum"} or trust_tier.startswith("tier_4")
        normalized.append({
            "envelope_id": str(item.get("envelope_id") or f"manual-body-read-envelope-{index + 1:03d}"),
            "title": str(item.get("title") or "Manual body-read envelope candidate"),
            "source_family": source_family,
            "trust_tier": trust_tier,
            "target_kind": str(item.get("target_kind") or "single_url"),
            "review_reason": str(item.get("review_reason") or "Operator review candidate only."),
            "risk_level": "high" if high_risk else "controlled",
            "state": "execution_envelope_modeled_not_authorized",
            "operator_approval_required": True,
            "single_target_only": True,
            "body_read_allowed": False,
            "body_read_performed": False,
            "network_request_performed": False,
            "crawl_expansion_allowed": False,
            "runtime_truth_mutated": False,
            "created_at": str(item.get("created_at") or _now_iso()),
        })
    return normalized


def build_execution_envelope_payload(envelopes: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    normalized = normalize_body_read_envelopes(envelopes)
    return {
        "stage_range": "S835-S848",
        "name": "Governed Manual Body-Read Execution Envelope",
        "terminal_state": "manual_body_read_execution_envelope_ready_execution_blocked",
        "authority": "envelope_model_only_no_network_no_body_read",
        "summary": {"envelopes": len(normalized), "authorizations_granted": 0, "body_reads_allowed": 0, "body_reads_performed": 0, "network_requests": 0, "runtime_truth_mutations": 0, "crawl_expansions": 0},
        "blocked_capabilities": get_blocked_capabilities(),
        "envelopes": normalized,
        "requirements": {"operator_approval_required": True, "single_url_only": True, "source_must_be_trusted_or_quarantined": True, "extraction_scope_required_before_read": True, "sanitizer_plan_required_before_read": True, "runtime_truth_mutation_allowed": False},
    }


def build_execution_envelope_cards(envelopes: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    return [{
        "card_id": f"body-read-envelope-{item['envelope_id']}",
        "title": item["title"],
        "subtitle": f"{item['source_family']} / {item['trust_tier']}",
        "state": item["state"],
        "summary": "Execution envelope is ready for review only; no body read or request can run in this build.",
        "risk_level": item["risk_level"],
        "badges": ["manual-envelope", "operator-review", "body-read-blocked", "network-blocked"],
        "actions": ["review_envelope", "deny_envelope", "prepare_source_ingestion_draft"],
        "execution_enabled": False,
        "body_read_allowed": False,
    } for item in build_execution_envelope_payload(envelopes)["envelopes"]]


def build_execution_envelope_actions() -> List[Dict[str, Any]]:
    return [
        {"action_id": "review_manual_body_read_envelope", "label": "Review body-read envelope", "description": "Review the modeled envelope; this does not authorize network or body reads.", "execution_enabled": False, "body_read_allowed": False, "requires_operator_approval": True},
        {"action_id": "reject_manual_body_read_envelope", "label": "Reject body-read envelope", "description": "Non-executable action descriptor for cockpit review flow.", "execution_enabled": False, "body_read_allowed": False, "requires_operator_approval": True},
    ]
