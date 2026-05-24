"""Governed metadata search-result quarantine store for S709-S715.

This module intentionally does not perform network requests, provider execution,
body reads, crawling, package installation, command execution, or runtime mutation.
It only models how metadata-only search results are represented while quarantined.
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
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

SOURCE_FAMILY_POLICIES: Dict[str, Dict[str, Any]] = {
    "official_docs": {
        "trust_tier": "tier_1_official",
        "default_action": "allow_metadata_only_when_operator_gated",
        "body_reads": "blocked",
        "runtime_truth": "never_auto_promote",
    },
    "primary_market_or_regulatory": {
        "trust_tier": "tier_1_primary",
        "default_action": "allow_metadata_only_when_operator_gated",
        "body_reads": "blocked",
        "runtime_truth": "never_auto_promote",
    },
    "reputable_secondary": {
        "trust_tier": "tier_2_secondary",
        "default_action": "quarantine_metadata_only",
        "body_reads": "blocked",
        "runtime_truth": "never_auto_promote",
    },
    "open_web": {
        "trust_tier": "tier_3_open_web",
        "default_action": "quarantine_metadata_only",
        "body_reads": "blocked",
        "runtime_truth": "never_auto_promote",
    },
    "unknown_or_user_supplied": {
        "trust_tier": "tier_4_unknown",
        "default_action": "quarantine_and_require_review",
        "body_reads": "blocked",
        "runtime_truth": "never_auto_promote",
    },
    "denied_or_unsafe": {
        "trust_tier": "denied",
        "default_action": "deny",
        "body_reads": "blocked",
        "runtime_truth": "never_auto_promote",
    },
}

_SAMPLE_METADATA_RESULTS: List[Dict[str, Any]] = [
    {
        "result_id": "meta-result-official-docs-001",
        "title": "Official documentation result placeholder",
        "url": "https://docs.example.invalid/platform/release-notes",
        "source_family": "official_docs",
        "provider": "manual_metadata_probe_preview",
        "snippet": "Metadata-only placeholder. Body text was not read.",
        "rank": 1,
        "metadata_only": True,
        "body_read": False,
        "network_request_performed": False,
        "captured_at": None,
    },
    {
        "result_id": "meta-result-regulatory-002",
        "title": "Primary regulatory source result placeholder",
        "url": "https://regulator.example.invalid/notice",
        "source_family": "primary_market_or_regulatory",
        "provider": "manual_metadata_probe_preview",
        "snippet": "Metadata-only placeholder. Body text was not read.",
        "rank": 2,
        "metadata_only": True,
        "body_read": False,
        "network_request_performed": False,
        "captured_at": None,
    },
    {
        "result_id": "meta-result-open-web-003",
        "title": "Open web result placeholder",
        "url": "https://example.invalid/open-web-result",
        "source_family": "open_web",
        "provider": "manual_metadata_probe_preview",
        "snippet": "Metadata-only placeholder. Body text was not read.",
        "rank": 3,
        "metadata_only": True,
        "body_read": False,
        "network_request_performed": False,
        "captured_at": None,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def classify_source_family(url: str, supplied_family: Optional[str] = None) -> str:
    """Classify a result's source family without fetching the URL."""
    if supplied_family in SOURCE_FAMILY_POLICIES:
        return str(supplied_family)
    lowered = (url or "").lower()
    if not lowered:
        return "unknown_or_user_supplied"
    denied_markers = ("malware", "phishing", "credential", "exploit", "piracy")
    if any(marker in lowered for marker in denied_markers):
        return "denied_or_unsafe"
    if "docs." in lowered or "/docs" in lowered or "developer." in lowered:
        return "official_docs"
    if "sec.gov" in lowered or "regulator" in lowered or "federalregister" in lowered:
        return "primary_market_or_regulatory"
    if "wikipedia" in lowered or "news" in lowered or "reuters" in lowered or "apnews" in lowered:
        return "reputable_secondary"
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return "open_web"
    return "unknown_or_user_supplied"


