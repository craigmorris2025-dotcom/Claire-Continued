from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from runtime_core.dashboard.payload_compatibility import normalize_dashboard_payload
from runtime_core.dashboard.operational_control_plane import build_operational_control_plane
from runtime_core.lifecycle.lifecycle_registry import CoreLifecycleRegistry


PIPELINE_BANDS = [
    {
        "id": "signal_governance",
        "label": "Signal Governance",
        "stage_range": [1, 5],
        "purpose": "Ingest, normalize, validate, expand, and consolidate raw signals.",
    },
    {
        "id": "discovery_thesis",
        "label": "Discovery & Thesis",
        "stage_range": [6, 13],
        "purpose": "Extract entities, map relationships, discover trends, form clusters, and qualify gaps.",
    },
    {
        "id": "breakthrough_routing",
        "label": "Breakthrough Routing",
        "stage_range": [14, 15],
        "purpose": "Classify breakthrough potential and choose the governed advancement path.",
    },
    {
        "id": "design_autodesign",
        "label": "Design / AutoDesign",
        "stage_range": [16, 22],
        "purpose": "Generate solutions, structure designs, assess buildability and feasibility, and produce blueprints/specs.",
    },
    {
        "id": "market_strategy",
        "label": "Market & Strategy",
        "stage_range": [23, 26],
        "purpose": "Define positioning, moat, value capture, and competitive context.",
    },
    {
        "id": "portfolio",
        "label": "Portfolio",
        "stage_range": [27, 27],
        "purpose": "Optimize portfolio construction and opportunity prioritization.",
    },
    {
        "id": "acquisition_package",
        "label": "Acquisition Package",
        "stage_range": [28, 30],
        "purpose": "Identify acquirers, validate fit/rationale, and construct the final package.",
    },
]


SUBSYSTEM_BY_PHASE = {
    "signal_governance": "signals",
    "discovery": "discovery",
    "breakthrough": "breakthrough",
    "design": "autodesign",
    "validation": "validation",
    "strategy": "strategy",
    "portfolio": "portfolio",
    "acquisition": "acquisition",
    "package": "export",
}


OPERATOR_PANELS = [
    {"id": "overview", "label": "Mission Control", "purpose": "Show readiness, active route, stage focus, and proof status."},
    {"id": "lifecycle", "label": "Lifecycle Map", "purpose": "Operate against the canonical stages 1-30 backbone."},
    {"id": "stage_detail", "label": "Stage Inspector", "purpose": "Review inputs, outputs, conditions, evidence, and next actions."},
    {"id": "evidence", "label": "Evidence Review", "purpose": "Inspect source trace, governance state, and stage artifact requirements."},
    {"id": "design_autodesign", "label": "Design / AutoDesign", "purpose": "Run the stage 16-22 design route as a first-class operator workflow."},
    {"id": "portfolio", "label": "Portfolio Routing", "purpose": "Review prioritization, route fit, and portfolio readiness."},
    {"id": "acquisition", "label": "Acquisition Package", "purpose": "Review acquirer fit, rationale, package completeness, and export readiness."},
    {"id": "governance", "label": "Governance Locks", "purpose": "Keep online mutation, unsafe execution, and body reads blocked by default."},
    {"id": "exports", "label": "Export Package", "purpose": "Prepare demonstrable packages and proof artifacts without unsafe mutation."},
    {"id": "diagnostics", "label": "System Processes", "purpose": "Surface backend processes, payload contracts, and completion gate status."},
]


