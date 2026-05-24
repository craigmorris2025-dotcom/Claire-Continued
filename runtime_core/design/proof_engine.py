from __future__ import annotations

from typing import Any, Dict, List


def _score(value: Any, fallback: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return fallback


def _components(solution: Dict[str, Any], existing_system_replacement: Dict[str, Any]) -> List[str]:
    values: List[str] = []
    for item in solution.get("components", []) if isinstance(solution.get("components"), list) else []:
        if item and str(item) not in values:
            values.append(str(item))
    replacement_design = existing_system_replacement.get("superior_system_design", {})
    for item in replacement_design.get("target_components", []) if isinstance(replacement_design, dict) else []:
        if item and str(item) not in values:
            values.append(str(item))
    if not values:
        values = ["signal_ingestion", "gap_detection", "solution_structuring", "portfolio_package"]
    return values[:10]


def build_design_proof(
    design: Dict[str, Any],
    solution: Dict[str, Any],
    existing_system_replacement: Dict[str, Any],
    advancement: Dict[str, Any],
) -> Dict[str, Any]:
    """Build deterministic design proof from runtime-owned candidate data.

    This implements the validation intent from the recovered design proof specs
    without importing those draft files as runtime programming.
    """

    scores = advancement.get("scores", {}) if isinstance(advancement.get("scores"), dict) else {}
    buildability = _score(scores.get("buildability_score"), 0.0)
    manufacturability = _score(scores.get("manufacturability_score"), 0.0)
    breakthrough = _score(scores.get("breakthrough_score"), 0.0)
    components = _components(solution, existing_system_replacement)
    functions = solution.get("functions", []) if isinstance(solution.get("functions"), list) else []
    has_replacement = bool(existing_system_replacement)
    integration_points = max(1, min(6, len(functions) // 2 or 1))
    complexity = min(1.0, 0.22 + len(components) * 0.045 + integration_points * 0.035 + (0.08 if has_replacement else 0.0))
    feasibility_score = round((buildability * 0.36) + (manufacturability * 0.26) + (breakthrough * 0.18) + ((1 - complexity) * 0.20), 4)
    maturity_score = round(
        min(
            1.0,
            0.28
            + (0.16 if design.get("blueprint_required") else 0.0)
            + (0.12 if design.get("cad_viewer_required") else 0.0)
            + (0.10 if design.get("video_viewer_required") else 0.0)
            + (0.16 if solution.get("constraints") else 0.0)
            + (0.18 if has_replacement else 0.0)
            + min(0.10, len(components) * 0.015),
        ),
        4,
    )
    dependency_risk_score = round(max(0.0, min(1.0, complexity - (0.12 if len(components) >= 4 else 0.0))), 4)
    deployment_score = round(min(1.0, (buildability * 0.45) + (manufacturability * 0.35) + (0.12 if has_replacement else 0.08)), 4)
    cost_complexity_factor = round(1.0 + complexity + dependency_risk_score * 0.4, 4)
    effort_hours = int(120 + len(components) * 28 + integration_points * 18 + (80 if has_replacement else 0))
    total_cost = int(effort_hours * 145 * cost_complexity_factor)
    overall = round(
        (feasibility_score * 0.30)
        + (maturity_score * 0.22)
        + (deployment_score * 0.18)
        + ((1 - dependency_risk_score) * 0.16)
        + (buildability * 0.14),
        4,
    )
    proof_status = "design_proof_ready" if overall >= 0.72 and feasibility_score >= 0.68 else "design_proof_needs_review"

    build_steps = [
        {"step": 1, "name": "evidence and signal contract", "depends_on": []},
        {"step": 2, "name": "gap and solution contract", "depends_on": [1]},
        {"step": 3, "name": "component architecture", "depends_on": [2]},
        {"step": 4, "name": "validation and governance gates", "depends_on": [3]},
        {"step": 5, "name": "portfolio and acquirer package", "depends_on": [4]},
    ]
    if has_replacement:
        build_steps.insert(2, {"step": 3, "name": "existing-system decomposition", "depends_on": [2]})
        for index, item in enumerate(build_steps, start=1):
            item["step"] = index

    return {
        "schema_version": "claire.design_proof.v1",
        "status": proof_status,
        "source": "runtime_candidate_contracts",
        "documents_used_as_runtime_programming": False,
        "architecture_feasibility": {
            "verdict": "feasible" if feasibility_score >= 0.74 else "conditionally_feasible",
            "score": feasibility_score,
            "component_count": len(components),
            "integration_points": integration_points,
            "complexity_score": round(complexity, 4),
        },
        "build_sequence": {
            "status": "valid_order",
            "steps": build_steps,
            "parallelizable_groups": [["evidence and signal contract"], ["component architecture", "validation and governance gates"]],
        },
        "dependency_risk": {
            "level": "low" if dependency_risk_score < 0.42 else "medium" if dependency_risk_score < 0.68 else "high",
            "score": dependency_risk_score,
            "single_points_of_failure": ["operator promotion gate"] if has_replacement else [],
            "circular_dependencies": [],
            "mitigation": "keep runtime truth promotion separate from candidate generation",
        },
        "deployment_model": {
            "status": "valid_bounded_deployment_model",
            "score": deployment_score,
            "target": "governed local runtime with external scheduler",
            "rollback": "disable scheduler tick and preserve candidate stores",
        },
        "implementation_cost": {
            "effort_hours": effort_hours,
            "complexity_factor": cost_complexity_factor,
            "estimated_total_usd": total_cost,
            "assumption": "engineering estimate for prototype-to-production hardening",
        },
        "design_maturity": {
            "level": "managed" if maturity_score >= 0.78 else "defined" if maturity_score >= 0.62 else "developing",
            "score": maturity_score,
            "dimensions": {
                "completeness": round(maturity_score, 4),
                "testability": 0.72 if proof_status == "design_proof_ready" else 0.58,
                "maintainability": round(max(0.45, 1 - dependency_risk_score), 4),
                "documentation": 0.76 if design.get("blueprint_required") else 0.55,
            },
        },
        "overall_score": overall,
        "operator_review_required": True,
    }
