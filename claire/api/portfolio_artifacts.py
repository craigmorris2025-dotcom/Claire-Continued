from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

router = APIRouter(tags=["Portfolio Artifacts"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

CONTINUOUS_DIR = PROJECT_ROOT / "data" / "continuous_runtime"
PORTFOLIO_ARTIFACT_DIR = CONTINUOUS_DIR / "artifacts" / "portfolio"

FINAL_PACKAGE_REQUIREMENTS = [
    "executive_summary",
    "signal_basis",
    "trend_basis",
    "thesis",
    "gap_explanation",
    "discovery_output",
    "breakthrough_classification",
    "advancement_path",
    "solution_or_invention_if_applicable",
    "buildability",
    "viability",
    "manufacturability_deployability",
    "feasibility",
    "design_portal_output_if_applicable",
    "market_positioning",
    "moat_and_differentiation",
    "business_model_and_value_capture",
    "competitor_analysis",
    "portfolio_placement",
    "acquirer_targets",
    "acquisition_rationale",
    "evidence",
    "confidence",
    "risks",
    "next_steps",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def write_json(path: Path, payload: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def latest_run_id(root: Path | None = None) -> str:
    base = root or PROJECT_ROOT
    current = read_json(base / "data" / "continuous_runtime" / "current_run.json", {})
    return str(current.get("run_id") or "")


def artifact_dir(run_id: str, root: Path | None = None) -> Path:
    base = root or PROJECT_ROOT
    return base / "data" / "continuous_runtime" / "artifacts" / "portfolio" / run_id


def artifact_routes(run_id: str) -> dict[str, str]:
    return {
        "metadata_url": f"/api/portfolio/artifacts/{run_id}",
        "view_url": f"/portfolio/artifacts/{run_id}/view",
        "download_url": f"/portfolio/artifacts/{run_id}/download",
        "latest_view_url": "/portfolio/artifacts/latest/view",
        "latest_download_url": "/portfolio/artifacts/latest/download",
    }


def _text(value: Any) -> str:
    return str(value or "").strip()


def _score(value: Any, fallback: float = 0.0) -> float:
    try:
        return round(max(0.0, min(1.0, float(value))), 4)
    except (TypeError, ValueError):
        return fallback


def _keywords(*values: Any) -> list[str]:
    stop = {"and", "the", "for", "with", "from", "into", "this", "that", "because", "should", "could"}
    counts: dict[str, int] = {}

    def walk(value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(walk(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(walk(item) for item in value)
        return str(value or "")

    for value in values:
        for raw in walk(value).lower().replace("/", " ").replace("-", " ").replace(",", " ").split():
            token = "".join(ch for ch in raw if ch.isalnum())
            if len(token) < 4 or token in stop:
                continue
            counts[token] = counts.get(token, 0) + 1
    return [key for key, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:16]]


def _industry_from_keywords(keywords: list[str]) -> str:
    joined = " ".join(keywords)
    if any(term in joined for term in ("regulatory", "compliance", "filing", "governance")):
        return "regulated enterprise technology"
    if any(term in joined for term in ("autonomous", "invention", "design", "technology")):
        return "autonomous invention and R&D intelligence"
    if any(term in joined for term in ("insurance", "risk", "climate")):
        return "insurance and risk analytics"
    return "enterprise intelligence"


def _readiness_label(score: float) -> str:
    if score >= 0.78:
        return "diligence_ready"
    if score >= 0.62:
        return "operator_review_ready"
    if score >= 0.48:
        return "needs_validation"
    return "early_signal"


def _money(value: int) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,}"


def _market_snapshot(root: Path | None = None) -> dict[str, Any]:
    base = root or PROJECT_ROOT
    snapshot = read_json(base / "data" / "market_validation" / "promoted_market_snapshot.json", {})
    return snapshot if isinstance(snapshot, dict) else {}


def _valuation_model(confidence: float, acquirer_fit: float, evidence_count: int, market_verified: bool = False) -> dict[str, Any]:
    evidence_multiplier = max(1, min(8, evidence_count))
    readiness = max(0.25, min(1.0, (confidence * 0.52) + (acquirer_fit * 0.38) + (evidence_multiplier / 8 * 0.10)))
    development_budget = {
        "prototype_mvp_low": 250_000,
        "prototype_mvp_high": 900_000,
        "enterprise_v1_low": 1_200_000,
        "enterprise_v1_high": 4_500_000,
    }
    option_value_low = int(1_500_000 + readiness * 3_500_000)
    option_value_high = int(7_500_000 + readiness * 24_000_000)
    return {
        "status": "requires_live_market_validation",
        "validation_rule": "Replace benchmark ranges with sourced TAM/SAM/SOM, pricing, comparable transaction, and buyer budget evidence before external claims.",
        "methodologies": [
            "venture-style option value for pre-revenue technology portfolio",
            "build-vs-buy avoided cost range",
            "strategic acquirer capability-gap premium",
            "TAM/SAM/SOM model after live market evidence promotion",
        ],
        "development_budget_estimate": {
            key: _money(value) for key, value in development_budget.items()
        },
        "pre_revenue_strategic_option_value_range": {
            "low": _money(option_value_low),
            "high": _money(option_value_high),
            "basis": "internal benchmark model until live market evidence is attached",
        },
        "required_real_world_inputs": [
            "current market size and growth source",
            "buyer budget or procurement signal",
            "comparable acquisition or licensing transaction",
            "competitive alternatives and pricing",
            "implementation cost and margin assumptions",
        ],
        "verified_current_market_value": "market_snapshot_attached" if market_verified else None,
        "verified_current_market_value_status": "verified_from_promoted_market_snapshot"
        if market_verified
        else "not_verified_without_promoted_live_market_source",
    }


def _candidate_holding_name(item: dict[str, Any]) -> str:
    ticker = _text(item.get("ticker")).upper()
    name = _text(item.get("name")) or ticker or "Unspecified candidate"
    return f"{name} ({ticker})" if ticker and ticker not in name.upper() else name


def _financial_verification_model(acquirers: list[Any], signals: list[Any], benchmark: str = "SPY") -> dict[str, Any]:
    candidates = [item for item in acquirers if isinstance(item, dict) and _text(item.get("ticker"))]
    snapshot = _market_snapshot()
    snapshot_holdings = snapshot.get("holdings", {}) if isinstance(snapshot.get("holdings"), dict) else {}
    snapshot_benchmark = snapshot.get("benchmark", {}) if isinstance(snapshot.get("benchmark"), dict) else {}
    raw_scores: list[float] = []
    for item in candidates:
        fit = _score(item.get("fit"), 0.0)
        capacity = _score(item.get("capacity"), 0.0)
        raw_scores.append(max(0.01, (fit * 0.72) + (capacity * 0.28)))

    total = sum(raw_scores)
    holdings: list[dict[str, Any]] = []
    if total:
        rounded_weights: list[float] = [round(score / total * 100, 2) for score in raw_scores]
        rounding_delta = round(100.0 - sum(rounded_weights), 2)
        if rounded_weights:
            rounded_weights[-1] = round(rounded_weights[-1] + rounding_delta, 2)
        for item, weight in zip(candidates, rounded_weights):
            ticker = _text(item.get("ticker")).upper()
            market_data = snapshot_holdings.get(ticker, {}) if isinstance(snapshot_holdings.get(ticker), dict) else {}
            market_data_complete = all(
                market_data.get(key) not in {None, ""}
                for key in ("price", "volume", "market_cap", "sector", "industry", "timestamp", "source")
            )
            holdings.append(
                {
                    "ticker": ticker,
                    "name": _candidate_holding_name(item),
                    "weight_percent": weight,
                    "weight_basis": "normalized strategic acquirer fit and capacity score",
                    "source": item.get("source") or "claire.acquirer_matching",
                    "traceability": {
                        "fit": item.get("fit"),
                        "capacity": item.get("capacity"),
                        "strategic_fit_rationale": item.get("strategic_fit_rationale"),
                        "capability_gap_narrative": item.get("capability_gap_narrative"),
                        "source_signal_count": len(signals),
                    },
                    "market_data": {
                        "price": market_data.get("price"),
                        "volume": market_data.get("volume"),
                        "market_cap": market_data.get("market_cap"),
                        "sector": market_data.get("sector"),
                        "industry": market_data.get("industry"),
                        "timestamp": market_data.get("timestamp"),
                        "source": market_data.get("source"),
                        "verification_status": "verified_from_promoted_market_snapshot"
                        if market_data_complete
                        else "pending_promoted_live_market_source",
                    },
                }
            )

    weight_total = round(sum(float(item.get("weight_percent", 0.0) or 0.0) for item in holdings), 2)
    math_passed = bool(holdings) and abs(weight_total - 100.0) <= 0.01
    market_data_complete = all(
        isinstance(item.get("market_data"), dict)
        and item["market_data"].get("price") is not None
        and item["market_data"].get("market_cap") is not None
        and item["market_data"].get("timestamp")
        and item["market_data"].get("source")
        for item in holdings
    )
    benchmark_ready = bool(benchmark) and market_data_complete and all(
        snapshot_benchmark.get(key) not in {None, ""} for key in ("symbol", "price", "volume", "timestamp", "source")
    )
    risk_ready = math_passed and bool(holdings)
    acceptance_checks = {
        "generated_by_claire_lifecycle": bool(holdings),
        "holdings_and_weights_traceable": bool(holdings) and all(item.get("traceability") for item in holdings),
        "weights_sum_to_100_percent": math_passed,
        "market_prices_timestamped_and_verifiable": market_data_complete,
        "benchmark_analysis_present": benchmark_ready,
        "risk_analysis_present": risk_ready,
        "spreadsheet_level_math_passed": math_passed,
    }
    return {
        "schema_version": "claire.financial_portfolio_verification.v1",
        "status": "finance_math_verified_market_data_pending" if math_passed else "insufficient_holdings_for_finance_proof",
        "portfolio_construction": "watchlist_allocation_from_acquirer_fit",
        "benchmark_symbol": benchmark,
        "market_snapshot": {
            "status": "promoted_market_snapshot_attached" if snapshot else "missing_promoted_market_snapshot",
            "snapshot_id": snapshot.get("snapshot_id"),
            "generated_at": snapshot.get("generated_at"),
            "source_policy": snapshot.get("source_policy"),
        },
        "candidate_holdings": holdings,
        "weight_total_percent": weight_total,
        "spreadsheet_checks": {
            "weight_total_percent": weight_total,
            "weights_sum_to_100_percent": math_passed,
            "holding_count": len(holdings),
            "non_negative_weights": all(float(item.get("weight_percent", 0.0) or 0.0) >= 0 for item in holdings),
        },
        "risk_analysis": {
            "status": "structure_ready_market_metrics_pending" if risk_ready else "pending_holdings",
            "concentration": "high" if holdings and max(float(item.get("weight_percent", 0.0) or 0.0) for item in holdings) > 45 else "balanced",
            "single_name_max_weight_percent": max(
                [float(item.get("weight_percent", 0.0) or 0.0) for item in holdings],
                default=0.0,
            ),
            "missing_live_metrics": [
                "price",
                "volume",
                "market_cap",
                "sector",
                "industry",
                "benchmark_returns",
            ]
            if holdings and not market_data_complete
            else [],
        },
        "benchmark_analysis": {
            "status": "pending_promoted_live_market_source" if holdings and not benchmark_ready else "ready",
            "benchmark_symbol": benchmark,
            "required_inputs": [
                "benchmark price history",
                "holding price history",
                "holding sectors and industries",
                "current market caps",
            ],
        },
        "acceptance_checks": acceptance_checks,
        "ready_for_independent_financial_review": all(acceptance_checks.values()),
        "ready_for_external_public_claims": market_data_complete and benchmark_ready,
    }


def build_business_portfolio(run_spine: dict[str, Any]) -> dict[str, Any]:
    run_id = _text(run_spine.get("run_id")) or "unknown_run"
    portfolio = run_spine.get("portfolio_candidate", {}) if isinstance(run_spine.get("portfolio_candidate"), dict) else {}
    discovery = run_spine.get("discovery_candidate", {}) if isinstance(run_spine.get("discovery_candidate"), dict) else {}
    trend = run_spine.get("trend", {}) if isinstance(run_spine.get("trend"), dict) else {}
    thesis = run_spine.get("thesis", {}) if isinstance(run_spine.get("thesis"), dict) else {}
    acquisition = run_spine.get("acquisition", {}) if isinstance(run_spine.get("acquisition"), dict) else {}
    breakthrough = run_spine.get("breakthrough_evaluation", {}) if isinstance(run_spine.get("breakthrough_evaluation"), dict) else {}
    design_gate = run_spine.get("design_gate", {}) if isinstance(run_spine.get("design_gate"), dict) else {}
    quality = run_spine.get("quality_gate", {}) if isinstance(run_spine.get("quality_gate"), dict) else {}
    strategic_world = run_spine.get("strategic_world", {}) if isinstance(run_spine.get("strategic_world"), dict) else {}
    signals = run_spine.get("signals", []) if isinstance(run_spine.get("signals"), list) else []
    acquirers = acquisition.get("acquirer_matches", []) if isinstance(acquisition.get("acquirer_matches"), list) else []
    keywords = _keywords(portfolio, discovery, trend, thesis, signals)
    industry = _industry_from_keywords(keywords)
    evidence_count = len(signals)
    trend_confidence = _score(trend.get("confidence"), 0.5)
    portfolio_confidence = _score(portfolio.get("confidence"), trend_confidence)
    acquirer_fit = _score(max([float(item.get("fit", 0.0) or 0.0) for item in acquirers], default=0.0), 0.0)
    evidence_quality = _score(min(0.9, 0.42 + evidence_count * 0.06), 0.42)
    viability_score = _score((portfolio_confidence * 0.38) + (evidence_quality * 0.25) + (acquirer_fit * 0.25) + (0.12 if keywords else 0.0))
    market_urgency = _score((trend_confidence * 0.45) + (evidence_quality * 0.35) + (0.20 if acquirer_fit >= 0.55 else 0.08))
    investment_readiness = _score((viability_score * 0.45) + (market_urgency * 0.25) + (acquirer_fit * 0.30))
    top_acquirer = acquirers[0] if acquirers else {}
    solution_name = portfolio.get("title") or trend.get("title") or "Claire-generated business portfolio"
    financial_verification = _financial_verification_model(acquirers, signals)
    market_numbers_verified = bool(financial_verification.get("ready_for_external_public_claims"))

    return {
        "schema_version": "claire.business_portfolio.v1",
        "portfolio_id": f"business-portfolio-{run_id}",
        "run_id": run_id,
        "status": _readiness_label(investment_readiness),
        "portfolio_type": "industry_standard_business_portfolio",
        "title": solution_name,
        "industry": industry,
        "created_at": utc_now(),
        "runtime_basis": {
            "source": "30_stage_runtime",
            "route_selected": run_spine.get("route_selected"),
            "stage_count": len(run_spine.get("stage_status", [])) if isinstance(run_spine.get("stage_status"), list) else 0,
            "advancement_path_policy_respected": bool(run_spine.get("advancement_path_policy_respected")),
            "runtime_truth_mutated": False,
            "operator_review_required": True,
        },
        "pipeline_alignment": {
            "status": "code_contract_runtime",
            "docs_used_as_runtime_source": False,
            "programming_source": "versioned_code_contracts_and_run_spine",
            "route_selected": run_spine.get("route_selected"),
            "stage_outputs": [
                item.get("output_key")
                for item in run_spine.get("stage_status", [])
                if isinstance(item, dict)
            ],
            "route_insertions": run_spine.get("route_insertions", []),
            "final_package_requirements": FINAL_PACKAGE_REQUIREMENTS,
            "operator_rules": {
                "nothing_auto_promotes": True,
                "review_queue_required": True,
                "runtime_truth_write_requires_promotion": True,
                "documents_are_validation_reference_only": True,
            },
        },
        "executive_summary": {
            "thesis": thesis.get("statement") or portfolio.get("portfolio_thesis") or portfolio.get("summary"),
            "problem": f"Signals indicate an active gap in {industry}: {trend.get('summary') or discovery.get('summary') or 'validated market pressure requires further source validation.'}",
            "solution": f"Create and package {solution_name} as a portfolio-ready solution with design, validation, and acquirer-fit handoff.",
            "why_now": "Fresh governed signals, a scored route decision, and acquirer-fit matching indicate a reviewable timing window.",
            "buyer": top_acquirer.get("name") or "strategic acquirer or enterprise buyer requiring gap validation",
        },
        "signal_to_portfolio_chain": {
            "signals": signals,
            "trend": trend,
            "gap_identified": {
                "status": "identified" if discovery else "needs_more_evidence",
                "title": discovery.get("title") or trend.get("title"),
                "summary": discovery.get("summary") or trend.get("summary"),
                "source_signal_ids": discovery.get("source_signal_ids") or trend.get("evidence_signal_ids", []),
            },
            "discovery": discovery,
            "innovation_possible": {
                "status": "possible_pending_design_validation",
                "route": run_spine.get("route_selected"),
                "breakthrough_status": breakthrough.get("status"),
                "design_status": design_gate.get("status"),
                "design_portal_required": True,
            },
        },
        "scoring": {
            "viability_score": viability_score,
            "market_urgency_score": market_urgency,
            "evidence_quality_score": evidence_quality,
            "acquirer_fit_score": acquirer_fit,
            "investment_readiness_score": investment_readiness,
            "readiness_label": _readiness_label(investment_readiness),
            "score_policy": "Scores are review signals, not financial claims, until live market valuation evidence is promoted.",
        },
        "market_validation": {
            "status": "source_backed_signal_present" if evidence_count else "insufficient_evidence",
            "industry_standard_validation_required": True,
            "validated_inputs_present": {
                "fresh_signals": bool(quality.get("fresh_input_present")),
                "trend": bool(quality.get("trend_present")),
                "thesis": bool(quality.get("thesis_present")),
                "portfolio_candidate": bool(quality.get("portfolio_candidate_present")),
                "acquirer_rationale": bool(quality.get("acquisition_rationale_present")),
                "verified_market_size": False,
                "verified_comparable_transactions": False,
                "verified_buyer_budget": False,
            },
            "keywords": keywords,
            "valuation": _valuation_model(portfolio_confidence, acquirer_fit, evidence_count, market_numbers_verified),
        },
        "financial_portfolio_verification": financial_verification,
        "solution_portfolio": {
            "portfolio_candidate": portfolio,
            "product_definition": {
                "name": solution_name,
                "category": portfolio.get("candidate_type") or "portfolio_solution",
                "target_gap": discovery.get("summary") or trend.get("summary"),
                "core_capabilities": keywords[:8],
                "route": run_spine.get("route_selected"),
            },
            "design_portal_handoff": {
                "required": True,
                "status": design_gate.get("status") or "pending_design_portal_review",
                "reason": design_gate.get("reason") or "Design portal validates buildability, component map, blueprint, CAD/video slots, and downstream package readiness.",
            },
            "implementation_roadmap": [
                {"phase": "evidence validation", "output": "promoted live/source-pack evidence and market valuation inputs"},
                {"phase": "design portal", "output": "blueprint, component map, materials manifest, CAD/video slots if applicable"},
                {"phase": "portfolio construction", "output": "business case, pricing assumptions, GTM path, risk register"},
                {"phase": "acquirer package", "output": "buyer fit rationale, capability-gap narrative, diligence memo"},
            ],
        },
        "acquirer_strategy": {
            "status": "matched" if acquirers else "needs_acquirer_search",
            "top_fit": top_acquirer,
            "matches": acquirers,
            "fit_logic": "Matched against strategic focus, capability gap, domain alignment, and build-vs-buy pressure.",
            "buyer_need_statement": top_acquirer.get("capability_gap_narrative") or "Identify corporations with an urgent capability gap this portfolio can fill.",
        },
        "risk_and_diligence": {
            "primary_risks": [
                "market valuation requires promoted live evidence",
                "technical buildability requires design portal validation",
                "buyer urgency must be confirmed through current source evidence",
                "IP/public disclosure posture must be reviewed before publishing implementation detail",
            ],
            "diligence_next": [
                "fetch current market-size and comparable transaction sources",
                "run connected search against likely acquirers and procurement/budget signals",
                "generate design portal package for the selected solution",
                "attach verified numbers to the portfolio valuation section",
            ],
        },
        "strategic_world_intelligence": {
            "status": strategic_world.get("status") or "not_attached",
            "domains": strategic_world.get("domains", []),
            "cross_domain_themes": strategic_world.get("world_snapshot", {}).get("cross_domain_themes", [])
            if isinstance(strategic_world.get("world_snapshot"), dict)
            else [],
            "top_recommendation": (
                strategic_world.get("ranked_recommendations", [])[0]
                if isinstance(strategic_world.get("ranked_recommendations"), list)
                and strategic_world.get("ranked_recommendations")
                else {}
            ),
            "governance": strategic_world.get("governance", {}),
            "execution_boundary": "recommendation_only_no_external_action_without_operator_approval",
        },
        "industry_standard_readiness": {
            "business_case": True,
            "signal_lineage": bool(signals),
            "market_numbers_verified": market_numbers_verified,
            "technical_design_validated": design_gate.get("status") not in {"not_selected", None},
            "acquirer_fit_generated": bool(acquirers),
            "ready_for_external_public_claims": market_numbers_verified,
            "ready_for_internal_operator_review": True,
        },
    }


def build_portfolio_artifact_payload(run_spine: dict[str, Any]) -> dict[str, Any]:
    run_id = _text(run_spine.get("run_id")) or "unknown_run"
    business_portfolio = build_business_portfolio(run_spine)
    portfolio = run_spine.get("portfolio_candidate", {}) if isinstance(run_spine.get("portfolio_candidate"), dict) else {}
    acquisition = run_spine.get("acquisition", {}) if isinstance(run_spine.get("acquisition"), dict) else {}
    quality = run_spine.get("quality_gate", {}) if isinstance(run_spine.get("quality_gate"), dict) else {}
    signals = run_spine.get("signals", []) if isinstance(run_spine.get("signals"), list) else []
    acquirers = acquisition.get("acquirer_matches", []) if isinstance(acquisition.get("acquirer_matches"), list) else []
    return {
        "schema_version": "claire.portfolio_artifact.v2",
        "artifact_id": f"portfolio-artifact-{run_id}",
        "run_id": run_id,
        "created_at": utc_now(),
        "status": business_portfolio["status"],
        "artifact_type": "professional_business_portfolio",
        "portfolio_type": "industry_standard_business_portfolio",
        "title": business_portfolio["title"],
        "summary": business_portfolio["executive_summary"]["thesis"] or portfolio.get("summary") or "",
        "route_selected": run_spine.get("route_selected"),
        "review_required": True,
        "download_available": True,
        "runtime_truth_write": "blocked",
        "body_read_performed": False,
        "automatic_update_performed": False,
        "business_portfolio": business_portfolio,
        "strategic_world": run_spine.get("strategic_world", {}) if isinstance(run_spine.get("strategic_world"), dict) else {},
        "quality_gate": quality,
        "portfolio": portfolio,
        "trend": run_spine.get("trend", {}),
        "thesis": run_spine.get("thesis", {}),
        "signals": signals,
        "acquirer_matches": acquirers,
        "breakthrough_evaluation": run_spine.get("breakthrough_evaluation", {}),
        "design_gate": run_spine.get("design_gate", {}),
        "final_package": run_spine.get("final_package", {}),
        "routes": artifact_routes(run_id),
    }


def render_portfolio_html(payload: dict[str, Any]) -> str:
    title = html.escape(_text(payload.get("title")) or "Portfolio Brief")
    summary = html.escape(_text(payload.get("summary")))
    business = payload.get("business_portfolio", {}) if isinstance(payload.get("business_portfolio"), dict) else {}
    executive = business.get("executive_summary", {}) if isinstance(business.get("executive_summary"), dict) else {}
    scoring = business.get("scoring", {}) if isinstance(business.get("scoring"), dict) else {}
    validation = business.get("market_validation", {}) if isinstance(business.get("market_validation"), dict) else {}
    valuation = validation.get("valuation", {}) if isinstance(validation.get("valuation"), dict) else {}
    finance = business.get("financial_portfolio_verification", {}) if isinstance(business.get("financial_portfolio_verification"), dict) else {}
    solution = business.get("solution_portfolio", {}) if isinstance(business.get("solution_portfolio"), dict) else {}
    product = solution.get("product_definition", {}) if isinstance(solution.get("product_definition"), dict) else {}
    design = solution.get("design_portal_handoff", {}) if isinstance(solution.get("design_portal_handoff"), dict) else {}
    acquirer_strategy = business.get("acquirer_strategy", {}) if isinstance(business.get("acquirer_strategy"), dict) else {}
    diligence = business.get("risk_and_diligence", {}) if isinstance(business.get("risk_and_diligence"), dict) else {}
    readiness = business.get("industry_standard_readiness", {}) if isinstance(business.get("industry_standard_readiness"), dict) else {}
    strategic_world = business.get("strategic_world_intelligence", {}) if isinstance(business.get("strategic_world_intelligence"), dict) else {}
    thesis = payload.get("thesis", {}) if isinstance(payload.get("thesis"), dict) else {}
    trend = payload.get("trend", {}) if isinstance(payload.get("trend"), dict) else {}
    signals = payload.get("signals", []) if isinstance(payload.get("signals"), list) else []
    acquirers = payload.get("acquirer_matches", []) if isinstance(payload.get("acquirer_matches"), list) else []

    def row(label: str, value: Any) -> str:
        return f"<tr><th>{html.escape(label)}</th><td>{html.escape(_text(value))}</td></tr>"

    signal_rows = "".join(
        f"<li><strong>{html.escape(_text(item.get('title')))}</strong><span>{html.escape(_text(item.get('summary')))}</span></li>"
        for item in signals[:12]
        if isinstance(item, dict)
    )
    acquirer_rows = "".join(
        f"<li><strong>{html.escape(_text(item.get('name')))}</strong><span>Fit {html.escape(_text(item.get('fit')))}. {html.escape(_text(item.get('strategic_fit_rationale')))}</span></li>"
        for item in acquirers[:8]
        if isinstance(item, dict)
    )
    roadmap_rows = "".join(
        f"<li><strong>{html.escape(_text(item.get('phase')))}</strong><span>{html.escape(_text(item.get('output')))}</span></li>"
        for item in solution.get("implementation_roadmap", [])
        if isinstance(item, dict)
    )
    risk_rows = "".join(f"<li>{html.escape(_text(item))}</li>" for item in diligence.get("primary_risks", []) if item)
    next_rows = "".join(f"<li>{html.escape(_text(item))}</li>" for item in diligence.get("diligence_next", []) if item)
    readiness_rows = "".join(
        row(label.replace("_", " ").title(), value)
        for label, value in readiness.items()
    )
    strategic_world_rows = "".join(
        row(label.replace("_", " ").title(), value)
        for label, value in {
            "status": strategic_world.get("status"),
            "domains": ", ".join(strategic_world.get("domains", [])) if isinstance(strategic_world.get("domains"), list) else "",
            "themes": ", ".join(strategic_world.get("cross_domain_themes", [])[:6]) if isinstance(strategic_world.get("cross_domain_themes"), list) else "",
            "top_recommendation": strategic_world.get("top_recommendation", {}).get("option_id") if isinstance(strategic_world.get("top_recommendation"), dict) else "",
            "execution_boundary": strategic_world.get("execution_boundary"),
        }.items()
    )
    score_rows = "".join(row(label.replace("_", " ").title(), value) for label, value in scoring.items())
    finance_rows = "".join(
        f"<li><strong>{html.escape(_text(item.get('ticker')))} - {html.escape(_text(item.get('name')))}</strong><span>Weight {html.escape(_text(item.get('weight_percent')))}%. {html.escape(_text(item.get('weight_basis')))}</span></li>"
        for item in finance.get("candidate_holdings", [])
        if isinstance(item, dict)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body{{margin:0;background:#f6f8fb;color:#172033;font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
    header{{background:#0a1b35;color:#eef6ff;padding:28px 34px;border-bottom:4px solid #00c9b1}}
    main{{max-width:1040px;margin:0 auto;padding:28px 24px 48px}}
    h1{{margin:0 0 8px;font-size:28px}} h2{{margin:26px 0 10px;font-size:18px;color:#0a1b35}} h3{{margin:18px 0 8px;font-size:15px;color:#33506f}}
    .meta{{color:#8fb3d9;font-size:13px}} .summary{{font-size:16px;color:#33506f;margin-top:10px}} .notice{{background:#fff7dc;border:1px solid #e8ce72;color:#5b4814;padding:10px 12px;border-radius:8px;margin:14px 0}}
    table{{width:100%;border-collapse:collapse;background:white;border:1px solid #d9e4ef;border-radius:8px;overflow:hidden}}
    th,td{{padding:10px 12px;border-bottom:1px solid #e5edf5;text-align:left;vertical-align:top}} th{{width:230px;color:#55708f;background:#f0f5fa}}
    ul{{list-style:none;padding:0;margin:0;display:grid;gap:10px}} li{{background:white;border:1px solid #d9e4ef;border-radius:8px;padding:12px 14px}}
    li strong{{display:block;color:#10233d;margin-bottom:4px}} li span{{color:#4f6885}}
    .actions{{display:flex;gap:10px;margin-top:16px}} .actions a{{background:#006ee6;color:white;text-decoration:none;padding:9px 12px;border-radius:7px;font-weight:700}}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <div class="meta">Run {html.escape(_text(payload.get("run_id")))} · {html.escape(_text(payload.get("status")))}</div>
    <p class="summary">{summary}</p>
    <div class="actions"><a href="{html.escape(payload.get("routes", {}).get("download_url", "#"))}">Download JSON</a></div>
  </header>
  <main>
    <div class="notice">Professional portfolio generated from the 30-stage runtime. Market valuation fields remain gated until current live/source-pack evidence is promoted.</div>
    <h2>Executive Summary</h2>
    <table>
      {row("Industry", business.get("industry"))}
      {row("Problem", executive.get("problem"))}
      {row("Solution", executive.get("solution"))}
      {row("Why Now", executive.get("why_now"))}
      {row("Buyer", executive.get("buyer"))}
    </table>
    <h2>Portfolio Thesis</h2>
    <table>
      {row("Route", payload.get("route_selected"))}
      {row("Trend", trend.get("title"))}
      {row("Thesis", thesis.get("statement"))}
      {row("Review", "Operator review required before runtime truth promotion")}
    </table>
    <h2>Scoring & Readiness</h2>
    <table>{score_rows}</table>
    <h2>Market Validation & Valuation</h2>
    <table>
      {row("Validation Status", validation.get("status"))}
      {row("Market Value Status", valuation.get("verified_current_market_value_status"))}
      {row("Strategic Option Value Low", valuation.get("pre_revenue_strategic_option_value_range", {}).get("low") if isinstance(valuation.get("pre_revenue_strategic_option_value_range"), dict) else "")}
      {row("Strategic Option Value High", valuation.get("pre_revenue_strategic_option_value_range", {}).get("high") if isinstance(valuation.get("pre_revenue_strategic_option_value_range"), dict) else "")}
      {row("Basis", valuation.get("pre_revenue_strategic_option_value_range", {}).get("basis") if isinstance(valuation.get("pre_revenue_strategic_option_value_range"), dict) else "")}
    </table>
    <h2>Financial Portfolio Verification</h2>
    <table>
      {row("Verification Status", finance.get("status"))}
      {row("Benchmark", finance.get("benchmark_symbol"))}
      {row("Weight Total", finance.get("weight_total_percent"))}
      {row("Independent Finance Review Ready", finance.get("ready_for_independent_financial_review"))}
      {row("External Public Claims Ready", finance.get("ready_for_external_public_claims"))}
    </table>
    <h3>Candidate Holdings</h3>
    <ul>{finance_rows or "<li>No finance allocation available.</li>"}</ul>
    <h2>Solution Portfolio</h2>
    <table>
      {row("Product", product.get("name"))}
      {row("Category", product.get("category"))}
      {row("Target Gap", product.get("target_gap"))}
      {row("Design Portal Required", design.get("required"))}
      {row("Design Portal Status", design.get("status"))}
    </table>
    <h3>Implementation Roadmap</h3>
    <ul>{roadmap_rows or "<li>No roadmap available.</li>"}</ul>
    <h2>Signals</h2>
    <ul>{signal_rows or "<li>No signals available.</li>"}</ul>
    <h2>Acquirer Strategy</h2>
    <table>
      {row("Status", acquirer_strategy.get("status"))}
      {row("Buyer Need", acquirer_strategy.get("buyer_need_statement"))}
      {row("Fit Logic", acquirer_strategy.get("fit_logic"))}
    </table>
    <ul>{acquirer_rows or "<li>No acquirer matches available.</li>"}</ul>
    <h2>Industry Standard Readiness</h2>
    <table>{readiness_rows}</table>
    <h2>Strategic World Intelligence</h2>
    <table>{strategic_world_rows}</table>
    <h2>Risks & Next Diligence</h2>
    <h3>Risks</h3>
    <ul>{risk_rows or "<li>No risks listed.</li>"}</ul>
    <h3>Next Steps</h3>
    <ul>{next_rows or "<li>No next diligence listed.</li>"}</ul>
  </main>
</body>
</html>"""


def persist_portfolio_artifact(run_spine: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    payload = build_portfolio_artifact_payload(run_spine)
    out_dir = artifact_dir(payload["run_id"], root)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "portfolio_brief.json", payload)
    (out_dir / "portfolio_brief.html").write_text(render_portfolio_html(payload), encoding="utf-8")
    latest = (root or PROJECT_ROOT) / "data" / "continuous_runtime" / "artifacts" / "portfolio" / "latest.json"
    write_json(
        latest,
        {
            "schema_version": "claire.portfolio_artifact_pointer.v1",
            "status": "ready",
            "run_id": payload["run_id"],
            "artifact_id": payload["artifact_id"],
            "title": payload["title"],
            "routes": payload["routes"],
            "updated_at": utc_now(),
        },
    )
    return {
        **payload["routes"],
        "artifact_id": payload["artifact_id"],
        "run_id": payload["run_id"],
        "title": payload["title"],
        "artifact_path": f"data/continuous_runtime/artifacts/portfolio/{payload['run_id']}/portfolio_brief.json",
        "html_path": f"data/continuous_runtime/artifacts/portfolio/{payload['run_id']}/portfolio_brief.html",
    }


def read_portfolio_artifact(run_id: str, root: Path | None = None) -> dict[str, Any]:
    path = artifact_dir(run_id, root) / "portfolio_brief.json"
    return read_json(path, {"status": "missing", "run_id": run_id})


def _latest_or_404() -> tuple[str, dict[str, Any] | None]:
    run_id = latest_run_id()
    if not run_id:
        return "", None
    payload = read_portfolio_artifact(run_id)
    return run_id, payload if payload.get("status") != "missing" else None


@router.get("/api/portfolio/artifacts/latest")
def get_latest_portfolio_artifact() -> dict[str, Any]:
    run_id, payload = _latest_or_404()
    if payload is None:
        return {"status": "missing", "run_id": run_id, "reason": "portfolio artifact has not been created"}
    return payload


@router.get("/api/portfolio/artifacts/{run_id}")
def get_portfolio_artifact(run_id: str) -> dict[str, Any]:
    return read_portfolio_artifact(run_id)


@router.get("/portfolio/artifacts/latest/view", response_class=HTMLResponse)
def view_latest_portfolio_artifact() -> HTMLResponse:
    run_id, payload = _latest_or_404()
    if payload is None:
        return HTMLResponse("<!doctype html><h1>Portfolio artifact missing</h1>", status_code=404)
    return HTMLResponse((artifact_dir(run_id) / "portfolio_brief.html").read_text(encoding="utf-8"))


@router.get("/portfolio/artifacts/{run_id}/view", response_class=HTMLResponse)
def view_portfolio_artifact(run_id: str) -> HTMLResponse:
    path = artifact_dir(run_id) / "portfolio_brief.html"
    if not path.exists():
        return HTMLResponse("<!doctype html><h1>Portfolio artifact missing</h1>", status_code=404)
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.get("/portfolio/artifacts/latest/download")
def download_latest_portfolio_artifact():
    run_id, payload = _latest_or_404()
    if payload is None:
        return JSONResponse({"status": "missing", "run_id": run_id}, status_code=404)
    return download_portfolio_artifact(run_id)


@router.get("/portfolio/artifacts/{run_id}/download")
def download_portfolio_artifact(run_id: str):
    path = artifact_dir(run_id) / "portfolio_brief.json"
    if not path.exists():
        return JSONResponse({"status": "missing", "run_id": run_id}, status_code=404)
    return FileResponse(
        path,
        media_type="application/json",
        filename=f"claire_portfolio_brief_{run_id}.json",
        headers={"Cache-Control": "no-store"},
    )
