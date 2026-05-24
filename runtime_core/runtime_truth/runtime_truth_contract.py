from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_VERSION = "v17.59"
VALID_STAGE_STATUSES = {"pending", "running", "completed", "skipped_by_route", "blocked", "failed", "not_applicable"}
SUCCESS_TERMINALS = {"portfolio_action_ready", "portfolio_optimization_ready", "discovery_ready", "breakthrough_classified", "advancement_path_selected", "design_output_ready", "acquisition_ready", "final_package_ready"}
FAILURE_TERMINALS = {"insufficient_data", "blocked", "failed", "max_iterations_reached"}
FINAL_TERMINALS = SUCCESS_TERMINALS | FAILURE_TERMINALS

LIFECYCLE_STAGES: List[Dict[str, Any]] = [{'number': 1, 'id': 'stage_01', 'name': 'Signal Ingestion', 'domain': 'governance', 'purpose': 'Capture raw signals from approved live/local sources.', 'critical_design_stage': False}, {'number': 2, 'id': 'stage_02', 'name': 'Signal Normalization', 'domain': 'governance', 'purpose': 'Normalize incoming signals into a consistent runtime format.', 'critical_design_stage': False}, {'number': 3, 'id': 'stage_03', 'name': 'Source Validation & Weighting', 'domain': 'governance', 'purpose': 'Validate source quality, freshness, trust weight, and usefulness.', 'critical_design_stage': False}, {'number': 4, 'id': 'stage_04', 'name': 'Context Expansion', 'domain': 'governance', 'purpose': 'Expand signal context using related sources, entities, and prior verified outputs.', 'critical_design_stage': False}, {'number': 5, 'id': 'stage_05', 'name': 'Signal Consolidation', 'domain': 'governance', 'purpose': 'Consolidate duplicate/conflicting signals into governed evidence baskets.', 'critical_design_stage': False}, {'number': 6, 'id': 'stage_06', 'name': 'Entity Extraction', 'domain': 'entity', 'purpose': 'Extract organizations, technologies, markets, people, assets, risks, and constraints.', 'critical_design_stage': False}, {'number': 7, 'id': 'stage_07', 'name': 'Relationship Mapping', 'domain': 'entity', 'purpose': 'Map relationships among entities, evidence, opportunities, constraints, and routes.', 'critical_design_stage': False}, {'number': 8, 'id': 'stage_08', 'name': 'Trend Discovery', 'domain': 'trend', 'purpose': 'Detect emerging trends, weak signals, clusters, anomalies, and market movement.', 'critical_design_stage': False}, {'number': 9, 'id': 'stage_09', 'name': 'Cluster Formation', 'domain': 'trend', 'purpose': 'Form durable clusters from related signals, entities, and evidence.', 'critical_design_stage': False}, {'number': 10, 'id': 'stage_10', 'name': 'Insight / Thesis Structuring + Route Gate', 'domain': 'route_gate', 'purpose': 'Structure the thesis and select the route or terminal failure state.', 'critical_design_stage': False}, {'number': 11, 'id': 'stage_11', 'name': 'Gap Detection', 'domain': 'breakthrough', 'purpose': 'Identify market, technical, operational, portfolio, regulatory, or system gaps.', 'critical_design_stage': False}, {'number': 12, 'id': 'stage_12', 'name': 'Gap Qualification', 'domain': 'breakthrough', 'purpose': 'Determine whether the gap is meaningful, material, and route-worthy.', 'critical_design_stage': False}, {'number': 13, 'id': 'stage_13', 'name': 'Discovery Generation', 'domain': 'breakthrough', 'purpose': 'Generate a qualified discovery from the gap/evidence structure.', 'critical_design_stage': False}, {'number': 14, 'id': 'stage_14', 'name': 'Breakthrough Identification / Classification', 'domain': 'breakthrough', 'purpose': 'Classify whether the discovery is a qualified breakthrough.', 'critical_design_stage': False}, {'number': 15, 'id': 'stage_15', 'name': 'Advancement Path Selection', 'domain': 'breakthrough', 'purpose': 'Select the correct advancement path: portfolio, design, system, acquisition, or other.', 'critical_design_stage': False}, {'number': 16, 'id': 'stage_16', 'name': 'Auto Invention / Solution Generation', 'domain': 'autodesign', 'purpose': 'Generate candidate solution concepts under governed constraints.', 'critical_design_stage': True}, {'number': 17, 'id': 'stage_17', 'name': 'Solution Structuring', 'domain': 'autodesign', 'purpose': 'Structure the selected solution into components, dependencies, and specifications.', 'critical_design_stage': True}, {'number': 18, 'id': 'stage_18', 'name': 'Buildability Assessment', 'domain': 'autodesign', 'purpose': 'Assess engineering, software, operational, or construction buildability.', 'critical_design_stage': True}, {'number': 19, 'id': 'stage_19', 'name': 'Viability Assessment', 'domain': 'autodesign', 'purpose': 'Assess market, economic, revenue, adoption, and strategic viability.', 'critical_design_stage': True}, {'number': 20, 'id': 'stage_20', 'name': 'Manufacturability / Deployability Assessment', 'domain': 'autodesign', 'purpose': 'Assess production, deployment, scaling, integration, and operations readiness.', 'critical_design_stage': True}, {'number': 21, 'id': 'stage_21', 'name': 'Feasibility Validation', 'domain': 'autodesign', 'purpose': 'Validate feasibility across buildability, viability, deployment, risk, and evidence.', 'critical_design_stage': True}, {'number': 22, 'id': 'stage_22', 'name': 'Design Portal Output / Blueprints / Specs', 'domain': 'autodesign', 'purpose': 'Produce blueprint, spec, architecture, component map, and design portal output.', 'critical_design_stage': True}, {'number': 23, 'id': 'stage_23', 'name': 'Market Positioning', 'domain': 'strategy', 'purpose': 'Position the thesis, product, portfolio, system, or package in the market.', 'critical_design_stage': False}, {'number': 24, 'id': 'stage_24', 'name': 'Moat & Differentiation', 'domain': 'strategy', 'purpose': 'Analyze defensibility, differentiation, uniqueness, and compounding advantage.', 'critical_design_stage': False}, {'number': 25, 'id': 'stage_25', 'name': 'Business Model & Value Capture', 'domain': 'strategy', 'purpose': 'Define business model, monetization, distribution, and value capture.', 'critical_design_stage': False}, {'number': 26, 'id': 'stage_26', 'name': 'Competitor Analysis', 'domain': 'strategy', 'purpose': 'Assess competitors, substitutes, comparative weaknesses, and opportunity wedges.', 'critical_design_stage': False}, {'number': 27, 'id': 'stage_27', 'name': 'Portfolio Creation / Optimization', 'domain': 'portfolio', 'purpose': 'Create or optimize the portfolio action, allocation, watchlist, or thesis basket.', 'critical_design_stage': False}, {'number': 28, 'id': 'stage_28', 'name': 'Acquirer Identification', 'domain': 'acquisition', 'purpose': 'Identify likely acquirers, strategic buyers, partners, or enterprise owners.', 'critical_design_stage': False}, {'number': 29, 'id': 'stage_29', 'name': 'Acquisition Fit & Rationale', 'domain': 'acquisition', 'purpose': 'Explain fit, synergies, integration logic, and acquisition rationale.', 'critical_design_stage': False}, {'number': 30, 'id': 'stage_30', 'name': 'Final Package Construction', 'domain': 'package', 'purpose': 'Construct the final package, export, memo, design pack, or acquisition-ready output.', 'critical_design_stage': False}]

