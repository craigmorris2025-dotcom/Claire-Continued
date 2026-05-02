"""Contract validation helpers for Claire core lifecycle stages."""

from __future__ import annotations

from typing import Any, Dict, List

from .stage_contracts import route_requires_contract, stage_contracts


def output_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, dict):
        if value.get("status") in {"failed", "portal_failed"}:
            return False
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, str):
        return bool(value.strip())
    return True


class LifecycleContractValidator:
    """Validates current run outputs against route-aware stage contracts."""

    def validate_stage(self, stage_id: str, route: str, outputs: Dict[str, Any]) -> Dict[str, Any]:
        contract = stage_contracts()[stage_id]
        required = route_requires_contract(contract, route)
        if not required:
            return {
                "stage_id": stage_id,
                "status": "skipped_by_route",
                "required": False,
                "missing_outputs": [],
                "present_outputs": [],
            }

        present: List[str] = []
        missing: List[str] = []
        for key in contract.required_outputs:
            if output_present(outputs.get(key)):
                present.append(key)
            else:
                missing.append(key)

        return {
            "stage_id": stage_id,
            "status": "complete" if not missing else "insufficient_data",
            "required": True,
            "missing_outputs": missing,
            "present_outputs": present,
        }

    def validate(self, route: str, outputs: Dict[str, Any]) -> Dict[str, Any]:
        validations = [self.validate_stage(stage_id, route, outputs) for stage_id in stage_contracts()]
        incomplete = [item for item in validations if item["required"] and item["missing_outputs"]]
        return {
            "status": "complete" if not incomplete else "incomplete",
            "route": route,
            "stage_count": len(validations),
            "incomplete_stage_count": len(incomplete),
            "validations": validations,
        }