def normalize_metadata_result(raw_result: Mapping[str, Any], index: int = 0) -> Dict[str, Any]:
    """Normalize one metadata result into Claire's quarantined contract."""
    url = str(raw_result.get("url") or raw_result.get("link") or "")
    source_family = classify_source_family(url, str(raw_result.get("source_family") or "") or None)
    policy = SOURCE_FAMILY_POLICIES[source_family]
    result_id = str(raw_result.get("result_id") or raw_result.get("id") or f"metadata-result-{index + 1:03d}")
    denied = source_family == "denied_or_unsafe"
    return {
        "result_id": result_id,
        "title": str(raw_result.get("title") or "Untitled metadata result"),
        "url": url,
        "provider": str(raw_result.get("provider") or "unexecuted_provider_boundary"),
        "rank": int(raw_result.get("rank") or index + 1),
        "snippet": str(raw_result.get("snippet") or raw_result.get("summary") or "Metadata-only result; body not read."),
        "source_family": source_family,
        "trust_tier": policy["trust_tier"],
        "quarantine_state": "denied" if denied else "quarantined_for_operator_review",
        "review_state": "blocked_by_source_policy" if denied else "pending_operator_review",
        "metadata_only": True,
        "body_read": False,
        "network_request_performed": False,
        "runtime_truth_mutated": False,
        "eligible_for_runtime_truth": False,
        "requires_operator_review": not denied,
        "blocked_reason": "source_family_denied" if denied else None,
        "captured_at": str(raw_result.get("captured_at") or _now_iso()),
        "policy": deepcopy(policy),
    }


def build_quarantine_store(results: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    """Build a deterministic quarantine store from metadata-only result records."""
    raw_results = list(results) if results is not None else deepcopy(_SAMPLE_METADATA_RESULTS)
    normalized = [normalize_metadata_result(item, i) for i, item in enumerate(raw_results)]
    denied_count = sum(1 for item in normalized if item["quarantine_state"] == "denied")
    review_count = sum(1 for item in normalized if item["review_state"] == "pending_operator_review")
    return {
        "stage_range": "S709-S715",
        "name": "Search Result Quarantine Store",
        "terminal_state": "metadata_results_quarantined",
        "authority": "metadata_only_quarantine",
        "store_id": "governed-search-result-quarantine-s709-s715",
        "summary": {
            "result_total": len(normalized),
            "quarantined_total": len(normalized) - denied_count,
            "denied_total": denied_count,
            "pending_review_total": review_count,
            "body_reads": 0,
            "network_requests": 0,
            "runtime_truth_mutations": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "source_family_policies": deepcopy(SOURCE_FAMILY_POLICIES),
        "results": normalized,
    }


def build_quarantine_cards(results: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    store = build_quarantine_store(results)
    cards: List[Dict[str, Any]] = []
    for item in store["results"]:
        cards.append(
            {
                "card_id": f"quarantine-card-{item['result_id']}",
                "title": item["title"],
                "subtitle": f"{item['source_family']} / {item['trust_tier']}",
                "state": item["quarantine_state"],
                "review_state": item["review_state"],
                "summary": item["snippet"],
                "url": item["url"],
                "badges": [
                    "metadata-only",
                    "body-read-blocked",
                    "network-not-performed",
                    "runtime-truth-not-mutated",
                ],
                "blocked_capabilities": get_blocked_capabilities(),
                "actions": [
                    "review_metadata",
                    "reject_result",
                    "prepare_evidence_card_preview",
                ] if item["requires_operator_review"] else ["deny_result"],
            }
        )
    return cards


def build_quarantine_status() -> Dict[str, Any]:
    store = build_quarantine_store()
    return {
        "stage_range": "S709-S715",
        "status": "ready",
        "stop_gate": "quarantine_store_ready",
        "summary": store["summary"],
        "blocked_capabilities": get_blocked_capabilities(),
    }
