"""Promoted evidence integration contract.

S33R15 defines how approved metadata evidence may integrate later.
It does not write runtime truth and does not promote anything automatically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
PROMOTED_STORE = ROOT / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json"


def get_promoted_evidence_integration_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R15",
        "status": "promoted_evidence_integration_contract_visible",
        "promoted_store_path": str(PROMOTED_STORE).replace("\\", "/"),
        "promotion_enabled": False,
        "automatic_promotion_allowed": False,
        "manual_promotion_required": True,
        "runtime_truth_write_allowed": False,
        "integration_target": "governed_evidence_basket",
        "accepted_evidence_types": [
            "metadata_probe_result",
            "provider_header_observation",
            "allowlist_validation_result",
            "rate_limit_validation_result",
        ],
        "forbidden_evidence_types": [
            "response_body",
            "rendered_dom",
            "browser_screenshot",
            "script_execution_output",
        ],
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
