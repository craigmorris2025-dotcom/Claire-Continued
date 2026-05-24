"""S35 first probe preflight audit report.

S35R11 aggregates the final evidence needed before a first metadata-only probe.
It performs no network request.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.s35_one_shot_execution_gate import get_s35_one_shot_execution_gate
from runtime_core.api.s35_operator_probe_command_contract import get_s35_operator_probe_command_contract
from runtime_core.api.s35_single_probe_run_manifest_contract import get_s35_single_probe_run_manifest_contract
from runtime_core.api.provider_environment_setup_guide import get_provider_environment_setup_guide


def get_s35_first_probe_preflight_audit_report() -> Dict[str, Any]:
    gate = get_s35_one_shot_execution_gate()
    command = get_s35_operator_probe_command_contract()
    manifest = get_s35_single_probe_run_manifest_contract()
    setup = get_provider_environment_setup_guide()

    passed = gate.get("go_for_single_operator_probe") is True

    return {
        "version": "v19.89.8-S35R11",
        "status": "preflight_passed" if passed else "preflight_blocked",
        "preflight_passed": passed,
        "gate": gate,
        "command_contract_visible": command.get("status") == "operator_probe_command_contract_visible",
        "manifest_contract_visible": manifest.get("status") == "single_probe_run_manifest_contract_visible",
        "setup_guide_visible": setup.get("status") == "provider_environment_setup_guide_visible",
        "operator_next_action": (
            "Run one controlled metadata-only probe only if preflight_passed is true."
            if passed
            else "Resolve listed gate failures before any live probe."
        ),
        "network_request": "blocked_until_operator_trigger" if passed else "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