PORTFOLIO_STAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 23, 26, 27, 30]
BREAKTHROUGH_ESCALATION_STAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 23, 24, 25, 26, 27, 30]
BREAKTHROUGH_DESIGN_STAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30]
ACQUISITION_STAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 23, 24, 25, 26, 28, 29, 30]

ROUTE_REQUIRED_STAGES: Dict[str, List[int]] = {
    "portfolio_creation_optimization": PORTFOLIO_STAGES,
    "breakthrough_escalation": BREAKTHROUGH_ESCALATION_STAGES,
    "breakthrough_design": BREAKTHROUGH_DESIGN_STAGES,
    "solution_design": BREAKTHROUGH_DESIGN_STAGES,
    "acquisition_package": ACQUISITION_STAGES,
    "portfolio": PORTFOLIO_STAGES,
    "breakthrough": BREAKTHROUGH_ESCALATION_STAGES,
    "design": BREAKTHROUGH_DESIGN_STAGES,
    "autodesign": BREAKTHROUGH_DESIGN_STAGES,
    "acquisition": ACQUISITION_STAGES,
    "discovery": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 30],
    "insufficient_data": [1, 2, 3, 4, 5, 10],
}

ROUTE_TERMINALS: Dict[str, set[str]] = {
    "portfolio_creation_optimization": {"portfolio_action_ready", "portfolio_optimization_ready", "final_package_ready"},
    "breakthrough_escalation": {"breakthrough_classified", "advancement_path_selected", "final_package_ready"},
    "breakthrough_design": {"design_output_ready", "final_package_ready"},
    "solution_design": {"design_output_ready", "final_package_ready"},
    "acquisition_package": {"acquisition_ready", "final_package_ready"},
    "portfolio": {"portfolio_action_ready", "portfolio_optimization_ready", "final_package_ready"},
    "breakthrough": {"breakthrough_classified", "advancement_path_selected", "final_package_ready", "design_output_ready"},
    "design": {"design_output_ready", "final_package_ready"},
    "autodesign": {"design_output_ready", "final_package_ready"},
    "acquisition": {"acquisition_ready", "final_package_ready"},
    "discovery": {"discovery_ready", "breakthrough_classified", "final_package_ready"},
    "insufficient_data": {"insufficient_data"},
}

