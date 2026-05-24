"""S35 operator command contract for first metadata probe.

S35R7 defines the operator command shape for a future one-shot metadata probe.
It does not execute the command.
"""

from __future__ import annotations

from typing import Any, Dict, List


REQUIRED_COMMAND_FIELDS: List[str] = [
    "command_type",
    "target_url",
    "operator_trigger_id",
    "reason",
]

ALLOWED_COMMAND_TYPES: List[str] = [
    "one_shot_metadata_head_probe",
]


def get_s35_operator_probe_command_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S35R7",
        "status": "operator_probe_command_contract_visible",
        "command_execution_enabled": False,
        "allowed_command_types": ALLOWED_COMMAND_TYPES,
        "required_fields": REQUIRED_COMMAND_FIELDS,
        "sample_command": {
            "command_type": "one_shot_metadata_head_probe",
            "target_url": "https://www.googleapis.com",
            "operator_trigger_id": "operator_generated_required",
            "reason": "first governed metadata-only probe",
        },
        "validation_rules": {
            "target_url_must_be_https": True,
            "host_must_be_allowlisted": True,
            "operator_trigger_required": True,
            "method": "HEAD",
            "metadata_only": True,
        },
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
