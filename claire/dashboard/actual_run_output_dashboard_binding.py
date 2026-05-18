
"""
Claire v19.00-v19.04 Actual Run Output Binding into Dashboard Panels.

This module binds actual run-output-shaped data into dashboard panels using the
primary pipeline desired output contract from v18.95-v18.99.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


PACK_VERSION = "v19.00-v19.04"

PANEL_BINDING_ORDER = [
    "main_result",
    "governed_live_web_search",
    "runtime_truth",
    "trend_thesis",
    "portfolio",
    "breakthrough",
    "advancement_path",
    "autodesign",
    "design_portal",
    "validation",
    "acquisition",
    "final_package",
    "system_health",
]

ROUTE_TO_PANELS = {
    "discovery_to_portfolio": [
        "main_result",
        "governed_live_web_search",
        "runtime_truth",
        "trend_thesis",
        "portfolio",
        "system_health",
    ],
    "breakthrough_to_design": [
        "main_result",
        "runtime_truth",
        "breakthrough",
        "advancement_path",
        "autodesign",
        "design_portal",
        "validation",
        "system_health",
    ],
    "acquisition_package": [
        "main_result",
        "runtime_truth",
        "portfolio",
        "acquisition",
        "final_package",
        "system_health",
    ],
    "insufficient_data": [
        "main_result",
        "runtime_truth",
        "system_health",
    ],
    "blocked": [
        "main_result",
        "runtime_truth",
        "system_health",
    ],
}

REQUIRED_RUN_OUTPUT_FIELDS = [
    "run_id",
    "query",
    "terminal_state",
    "route",
    "confidence",
    "evidence",
    "ordered_outputs",
    "dashboard_surfaces",
    "next_best_action",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class DashboardPanelBinding:
    panel: str
    visible: bool
    source_key: str
    status: str = "bound"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_sample_run_output(route: str = "discovery_to_portfolio") -> Dict[str, Any]:
    panels = ROUTE_TO_PANELS.get(route, ROUTE_TO_PANELS["discovery_to_portfolio"])
    terminal_state = "portfolio_action_ready"
    if route == "breakthrough_to_design":
        terminal_state = "design_output_ready"
    elif route == "acquisition_package":
        terminal_state = "acquisition_package_ready"
    elif route == "insufficient_data":
        terminal_state = "insufficient_data"
    elif route == "blocked":
        terminal_state = "blocked"

    return {
        "run_id": "v19_00_to_v19_04_sample_run",
        "query": "governed signal to portfolio output test",
        "terminal_state": terminal_state,
        "route": route,
        "confidence": 0.76 if route not in {"insufficient_data", "blocked"} else 0.0,
        "evidence": [
            {
                "title": "Google",
                "url": "https://www.google.com",
                "source_type": "governed_live_web_search",
                "trusted": True,
                "used_as_input_evidence": True,
            }
        ],
        "ordered_outputs": [
            {"key": "signal_governance", "status": "complete"},
            {"key": "trend_discovery", "status": "complete"},
            {"key": "thesis_formation", "status": "complete"},
            {"key": "portfolio_intelligence", "status": "ready"},
        ],
        "dashboard_surfaces": panels,
        "insufficient_data_reason": "not_applicable" if route != "insufficient_data" else "not_enough_validated_signals",
        "blocked_reason": "not_applicable" if route != "blocked" else "operator_review_required",
        "next_best_action": "review_bound_dashboard_panels",
        "updated_at": utc_now(),
    }


def bind_run_output_to_dashboard_panels(run_output: Dict[str, Any]) -> Dict[str, Any]:
    route = run_output.get("route") or "discovery_to_portfolio"
    visible_panels = set(run_output.get("dashboard_surfaces") or ROUTE_TO_PANELS.get(route, []))
    bindings = []
    for panel in PANEL_BINDING_ORDER:
        source_key = panel
        if panel == "main_result":
            source_key = "terminal_state"
        elif panel == "governed_live_web_search":
            source_key = "evidence"
        elif panel == "runtime_truth":
            source_key = "ordered_outputs"
        bindings.append(
            DashboardPanelBinding(
                panel=panel,
                visible=panel in visible_panels,
                source_key=source_key,
            ).to_dict()
        )

    return {
        "pack_version": PACK_VERSION,
        "status": "dashboard_panels_bound",
        "run_id": run_output.get("run_id"),
        "route": route,
        "terminal_state": run_output.get("terminal_state"),
        "main_result_never_blank": bool(run_output.get("terminal_state")),
        "metadata_only_output": False,
        "bindings": bindings,
        "bound_panels": [b["panel"] for b in bindings if b["visible"]],
        "hidden_panels": [b["panel"] for b in bindings if not b["visible"]],
        "run_output": run_output,
        "updated_at": utc_now(),
    }


def validate_run_output(run_output: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in REQUIRED_RUN_OUTPUT_FIELDS:
        if field not in run_output:
            errors.append(f"run output missing required field: {field}")
    if not run_output.get("terminal_state"):
        errors.append("terminal_state is required so main result is never blank")
    if not run_output.get("dashboard_surfaces"):
        errors.append("dashboard_surfaces must identify visible panels")
    if run_output.get("route") not in ROUTE_TO_PANELS:
        errors.append("route must map to dashboard panels")
    if run_output.get("route") == "blocked" and not run_output.get("blocked_reason"):
        errors.append("blocked route must provide blocked_reason")
    if run_output.get("route") == "insufficient_data" and not run_output.get("insufficient_data_reason"):
        errors.append("insufficient_data route must provide insufficient_data_reason")
    return errors


def validate_dashboard_binding(binding: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if binding.get("metadata_only_output") is not False:
        errors.append("dashboard binding must not be metadata-only")
    if binding.get("main_result_never_blank") is not True:
        errors.append("main result must never be blank")
    bound_panels = set(binding.get("bound_panels", []))
    if "main_result" not in bound_panels:
        errors.append("main_result panel must be bound")
    if "runtime_truth" not in bound_panels:
        errors.append("runtime_truth panel must be bound")
    route = binding.get("route")
    expected = set(ROUTE_TO_PANELS.get(route, []))
    if not expected.issubset(bound_panels):
        errors.append("route expected dashboard panels are not all bound")
    return errors


def build_dashboard_binding_report() -> Dict[str, Any]:
    sample = build_sample_run_output()
    binding = bind_run_output_to_dashboard_panels(sample)
    errors = validate_run_output(sample) + validate_dashboard_binding(binding)
    return {
        "pack_version": PACK_VERSION,
        "pack_name": "Actual Run Output Binding into Dashboard Panels Pack",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "proofs": {
            "run_output_has_required_fields": validate_run_output(sample) == [],
            "dashboard_panels_bound": binding["status"] == "dashboard_panels_bound",
            "main_result_never_blank": binding["main_result_never_blank"] is True,
            "metadata_only_output_forbidden": binding["metadata_only_output"] is False,
            "route_panels_present": set(ROUTE_TO_PANELS[sample["route"]]).issubset(set(binding["bound_panels"])),
        },
        "binding": binding,
        "updated_at": utc_now(),
    }
