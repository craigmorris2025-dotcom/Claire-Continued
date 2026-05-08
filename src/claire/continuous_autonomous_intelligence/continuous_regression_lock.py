from __future__ import annotations

from typing import Dict, List


class ContinuousIntelligenceRegressionLock:
    def validate(self, output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if output.get("layer") != "continuous_autonomous_intelligence":
            errors.append("Invalid layer marker.")

        if output.get("governance_boundary") != "bounded_internal_orchestration_no_unreviewed_external_action":
            errors.append("Governance boundary missing or invalid.")

        required = ["workers", "events", "supervisor_tick", "campaigns", "escalation"]
        for key in required:
            if key not in output:
                errors.append(f"Missing required output key: {key}")

        escalation = output.get("escalation", {})
        if isinstance(escalation, dict) and escalation.get("status") == "requires_review":
            warnings.append("Escalation requires user/operator review before downstream action.")

        return {
            "version": "v17.30",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "worker_registry_present": "workers" in output,
                "event_bus_present": "events" in output,
                "supervisor_present": "supervisor_tick" in output,
                "state_recovery_present": "checkpoint" in output,
                "bounded_external_action": output.get("governance_boundary") == "bounded_internal_orchestration_no_unreviewed_external_action",
            },
        }
