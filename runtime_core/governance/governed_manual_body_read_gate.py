"""S821-S834 manual body-read gate and cockpit stop gate.

This module creates the final visible gate before any later build may consider
manual body-read execution. In this build, execution remains disabled.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

from runtime_core.governance.governed_body_read_authorization import (
    build_authorization_actions,
    build_authorization_cards,
    build_authorization_payload,
)
from runtime_core.governance.governed_content_safety_sanitizer import (
    build_sanitizer_actions,
    build_sanitizer_cards,
    build_sanitizer_payload,
)
from runtime_core.governance.governed_extraction_scope_contract import (
    build_extraction_scope_actions,
    build_extraction_scope_cards,
    build_extraction_scope_contract,
)

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


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def build_manual_body_read_gate_payload() -> Dict[str, Any]:
    authorization = build_authorization_payload()
    extraction = build_extraction_scope_contract()
    sanitizer = build_sanitizer_payload()
    cards = build_manual_body_read_gate_cards(include_nested=False)
    actions = build_manual_body_read_gate_actions(include_nested=False)
    return {
        "stage_range": "S779-S834",
        "name": "Governed Body-Read Gate + Extraction Safety",
        "terminal_state": "manual_body_read_gate_ready_execution_blocked",
        "authority": "manual_gate_model_only_body_reads_blocked",
        "updated_at": _now_iso(),
        "summary": {
            "subsystems_ready": 4,
            "authorization_requests": authorization["summary"]["authorization_requests"],
            "extraction_fields": extraction["summary"]["field_total"],
            "sanitizer_rules": sanitizer["summary"]["sanitizer_rules"],
            "cockpit_cards": len(cards),
            "governed_actions": len(actions),
            "executable_actions": 0,
            "body_reads_allowed": 0,
            "body_reads_performed": 0,
            "network_requests": 0,
            "runtime_truth_mutations": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "subsystems": {
            "authorization": authorization,
            "extraction_scope": extraction,
            "content_sanitizer": sanitizer,
        },
        "cards": cards,
        "actions": actions,
        "stop_gate": build_manual_body_read_stop_gate(),
    }


def build_manual_body_read_gate_cards(include_nested: bool = True) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = [
        {
            "card_id": "manual-body-read-gate-overview",
            "title": "Manual body-read gate",
            "subtitle": "Ready for future operator-gated execution design",
            "state": "gate_ready_execution_blocked",
            "summary": "Authorization, extraction scope, and sanitizer planning are visible, but body reads remain blocked.",
            "badges": ["manual-gate", "body-read-blocked", "crawl-blocked", "runtime-mutation-blocked"],
            "execution_enabled": False,
        },
        {
            "card_id": "manual-body-read-single-url-boundary",
            "title": "Single URL boundary",
            "subtitle": "No crawling or link following",
            "state": "boundary_defined",
            "summary": "Future reads must stay scoped to a single reviewed URL unless a later gate changes policy.",
            "badges": ["single-url", "no-crawl", "no-browser-execution"],
            "execution_enabled": False,
        },
        {
            "card_id": "manual-body-read-runtime-truth-boundary",
            "title": "Runtime truth boundary",
            "subtitle": "No automatic promotion",
            "state": "runtime_truth_blocked",
            "summary": "Any future body-read output must remain quarantined until operator review.",
            "badges": ["quarantine-first", "no-auto-promotion", "updates-blocked"],
            "execution_enabled": False,
        },
    ]
    if include_nested:
        cards.extend(build_authorization_cards())
        cards.extend(build_extraction_scope_cards())
        cards.extend(build_sanitizer_cards())
    return cards


def build_manual_body_read_gate_actions(include_nested: bool = True) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = [
        {
            "action_id": "prepare_manual_body_read_preflight",
            "label": "Prepare manual body-read preflight",
            "description": "Create a future preflight packet; execution remains disabled in this build.",
            "execution_enabled": False,
            "body_read_allowed": False,
            "requires_operator_approval": True,
        },
        {
            "action_id": "reject_manual_body_read_preflight",
            "label": "Reject manual body-read preflight",
            "description": "Visible operator action descriptor only; no destructive action is executed.",
            "execution_enabled": False,
            "body_read_allowed": False,
            "requires_operator_approval": True,
        },
        {
            "action_id": "hold_for_next_gate",
            "label": "Hold for next gate",
            "description": "Stop at S834 before any build attempts body-read execution authority.",
            "execution_enabled": False,
            "body_read_allowed": False,
            "requires_operator_approval": True,
        },
    ]
    if include_nested:
        actions.extend(build_authorization_actions())
        actions.extend(build_extraction_scope_actions())
        actions.extend(build_sanitizer_actions())
    return actions


def build_manual_body_read_stop_gate() -> Dict[str, Any]:
    return {
        "gate_id": "S834_MANUAL_BODY_READ_GATE_STOP",
        "stage_range": "S779-S834",
        "passed": True,
        "ready_for_next_phase": True,
        "next_phase": "manual_body_read_execution_gate_design",
        "blocked_next_phase": "body_read_execution_crawling_or_runtime_mutation",
        "must_remain_false": deepcopy(BLOCKED_CAPABILITIES),
        "operator_message": "The cockpit can now show body-read authorization, extraction scope, sanitizer, and manual gate cards, but no body read is allowed yet.",
    }


def build_manual_body_read_status() -> Dict[str, Any]:
    return {
        "stage_range": "S779-S834",
        "status": "ready",
        "terminal_state": "manual_body_read_gate_ready_execution_blocked",
        "blocked_capabilities": get_blocked_capabilities(),
        "stop_gate": build_manual_body_read_stop_gate(),
    }
