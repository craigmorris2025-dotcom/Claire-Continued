"""S807-S820 governed content safety and sanitization planning.

Builds sanitization rules for future body-read text. It does not fetch, read,
parse, execute, or mutate content.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

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

SANITIZER_RULES: List[Dict[str, Any]] = [
    {"rule_id": "strip_scripts", "label": "Strip scripts", "state": "planned", "execution_enabled": False},
    {"rule_id": "strip_forms", "label": "Strip forms and input fields", "state": "planned", "execution_enabled": False},
    {"rule_id": "preserve_source_lineage", "label": "Preserve source lineage", "state": "planned", "execution_enabled": False},
    {"rule_id": "quote_limit_guard", "label": "Limit quoted text", "state": "planned", "execution_enabled": False},
    {"rule_id": "no_credential_capture", "label": "No credential capture", "state": "planned", "execution_enabled": False},
]


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def classify_content_risk(content_type: Optional[str] = None, source_family: Optional[str] = None) -> Dict[str, Any]:
    content = (content_type or "text/html").lower()
    family = (source_family or "unknown_or_user_supplied").lower()
    high_risk = any(token in content for token in ["application/octet-stream", "application/x-msdownload", "zip"]) or family in {
        "denied_source_family",
        "open_web_unknown",
    }
    return {
        "content_type": content,
        "source_family": family,
        "risk_level": "high" if high_risk else "controlled",
        "body_read_allowed": False,
        "body_read_performed": False,
        "network_request_performed": False,
        "sanitization_execution_enabled": False,
        "requires_operator_review": True,
    }


def build_sanitizer_payload(content_type: Optional[str] = None, source_family: Optional[str] = None) -> Dict[str, Any]:
    risk = classify_content_risk(content_type, source_family)
    return {
        "stage_range": "S807-S820",
        "name": "Governed Content Safety Sanitizer Plan",
        "terminal_state": "content_sanitizer_plan_ready_execution_blocked",
        "authority": "sanitizer_plan_only_no_body_read_execution",
        "summary": {
            "sanitizer_rules": len(SANITIZER_RULES),
            "sanitizer_rules_executed": 0,
            "body_reads": 0,
            "network_requests": 0,
            "runtime_truth_mutations": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "risk": risk,
        "rules": deepcopy(SANITIZER_RULES),
        "guards": {
            "no_script_execution": True,
            "no_file_download": True,
            "no_credential_capture": True,
            "no_link_following": True,
            "no_crawl_expansion": True,
            "no_runtime_truth_mutation": True,
        },
    }


def build_sanitizer_cards() -> List[Dict[str, Any]]:
    payload = build_sanitizer_payload()
    return [
        {
            "card_id": f"sanitizer-{rule['rule_id']}",
            "title": rule["label"],
            "subtitle": "Planned content safety rule",
            "state": rule["state"],
            "summary": "Sanitizer rule is visible for review; no content is fetched or sanitized by this build.",
            "badges": ["sanitizer-plan", "body-read-blocked", "no-execution"],
            "execution_enabled": False,
        }
        for rule in payload["rules"]
    ]


def build_sanitizer_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "inspect_content_sanitizer_plan",
            "label": "Inspect sanitizer plan",
            "description": "Display planned sanitizer guards without fetching or reading content.",
            "execution_enabled": False,
            "body_read_allowed": False,
        }
    ]
