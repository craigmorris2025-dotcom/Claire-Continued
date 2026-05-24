"""S793-S806 governed extraction scope contract.

Defines what a future body-read extraction would be allowed to collect, while
execution and body reads remain blocked.
"""
from __future__ import annotations

from copy import deepcopy
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

DEFAULT_FIELDS: List[Dict[str, Any]] = [
    {"field_id": "title", "label": "Page title", "allowed": True, "body_required": False},
    {"field_id": "canonical_url", "label": "Canonical URL", "allowed": True, "body_required": False},
    {"field_id": "published_or_updated_at", "label": "Published or updated date", "allowed": True, "body_required": False},
    {"field_id": "source_publisher", "label": "Source publisher", "allowed": True, "body_required": False},
    {"field_id": "summary_excerpt", "label": "Short summary excerpt", "allowed": False, "body_required": True},
    {"field_id": "claims", "label": "Claim candidates", "allowed": False, "body_required": True},
    {"field_id": "citations", "label": "Citation candidates", "allowed": False, "body_required": True},
]


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def build_extraction_scope_contract(fields: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    raw = list(fields) if fields is not None else deepcopy(DEFAULT_FIELDS)
    normalized: List[Dict[str, Any]] = []
    for index, field in enumerate(raw):
        body_required = bool(field.get("body_required", False))
        normalized.append(
            {
                "field_id": str(field.get("field_id") or f"field_{index + 1:03d}"),
                "label": str(field.get("label") or "Extraction field"),
                "allowed_in_current_build": bool(field.get("allowed", False)) and not body_required,
                "requires_body_read": body_required,
                "collection_state": "metadata_only_allowed" if not body_required else "blocked_until_body_read_gate",
                "network_request_performed": False,
                "body_read_performed": False,
            }
        )
    return {
        "stage_range": "S793-S806",
        "name": "Governed Extraction Scope Contract",
        "terminal_state": "extraction_scope_contract_ready_body_fields_blocked",
        "authority": "contract_only_no_extraction_execution",
        "summary": {
            "field_total": len(normalized),
            "metadata_fields_allowed": len([item for item in normalized if item["allowed_in_current_build"]]),
            "body_fields_blocked": len([item for item in normalized if item["requires_body_read"]]),
            "body_reads_performed": 0,
            "network_requests": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "fields": normalized,
        "contract_rules": {
            "single_page_scope": True,
            "no_link_following": True,
            "no_crawling": True,
            "no_script_execution": True,
            "no_runtime_truth_mutation": True,
            "no_package_download": True,
        },
    }


def build_extraction_scope_cards() -> List[Dict[str, Any]]:
    payload = build_extraction_scope_contract()
    return [
        {
            "card_id": f"extraction-scope-{field['field_id']}",
            "title": field["label"],
            "subtitle": "Metadata field" if not field["requires_body_read"] else "Body-read field blocked",
            "state": field["collection_state"],
            "summary": "Allowed only if metadata-level; any body-required field remains blocked.",
            "badges": ["scope-contract", "no-crawl", "no-runtime-mutation"],
            "execution_enabled": False,
        }
        for field in payload["fields"]
    ]


def build_extraction_scope_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "inspect_extraction_scope_contract",
            "label": "Inspect extraction scope contract",
            "description": "Show which fields would be metadata-only versus body-read-blocked.",
            "execution_enabled": False,
            "body_read_allowed": False,
        }
    ]
