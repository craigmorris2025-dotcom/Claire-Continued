"""S35 one-shot metadata probe execution gate.

S35R10 is the final go/no-go gate before the first real metadata-only probe.
It performs no network request.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.s35_provider_activation_verifier import get_s35_provider_activation_verifier
from runtime_core.api.s35_endpoint_registration_preflight import get_s35_endpoint_registration_preflight
from runtime_core.api.s35_quarantine_verification_report import get_s35_quarantine_verification_report
from runtime_core.api.s35_no_network_endpoint_contract_test import get_s35_no_network_endpoint_contract_test


def get_s35_one_shot_execution_gate() -> Dict[str, Any]:
    provider = get_s35_provider_activation_verifier()
    preflight = get_s35_endpoint_registration_preflight()
    quarantine = get_s35_quarantine_verification_report()
    contract_test = get_s35_no_network_endpoint_contract_test()

    failures = []
    if provider.get("ready") is not True:
        failures.append("provider_activation_not_ready")
    if preflight.get("registration_allowed") is not True:
        failures.append("endpoint_registration_preflight_not_passed")
    if quarantine.get("quarantine_ready_for_first_probe") is not True:
        failures.append("quarantine_not_ready")
    if contract_test.get("contract_test_passed") is not True:
        failures.append("endpoint_contract_test_not_passed")

    go = len(failures) == 0

    return {
        "version": "v19.89.8-S35R10",
        "status": "go_for_single_operator_probe" if go else "blocked_before_single_operator_probe",
        "go_for_single_operator_probe": go,
        "failures": failures,
        "single_probe_only": True,
        "operator_trigger_required": True,
        "method": "HEAD",
        "metadata_only": True,
        "quarantine_required": True,
        "manual_promotion_required": True,
        "network_request": "blocked_until_operator_trigger" if go else "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
