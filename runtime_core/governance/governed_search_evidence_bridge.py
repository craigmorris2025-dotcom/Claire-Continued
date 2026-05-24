from __future__ import annotations

from hashlib import sha256
from typing import Any

BLOCKED_AUTHORITY: dict[str, bool] = {
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


def _result_id(title: str, url: str) -> str:
    return "meta_" + sha256(f"{title}|{url}".encode("utf-8")).hexdigest()[:12]


def sample_metadata_results() -> list[dict[str, Any]]:
    return [
        {
            "result_id": _result_id("Official source metadata placeholder", "https://example.invalid/official"),
            "title": "Official source metadata placeholder",
            "url": "https://example.invalid/official",
            "source_family": "official_docs",
            "trust_tier": "tier_1_authoritative",
            "published_at": None,
            "summary_hint": "Placeholder metadata generated locally. No network request was performed.",
            "body_read": False,
            "network_request_performed": False,
        },
        {
            "result_id": _result_id("Market source metadata placeholder", "https://example.invalid/market"),
            "title": "Market source metadata placeholder",
            "url": "https://example.invalid/market",
            "source_family": "market_and_news",
            "trust_tier": "tier_2_corroborrated",
            "published_at": None,
            "summary_hint": "Placeholder metadata generated locally for the search-to-evidence bridge contract.",
            "body_read": False,
            "network_request_performed": False,
        },
    ]


def build_search_to_evidence_bridge(results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    metadata_results = results or sample_metadata_results()
    evidence_items = []
    for item in metadata_results:
        evidence_items.append(
            {
                "evidence_id": "evidence_" + item["result_id"].replace("meta_", ""),
                "source_result_id": item["result_id"],
                "title": item["title"],
                "url": item["url"],
                "source_family": item["source_family"],
                "trust_tier": item["trust_tier"],
                "review_state": "quarantined_pending_operator_review",
                "runtime_truth_promoted": False,
                "body_read": False,
                "network_request_performed": False,
                "summary_hint": item.get("summary_hint"),
            }
        )
    return {
        "bridge_id": "s660_s666_search_to_evidence_bridge",
        "status": "bridge_ready_with_sample_metadata_only_inputs",
        "metadata_result_count": len(metadata_results),
        "evidence_item_count": len(evidence_items),
        "runtime_truth_mutated": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "blocked_authority": BLOCKED_AUTHORITY.copy(),
        "evidence_items": evidence_items,
    }


def build_search_evidence_cards(results: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    bridge = build_search_to_evidence_bridge(results)
    cards = [
        {
            "card_id": "search_to_evidence_bridge",
            "title": "Search-to-evidence basket bridge",
            "status": "ready_blocked",
            "summary": "Metadata results can be shaped into quarantined evidence cards for review.",
            "counts": {
                "metadata_results": bridge["metadata_result_count"],
                "evidence_items": bridge["evidence_item_count"],
            },
            "runtime_truth_mutated": False,
        }
    ]
    for item in bridge["evidence_items"]:
        cards.append(
            {
                "card_id": item["evidence_id"],
                "title": item["title"],
                "status": item["review_state"],
                "summary": item["summary_hint"],
                "source_family": item["source_family"],
                "trust_tier": item["trust_tier"],
                "url": item["url"],
                "runtime_truth_promoted": False,
                "body_read": False,
            }
        )
    return cards


def build_search_evidence_actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": "build_quarantined_evidence_preview",
            "label": "Build quarantined evidence preview",
            "status": "available_for_review",
            "executable": False,
            "endpoint": "/api/search/evidence/bridge/preview",
            "reason": "The action describes the bridge contract but does not promote evidence to runtime truth.",
        },
        {
            "action_id": "promote_search_evidence_to_runtime_truth",
            "label": "Promote search evidence to runtime truth",
            "status": "blocked",
            "executable": False,
            "endpoint": None,
            "reason": "Runtime mutation remains blocked.",
        },
    ]


def build_search_evidence_status() -> dict[str, Any]:
    return {
        "status": "bridge_ready",
        "stage_range": "S660-S666",
        "metadata_to_evidence_bridge_present": True,
        "quarantine_first": True,
        "runtime_truth_mutated": False,
        "network_request_performed": False,
    }


def build_search_evidence_payload() -> dict[str, Any]:
    return {
        "payload_id": "s660_s666_search_to_evidence_bridge",
        "bridge": build_search_to_evidence_bridge(),
        "cards": build_search_evidence_cards(),
        "actions": build_search_evidence_actions(),
        "status": build_search_evidence_status(),
    }