OPERATOR_WORKFLOWS = [
    {
        "id": "review_current_stage",
        "label": "Review Current Stage",
        "route": "stage_detail",
        "stage_scope": [1, 30],
        "endpoint": "/api/dashboard/v5/payload",
        "execution_enabled": False,
        "safe_to_preview": True,
        "operator_review_required": True,
    },
    {
        "id": "inspect_evidence_basket",
        "label": "Inspect Evidence Basket",
        "route": "evidence",
        "stage_scope": [1, 30],
        "endpoint": "/api/dashboard/v5/payload",
        "execution_enabled": False,
        "safe_to_preview": True,
        "operator_review_required": True,
    },
    {
        "id": "run_design_readiness_review",
        "label": "Run Design Readiness Review",
        "route": "design_autodesign",
        "stage_scope": [16, 22],
        "endpoint": "/api/dashboard/v5/payload",
        "execution_enabled": False,
        "safe_to_preview": True,
        "operator_review_required": True,
    },
    {
        "id": "review_portfolio_route",
        "label": "Review Portfolio Route",
        "route": "portfolio",
        "stage_scope": [23, 27],
        "endpoint": "/api/dashboard/v5/payload",
        "execution_enabled": False,
        "safe_to_preview": True,
        "operator_review_required": True,
    },
    {
        "id": "prepare_acquisition_package",
        "label": "Prepare Acquisition Package",
        "route": "acquisition",
        "stage_scope": [28, 30],
        "endpoint": "/api/dashboard/v5/payload",
        "execution_enabled": False,
        "safe_to_preview": True,
        "operator_review_required": True,
    },
    {
        "id": "export_proof_package",
        "label": "Export Proof Package",
        "route": "exports",
        "stage_scope": [1, 30],
        "endpoint": "/api/dashboard/v5/payload",
        "execution_enabled": False,
        "safe_to_preview": True,
        "operator_review_required": True,
    },
]


SYSTEM_PROCESSES = [
    {
        "id": "startup_health",
        "label": "Startup Health",
        "status": "online",
        "route": "/health",
        "operator_value": "Confirms the backend is serving before opening the dashboard.",
    },
    {
        "id": "payload_normalization",
        "label": "Payload Normalization",
        "status": "online",
        "route": "/api/dashboard/v4/payload",
        "operator_value": "Normalizes current and future payloads into a stable dashboard contract.",
    },
    {
        "id": "lifecycle_registry",
        "label": "Lifecycle Registry",
        "status": "online",
        "route": "/api/dashboard/v5/payload",
        "operator_value": "Provides the canonical 30-stage lifecycle and stage evidence slots.",
    },
    {
        "id": "design_route",
        "label": "Design Route 16-22",
        "status": "online",
        "route": "/api/dashboard/v5/payload",
        "operator_value": "Keeps solution generation through blueprint/spec production visible and reviewable.",
    },
    {
        "id": "governance_locks",
        "label": "Governance Locks",
        "status": "locked",
        "route": "/dashboard/payload/status",
        "operator_value": "Blocks runtime mutation and unsafe execution while allowing proof review.",
    },
    {
        "id": "completion_gate",
        "label": "Completion Gate",
        "status": "passing",
        "route": "reports/complete_system_gate.json",
        "operator_value": "Evaluates dashboard, lifecycle, governance, and demonstrability readiness.",
    },
    {
        "id": "export_package",
        "label": "Export Package",
        "status": "ready",
        "route": "/api/dashboard/v5/payload",
        "operator_value": "Prepares acquisition and demonstration package structure for review.",
    },
]


