from __future__ import annotations

from dataclasses import asdict, dataclass
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

ALLOWED_METADATA_FIELDS: list[str] = ["result_id", "title", "url", "display_url", "source_family", "trust_tier", "provider_id", "published_at", "retrieved_at", "summary_hint", "query", "rank"]
DENIED_FIELDS: list[str] = ["body", "html", "raw_response_body", "downloaded_file", "script_output", "runtime_patch", "credential_value"]

@dataclass(frozen=True)
class MetadataAdapterBoundary:
    boundary_id: str
    stage_range: str
    status: str
    provider_execution_allowed: bool
    network_request_performed: bool
    body_read_allowed: bool
    allowed_fields: list[str]
    denied_fields: list[str]
    quarantine_required: bool
    blocked_authority: dict[str, bool]


def _id(query: str, rank: int) -> str:
    return "preview_meta_" + sha256(f"{query}|{rank}".encode("utf-8")).hexdigest()[:12]


def build_metadata_adapter_boundary() -> dict[str, Any]:
    return asdict(MetadataAdapterBoundary(boundary_id="s695_s701_metadata_only_provider_adapter_boundary", stage_range="S695-S701", status="adapter_boundary_ready_execution_blocked", provider_execution_allowed=False, network_request_performed=False, body_read_allowed=False, allowed_fields=ALLOWED_METADATA_FIELDS, denied_fields=DENIED_FIELDS, quarantine_required=True, blocked_authority=BLOCKED_AUTHORITY.copy()))


def normalize_metadata_preview(query: str | None = None) -> list[dict[str, Any]]:
    clean_query = (query or "Claire governed metadata search readiness").strip()
    samples = [
        {"title": "Metadata-only result boundary preview", "url": "https://example.invalid/metadata-boundary-preview", "display_url": "example.invalid", "source_family": "open_web_preview", "trust_tier": "tier_3_unverified_until_review", "provider_id": "manual_preview_no_network", "published_at": None, "retrieved_at": None, "summary_hint": "Preview record produced locally to validate the metadata contract without a network request.", "query": clean_query, "rank": 1},
        {"title": "Official-source metadata preview", "url": "https://docs.example.invalid/source-policy", "display_url": "docs.example.invalid", "source_family": "official_docs_preview", "trust_tier": "tier_1_authoritative_when_domain_allowed", "provider_id": "manual_preview_no_network", "published_at": None, "retrieved_at": None, "summary_hint": "Preview record showing how official documentation metadata would be shaped before quarantine.", "query": clean_query, "rank": 2},
    ]
    normalized: list[dict[str, Any]] = []
    for item in samples:
        rank = int(item["rank"])
        result = {"result_id": _id(clean_query, rank), **item}
        normalized.append({key: result[key] for key in ALLOWED_METADATA_FIELDS if key in result})
    return normalized


def validate_metadata_result(result: dict[str, Any]) -> dict[str, Any]:
    present_denied = [field for field in DENIED_FIELDS if field in result]
    missing_required = [field for field in ["title", "url", "provider_id", "query", "rank"] if field not in result]
    accepted = not present_denied and not missing_required
    return {"accepted": accepted, "present_denied_fields": present_denied, "missing_required_fields": missing_required, "quarantine_required": True, "runtime_truth_mutation_allowed": False, "body_read_detected": any(field in result for field in ["body", "html", "raw_response_body"])}


def build_metadata_adapter_cards(query: str | None = None) -> list[dict[str, Any]]:
    return [
        {"card_id": "metadata_adapter_boundary", "title": "Metadata-only adapter boundary", "status": "ready_blocked", "summary": "Only metadata-shaped result records are allowed through this boundary; body fields are rejected.", "allowed_fields": ALLOWED_METADATA_FIELDS, "denied_fields": DENIED_FIELDS},
        {"card_id": "metadata_preview_results", "title": "Local metadata preview results", "status": "preview_only_no_network", "summary": "Local preview records demonstrate result shape without executing a provider request.", "results": normalize_metadata_preview(query)},
    ]


def build_metadata_adapter_actions() -> list[dict[str, Any]]:
    return [
        {"action_id": "review_metadata_adapter_boundary", "label": "Review metadata adapter boundary", "status": "available_for_review", "executable": False, "endpoint": "/api/search/metadata/adapter/boundary"},
        {"action_id": "execute_metadata_provider_adapter", "label": "Execute metadata provider adapter", "status": "blocked", "executable": False, "endpoint": None, "reason": "Provider execution remains disabled in S681-S708."},
    ]


def build_metadata_adapter_status() -> dict[str, Any]:
    return {"status": "metadata_adapter_boundary_ready_execution_blocked", "stage_range": "S695-S701", "allowed_metadata_fields": len(ALLOWED_METADATA_FIELDS), "denied_fields": DENIED_FIELDS, "provider_execution_allowed": False, "network_request_performed": False, "body_read_allowed": False, "blocked_authority": BLOCKED_AUTHORITY.copy()}


def build_metadata_adapter_payload(query: str | None = None) -> dict[str, Any]:
    return {"payload_id": "s695_s701_metadata_adapter_boundary_payload", "boundary": build_metadata_adapter_boundary(), "preview_results": normalize_metadata_preview(query), "cards": build_metadata_adapter_cards(query), "actions": build_metadata_adapter_actions(), "status": build_metadata_adapter_status()}
