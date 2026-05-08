from __future__ import annotations

from typing import Dict, List


class ProductionRuntimeRegressionLock:
    def validate(self, output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if output.get("layer") != "distributed_production_runtime":
            errors.append("Invalid layer marker.")

        if output.get("governance_boundary") != "production_contract_no_unreviewed_external_action":
            errors.append("Governance boundary missing or invalid.")

        required = [
            "workers",
            "shards",
            "partitions",
            "streaming",
            "workload_assignment",
            "daemon",
            "telemetry",
            "health",
        ]
        for key in required:
            if key not in output:
                errors.append(f"Missing required output key: {key}")

        health = output.get("health", {})
        if isinstance(health, dict) and health.get("status") != "healthy":
            warnings.append(f"Health dashboard status: {health.get('status')}")

        return {
            "version": "v17.40",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "distributed_workers_present": "workers" in output,
                "sharding_present": "shards" in output,
                "partitioning_present": "partitions" in output,
                "telemetry_present": "telemetry" in output,
                "health_dashboard_present": "health" in output,
                "bounded_external_action": output.get("governance_boundary") == "production_contract_no_unreviewed_external_action",
            },
        }
