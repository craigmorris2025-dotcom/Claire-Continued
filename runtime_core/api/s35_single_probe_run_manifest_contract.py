"""S35 single-probe run manifest contract.

S35R8 defines the manifest required before and after a future first probe.
It does not create a live probe run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "data" / "internet_live_probe" / "metadata_probe_runs"


REQUIRED_MANIFEST_FIELDS: List[str] = [
    "run_id",
    "created_at_utc",
    "operator_trigger_id",
    "target_url",
    "method",
    "provider_id",
    "policy_result",
    "execution_result",
    "quarantine_record_id",
    "rollback_reference",
]


def get_s35_single_probe_run_manifest_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S35R8",
        "status": "single_probe_run_manifest_contract_visible",
        "runs_dir": str(RUNS_DIR).replace("\\", "/"),
        "manifest_write_enabled": False,
        "required_manifest_fields": REQUIRED_MANIFEST_FIELDS,
        "method": "HEAD",
        "metadata_only": True,
        "one_probe_only": True,
        "operator_trigger_required": True,
        "quarantine_required": True,
        "manual_promotion_required": True,
        "runtime_truth_write_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
