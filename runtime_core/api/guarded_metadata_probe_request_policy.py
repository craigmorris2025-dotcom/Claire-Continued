"""Guarded metadata probe request policy.

S33R12 validates a would-be request without executing it.
"""

from __future__ import annotations

from urllib.parse import urlparse
from typing import Any, Dict

from runtime_core.api.allowlist_rate_limit_enforcement_proof import (
    get_allowlist_rate_limit_enforcement_proof,
)
from runtime_core.api.governed_provider_readiness_validator import (
    get_governed_provider_readiness_validator,
)


def _host_allowed(host: str | None) -> bool:
    if not host:
        return False
    proof = get_allowlist_rate_limit_enforcement_proof()
    return any(item.get("host") == host for item in proof.get("allowlist", []))


def validate_guarded_metadata_probe_request(
    target_url: str,
    operator_trigger_id: str | None = None,
    method: str = "HEAD",
) -> Dict[str, Any]:
    parsed = urlparse(target_url or "")
    readiness = get_governed_provider_readiness_validator()

    failures = []
    if not operator_trigger_id:
        failures.append("missing_operator_trigger_id")
    if method != "HEAD":
        failures.append("method_not_allowed")
    if parsed.scheme != "https":
        failures.append("target_url_must_be_https")
    if not _host_allowed(parsed.hostname):
        failures.append("target_host_not_allowlisted")
    if readiness.get("readiness_passed") is not True:
        failures.append("provider_readiness_not_passed")

    accepted = len(failures) == 0

    return {
        "version": "v19.89.8-S33R12",
        "status": "request_policy_passed" if accepted else "request_policy_blocked",
        "accepted_for_future_execution": accepted,
        "execution_performed": False,
        "target_host": parsed.hostname,
        "method": method,
        "failures": failures,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
    }


def get_guarded_metadata_probe_request_policy() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R12",
        "status": "request_policy_visible",
        "route_registered": False,
        "execution_enabled": False,
        "sample_validation": validate_guarded_metadata_probe_request(
            target_url="https://www.googleapis.com",
            operator_trigger_id=None,
            method="HEAD",
        ),
        "policy": {
            "operator_trigger_required": True,
            "https_required": True,
            "allowlist_required": True,
            "provider_readiness_required": True,
            "method": "HEAD",
            "body_read_allowed": False,
        },
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
