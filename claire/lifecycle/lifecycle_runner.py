"""Route-aware 30-stage lifecycle runner for Claire core completion."""

from __future__ import annotations

from typing import Any, Dict

from .completion_gate import CompletionGate
from .contract_validator import LifecycleContractValidator
from .lifecycle_context import (
    initialize_context,
    mark_stage_complete,
    mark_stage_insufficient_data,
    mark_stage_skipped_by_route,
    summarize_run_state,
)
from .lifecycle_registry import CoreLifecycleRegistry


class CoreLifecycleRunner:
    """Maps existing pipeline outputs onto the canonical 30-stage lifecycle."""

    def run(self, outputs: Dict[str, Any], run_id: str = "unknown", route: str | None = None) -> Dict[str, Any]:
        outputs = outputs or {}
        route = route or self.detect_route(outputs)
        context = initialize_context(run_id=run_id, route=route, metadata={
            "domain": outputs.get("domain"),
            "keywords": outputs.get("keywords", []),
            "signal_governance_version": (outputs.get("governed_signals") or {}).get("version"),
        })
        if outputs.get("governed_signals") is not None:
            context.evidence["governed_signals"] = outputs.get("governed_signals")
        if outputs.get("trend_discovery") is not None:
            context.evidence["trend_discovery"] = outputs.get("trend_discovery")
        if outputs.get("thesis_formation") is not None:
            context.evidence["thesis_formation"] = outputs.get("thesis_formation")
        if outputs.get("portfolio_optimization") is not None:
            context.evidence["portfolio_optimization"] = outputs.get("portfolio_optimization")
        validator = LifecycleContractValidator()
        validations = {
            item["stage_id"]: item
            for item in validator.validate(route, outputs)["validations"]
        }

        stages = []
        for stage in CoreLifecycleRegistry().stages():
            validation = validations[stage["id"]]
            if validation["status"] == "skipped_by_route":
                mark_stage_skipped_by_route(context, stage["id"], "stage not required for selected route")
            elif validation["status"] == "complete":
                mark_stage_complete(context, stage["id"], output=self._stage_output(stage, outputs), message="required outputs present")
            else:
                mark_stage_insufficient_data(context, stage["id"], "required outputs missing")

            state = context.stage_statuses[stage["id"]]
            stages.append({
                **stage,
                "status": state["status"],
                "message": state["message"],
                "required": validation["required"],
                "missing_outputs": validation["missing_outputs"],
                "present_outputs": validation["present_outputs"],
                "errors": state["errors"],
                "warnings": state["warnings"],
            })

        payload = {
            "status": "success",
            "lifecycle_name": CoreLifecycleRegistry.lifecycle_name,
            "registry_version": CoreLifecycleRegistry.version,
            "route": route,
            "stage_count": len(stages),
            "stages": stages,
            "context": context.to_dict(),
            "summary": summarize_run_state(context),
        }
        payload["completion_gate"] = CompletionGate().evaluate(payload)
        return payload

    def detect_route(self, outputs: Dict[str, Any]) -> str:
        design_portal = outputs.get("design_portal") or {}
        design_output = outputs.get("design_output") or {}
        if design_portal.get("route_to_design") or design_output.get("status") in {"success", "design_ready"}:
            return "breakthrough_design"
        return "portfolio_only"

    def _stage_output(self, stage: Dict[str, Any], outputs: Dict[str, Any]) -> Any:
        return outputs.get(stage["output_key"])
