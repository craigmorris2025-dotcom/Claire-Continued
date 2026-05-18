"""S646-S652 metadata-only result contract.

The contract defines the first safe shape for future search/provider results.
It explicitly excludes page-body content, crawling, runtime mutation, package
operations, and automatic updates.
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

METADATA_ONLY_FIELDS: List[str] = [
    "result_id",
    "provider_id",
    "query_id",
    "title",
    "url",
    "display_url",
    "snippet",
    "source_family",
    "trust_tier",
    "observed_at",
    "rank",
    "policy_state",
    "lineage",
]

DISALLOWED_FIELDS: List[str] = [
    "body",
    "html",
    "full_text",
    "article_text",
    "downloaded_file",
    "package_payload",
    "runtime_patch",
    "executable_command",
]

SAMPLE_METADATA_RESULTS: List[Dict[str, Any]] = [
    {
        "result_id": "meta_official_docs_001",
        "provider_id": "manual_or_configured_provider_placeholder",
        "query_id": "query_official_docs_candidate",
        "title": "Official source result candidate",
        "url": "https://example.invalid/official-docs-placeholder",
        "display_url": "example.invalid/official-docs-placeholder",
        "snippet": "Metadata-only placeholder representing a future provider result candidate.",
        "source_family": "official_docs",
        "trust_tier": "tier_1_official",
        "observed_at": "not_performed",
        "rank": 1,
        "policy_state": "quarantined_not_runtime_truth",
        "lineage": ["query_compiler", "metadata_result_contract", "quarantine_store"],
    },
    {
        "result_id": "meta_open_web_001",
        "provider_id": "manual_or_configured_provider_placeholder",
        "query_id": "query_open_web_discovery_candidate",
        "title": "Open web result candidate",
        "url": "https://example.invalid/open-web-placeholder",
        "display_url": "example.invalid/open-web-placeholder",
        "snippet": "Discovery candidate metadata only; no body read and no network request performed by this layer.",
        "source_family": "open_web",
        "trust_tier": "tier_4_unverified",
        "observed_at": "not_performed",
        "rank": 2,
        "policy_state": "quarantined_requires_review",
        "lineage": ["source_scope_planner", "metadata_result_contract", "review_queue"],
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_metadata_result_contract() -> Dict[str, Any]:
    return {
        "phase": "S646-S652",
        "contract_id": "governed_metadata_only_result_contract_v1",
        "status": "defined_non_executing",
        "allowed_fields": list(METADATA_ONLY_FIELDS),
        "disallowed_fields": list(DISALLOWED_FIELDS),
        "result_authority": "quarantine_only",
        "runtime_truth_mutation": "blocked",
        "body_read_policy": "blocked",
        "network_policy": "not_performed_by_contract",
        "automatic_update_policy": "blocked",
        "validation_rules": [
            "metadata_results_must_not_include_body_fields",
            "metadata_results_must_include_source_family",
            "metadata_results_must_include_trust_tier",
            "metadata_results_must_include_lineage",
            "metadata_results_enter_quarantine_before_review",
        ],
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }


def validate_metadata_result(result: Dict[str, Any]) -> Dict[str, Any]:
    present_disallowed = [field for field in DISALLOWED_FIELDS if field in result and result.get(field) not in (None, "")]
    missing_required = [field for field in ["result_id", "title", "url", "source_family", "trust_tier", "lineage"] if not result.get(field)]
    return {
        "valid": not present_disallowed and not missing_required,
        "present_disallowed_fields": present_disallowed,
        "missing_required_fields": missing_required,
        "policy_state": "metadata_only_valid" if not present_disallowed and not missing_required else "metadata_contract_violation",
    }


def get_sample_metadata_results() -> List[Dict[str, Any]]:
    return deepcopy(SAMPLE_METADATA_RESULTS)


def build_metadata_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for result in SAMPLE_METADATA_RESULTS:
        validation = validate_metadata_result(result)
        cards.append(
            {
                "id": f"card_{result['result_id']}",
                "title": result["title"],
                "category": "metadata_only_search_result",
                "state": result["policy_state"],
                "source_family": result["source_family"],
                "trust_tier": result["trust_tier"],
                "summary": result["snippet"],
                "display_url": result["display_url"],
                "rank": result["rank"],
                "validation": validation,
                "badges": ["metadata_only", "body_read_blocked", "quarantine_only"],
                "lineage": list(result["lineage"]),
                "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
            }
        )
    return cards


def build_metadata_actions() -> List[Dict[str, Any]]:
    return [
        {
            "id": "inspect_metadata_result_contract",
            "label": "Inspect metadata-only result contract",
            "tab": "Governed Web",
            "state": "available_non_executable_descriptor",
            "requires_operator": False,
            "executes_network_request": False,
            "reads_body": False,
            "description": "Shows exactly what future provider results may contain before body reads are allowed.",
        },
        {
            "id": "send_metadata_result_to_quarantine_descriptor",
            "label": "Send metadata result to quarantine preview",
            "tab": "Actions",
            "state": "descriptor_only",
            "requires_operator": True,
            "executes_network_request": False,
            "reads_body": False,
            "description": "Defines the future movement from provider metadata to quarantine review.",
        },
    ]


def build_metadata_status() -> Dict[str, Any]:
    return {
        "phase": "S646-S652",
        "status": "metadata_contract_ready",
        "metadata_contract_ready": True,
        "contract_ready": True,
        "sample_results_ready": True,
        "card_normalization_ready": True,
        "valid_sample_count": sum(1 for item in SAMPLE_METADATA_RESULTS if validate_metadata_result(item)["valid"]),
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
        "generated_at": _now(),
    }


def build_metadata_payload() -> Dict[str, Any]:
    return {
        "phase": "S646-S652",
        "surface": "Governed Web",
        "headline": "Metadata-only result contract ready",
        "summary": "Future search results now have a safe metadata-only contract and quarantine path without body reads or live execution.",
        "contract": get_metadata_result_contract(),
        "sample_results": get_sample_metadata_results(),
        "cards": build_metadata_cards(),
        "actions": build_metadata_actions(),
        "status": build_metadata_status(),
    }


def build_metadata_stop_gate() -> Dict[str, Any]:
    status = build_metadata_status()
    return {
        "gate": "S652",
        "passed": all(
            [
                status["contract_ready"],
                status["sample_results_ready"],
                status["card_normalization_ready"],
                status["valid_sample_count"] == len(SAMPLE_METADATA_RESULTS),
                not status["blocked_capabilities"]["body_read_allowed"],
                not status["blocked_capabilities"]["network_request_performed"],
                not status["blocked_capabilities"]["runtime_mutation_enabled"],
            ]
        ),
        "next_phase": "S653-S666 manual provider probe gate and search-to-evidence basket bridge",
        "blocked_capabilities": deepcopy(BLOCKED_CAPABILITIES),
    }
