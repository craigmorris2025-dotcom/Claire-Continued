from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from runtime_core.lifecycle.canonical_paths import CANONICAL_ROUTE_PATHS


PROJECT_OWNERS = {
    "source_ingestion": ["runtime_core/api/routes_pipeline.py", "runtime_core/ingestion/live_ingestion_adapter.py"],
    "source_authority": ["runtime_core/orchestrator/pipeline_v4.py", "runtime_core/validation/run_quality_gate.py"],
    "lifecycle_routes": ["runtime_core/lifecycle/canonical_paths.py", "runtime_core/lifecycle/lifecycle_runner.py", "runtime_core/lifecycle/stage_contracts.py"],
    "portfolio": ["runtime_core/portfolio/optimization_engine.py", "runtime_core/portfolio/binder_builder.py"],
    "breakthrough": ["runtime_core/engines/breakthrough_synthesis_engine.py", "runtime_core/design/portal.py"],
    "design": ["runtime_core/design/portal.py", "runtime_core/engines/system_design_engine.py", "runtime_core/technology/technology_intelligence.py"],
    "acquisition": ["runtime_core/engines/acquirer_matching.py", "runtime_core/engines/deal_exit_modeling_engine.py"],
    "package": ["runtime_core/engines/export_package_engine.py", "runtime_core/export/export_writer.py"],
    "memory": ["runtime_core/memory/lifecycle_memory_signal.py", "runtime_core/memory/store.py"],
    "dashboard": ["runtime_core/dashboard/cockpit_dashboard_state.py", "runtime_core/api/routes_operator_dashboard.py", "frontend/command_center/modern/platform_dashboard.js"],
}


DASHBOARD_BINDINGS = {
    "selected_route": "dashboardState.lifecycle.route_selected",
    "canonical_route_path": "dashboardState.system_wiring.routes[*].stage_ids",
    "source_authority": "dashboardState.system_wiring.source_authority",
    "portfolio_records": "dashboardState.records.portfolio",
    "breakthrough_records": "dashboardState.records.breakthroughs",
    "design_records": "dashboardState.records.design",
    "acquirer_records": "dashboardState.records.acquirers",
    "lifecycle_memory": "dashboardState.records.learning + dashboardState.lifecycle_memory_feedback",
}


def build_system_wiring_map(
    root: Path,
    lifecycle: Dict[str, Any] | None = None,
    core_output: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    lifecycle = lifecycle or {}
    core_output = core_output or {}
    source_authority = core_output.get("source_authority") if isinstance(core_output.get("source_authority"), dict) else {}
    route_selected = str(lifecycle.get("route_selected") or core_output.get("route_selected") or "").strip()
    owner_groups = [_owner_group(root, group, paths) for group, paths in PROJECT_OWNERS.items()]
    missing = [
        {"group": group["group"], "path": item["path"]}
        for group in owner_groups
        for item in group["files"]
        if not item["exists"]
    ]
    routes = [
        {
            "route": route,
            "stage_ids": stage_ids,
            "stage_count": len(stage_ids),
            "dashboard_fields": _route_dashboard_fields(route),
            "activation": _route_activation(route),
        }
        for route, stage_ids in CANONICAL_ROUTE_PATHS.items()
    ]
    return {
        "schema_version": "claire.dashboard.system_wiring_map.v1",
        "status": "bound" if not missing else "missing_files",
        "selected_route": route_selected,
        "owner_groups": owner_groups,
        "missing": missing,
        "routes": routes,
        "dashboard_bindings": DASHBOARD_BINDINGS,
        "source_authority": {
            "source_mode": source_authority.get("source_mode"),
            "source_evidence_present": bool(source_authority.get("source_evidence_present")),
            "live_evidence_present": bool(source_authority.get("live_evidence_present")),
            "recursive_memory_source_present": bool(source_authority.get("recursive_memory_source_present")),
            "recursive_memory_stage_1_role": source_authority.get("recursive_memory_stage_1_role"),
            "request_source_keys": source_authority.get("request_source_keys", []),
            "live_source_keys": source_authority.get("live_source_keys", []),
        },
        "proof_rules": [
            "Dashboard route state comes from latest lifecycle/core output.",
            "Breakthrough/design route is activated only by explicit design route or live source-backed breakthrough conditions.",
            "Prior Claire output is Stage 1 context only and cannot promote live truth.",
            "Portfolio remains the default route when branch conditions are not met.",
            "Dashboard route panels are bound only after backend route tests pass.",
        ],
    }


def _owner_group(root: Path, group: str, paths: List[str]) -> Dict[str, Any]:
    files = []
    for rel in paths:
        path = root / rel
        files.append({
            "path": rel,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
        })
    return {
        "group": group,
        "status": "bound" if all(item["exists"] for item in files) else "missing_files",
        "files": files,
    }


def _route_dashboard_fields(route: str) -> List[str]:
    common = ["lifecycle.route_selected", "lifecycle.stages", "lifecycle.decision_context"]
    if route == "portfolio_creation_optimization":
        return [*common, "records.portfolio", "metrics.portfolio_items"]
    if route == "acquisition_package":
        return [*common, "records.acquirers", "records.deals", "metrics.acquirer_matches"]
    if route in {"breakthrough_design", "solution_design", "breakthrough_escalation"}:
        return [*common, "records.breakthroughs", "records.design", "metrics.breakthroughs", "metrics.design_candidates"]
    return common


def _route_activation(route: str) -> str:
    if route == "portfolio_creation_optimization":
        return "default when source-governed trend/thesis is actionable and no stronger branch gate is met"
    if route == "acquisition_package":
        return "strategic acquisition/deal-fit signals meet acquisition route conditions"
    if route == "breakthrough_design":
        return "live source-backed breakthrough and synthesis thresholds meet design activation conditions"
    if route == "solution_design":
        return "explicit design/software/system route is requested and design validation passes"
    if route == "breakthrough_escalation":
        return "breakthrough candidate requires classification and advancement path selection"
    return "route-specific conditions"
