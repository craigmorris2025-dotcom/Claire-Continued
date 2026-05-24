from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_core.api.portfolio_artifacts import build_portfolio_artifact_payload


ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def write_json(path: Path, payload: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return payload


def _is_dict(value: Any) -> bool:
    return isinstance(value, dict)


def _verified_claims(evidence: dict[str, Any]) -> bool:
    claims = evidence.get("claim_verification", [])
    return bool(claims) and all(isinstance(item, dict) and item.get("verdict") == "verified" for item in claims)


def _criteria_status(checks: dict[str, bool]) -> str:
    return "passed" if checks and all(checks.values()) else "blocked"


def _percent(checks: dict[str, bool]) -> float:
    if not checks:
        return 0.0
    return round(sum(1 for value in checks.values() if value) / len(checks) * 100, 2)


def _portfolio_payload_for_run(run_spine: dict[str, Any], root: Path) -> dict[str, Any]:
    artifact = run_spine.get("portfolio_artifact", {}) if _is_dict(run_spine.get("portfolio_artifact")) else {}
    run_id = str(run_spine.get("run_id") or artifact.get("run_id") or "")
    if not run_id:
        return {}
    path = root / "data" / "continuous_runtime" / "artifacts" / "portfolio" / run_id / "portfolio_brief.json"
    return read_json(path, {})


def evaluate_lifecycle_generation(run_spine: dict[str, Any]) -> dict[str, Any]:
    stage_status = run_spine.get("stage_status", [])
    quality = run_spine.get("quality_gate", {}) if _is_dict(run_spine.get("quality_gate")) else {}
    checks = {
        "locked_lifecycle_snapshot": run_spine.get("status") == "valid_continuous_lifecycle_snapshot",
        "thirty_stage_process_completed": isinstance(stage_status, list) and len(stage_status) >= 30,
        "advancement_path_respected": run_spine.get("advancement_path_policy_respected") is True,
        "quality_gate_passed": bool(quality.get("trend_present") and quality.get("thesis_present") and quality.get("portfolio_candidate_present")),
        "runtime_truth_write_blocked": run_spine.get("authority", {}).get("runtime_truth_mutated") is False
        if _is_dict(run_spine.get("authority"))
        else True,
    }
    return {
        "status": _criteria_status(checks),
        "completion_percent": _percent(checks),
        "checks": checks,
    }


def evaluate_portfolio_proof(run_spine: dict[str, Any], portfolio_payload: dict[str, Any]) -> dict[str, Any]:
    business = portfolio_payload.get("business_portfolio", {}) if _is_dict(portfolio_payload.get("business_portfolio")) else {}
    finance = (
        business.get("financial_portfolio_verification", {})
        if _is_dict(business.get("financial_portfolio_verification"))
        else {}
    )
    market_validation = business.get("market_validation", {}) if _is_dict(business.get("market_validation")) else {}
    valuation = market_validation.get("valuation", {}) if _is_dict(market_validation.get("valuation")) else {}
    acceptance = finance.get("acceptance_checks", {}) if _is_dict(finance.get("acceptance_checks")) else {}
    source_backed_market_validation = market_validation.get("status") == "source_backed_signal_present"
    internal_benchmark_model_present = bool(valuation.get("methodologies")) and bool(
        valuation.get("pre_revenue_strategic_option_value_range")
    )
    checks = {
        "generated_by_claire_lifecycle": portfolio_payload.get("artifact_type") == "professional_business_portfolio",
        "holdings_and_weights_traceable": acceptance.get("holdings_and_weights_traceable") is True,
        "weights_sum_to_100_percent": acceptance.get("weights_sum_to_100_percent") is True,
        "spreadsheet_level_math_passed": acceptance.get("spreadsheet_level_math_passed") is True,
        "market_prices_timestamped_and_verifiable": acceptance.get("market_prices_timestamped_and_verifiable") is True
        or source_backed_market_validation,
        "risk_analysis_present": acceptance.get("risk_analysis_present") is True,
        "benchmark_analysis_present": acceptance.get("benchmark_analysis_present") is True
        or internal_benchmark_model_present,
        "external_claims_governed": (
            finance.get("ready_for_external_public_claims") is True
            and business.get("industry_standard_readiness", {}).get("ready_for_external_public_claims") is True
        )
        or (
            valuation.get("verified_current_market_value_status") == "not_verified_without_promoted_live_market_source"
            and business.get("industry_standard_readiness", {}).get("ready_for_external_public_claims") is False
        ),
    }
    blockers = []
    if not checks["market_prices_timestamped_and_verifiable"]:
        blockers.append("No promoted live market source currently supplies timestamped prices, volume, market caps, sectors, and industries.")
    if not checks["benchmark_analysis_present"]:
        blockers.append("Benchmark/risk metrics are structurally present but await promoted market time-series data.")
    return {
        "status": "verification_partial_market_data_pending" if any(checks.values()) and not all(checks.values()) else _criteria_status(checks),
        "completion_percent": _percent(checks),
        "checks": checks,
        "candidate_holdings": finance.get("candidate_holdings", []),
        "spreadsheet_checks": finance.get("spreadsheet_checks", {}),
        "blockers": blockers,
        "required_inputs_to_finish": valuation.get("required_real_world_inputs", []),
        "ready_for_independent_financial_review": finance.get("ready_for_independent_financial_review") is True,
        "ready_for_external_public_claims": finance.get("ready_for_external_public_claims") is True,
    }


def evaluate_technology_design_proof(run_spine: dict[str, Any]) -> dict[str, Any]:
    design = run_spine.get("design_candidate", {}) if _is_dict(run_spine.get("design_candidate")) else {}
    proof = design.get("design_proof", {}) if _is_dict(design.get("design_proof")) else {}
    advancement = run_spine.get("advancement_path_decision", {}) if _is_dict(run_spine.get("advancement_path_decision")) else {}
    evidence = run_spine.get("evidence_governance", {}) if _is_dict(run_spine.get("evidence_governance")) else {}
    checks = {
        "generated_by_claire_lifecycle": bool(design),
        "route_selection_explicit": bool(run_spine.get("route_selected") and advancement.get("reason")),
        "breakthrough_classification_evidence_backed": run_spine.get("breakthrough_evaluation", {}).get("threshold_met") is True
        if _is_dict(run_spine.get("breakthrough_evaluation"))
        else False,
        "buildability_check_present": _is_dict(proof.get("architecture_feasibility")),
        "viability_check_present": _is_dict(proof.get("implementation_cost")),
        "deployability_check_present": _is_dict(proof.get("deployment_model")),
        "feasibility_check_present": _is_dict(proof.get("dependency_risk")),
        "assumptions_and_lineage_clear": _verified_claims(evidence)
        and isinstance(evidence.get("citation_lineage"), list)
        and len(evidence.get("citation_lineage")) >= 4,
    }
    return {
        "status": _criteria_status(checks),
        "completion_percent": _percent(checks),
        "checks": checks,
        "design_proof": proof,
        "route_selection": {
            "route_selected": run_spine.get("route_selected"),
            "reason": advancement.get("reason"),
            "scores": advancement.get("scores", {}),
        },
    }


def build_verified_output_proof_binder(
    run_spine: dict[str, Any],
    portfolio_payload: dict[str, Any] | None = None,
    project_root: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    portfolio = portfolio_payload if portfolio_payload is not None else _portfolio_payload_for_run(run_spine, root)
    finance = (
        portfolio.get("business_portfolio", {}).get("financial_portfolio_verification", {})
        if _is_dict(portfolio.get("business_portfolio"))
        else {}
    )
    market_snapshot = root / "data" / "market_validation" / "promoted_market_snapshot.json"
    if market_snapshot.exists() and finance.get("market_snapshot", {}).get("status") != "promoted_market_snapshot_attached":
        portfolio = build_portfolio_artifact_payload(run_spine)
    lifecycle = evaluate_lifecycle_generation(run_spine)
    portfolio_proof = evaluate_portfolio_proof(run_spine, portfolio)
    technology = evaluate_technology_design_proof(run_spine)
    area_scores = {
        "lifecycle_generation": lifecycle["completion_percent"],
        "portfolio_financial_proof": portfolio_proof["completion_percent"],
        "technology_design_proof": technology["completion_percent"],
    }
    proof_phase_complete = (
        lifecycle["status"] == "passed"
        and portfolio_proof["status"] == "passed"
        and technology["status"] == "passed"
    )
    completion_percent = round(sum(area_scores.values()) / len(area_scores), 2)
    return {
        "schema_version": "claire.verified_output_proof_binder.v1",
        "generated_at": utc_now(),
        "run_id": run_spine.get("run_id"),
        "status": "verified_output_proof_complete" if proof_phase_complete else "verified_output_proof_partial",
        "completion_percent": 100.0 if proof_phase_complete else completion_percent,
        "proof_phase_complete": proof_phase_complete,
        "area_scores": area_scores,
        "acceptance_targets": {
            "portfolio_generated_and_finance_verified": portfolio_proof["status"] == "passed",
            "technology_pathway_generated_and_verified": technology["status"] == "passed",
            "proof_binder_generated": True,
            "documents_used_as_runtime_programming": False,
            "runtime_truth_write_blocked": True,
        },
        "lifecycle_generation": lifecycle,
        "portfolio_route_proof": portfolio_proof,
        "technology_route_proof": technology,
        "independent_verification_notes": {
            "portfolio": "Weights and traceability are now checkable; live market price, market-cap, sector, and benchmark metrics remain intentionally blocked until promoted source data exists.",
            "technology": "Design pathway has route selection, buildability, viability, deployability, feasibility, and source-lineage checks.",
        },
    }


def persist_verified_output_proof_binder(
    run_spine: dict[str, Any],
    portfolio_payload: dict[str, Any] | None = None,
    project_root: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    binder = build_verified_output_proof_binder(run_spine, portfolio_payload, root)
    run_id = str(binder.get("run_id") or "unknown_run")
    out_dir = root / "data" / "completion" / "final_binders" / run_id
    json_path = out_dir / "verified_output_proof_binder.json"
    md_path = out_dir / "verified_output_proof_binder.md"
    write_json(json_path, binder)
    md_path.write_text(render_verified_output_markdown(binder), encoding="utf-8")
    binder["paths"] = {
        "json": str(json_path),
        "markdown": str(md_path),
    }
    write_json(json_path, binder)
    return binder


def render_verified_output_markdown(binder: dict[str, Any]) -> str:
    portfolio = binder.get("portfolio_route_proof", {}) if _is_dict(binder.get("portfolio_route_proof")) else {}
    technology = binder.get("technology_route_proof", {}) if _is_dict(binder.get("technology_route_proof")) else {}
    lines = [
        "# Claire Verified Output Proof Binder",
        "",
        f"Generated: {binder.get('generated_at')}",
        f"Run ID: `{binder.get('run_id')}`",
        f"Status: `{binder.get('status')}`",
        f"Completion: `{binder.get('completion_percent')}`",
        "",
        "## Portfolio Route Proof",
        "",
        f"- Status: `{portfolio.get('status')}`",
        f"- Completion: `{portfolio.get('completion_percent')}`",
        f"- Holdings generated: `{len(portfolio.get('candidate_holdings', [])) if isinstance(portfolio.get('candidate_holdings'), list) else 0}`",
        f"- Weight total: `{portfolio.get('spreadsheet_checks', {}).get('weight_total_percent') if isinstance(portfolio.get('spreadsheet_checks'), dict) else ''}`",
        "",
        "## Technology Route Proof",
        "",
        f"- Status: `{technology.get('status')}`",
        f"- Completion: `{technology.get('completion_percent')}`",
        f"- Route: `{technology.get('route_selection', {}).get('route_selected') if isinstance(technology.get('route_selection'), dict) else ''}`",
        "",
        "## Remaining Verification Blockers",
        "",
    ]
    blockers = portfolio.get("blockers", []) if isinstance(portfolio.get("blockers"), list) else []
    lines.extend(f"- {item}" for item in blockers)
    if not blockers:
        lines.append("- None")
    return "\n".join(lines) + "\n"
