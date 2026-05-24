"""Route-aware 30-stage lifecycle runner for Claire core completion."""

from __future__ import annotations

from typing import Any, Dict

from .completion_gate import CompletionGate
from .contract_validator import LifecycleContractValidator
from .canonical_paths import (
    ACQUISITION_ROUTE,
    BREAKTHROUGH_DESIGN_ROUTE,
    BREAKTHROUGH_ESCALATION_ROUTE,
    PORTFOLIO_ROUTE,
    SOLUTION_DESIGN_ROUTE,
    normalize_route,
    route_path,
)
from .lifecycle_context import (
    initialize_context,
    mark_stage_complete,
    mark_stage_insufficient_data,
    mark_stage_skipped_by_route,
    summarize_run_state,
)
from .lifecycle_registry import CoreLifecycleRegistry
from .route_contracts import select_route_by_center_contract


class CoreLifecycleRunner:
    """Maps existing pipeline outputs onto the canonical 30-stage lifecycle."""

    def run(self, outputs: Dict[str, Any], run_id: str = "unknown", route: str | None = None) -> Dict[str, Any]:
        outputs = outputs or {}
        route = normalize_route(route or self.detect_route(outputs))
        context = initialize_context(run_id=run_id, route=route, metadata={
            "domain": outputs.get("domain"),
            "keywords": outputs.get("keywords", []),
            "signal_governance_version": (outputs.get("governed_signals") or {}).get("version"),
            "canonical_route_path": route_path(route),
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
            "canonical_route_path": route_path(route),
            "stage_count": len(stages),
            "stages": stages,
            "context": context.to_dict(),
            "summary": summarize_run_state(context),
        }
        payload["completion_gate"] = CompletionGate().evaluate(payload)
        return payload

    def detect_route(self, outputs: Dict[str, Any]) -> str:
        explicit_route = self._explicit_route(outputs)
        if explicit_route:
            return normalize_route(explicit_route)

        center_decision = select_route_by_center_contract(outputs)
        center_route_id = str(center_decision.get("selected_route_id") or "")
        center_primary = str(center_decision.get("breakthrough_primary") or "").strip()
        if center_decision.get("used_center_contract") and (
            center_route_id != "breakthrough" or center_primary
        ):
            return normalize_route(str(center_decision.get("selected_route") or PORTFOLIO_ROUTE))

        design_portal = outputs.get("design_portal") or {}
        design_output = outputs.get("design_output") or {}
        design_route_requested = self._design_route_requested(outputs)
        signal_activated_design = bool(
            design_portal.get("route_to_design")
            and (
                design_portal.get("inputs", {}).get("signal_activated_breakthrough")
                or design_portal.get("status") == "design_ready"
            )
        )
        if (
            design_route_requested
            or signal_activated_design
        ) and (
            design_portal.get("route_to_design") or design_output.get("status") in {"success", "design_ready"}
        ):
            return BREAKTHROUGH_DESIGN_ROUTE
        if self._acquisition_route_requested(outputs):
            return ACQUISITION_ROUTE
        if design_route_requested:
            return BREAKTHROUGH_ESCALATION_ROUTE
        return PORTFOLIO_ROUTE

    def _stage_output(self, stage: Dict[str, Any], outputs: Dict[str, Any]) -> Any:
        return outputs.get(stage["output_key"])

    def _design_route_requested(self, outputs: Dict[str, Any]) -> bool:
        thesis = outputs.get("thesis_formation") if isinstance(outputs.get("thesis_formation"), dict) else {}
        breakthrough = outputs.get("breakthrough") if isinstance(outputs.get("breakthrough"), dict) else {}
        route = str(
            thesis.get("route_recommendation")
            or breakthrough.get("route_recommendation")
            or ""
        ).strip()
        return route in {"breakthrough_design", "breakthrough_escalation_candidate", "solution_design"}

    def _explicit_route(self, outputs: Dict[str, Any]) -> str:
        core_output = outputs.get("core_output") if isinstance(outputs.get("core_output"), dict) else {}
        for key in ("scan_route_selected", "route_selected", "selected_route", "route"):
            value = outputs.get(key) or core_output.get(key)
            if value:
                route = normalize_route(str(value))
                if route not in {"blocked_output", "insufficient_data_output", "failed_output", "trend_thesis"}:
                    return route
        return ""

    def _acquisition_route_requested(self, outputs: Dict[str, Any]) -> bool:
        thesis = outputs.get("thesis_formation") if isinstance(outputs.get("thesis_formation"), dict) else {}
        route = str(thesis.get("route_recommendation") or "").strip()
        if route in {ACQUISITION_ROUTE, "acquisition", "acquisition_strategy"}:
            return True
        scores = outputs.get("scores") if isinstance(outputs.get("scores"), dict) else {}
        try:
            if float(scores.get("acquisition_score") or 0.0) >= 0.78:
                return True
        except Exception:
            pass
        deal_exit = outputs.get("deal_exit_modeling") if isinstance(outputs.get("deal_exit_modeling"), dict) else {}
        return bool(deal_exit.get("acquisition_fit_rationale") or deal_exit.get("likely_acquirers"))
