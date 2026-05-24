"""S639-S645 governed quarantine evidence store.

This module keeps web/source/search evidence reviewable while preserving the
hard stop: quarantined evidence is not runtime truth, not a package install,
not a body read, and not an autonomous crawl.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

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

QUARANTINE_POLICY: Dict[str, Any] = {
    "policy_id": "s639_s645_quarantine_evidence_policy",
    "authority": "operator_review_required",
    "default_state": "quarantined",
    "promotion_target": "review_packet_only",
    "runtime_truth_mutation": "blocked",
    "body_reads": "blocked",
    "network_requests": "blocked_by_this_layer",
    "allowed_inputs": [
        "metadata_only_result_candidate",
        "source_registry_record",
        "provider_readiness_record",
        "manual_operator_annotation",
    ],
    "quarantine_rules": [
        "never_promote_directly_to_runtime_truth",
        "never_treat_metadata_as_verified_content_body",
        "require_source_family_and_trust_tier",
        "require_operator_review_before_evidence_basket_promotion",
        "preserve_lineage_and_blocked_capability_state",
    ],
}

QUARANTINE_RECORDS: List[Dict[str, Any]] = [
    {
        "id": "qe_official_docs_candidate",
        "title": "Official documentation candidate",
        "source_family": "official_docs",
        "trust_tier": "tier_1_official",
        "state": "quarantined",
        "result_type": "metadata_only",
        "claim_scope": "source_identity_and_snippet_only",
        "lineage": ["source_registry", "query_compiler", "metadata_contract"],
        "review_status": "needs_operator_review",
        "reason": "Metadata can identify a candidate source but cannot establish body-level truth while body reads remain blocked.",
    },
    {
        "id": "qe_market_source_candidate",
        "title": "Market source candidate",
        "source_family": "market_source",
        "trust_tier": "tier_2_primary_or_regulated",
        "state": "quarantined",
        "result_type": "metadata_only",
        "claim_scope": "market_reference_candidate",
        "lineage": ["provider_capability_map", "source_policy_controls"],
        "review_status": "needs_operator_review",
        "reason": "Market data source needs trust, timestamp, and source-family review before lifecycle use.",
    },
    {
        "id": "qe_open_web_candidate",
        "title": "Open web candidate",
        "source_family": "open_web",
        "trust_tier": "tier_4_unverified",
        "state": "quarantined",
        "result_type": "metadata_only",
        "claim_scope": "discovery_candidate_only",
        "lineage": ["source_gap_matrix", "search_scope_planner"],
        "review_status": "needs_triage",
        "reason": "Open-web evidence remains low-trust until independently reviewed and promoted.",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_quarantine_policy() -> Dict[str, Any]:
    policy = deepcopy(QUARANTINE_POLICY)
    policy["blocked_capabilities"] = deepcopy(BLOCKED_CAPABILITIES)
    return policy


def get_quarantine_store() -> Dict[str, Any]:
    return {
        "phase": "S639-S645",
        "name": "governed_quarantine_evidence_store",
        "status": "ready_for_metadata_intake",
        "records": deepcopy(QUARANTINE_RECORDS),
        "record_count": len(QUARANTINE_RECORDS),
        "policy": get_quarantine_policy(),
        "generated_at": _now(),
    }


def build_quarantine_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for record in QUARANTINE_RECORDS:
        cards.append(
            {
                "id": f"card_{record['id']}",
                "title": record["title"],
                "category": "quarantined_evidence",
                "state": record["state"],
                "severity": "review_required",
                "source_family": record["source_family"],
                "trust_tier": record["trust_tier"],
                "summary": record["reason"],
                "badges": [record["result_type"], record["review_status"], "runtime_truth_blocked"],
                "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
                "lineage": list(record["lineage"]),
            }
        )
    return cards


def build_review_queue() -> Dict[str, Any]:
    cards = build_quarantine_cards()
    return {
        "queue_id": "s639_s645_source_search_review_queue",
        "status": "waiting_for_operator_review",
        "runtime_truth_mutation": "blocked",
        "body_read_allowed": False,
        "items": cards,
        "item_count": len(cards),
        "review_rules": deepcopy(QUARANTINE_POLICY["quarantine_rules"]),
    }


def build_quarantine_actions() -> List[Dict[str, Any]]:
    return [
        {
            "id": "review_quarantined_source_metadata",
            "label": "Review quarantined source metadata",
            "tab": "Evidence & Review",
            "state": "available_non_executable_descriptor",
            "requires_operator": True,
            "executes_network_request": False,
            "mutates_runtime_truth": False,
            "description": "Shows the evidence-card review path without promoting evidence automatically.",
        },
        {
            "id": "reject_quarantined_candidate_descriptor",
            "label": "Reject quarantined candidate",
            "tab": "Actions",
            "state": "descriptor_only",
            "requires_operator": True,
            "executes_network_request": False,
            "mutates_runtime_truth": False,
            "description": "Defines the future rejection action while preserving fail-closed execution.",
        },
        {
            "id": "prepare_promotion_packet_descriptor",
            "label": "Prepare promotion packet preview",
            "tab": "Actions",
            "state": "blocked_until_review",
            "requires_operator": True,
            "executes_network_request": False,
            "mutates_runtime_truth": False,
            "description": "Creates a visible path toward later evidence-basket promotion preview only.",
        },
    ]


def build_quarantine_status() -> Dict[str, Any]:
    return {
        "phase": "S639-S645",
        "status": "passive_quarantine_ready",
        "quarantine_store_ready": True,
        "review_queue_ready": True,
        "cockpit_cards_ready": True,
        "record_count": len(QUARANTINE_RECORDS),
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }


def build_quarantine_payload() -> Dict[str, Any]:
    return {
        "phase": "S639-S645",
        "surface": "Evidence & Review",
        "headline": "Quarantine evidence store ready",
        "summary": "Source/search evidence can be represented as reviewable cards while remaining quarantined and non-authoritative.",
        "status": build_quarantine_status(),
        "policy": get_quarantine_policy(),
        "store": get_quarantine_store(),
        "review_queue": build_review_queue(),
        "cards": build_quarantine_cards(),
        "actions": build_quarantine_actions(),
    }


def build_quarantine_stop_gate() -> Dict[str, Any]:
    status = build_quarantine_status()
    return {
        "gate": "S645",
        "passed": all(
            [
                status["quarantine_store_ready"],
                status["review_queue_ready"],
                status["cockpit_cards_ready"],
                not status["blocked_capabilities"]["runtime_mutation_enabled"],
                not status["blocked_capabilities"]["body_read_allowed"],
                not status["blocked_capabilities"]["network_request_performed"],
            ]
        ),
        "next_phase": "S646-S652 metadata-only result contract",
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }
