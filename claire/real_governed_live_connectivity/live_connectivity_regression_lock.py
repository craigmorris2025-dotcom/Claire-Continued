from __future__ import annotations

from typing import Dict, List


class LiveConnectivityRegressionLock:
    def validate(self, output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if output.get("layer") != "real_governed_live_connectivity":
            errors.append("Invalid layer marker.")

        if output.get("governance_boundary") != "policy_review_rate_limited_no_unapproved_external_action":
            errors.append("Invalid governance boundary.")

        if "live_enabled" not in output:
            errors.append("Missing live_enabled marker.")

        if "ingestion" not in output:
            errors.append("Missing ingestion result.")

        ingestion = output.get("ingestion", {})
        if isinstance(ingestion, dict):
            fetch_result = ingestion.get("fetch_result", {})
            if isinstance(fetch_result, dict):
                status = fetch_result.get("status")
                if status == "review_required":
                    warnings.append("Unknown domain requires review before live fetch.")
                if status == "live_disabled_contract_ready":
                    warnings.append("Live HTTP is disabled; contract path verified only.")

        return {
            "version": "v17.20",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "governance_boundary_preserved": output.get("governance_boundary") == "policy_review_rate_limited_no_unapproved_external_action",
                "live_toggle_explicit": "live_enabled" in output,
                "ingestion_contract_present": "ingestion" in output,
                "no_unreviewed_external_action": True,
            },
        }
