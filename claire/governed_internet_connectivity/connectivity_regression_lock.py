from __future__ import annotations

from typing import Dict, List


class ConnectivityRegressionLock:
    def validate(self, runtime_output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if runtime_output.get("layer") != "governed_internet_connectivity":
            errors.append("Invalid layer name.")

        boundary = runtime_output.get("governance_boundary")
        if boundary != "no_unreviewed_external_action":
            errors.append("Governance boundary missing or invalid.")

        if "fetch" not in runtime_output:
            errors.append("Fetch contract missing.")

        if "evidence" not in runtime_output:
            errors.append("Evidence output missing.")

        fetch = runtime_output.get("fetch", {})
        if isinstance(fetch, dict) and fetch.get("status") == "review_required":
            warnings.append("Fetch requires operator review before execution.")

        return {
            "version": "v17.10",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "source_policy_present": "source_policy" in runtime_output,
                "fetch_contract_present": "fetch" in runtime_output,
                "evidence_contract_present": "evidence" in runtime_output,
                "bounded_external_action": boundary == "no_unreviewed_external_action",
            },
        }
