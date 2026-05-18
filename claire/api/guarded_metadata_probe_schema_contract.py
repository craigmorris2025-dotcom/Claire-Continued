"""Guarded metadata probe schemas.

S33R11 defines request/response contracts only.
No endpoint registration and no network execution.
"""

from __future__ import annotations

from typing import Any, Dict, List


ALLOWED_METHODS = ["HEAD"]
FORBIDDEN_CAPTURE_FIELDS = [
    "response_body",
    "rendered_dom",
    "browser_screenshot",
    "script_execution",
    "runtime_truth_write",
]
ALLOWED_CAPTURE_FIELDS = [
    "status_code",
    "response_headers",
    "content_type",
    "server",
    "date",
    "elapsed_ms",
    "final_url",
    "redirect_count",
]


def get_guarded_metadata_probe_schema_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R11",
        "status": "schema_contract_visible",
        "route_registered": False,
        "execution_enabled": False,
        "request_schema": {
            "required": ["target_url", "operator_trigger_id"],
            "optional": ["provider_id", "reason"],
            "target_url_policy": "must_match_allowlist_before_execution",
            "operator_trigger_required": True,
        },
        "response_schema": {
            "allowed_capture_fields": ALLOWED_CAPTURE_FIELDS,
            "forbidden_capture_fields": FORBIDDEN_CAPTURE_FIELDS,
            "metadata_only": True,
            "body_allowed": False,
        },
        "method_policy": {
            "allowed_methods": ALLOWED_METHODS,
            "metadata_get_allowed": False,
            "response_body_allowed": False,
        },
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
    }
