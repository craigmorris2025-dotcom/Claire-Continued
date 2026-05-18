"""S35 blocked-by-default execution capsule.

S35R12 defines the first probe execution capsule but keeps execution disabled.
This module does not perform network requests.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.api.s35_first_probe_preflight_audit_report import (
    get_s35_first_probe_preflight_audit_report,
)


def get_s35_blocked_by_default_execution_capsule() -> Dict[str, Any]:
    preflight = get_s35_first_probe_preflight_audit_report()
    preflight_passed = preflight.get("preflight_passed") is True

    return {
        "version": "v19.89.8-S35R12",
        "status": "execution_capsule_ready_but_blocked" if preflight_passed else "execution_capsule_blocked",
        "execution_capsule_defined": True,
        "execution_enabled_by_default": False,
        "requires_explicit_operator_trigger": True,
        "requires_registered_endpoint": True,
        "requires_preflight_passed": True,
        "requires_quarantine_writer": True,
        "allowed_execution_count": 1,
        "method": "HEAD",
        "metadata_only": True,
        "body_read_allowed": False,
        "browser_allowed": False,
        "runtime_truth_write_allowed": False,
        "automatic_update_allowed": False,
        "network_request": "blocked_until_explicit_operator_trigger" if preflight_passed else "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "next_safe_step": (
            "If capsule is ready, the next build may create a guarded single-probe "
            "runner that remains operator-triggered only."
        ),
    }
