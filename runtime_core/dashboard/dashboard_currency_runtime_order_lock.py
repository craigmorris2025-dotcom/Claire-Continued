
"""
Claire v18.90-v18.94 Dashboard Currency + Runtime Output Order Lock.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


PACK_VERSION = "v18.90-v18.94"
NORMAL_SEARCH_ENDPOINT = "/api/dashboard/search/live"
PROVIDER_PROBE_ENDPOINT = "/api/dashboard/search/provider/probe"

PIPELINE_OUTPUT_ORDER = [
    "signal_governance",
    "trend_discovery",
    "thesis_formation",
    "portfolio_intelligence",
    "breakthrough_escalation",
    "advancement_path_selection",
    "autodesign_handoff",
    "design_portal_output",
    "validation_stack",
    "acquisition_package",
    "final_package",
]

DASHBOARD_REQUIRED_SURFACES = [
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
    "system_health",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class DashboardCurrencySurface:
    key: str
    label: str
    required: bool = True
    status: str = "expected"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_runtime_output_order() -> List[Dict[str, Any]]:
    return [
        {
            "index": idx + 1,
            "key": key,
            "locked": True,
            "dashboard_visible": True,
        }
        for idx, key in enumerate(PIPELINE_OUTPUT_ORDER)
    ]


def build_dashboard_currency_state() -> Dict[str, Any]:
    surfaces = [
        DashboardCurrencySurface(key=key, label=key.replace("_", " ").title()).to_dict()
        for key in DASHBOARD_REQUIRED_SURFACES
    ]
    return {
        "pack_version": PACK_VERSION,
        "status": "dashboard_currency_locked",
        "dashboard_must_update_each_pack": True,
        "dashboard_no_change_requires_explicit_report": True,
        "normal_search_endpoint": NORMAL_SEARCH_ENDPOINT,
        "provider_probe_endpoint": PROVIDER_PROBE_ENDPOINT,
        "provider_probe_manual_gated": True,
        "live_connectivity_visible": True,
        "runtime_output_order": build_runtime_output_order(),
        "required_surfaces": surfaces,
        "stage_16_to_22_preserved": {
            "16": "auto_invention_solution_generation",
            "17": "solution_structuring",
            "18": "buildability_assessment",
            "19": "viability_assessment",
            "20": "manufacturability_deployability_assessment",
            "21": "feasibility_validation",
            "22": "design_portal_output_blueprints_specs",
        },
        "updated_at": utc_now(),
    }


def validate_dashboard_currency_state(state: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if state.get("dashboard_must_update_each_pack") is not True:
        errors.append("dashboard must have explicit currency check each pack")
    if state.get("dashboard_no_change_requires_explicit_report") is not True:
        errors.append("no-dashboard-change must be explicitly reported")
    if state.get("normal_search_endpoint") != NORMAL_SEARCH_ENDPOINT:
        errors.append("normal search endpoint must remain /api/dashboard/search/live")
    if state.get("provider_probe_endpoint") == state.get("normal_search_endpoint"):
        errors.append("provider probe must remain separate from normal search")
    if state.get("provider_probe_manual_gated") is not True:
        errors.append("provider probe must remain manual gated")
    if state.get("live_connectivity_visible") is not True:
        errors.append("live connectivity must be visible in dashboard")
    ordered = [row.get("key") for row in state.get("runtime_output_order", [])]
    if ordered != PIPELINE_OUTPUT_ORDER:
        errors.append("runtime output order does not match locked canonical route order")
    surface_keys = {row.get("key") for row in state.get("required_surfaces", [])}
    for key in DASHBOARD_REQUIRED_SURFACES:
        if key not in surface_keys:
            errors.append(f"required dashboard surface missing: {key}")
    preserved = state.get("stage_16_to_22_preserved", {})
    for n in ["16", "17", "18", "19", "20", "21", "22"]:
        if n not in preserved:
            errors.append(f"stage {n} missing from preserved design route block")
    return errors


def build_dashboard_currency_report() -> Dict[str, Any]:
    state = build_dashboard_currency_state()
    errors = validate_dashboard_currency_state(state)
    return {
        "pack_version": PACK_VERSION,
        "pack_name": "Dashboard Currency + Runtime Output Order Lock Pack",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "proofs": {
            "dashboard_currency_required": state["dashboard_must_update_each_pack"] is True,
            "normal_search_visible": state["normal_search_endpoint"] == NORMAL_SEARCH_ENDPOINT,
            "provider_probe_separate": state["provider_probe_endpoint"] != state["normal_search_endpoint"],
            "runtime_output_order_locked": [row["key"] for row in state["runtime_output_order"]] == PIPELINE_OUTPUT_ORDER,
            "stage_16_to_22_preserved": len(state["stage_16_to_22_preserved"]) == 7,
            "required_surfaces_present": len(state["required_surfaces"]) >= len(DASHBOARD_REQUIRED_SURFACES),
        },
        "state": state,
        "updated_at": utc_now(),
    }
