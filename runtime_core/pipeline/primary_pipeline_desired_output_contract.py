
"""
Claire v18.95-v18.99 Primary Pipeline Connection + Desired Output Contract.

This module locks Claire's primary-purpose pipeline contract:
Signal -> Trend -> Thesis -> Portfolio/Breakthrough -> Advancement Path ->
AutoDesign -> Design Portal -> Validation -> Acquisition/Final Package.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


PACK_VERSION = "v18.95-v18.99"

PRIMARY_PIPELINE_ORDER = [
    "signal_ingestion",
    "signal_governance",
    "trend_discovery",
    "thesis_formation",
    "portfolio_intelligence",
    "breakthrough_escalation",
    "advancement_path_selection",
    "autodesign_handoff",
    "design_portal_output",
    "validation_stack",
    "acquisition_readiness",
    "final_package",
]

TERMINAL_STATES = [
    "trend_thesis_ready",
    "portfolio_action_ready",
    "portfolio_optimization_ready",
    "discovery_ready",
    "breakthrough_classified",
    "advancement_path_selected",
    "design_output_ready",
    "acquisition_package_ready",
    "final_package_ready",
    "insufficient_data",
    "blocked",
    "failed",
    "max_iterations_reached",
]

ROUTE_SURFACES = {
    "trend_thesis_ready": ["main_result", "trend_thesis", "runtime_truth"],
    "portfolio_action_ready": ["main_result", "portfolio", "runtime_truth"],
    "breakthrough_classified": ["main_result", "breakthrough", "advancement_path", "runtime_truth"],
    "design_output_ready": ["main_result", "autodesign", "design_portal", "validation", "runtime_truth"],
    "acquisition_package_ready": ["main_result", "acquisition", "final_package", "runtime_truth"],
    "insufficient_data": ["main_result", "system_health", "runtime_truth"],
    "blocked": ["main_result", "system_health", "runtime_truth"],
}

DESIRED_OUTPUT_FIELDS = [
    "run_id",
    "query",
    "terminal_state",
    "route",
    "confidence",
    "evidence",
    "ordered_outputs",
    "dashboard_surfaces",
    "insufficient_data_reason",
    "blocked_reason",
    "next_best_action",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class PipelineOutputStep:
    index: int
    key: str
    required: bool = True
    dashboard_visible: bool = True
    output_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_primary_pipeline_order() -> List[Dict[str, Any]]:
    return [
        PipelineOutputStep(index=i + 1, key=key).to_dict()
        for i, key in enumerate(PRIMARY_PIPELINE_ORDER)
    ]


def build_desired_output_contract(route: str = "discovery_to_portfolio") -> Dict[str, Any]:
    terminal_state = "portfolio_action_ready"
    surfaces = ROUTE_SURFACES[terminal_state]
    ordered_outputs = build_primary_pipeline_order()
    return {
        "pack_version": PACK_VERSION,
        "contract_name": "primary_pipeline_desired_output_contract",
        "primary_purpose": "governed_discovery_breakthrough_portfolio_autodesign_acquisition_readiness",
        "route": route,
        "terminal_state": terminal_state,
        "terminal_states_allowed": TERMINAL_STATES,
        "ordered_outputs": ordered_outputs,
        "desired_output_fields": DESIRED_OUTPUT_FIELDS,
        "dashboard_surfaces": surfaces,
        "must_not_stop_at_metadata": True,
        "must_emit_user_facing_main_result": True,
        "must_preserve_route_awareness": True,
        "web_search_is_input_capability_not_primary_output": True,
        "stage_16_to_22_design_route_required": True,
        "updated_at": utc_now(),
    }


def build_sample_primary_pipeline_result(query: str = "google signal test") -> Dict[str, Any]:
    contract = build_desired_output_contract()
    return {
        "run_id": "v18_95_to_v18_99_sample_run",
        "query": query,
        "terminal_state": contract["terminal_state"],
        "route": contract["route"],
        "confidence": 0.72,
        "evidence": [
            {
                "title": "Google",
                "url": "https://www.google.com",
                "source_type": "governed_live_web_search",
                "trusted": True,
            }
        ],
        "ordered_outputs": contract["ordered_outputs"],
        "dashboard_surfaces": contract["dashboard_surfaces"],
        "insufficient_data_reason": None,
        "blocked_reason": None,
        "next_best_action": "review_portfolio_action_ready_output",
        "updated_at": utc_now(),
    }


def validate_primary_pipeline_contract(contract: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    ordered = [row.get("key") for row in contract.get("ordered_outputs", [])]
    if ordered != PRIMARY_PIPELINE_ORDER:
        errors.append("primary pipeline output order is not locked")
    if contract.get("must_not_stop_at_metadata") is not True:
        errors.append("pipeline must not stop at metadata")
    if contract.get("must_emit_user_facing_main_result") is not True:
        errors.append("pipeline must emit user-facing main result")
    if contract.get("must_preserve_route_awareness") is not True:
        errors.append("pipeline must preserve route awareness")
    if contract.get("web_search_is_input_capability_not_primary_output") is not True:
        errors.append("web search must remain an input capability, not the primary output")
    if contract.get("stage_16_to_22_design_route_required") is not True:
        errors.append("stage 16-22 design route must remain required")
    for field in DESIRED_OUTPUT_FIELDS:
        if field not in contract.get("desired_output_fields", []):
            errors.append(f"desired output field missing from contract: {field}")
    if "main_result" not in contract.get("dashboard_surfaces", []):
        errors.append("main_result dashboard surface is required")
    return errors


def validate_sample_primary_pipeline_result(result: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in DESIRED_OUTPUT_FIELDS:
        if field not in result:
            errors.append(f"sample result missing desired field: {field}")
    ordered = [row.get("key") for row in result.get("ordered_outputs", [])]
    if ordered != PRIMARY_PIPELINE_ORDER:
        errors.append("sample result output order does not match canonical primary pipeline order")
    if result.get("terminal_state") not in TERMINAL_STATES:
        errors.append("sample result terminal_state is not allowed")
    if "main_result" not in result.get("dashboard_surfaces", []):
        errors.append("sample result must target main_result dashboard surface")
    if result.get("blocked_reason") is not None and result.get("terminal_state") != "blocked":
        errors.append("blocked_reason should only be populated for blocked terminal state")
    return errors


def build_primary_pipeline_report() -> Dict[str, Any]:
    contract = build_desired_output_contract()
    sample = build_sample_primary_pipeline_result()
    errors = validate_primary_pipeline_contract(contract) + validate_sample_primary_pipeline_result(sample)
    return {
        "pack_version": PACK_VERSION,
        "pack_name": "Primary Pipeline Connection + Desired Output Contract Pack",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "proofs": {
            "primary_pipeline_order_locked": [row["key"] for row in contract["ordered_outputs"]] == PRIMARY_PIPELINE_ORDER,
            "desired_output_contract_present": bool(contract["desired_output_fields"]),
            "metadata_only_output_forbidden": contract["must_not_stop_at_metadata"] is True,
            "main_result_required": contract["must_emit_user_facing_main_result"] is True,
            "route_awareness_required": contract["must_preserve_route_awareness"] is True,
            "web_search_is_input_capability": contract["web_search_is_input_capability_not_primary_output"] is True,
            "stage_16_to_22_required": contract["stage_16_to_22_design_route_required"] is True,
        },
        "contract": contract,
        "sample_result": sample,
        "updated_at": utc_now(),
    }