ROUTE_ALIASES = {
    "portfolio_only": "portfolio_creation_optimization",
    "portfolio": "portfolio_creation_optimization",
    "portfolio_intelligence": "portfolio_creation_optimization",
    "portfolio_candidate": "portfolio_creation_optimization",
    "portfolio_optimization": "portfolio_creation_optimization",
    "market": "portfolio_creation_optimization",
    "breakthrough": "breakthrough_escalation",
    "breakthrough_system_transformation": "breakthrough_design",
    "breakthrough_escalation_candidate": "breakthrough_escalation",
    "design": "breakthrough_design",
    "auto_design": "breakthrough_design",
    "auto-design": "breakthrough_design",
    "autodesign": "breakthrough_design",
    "design_portal": "breakthrough_design",
    "system_design": "solution_design",
    "technology_design": "breakthrough_design",
    "acquisition": "acquisition_package",
    "acquisition_intelligence": "acquisition_package",
    "package": "acquisition_package",
    "final_package": "acquisition_package",
    "no_data": "insufficient_data",
    "insufficient": "insufficient_data",
}


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_key(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text


def normalize_route(value: Any) -> str:
    key = normalize_key(value)
    if not key:
        return ""
    return ROUTE_ALIASES.get(key, key)


def normalize_stage_status(value: Any, default: str = "pending") -> str:
    key = normalize_key(value)
    aliases = {
        "done": "completed",
        "complete": "completed",
        "success": "completed",
        "succeeded": "completed",
        "ok": "completed",
        "pass": "completed",
        "passed": "completed",
        "skip": "skipped_by_route",
        "skipped": "skipped_by_route",
        "skipped_route": "skipped_by_route",
        "not_applicable": "not_applicable",
        "na": "not_applicable",
        "n_a": "not_applicable",
        "not_started": "pending",
        "waiting": "pending",
        "missing": "pending",
        "error": "failed",
        "failure": "failed",
        "blocked_error": "blocked",
    }
    status = aliases.get(key, key or default)
    return status if status in VALID_STAGE_STATUSES else default


def normalize_terminal(value: Any) -> str:
    key = normalize_key(value)
    aliases = {
        "ok": "final_package_ready",
        "success": "final_package_ready",
        "completed": "final_package_ready",
        "complete": "final_package_ready",
        "portfolio_ready": "portfolio_action_ready",
        "breakthrough_ready": "breakthrough_classified",
        "design_ready": "design_output_ready",
        "acquisition_fit_ready": "acquisition_ready",
        "no_data": "insufficient_data",
        "insufficient": "insufficient_data",
        "error": "failed",
    }
    return aliases.get(key, key)


def coerce_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def dig(data: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        current: Any = data
        ok = True
        for part in key.split("."):
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                ok = False
                break
        if ok and current is not None:
            return current
    return default


def first_present(data: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        value = dig(data, key, default=None)
        if value is not None and value != "":
            return value
    return default


def stage_name(number: int) -> str:
    for stage in LIFECYCLE_STAGES:
        if stage["number"] == number:
            return stage["name"]
    return f"Stage {number}"


def stage_domain(number: int) -> str:
    for stage in LIFECYCLE_STAGES:
        if stage["number"] == number:
            return stage.get("domain", "unknown")
    return "unknown"
