from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

BLOCKED_AUTHORITIES = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

OPERATOR_BUTTONS: List[Dict[str, Any]] = [
    {"key": "plan_search", "label": "Plan a governed search", "group": "Search", "intent": "Build the search plan before anything touches the web.", "primary": True, "mode": "preview_only", "endpoint_hint": "/api/search/governed/query/compile", "result_kind": "search_plan_preview"},
    {"key": "check_sources", "label": "Check source policy", "group": "Sources", "intent": "Review allowed, denied, quarantined, and trusted source families.", "primary": True, "mode": "read_only", "endpoint_hint": "/api/sources/policy/payload", "result_kind": "source_policy_status"},
    {"key": "inspect_providers", "label": "Inspect providers", "group": "Providers", "intent": "See configured search providers and why execution is still blocked.", "primary": True, "mode": "read_only", "endpoint_hint": "/api/search/providers/capability/payload", "result_kind": "provider_readiness"},
    {"key": "preview_metadata_search", "label": "Preview metadata search", "group": "Search", "intent": "Preview a metadata-only query path without contacting providers.", "primary": True, "mode": "preview_only", "endpoint_hint": "/api/search/metadata/probe/manual/preview", "result_kind": "metadata_search_preview"},
    {"key": "review_quarantine", "label": "Review quarantined results", "group": "Evidence", "intent": "Open the review queue for quarantined source/search evidence.", "primary": True, "mode": "review_only", "endpoint_hint": "/api/evidence/quarantine/review-queue", "result_kind": "quarantine_review"},
    {"key": "build_evidence_cards", "label": "Build evidence cards", "group": "Evidence", "intent": "Normalize reviewed metadata into human-readable evidence cards.", "primary": False, "mode": "preview_only", "endpoint_hint": "/api/search/results/normalize/payload", "result_kind": "evidence_cards"},
    {"key": "score_sources", "label": "Score source confidence", "group": "Evidence", "intent": "Preview source confidence and citation usefulness scoring.", "primary": False, "mode": "preview_only", "endpoint_hint": "/api/search/source-confidence/payload", "result_kind": "source_confidence"},
    {"key": "request_body_read", "label": "Prepare body-read request", "group": "Body read", "intent": "Draft a manual body-read request while body reads remain blocked.", "primary": False, "mode": "request_draft_only", "endpoint_hint": "/api/web/body-read/request-packet", "result_kind": "body_read_request"},
    {"key": "body_read_preflight", "label": "Run body-read preflight", "group": "Body read", "intent": "Check authorization, sanitizer, and extraction limits without reading a page body.", "primary": False, "mode": "preflight_only", "endpoint_hint": "/api/web/body-read/preflight/payload", "result_kind": "body_read_preflight"},
    {"key": "draft_source_ingestion", "label": "Draft source ingestion", "group": "Ingestion", "intent": "Preview how reviewed evidence could become a source-ingestion draft.", "primary": False, "mode": "draft_only", "endpoint_hint": "/api/web/source-ingestion/draft", "result_kind": "source_ingestion_draft"},
    {"key": "preview_truth_promotion", "label": "Preview truth promotion", "group": "Governance", "intent": "Show the promotion path while runtime truth mutation stays blocked.", "primary": False, "mode": "preview_only", "endpoint_hint": "/api/web/runtime-truth/promotion-preview", "result_kind": "truth_promotion_preview"},
    {"key": "verify_safety_gate", "label": "Verify safety gate", "group": "Governance", "intent": "Confirm the current web/source/search gate remains fail-closed.", "primary": False, "mode": "verification_only", "endpoint_hint": "/api/internet/s900-stop-gate", "result_kind": "stop_gate_status"},
]

def get_operator_buttons() -> List[Dict[str, Any]]:
    return deepcopy(OPERATOR_BUTTONS)

def get_primary_buttons() -> List[Dict[str, Any]]:
    return [button for button in get_operator_buttons() if button.get("primary")]

def build_operator_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for button in OPERATOR_BUTTONS:
        cards.append({
            "id": f"operator-card-{button['key']}",
            "title": button["label"],
            "category": button["group"],
            "summary": button["intent"],
            "button_label": "Preview" if button["mode"] != "read_only" else "Open",
            "execution_state": "blocked_or_preview_only",
            "safe_to_click": True,
            "authority": "non_executing_operator_control",
            "endpoint_hint": button["endpoint_hint"],
            "result_kind": button["result_kind"],
        })
    return cards

def build_operator_actions() -> List[Dict[str, Any]]:
    return [{
        "key": button["key"],
        "label": button["label"],
        "group": button["group"],
        "description": button["intent"],
        "action_type": "operator_preview",
        "execution_enabled": False,
        "requires_manual_review": True,
        "blocked_authorities": deepcopy(BLOCKED_AUTHORITIES),
    } for button in OPERATOR_BUTTONS]

def preview_operation(operation_key: str) -> Dict[str, Any]:
    buttons = {button["key"]: button for button in OPERATOR_BUTTONS}
    button = buttons.get(operation_key)
    if not button:
        return {"status": "unknown_operation", "operation_key": operation_key, "execution_enabled": False, "blocked_authorities": deepcopy(BLOCKED_AUTHORITIES)}
    return {
        "status": "preview_ready",
        "operation_key": operation_key,
        "title": button["label"],
        "group": button["group"],
        "summary": button["intent"],
        "mode": button["mode"],
        "endpoint_hint": button["endpoint_hint"],
        "result_kind": button["result_kind"],
        "execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "runtime_mutation_enabled": False,
        "manual_review_required": True,
        "blocked_authorities": deepcopy(BLOCKED_AUTHORITIES),
        "operator_message": "This button is mounted and safe to click. It returns a local preview packet only.",
    }

def build_operator_experience_payload() -> Dict[str, Any]:
    buttons = get_operator_buttons()
    actions = build_operator_actions()
    return {
        "status": "ready",
        "stage_range": "S1013-S1040",
        "surface": "operator_experience_console",
        "headline": "Operator controls ready",
        "summary": "User-facing cockpit controls are mounted for governed search, source review, evidence handling, body-read preflight, and source-ingestion previews.",
        "operator_mode": "preview_and_review_only",
        "button_count": len(buttons),
        "primary_button_count": len(get_primary_buttons()),
        "action_count": len(actions),
        "buttons": buttons,
        "cards": build_operator_cards(),
        "actions": actions,
        "blocked_authorities": deepcopy(BLOCKED_AUTHORITIES),
        "guardrails": [
            "No live web execution is enabled.",
            "No provider search is executed from these buttons.",
            "No page body is read.",
            "No automatic update, runtime mutation, package install, or command execution is permitted.",
        ],
        "visual_contract": {
            "hide_dev_stage_labels": True,
            "show_user_action_labels": True,
            "show_buttons_near_command_bar": True,
            "show_actions_tab_content": True,
            "show_preview_result_panel": True,
        },
        "stop_gate": {
            "name": "S1040 operator-console usability stop gate",
            "passed": True,
            "forward_motion_allowed": True,
            "unlock_allowed": False,
            "reason": "Cockpit buttons are usability controls only; internet/body-read/runtime authorities remain blocked.",
        },
    }

def build_operator_status() -> Dict[str, Any]:
    payload = build_operator_experience_payload()
    return {
        "status": payload["status"],
        "surface": payload["surface"],
        "button_count": payload["button_count"],
        "action_count": payload["action_count"],
        "blocked_authorities": payload["blocked_authorities"],
        "unlock_allowed": False,
    }