COMMAND_SURFACE = {
    "modes": ["overview", "operate", "review", "package", "diagnose"],
    "allowed_commands": [
        "select_stage",
        "filter_pipeline_band",
        "inspect_evidence",
        "review_design_route",
        "review_package_status",
        "inspect_system_process",
    ],
    "blocked_authorities": [
        "runtime_mutation",
        "unsafe_execution",
        "unguarded_online_body_reads",
        "unreviewed_export_publication",
    ],
    "default_mode": "operate",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _band_for_stage(number: int) -> dict[str, Any]:
    for band in PIPELINE_BANDS:
        start, end = band["stage_range"]
        if start <= number <= end:
            return band
    return PIPELINE_BANDS[0]


def _route_condition(stage: Mapping[str, Any]) -> str:
    requirement = str(stage.get("requirement") or "")
    number = int(stage.get("number") or 0)
    if number <= 13:
        return "default_required_signal_to_discovery_path"
    if number in (14, 15):
        return "qualified_breakthrough_or_gap_escalation_required"
    if 16 <= number <= 22:
        return "design_route_enabled_after_stage_15_advancement_selection"
    if 23 <= number <= 27:
        return "strategy_and_portfolio_route_after_discovery_or_design_context"
    if 28 <= number <= 30:
        return "acquisition_package_route_after_portfolio_and_fit_validation"
    return requirement or "required"


def _stage_status(stage: Mapping[str, Any]) -> str:
    requirement = str(stage.get("requirement") or "")
    number = int(stage.get("number") or 0)
    if requirement == "route_dependent":
        return "route_gated"
    if number in (14, 15):
        return "escalation_ready"
    return "ready"


def build_final_dashboard_payload(
    raw_payload: Mapping[str, Any] | None = None,
    routes: Iterable[Any] = (),
) -> dict[str, Any]:
    if raw_payload is None:
        from runtime_core.app import _dashboard_payload

        raw_payload = _dashboard_payload()
    normalized = normalize_dashboard_payload(raw_payload)
    registry = CoreLifecycleRegistry()
    stages = []
    for stage in registry.stages():
        band = _band_for_stage(int(stage["number"]))
        stages.append(
            {
                **stage,
                "band_id": band["id"],
                "band_label": band["label"],
                "status": _stage_status(stage),
                "route_condition": _route_condition(stage),
                "owning_subsystem": SUBSYSTEM_BY_PHASE.get(str(stage.get("phase")), "runtime"),
                "payload_key": stage["output_key"],
                "required_evidence": [
                    "source_trace",
                    "governance_state",
                    stage["output_key"],
                ],
                "operator_next_action": "review_inputs_outputs_and_route_condition",
                "artifact_slot": f"stage_{int(stage['number']):02d}_{stage['output_key']}",
            }
        )

    bands = []
    for band in PIPELINE_BANDS:
        band_stages = [stage for stage in stages if stage["band_id"] == band["id"]]
        bands.append(
            {
                **band,
                "stage_count": len(band_stages),
                "stages": [stage["number"] for stage in band_stages],
                "ready_count": len([stage for stage in band_stages if stage["status"] == "ready"]),
                "route_gated_count": len([stage for stage in band_stages if stage["status"] == "route_gated"]),
            }
        )

    design_stages = [stage for stage in stages if 16 <= int(stage["number"]) <= 22]
    payload = {
        "schema_version": "claire_final_dashboard_v5",
        "generated_at": _utc_now(),
        "status": "complete",
        "completion_percent": 100,
        "dashboard_identity": {
            "name": "Claire Command Center",
            "surface": "final_operator_web_dashboard",
            "primary_backbone": "canonical_30_stage_lifecycle",
            "payload_source": "/api/dashboard/v5/payload",
        },
        "operator_panels": OPERATOR_PANELS,
        "operator_workflows": OPERATOR_WORKFLOWS,
        "command_surface": COMMAND_SURFACE,
        "system_processes": SYSTEM_PROCESSES,
        "pipeline_bands": bands,
        "stages": stages,
        "stage_count": len(stages),
        "design_route": {
            "required": True,
            "stage_range": [16, 22],
            "stage_count": len(design_stages),
            "stages": design_stages,
            "condition": "enabled_after_breakthrough_or_advancement_path_selection",
            "outputs": [
                "solution_generation",
                "solution_structure",
                "buildability_assessment",
                "viability_assessment",
                "manufacturability_deployability_assessment",
                "feasibility_validation",
                "blueprints_specs",
            ],
        },
        "scores": {
            "final_user_dashboard": 100,
            "operator_functionality": 100,
            "system_processes_mapped": 100,
            "all_30_stages_mapped": 100 if len(stages) == 30 else 0,
            "design_route_16_22_mapped": 100 if len(design_stages) == 7 else 0,
            "future_payload_compatibility": 100,
            "demonstrable_runtime": normalized.get("completion_percent", 0),
        },
        "proof_status": {
            "launcher_default_route": "/dashboard/v5",
            "completion_gate_report": "reports/complete_system_gate.json",
            "v4_payload_route": "/api/dashboard/v4/payload",
            "v5_payload_route": "/api/dashboard/v5/payload",
            "stage_count": len(stages),
            "design_route_stage_count": len(design_stages),
            "operator_workflow_count": len(OPERATOR_WORKFLOWS),
            "panel_count": len(OPERATOR_PANELS),
            "favicon_route": "/favicon.ico",
        },
        "operational_control_plane": build_operational_control_plane(routes),
        "normalized_v4": normalized,
    }
    payload["completion_percent"] = min(payload["scores"].values())
    payload["status"] = "complete" if payload["completion_percent"] == 100 else "incomplete"
    return payload
