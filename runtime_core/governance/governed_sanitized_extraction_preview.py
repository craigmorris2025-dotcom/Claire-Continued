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

DEFAULT_PREVIEWS: List[Dict[str, Any]] = [
    {"preview_id": "sanitized-extraction-preview-official-docs-001", "title": "Official docs extraction preview", "source_family": "official_docs", "fields": ["title", "canonical_url", "publisher", "updated_at", "claim_candidates"]},
    {"preview_id": "sanitized-extraction-preview-market-002", "title": "Market/regulatory extraction preview", "source_family": "primary_market_or_regulatory", "fields": ["title", "canonical_url", "publisher", "publication_date", "risk_notes"]},
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def normalize_extraction_previews(previews: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    raw = list(previews) if previews is not None else deepcopy(DEFAULT_PREVIEWS)
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(raw):
        fields = [str(field) for field in item.get("fields", [])] or ["title", "canonical_url"]
        body_fields = [field for field in fields if field in {"claim_candidates", "risk_notes", "summary_excerpt", "quotes"}]
        normalized.append({
            "preview_id": str(item.get("preview_id") or f"sanitized-extraction-preview-{index + 1:03d}"),
            "title": str(item.get("title") or "Sanitized extraction preview"),
            "source_family": str(item.get("source_family") or "unknown_or_user_supplied"),
            "state": "preview_ready_body_read_blocked",
            "fields_requested": fields,
            "fields_requiring_body_read": body_fields,
            "fields_allowed_now": [field for field in fields if field not in body_fields],
            "sanitizer_required": bool(body_fields),
            "sanitizer_executed": False,
            "body_read_allowed": False,
            "body_read_performed": False,
            "network_request_performed": False,
            "created_at": str(item.get("created_at") or _now_iso()),
        })
    return normalized


def build_sanitized_extraction_preview_payload(previews: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    normalized = normalize_extraction_previews(previews)
    blocked_fields = sum(len(item["fields_requiring_body_read"]) for item in normalized)
    return {
        "stage_range": "S849-S855",
        "name": "Sanitized Extraction Preview",
        "terminal_state": "sanitized_extraction_preview_ready_body_read_blocked",
        "authority": "preview_only_no_fetch_no_body_parse",
        "summary": {"previews": len(normalized), "blocked_body_fields": blocked_fields, "sanitizer_executions": 0, "body_reads_performed": 0, "network_requests": 0, "runtime_truth_mutations": 0},
        "blocked_capabilities": get_blocked_capabilities(),
        "previews": normalized,
        "policy": {"scripts_never_execute": True, "external_resources_never_load": True, "quoted_text_requires_operator_approved_body_read": True, "claim_extraction_requires_review": True},
    }


def build_sanitized_extraction_cards(previews: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for item in build_sanitized_extraction_preview_payload(previews)["previews"]:
        cards.append({
            "card_id": f"sanitized-extraction-{item['preview_id']}",
            "title": item["title"],
            "subtitle": item["source_family"],
            "state": item["state"],
            "summary": f"{len(item['fields_allowed_now'])} metadata fields available now; {len(item['fields_requiring_body_read'])} fields blocked until manual body-read approval.",
            "badges": ["sanitized-preview", "no-fetch", "body-fields-blocked"],
            "actions": ["review_extraction_scope", "reject_body_fields", "prepare_ingestion_draft"],
            "execution_enabled": False,
        })
    return cards
