"""
Breakthrough Synthesis Engine — dedicated Stage 8 engine for Claire.

Purpose:
- Convert breakthrough scoring into a real synthesis layer.
- Explain why a run is or is not a breakthrough.
- Identify non-obvious pattern combinations, breakthrough mechanisms,
  novelty, falsifiers, validation path, and portfolio implications.
"""

from typing import Any, Dict, List, Optional


class BreakthroughSynthesisEngine:
    """Deterministic breakthrough synthesis analyzer."""

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        scores: Optional[Dict[str, Any]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        market_formation: Optional[Dict[str, Any]] = None,
        opportunity_discovery: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        business_model: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        keywords = keywords or []
        scores = scores or {}
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        opportunity_discovery = opportunity_discovery or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        business_model = business_model or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text or "",
            keywords=keywords,
            domain=domain,
            scores=scores,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            opportunity_discovery=opportunity_discovery,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            connector_sources=connector_sources,
        )

        synthesis_score = self._synthesis_score(signals)
        classification = self._classification(signals, synthesis_score)
        novelty = self._novelty_assessment(signals)
        non_obviousness = self._non_obviousness(signals)
        mechanism = self._breakthrough_mechanism(signals, classification)

        return {
            "status": "success",
            "domain": signals["domain"],
            "sector": signals["sector"],
            "breakthrough_synthesis_score": synthesis_score,
            "breakthrough_classification": classification,
            "novelty_assessment": novelty,
            "non_obviousness": non_obviousness,
            "breakthrough_mechanism": mechanism,
            "pattern_synthesis": self._pattern_synthesis(signals),
            "historical_analogues": self._historical_analogues(signals),
            "falsifiers": self._falsifiers(signals),
            "validation_path": self._validation_path(signals, classification),
            "portfolio_implications": self._portfolio_implications(signals, classification),
            "commercialization_implications": self._commercialization_implications(signals, classification),
            "recommended_next_actions": self._recommended_next_actions(signals, classification),
            "breakthrough_thesis": self._breakthrough_thesis(signals, classification, mechanism, non_obviousness),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, synthesis_score),
        }

    def _signals(
        self,
        text: str,
        keywords: List[str],
        domain: str,
        scores: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        opportunity_discovery: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector = market_gap.get("sector", "general_intelligence") if isinstance(market_gap, dict) else "general_intelligence"
        domain = self._domain_for_sector(sector, domain)

        market = connector_sources.get("market", {}) if isinstance(connector_sources, dict) else {}
        patent = connector_sources.get("patent", {}) if isinstance(connector_sources, dict) else {}
        financial = connector_sources.get("financial", {}) if isinstance(connector_sources, dict) else {}

        combined = f"{text.lower()} {' '.join([str(k).lower() for k in keywords])}"
        hidden_terms = self._count_terms(combined, [
            "hidden", "overlooked", "before", "early", "weak signal", "accelerating",
            "repricing", "withdrawal", "bottleneck", "shortage", "exposure", "stress",
        ])
        synthesis_terms = self._count_terms(combined, [
            "maps", "detects", "forecasts", "recommends", "integrates",
            "benchmarks", "countermeasures", "platform", "workflow", "data",
            "simulation", "scenario", "intelligence",
        ])
        transformation_terms = self._count_terms(combined, [
            "automatically", "autonomous", "decision", "real-time", "real time",
            "enterprise", "risk-transfer", "risk transfer", "underwriting",
            "mission", "patient-flow", "patient flow",
        ])

        return {
            "domain": domain,
            "sector": sector,
            "hidden_signal_term_count": hidden_terms,
            "synthesis_term_count": synthesis_terms,
            "transformation_term_count": transformation_terms,
            "analysis_score": float(scores.get("analysis_score", 0.0) or 0.0),
            "discovery_score": float(scores.get("discovery_score", 0.0) or 0.0),
            "breakthrough_score": float(scores.get("breakthrough_score", 0.0) or 0.0),
            "innovation_score": float(scores.get("innovation_score", 0.0) or 0.0),
            "viability_score": float(scores.get("viability_score", 0.0) or 0.0),
            "feasibility_score": float(scores.get("feasibility_score", 0.0) or 0.0),
            "portfolio_score": float(scores.get("portfolio_score", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": self._nested(market_gap, "strategic_pressure", "score"),
            "trend_direction": self._nested_text(trend_trajectory, "trend_direction", "direction"),
            "market_momentum_score": self._nested(trend_trajectory, "market_momentum", "score"),
            "inevitability_score": self._nested(trend_trajectory, "inevitability_score", "score"),
            "timing_pressure_score": self._nested(trend_trajectory, "timing_pressure", "score"),
            "strategic_window": self._nested_text(trend_trajectory, "strategic_window", "window"),
            "formation_type": self._nested_text(market_formation, "formation_type", "type"),
            "market_stage": self._nested_text(market_formation, "market_stage", "stage"),
            "category_creation_score": self._nested(market_formation, "category_creation_score", "score"),
            "buyer_pull_score": self._nested(market_formation, "buyer_pull", "score"),
            "opportunity_score": self._nested(opportunity_discovery, "opportunity_score", "score"),
            "opportunity_type": self._nested_text(opportunity_discovery, "opportunity_type", "type"),
            "opportunity_priority": self._nested_text(opportunity_discovery, "priority_assessment", "priority"),
            "validation_urgency_score": self._nested(opportunity_discovery, "validation_urgency", "score"),
            "validation_urgency_level": self._nested_text(opportunity_discovery, "validation_urgency", "level"),
            "moat_score": self._nested(moat, "moat_type", "moat_score"),
            "moat_strength": self._nested_text(moat, "moat_type", "strength"),
            "primary_moat": self._nested_text(moat, "moat_type", "primary_moat"),
            "copy_risk_score": self._nested(moat, "copy_risk", "score"),
            "copy_risk_level": self._nested_text(moat, "copy_risk", "level"),
            "risk_score": self._nested(risk_regulation, "risk_profile", "score"),
            "risk_level": self._nested_text(risk_regulation, "risk_profile", "level"),
            "regulatory_exposure_score": self._nested(risk_regulation, "regulation_profile", "score"),
            "blocker_level": self._nested_text(risk_regulation, "blocker_assessment", "blocker_level") or "unknown",
            "revenue_model": self._nested_text(business_model, "revenue_model", "primary_model"),
            "value_capture_score": self._nested(business_model, "value_capture", "score"),
            "buyer_roi_score": self._nested(business_model, "buyer_roi", "score"),
            "commercial_risk_score": self._nested(business_model, "commercial_risk", "score"),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
        }

    def _synthesis_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.14
            + signals["breakthrough_score"] * 0.135
            + signals["opportunity_score"] * 0.125
            + signals["market_gap_confidence"] * 0.080
            + signals["strategic_pressure_score"] * 0.070
            + signals["category_creation_score"] * 0.070
            + signals["buyer_pull_score"] * 0.065
            + signals["inevitability_score"] * 0.060
            + signals["timing_pressure_score"] * 0.050
            + signals["moat_score"] * 0.065
            + signals["value_capture_score"] * 0.050
            + signals["buyer_roi_score"] * 0.035
            + signals["patent_novelty"] * 0.040
            + min(0.040, signals["hidden_signal_term_count"] * 0.008)
            + min(0.040, signals["synthesis_term_count"] * 0.006)
            + min(0.025, signals["transformation_term_count"] * 0.005)
            - signals["risk_score"] * 0.020
            - signals["commercial_risk_score"] * 0.015
            - (0.025 if signals["blocker_level"] == "conditional" else 0.0)
        )

        level = (
            "category_breakthrough" if score >= 0.88 else
            "strategic_breakthrough" if score >= 0.78 else
            "innovation_candidate" if score >= 0.64 else
            "incremental_opportunity"
        )
        return {"level": level, "score": round(score, 4), "drivers": self._synthesis_drivers(signals)}

    def _classification(self, signals: Dict[str, Any], synthesis_score: Dict[str, Any]) -> Dict[str, Any]:
        score = synthesis_score.get("score", 0.0)
        if score >= 0.88:
            classification, confidence_band = "breakthrough", "very_high"
        elif score >= 0.78:
            classification, confidence_band = "breakthrough_candidate", "high"
        elif score >= 0.64:
            classification, confidence_band = "innovation_candidate", "moderate"
        else:
            classification, confidence_band = "opportunity_candidate", "early"

        if signals["blocker_level"] == "conditional" and classification == "breakthrough":
            readiness_modifier = "conditional_breakthrough"
        elif signals["risk_score"] >= 0.70:
            readiness_modifier = "risk_constrained"
        elif signals["feasibility_score"] < 0.62:
            readiness_modifier = "feasibility_constrained"
        else:
            readiness_modifier = "advancable"

        return {
            "classification": classification,
            "confidence_band": confidence_band,
            "readiness_modifier": readiness_modifier,
            "breakthrough_score_used": round(signals["breakthrough_score"], 4),
            "synthesis_score_used": round(score, 4),
        }

    def _novelty_assessment(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.18
            + signals["patent_novelty"] * 0.16
            + signals["category_creation_score"] * 0.14
            + signals["opportunity_score"] * 0.12
            + signals["hidden_signal_term_count"] * 0.018
            + signals["synthesis_term_count"] * 0.012
            + signals["moat_score"] * 0.08
        )
        level = "high" if score >= 0.76 else "moderate" if score >= 0.58 else "low"
        return {
            "level": level,
            "score": round(score, 4),
            "what_is_new": profile["what_is_new"],
            "what_is_not_new": profile["what_is_not_new"],
            "novel_combination": profile["novel_combination"],
        }

    def _non_obviousness(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.15
            + signals["hidden_signal_term_count"] * 0.025
            + signals["opportunity_score"] * 0.13
            + signals["category_creation_score"] * 0.12
            + signals["market_gap_confidence"] * 0.09
            + signals["inevitability_score"] * 0.08
            + signals["moat_score"] * 0.08
            + (0.06 if signals["formation_type"] == "platform_layer" else 0.0)
        )
        level = "strong" if score >= 0.76 else "moderate" if score >= 0.58 else "weak"
        return {
            "level": level,
            "score": round(score, 4),
            "non_obvious_pattern": profile["non_obvious_pattern"],
            "why_others_may_miss_it": profile["why_others_may_miss_it"],
            "signal_combination": self._signal_combination(signals),
        }

    def _breakthrough_mechanism(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.20
            + signals["opportunity_score"] * 0.14
            + signals["category_creation_score"] * 0.12
            + signals["buyer_pull_score"] * 0.11
            + signals["moat_score"] * 0.10
            + signals["value_capture_score"] * 0.09
            + signals["timing_pressure_score"] * 0.07
        )
        return {
            "primary_mechanism": profile["primary_mechanism"],
            "mechanism_score": round(score, 4),
            "mechanism_type": self._mechanism_type(signals),
            "value_creation_path": profile["value_creation_path"],
            "breakthrough_unlock": profile["breakthrough_unlock"],
            "readiness_modifier": classification.get("readiness_modifier"),
        }

    def _pattern_synthesis(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "synthesis_summary": profile["synthesis_summary"],
            "combined_patterns": [
                {"pattern": "market pressure", "evidence": f"strategic pressure {signals['strategic_pressure_score']:.4f}", "interpretation": profile["market_pressure_interpretation"]},
                {"pattern": "timing window", "evidence": f"timing pressure {signals['timing_pressure_score']:.4f}; strategic window {signals['strategic_window'] or 'unknown'}", "interpretation": "the validation window is active before the market becomes fully obvious"},
                {"pattern": "category formation", "evidence": f"category creation {signals['category_creation_score']:.4f}; formation type {signals['formation_type'] or 'unknown'}", "interpretation": "the opportunity can be framed as a platform/category wedge instead of a point feature"},
                {"pattern": "buyer pull", "evidence": f"buyer pull {signals['buyer_pull_score']:.4f}", "interpretation": "the opportunity has a plausible near-term buyer validation path"},
                {"pattern": "defensibility", "evidence": f"moat {signals['moat_score']:.4f}; primary moat {signals['primary_moat'] or 'unknown'}", "interpretation": "the opportunity can compound if data loops and workflow footprint are captured early"},
            ],
            "non_linear_insight": profile["non_linear_insight"],
            "synthesis_risk": self._synthesis_risk(signals),
        }

    def _historical_analogues(self, signals: Dict[str, Any]) -> List[Dict[str, str]]:
        return self._sector_profile(signals["sector"])["historical_analogues"]

    def _falsifiers(self, signals: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        falsifiers = list(profile["falsifiers"])

        if signals["buyer_pull_score"] < 0.70:
            falsifiers.append({
                "falsifier": "Buyer pull is weaker than expected.",
                "test": "Run buyer interviews and pilot-offer tests.",
                "failure_signal": "Buyers agree the problem exists but will not allocate budget, data, or workflow access.",
                "severity": "high",
            })

        if signals["moat_score"] < 0.70:
            falsifiers.append({
                "falsifier": "The visible product is easy for incumbents to copy.",
                "test": "Map incumbent feature roadmaps and compare proprietary data-loop requirements.",
                "failure_signal": "Incumbents can replicate the core outcome without unique data, workflow access, or technical novelty.",
                "severity": "medium",
            })

        if signals["blocker_level"] == "conditional":
            falsifiers.append({
                "falsifier": "Deployment blockers overwhelm the commercial value case.",
                "test": "Run governance, compliance, and buyer-control review before commercialization.",
                "failure_signal": "Controls needed to deploy safely remove the speed, ROI, or usability advantage.",
                "severity": "high",
            })

        return falsifiers

    def _validation_path(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        profile = self._sector_profile(signals["sector"])
        path = [
            {"step": 1, "name": "Prove the non-obvious signal", "objective": profile["validate_signal_objective"], "evidence_required": profile["validate_signal_evidence"], "priority": "critical"},
            {"step": 2, "name": "Prove buyer urgency", "objective": profile["validate_buyer_objective"], "evidence_required": profile["validate_buyer_evidence"], "priority": "critical"},
            {"step": 3, "name": "Prove the workflow wedge", "objective": profile["validate_workflow_objective"], "evidence_required": profile["validate_workflow_evidence"], "priority": "high"},
            {"step": 4, "name": "Prove defensibility", "objective": profile["validate_moat_objective"], "evidence_required": profile["validate_moat_evidence"], "priority": "high"},
            {"step": 5, "name": "Prove economic unlock", "objective": profile["validate_economic_objective"], "evidence_required": profile["validate_economic_evidence"], "priority": "high"},
        ]

        if classification.get("readiness_modifier") == "conditional_breakthrough":
            path.insert(3, {"step": 4, "name": "Resolve conditional blocker", "objective": "Prove the opportunity can be deployed with acceptable controls, governance, and human review.", "evidence_required": ["control plan", "human-review workflow", "deployment policy", "audit evidence"], "priority": "critical"})
            for idx, item in enumerate(path, start=1):
                item["step"] = idx
        return path

    def _portfolio_implications(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        if classification["classification"] in {"breakthrough", "breakthrough_candidate"}:
            binder_priority = "front_of_portfolio"
        elif classification["classification"] == "innovation_candidate":
            binder_priority = "portfolio_candidate"
        else:
            binder_priority = "watchlist"
        return {
            "binder_priority": binder_priority,
            "portfolio_role": profile["portfolio_role"],
            "recommended_artifacts": profile["recommended_artifacts"],
            "design_routing_recommendation": "route_to_design" if classification["classification"] in {"breakthrough", "breakthrough_candidate"} else "validate_before_design",
        }

    def _commercialization_implications(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        if classification["classification"] == "breakthrough":
            motion = profile["commercial_motion"]
        elif classification["classification"] == "breakthrough_candidate":
            motion = "paid validation pilot before enterprise packaging"
        else:
            motion = "research validation before commercial packaging"
        return {
            "recommended_motion": motion,
            "first_offer": profile["first_offer"],
            "expansion_offer": profile["expansion_offer"],
            "commercial_risk_note": self._commercial_risk_note(signals),
        }

    def _recommended_next_actions(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        actions = [
            {"action": profile["first_action"], "purpose": "prove the most important non-obvious breakthrough signal", "priority": "critical"},
            {"action": profile["second_action"], "purpose": "test buyer urgency and workflow fit", "priority": "critical"},
            {"action": "build breakthrough falsification memo", "purpose": "explicitly define what evidence would kill or downgrade the thesis", "priority": "high"},
            {"action": "prepare binder-ready breakthrough thesis", "purpose": "convert synthesis into a portfolio, design, acquirer, and deal artifact", "priority": "high"},
        ]
        if classification.get("readiness_modifier") == "conditional_breakthrough":
            actions.insert(2, {"action": "burn down conditional deployment blocker", "purpose": "protect the breakthrough from being discounted by compliance, safety, or governance concerns", "priority": "critical"})
        return actions

    def _breakthrough_thesis(self, signals: Dict[str, Any], classification: Dict[str, Any], mechanism: Dict[str, Any], non_obviousness: Dict[str, Any]) -> str:
        sector = self._sector_label(signals["sector"])
        cls = self._pretty(classification.get("classification"))
        return (
            f"{sector} is classified as a {cls}. The breakthrough mechanism is: "
            f"{mechanism.get('primary_mechanism')} The non-obvious pattern is: "
            f"{non_obviousness.get('non_obvious_pattern')} The thesis is strongest if buyer urgency, "
            f"workflow adoption, economic value, and proprietary data-loop capture are validated."
        )

    def _sector_profile(self, sector: str) -> Dict[str, Any]:
        profiles = {
            "climate_insurance": {
                "what_is_new": "the synthesis of climate-loss history, exposure concentration, underwriting repricing pressure, market-withdrawal risk, and risk-transfer recommendations into one decision layer",
                "what_is_not_new": "catastrophe modeling, property data, and insurance analytics each exist separately",
                "novel_combination": "underwriting-grade climate exposure intelligence plus repricing signals plus workflow-ready risk-transfer recommendations",
                "non_obvious_pattern": "climate exposure can become an underwriting and market-withdrawal signal before it is fully visible in legacy pricing workflows",
                "why_others_may_miss_it": "incumbents often treat catastrophe modeling, exposure data, pricing, and workflow systems as separate categories",
                "primary_mechanism": "convert fragmented weather-loss, exposure, and underwriting signals into a recurring climate-insurance risk intelligence workflow",
                "value_creation_path": "better repricing confidence, earlier exposure concentration detection, improved risk-transfer planning, and portfolio-level market withdrawal warning",
                "breakthrough_unlock": "validated weather-loss backtesting and underwriter adoption turn climate-risk analytics into a workflow-embedded intelligence platform",
                "market_pressure_interpretation": "insurance markets face accelerating loss, repricing, and withdrawal pressure",
                "synthesis_summary": "The breakthrough is the combination of climate exposure intelligence, underwriting workflow, catastrophe scenario modeling, and risk-transfer planning.",
                "non_linear_insight": "the value is not just better climate data; it is the shift from climate analytics to underwriting-grade decision infrastructure",
                "historical_analogues": [
                    {"analogue": "credit scoring platforms", "similarity": "converted fragmented risk signals into repeatable underwriting infrastructure", "difference": "climate insurance adds geospatial, catastrophe, and market-withdrawal dynamics"},
                    {"analogue": "catastrophe modeling platforms", "similarity": "made complex risk models central to insurance decisions", "difference": "this layer adds repricing pressure, workflow embedding, and risk-transfer recommendations"},
                ],
                "falsifiers": [
                    {"falsifier": "Weather-loss and exposure signals do not improve underwriting decisions.", "test": "Backtest signals against historical losses, pricing changes, and portfolio outcomes.", "failure_signal": "Signals arrive too late, are too noisy, or do not change underwriting actions.", "severity": "critical"},
                    {"falsifier": "Underwriters will not adopt a new workflow layer.", "test": "Run workflow pilots with underwriting teams.", "failure_signal": "Users prefer existing catastrophe tools or manual analysis without recurring platform use.", "severity": "high"},
                ],
                "validate_signal_objective": "Prove climate exposure and weather-loss signals predict repricing or underwriting pressure before legacy workflows react.",
                "validate_signal_evidence": ["weather-loss backtest", "repricing signal accuracy", "market-withdrawal case study"],
                "validate_buyer_objective": "Prove underwriters, reinsurers, and risk teams see urgent budget-worthy pain.",
                "validate_buyer_evidence": ["underwriter interviews", "reinsurer feedback", "budget-owner validation"],
                "validate_workflow_objective": "Prove the product fits underwriting review and portfolio risk workflows.",
                "validate_workflow_evidence": ["underwriter review console test", "workflow acceptance notes", "pilot usage logs"],
                "validate_moat_objective": "Prove climate-loss data loops and exposure benchmarks compound.",
                "validate_moat_evidence": ["data-rights plan", "benchmark dataset", "scenario model history"],
                "validate_economic_objective": "Prove avoided loss exposure, repricing accuracy, or risk-transfer improvement.",
                "validate_economic_evidence": ["ROI model", "pricing improvement case", "risk-transfer benefit estimate"],
                "portfolio_role": "frontier climate-risk platform candidate",
                "recommended_artifacts": ["weather-loss backtest", "exposure benchmark appendix", "underwriting workflow demo", "risk-transfer use-case memo"],
                "commercial_motion": "underwriting design-partner pilot to enterprise insurance-risk platform",
                "first_offer": "climate exposure and repricing pilot",
                "expansion_offer": "enterprise climate insurance risk platform with exposure benchmarks and risk-transfer modules",
                "first_action": "run weather-loss repricing backtest",
                "second_action": "test underwriter workflow adoption",
            },
            "defense_autonomy": {
                "what_is_new": "the synthesis of mission simulation, secure command review, autonomy coordination, human authorization, and audit evidence",
                "what_is_not_new": "drones, sensors, command systems, and autonomy tools exist separately",
                "novel_combination": "human-reviewed mission intelligence that connects autonomous coordination with secure command workflows",
                "non_obvious_pattern": "the breakthrough is not autonomy alone; it is governable autonomy that can be reviewed, simulated, and authorized",
                "why_others_may_miss_it": "teams may focus on platform hardware or autonomy algorithms instead of the reviewable decision layer",
                "primary_mechanism": "convert sensor and mission context into authorized, explainable, and simulation-backed decision support",
                "value_creation_path": "better coordination, faster mission review, controlled autonomy adoption, and auditable command decisions",
                "breakthrough_unlock": "validated simulation and secure review workflows make autonomy deployable under constraints",
                "market_pressure_interpretation": "defense autonomy pressure is rising, but deployment must remain controlled",
                "synthesis_summary": "The breakthrough is the bridge between autonomy, secure command workflows, simulation validation, and human review.",
                "non_linear_insight": "the value is not full autonomy; it is deployable autonomy with trust, authorization, and auditability",
                "historical_analogues": [{"analogue": "fly-by-wire control systems", "similarity": "made complex automation usable through controlled interfaces and safeguards", "difference": "mission autonomy adds adversarial and authorization constraints"}],
                "falsifiers": [{"falsifier": "Mission users do not trust or adopt the review workflow.", "test": "Run simulation-based operator reviews.", "failure_signal": "Operators reject outputs or cannot explain how recommendations support mission decisions.", "severity": "critical"}],
                "validate_signal_objective": "Prove simulation and mission signals improve coordination decisions.",
                "validate_signal_evidence": ["mission simulation test", "scenario performance review", "operator feedback"],
                "validate_buyer_objective": "Prove mission stakeholders need the capability and will support controlled pilots.",
                "validate_buyer_evidence": ["mission stakeholder interviews", "program sponsor feedback", "secure workflow constraints"],
                "validate_workflow_objective": "Prove secure command review and authorization workflows.",
                "validate_workflow_evidence": ["review console test", "authorization workflow map", "audit trail"],
                "validate_moat_objective": "Prove simulation data and secure workflow integration compound.",
                "validate_moat_evidence": ["mission simulation dataset", "secure integration footprint", "review history"],
                "validate_economic_objective": "Prove time-to-decision improvement or mission-risk reduction.",
                "validate_economic_evidence": ["time-to-decision model", "mission risk reduction estimate", "operator feedback"],
                "portfolio_role": "controlled autonomy platform candidate",
                "recommended_artifacts": ["mission simulation memo", "human-review controls appendix", "secure deployment map"],
                "commercial_motion": "controlled defense design-partner pilot to secure platform contract",
                "first_offer": "mission simulation and secure review pilot",
                "expansion_offer": "secure mission intelligence platform",
                "first_action": "run mission simulation validation",
                "second_action": "test secure command review workflow",
            },
            "healthcare_operations": {
                "what_is_new": "the synthesis of capacity, staffing, patient-flow, and operations decision support into a proactive command layer",
                "what_is_not_new": "hospital operations tools, scheduling tools, and EHR data exist separately",
                "novel_combination": "predictive capacity intelligence embedded into operational workflows",
                "non_obvious_pattern": "capacity failure can be detected as an operational signal before it appears as a visible crisis",
                "why_others_may_miss_it": "health systems often see capacity, staffing, and patient flow as separate operational problems",
                "primary_mechanism": "convert historical and live operations patterns into proactive staffing and capacity countermeasures",
                "value_creation_path": "improved throughput, reduced delays, better staffing allocation, and fewer bottlenecks",
                "breakthrough_unlock": "validated patient-flow backtesting and operations workflow adoption",
                "market_pressure_interpretation": "health systems face persistent staffing and capacity pressure",
                "synthesis_summary": "The breakthrough is the operational intelligence layer connecting patient flow, staffing, capacity, and workflow action.",
                "non_linear_insight": "the value is not another dashboard; it is earlier operational intervention",
                "historical_analogues": [{"analogue": "airline operations control centers", "similarity": "turned complex operational signals into coordinated real-time decisions", "difference": "healthcare adds clinical workflow, privacy, and patient-safety constraints"}],
                "falsifiers": [{"falsifier": "Forecasts do not create actionable intervention windows.", "test": "Backtest patient-flow and capacity predictions.", "failure_signal": "Signals are too late or too noisy for operations teams to act.", "severity": "critical"}],
                "validate_signal_objective": "Prove forecasts identify bottlenecks early enough for intervention.",
                "validate_signal_evidence": ["patient-flow backtest", "capacity forecast report", "staffing-risk precision"],
                "validate_buyer_objective": "Prove operations leaders have urgent budget-worthy pain.",
                "validate_buyer_evidence": ["operations interviews", "capacity incident examples", "staffing pain evidence"],
                "validate_workflow_objective": "Prove fit with command-center and staffing workflows.",
                "validate_workflow_evidence": ["workflow test", "operator feedback", "review console usage"],
                "validate_moat_objective": "Prove capacity data loops and workflow footprint compound.",
                "validate_moat_evidence": ["patient-flow dataset", "capacity benchmarks", "workflow usage history"],
                "validate_economic_objective": "Prove throughput, wait-time, staffing, or capacity ROI.",
                "validate_economic_evidence": ["capacity ROI model", "staffing efficiency case", "throughput estimate"],
                "portfolio_role": "healthcare operations platform candidate",
                "recommended_artifacts": ["patient-flow backtest", "capacity ROI memo", "workflow validation appendix"],
                "commercial_motion": "health-system pilot to enterprise operations platform",
                "first_offer": "capacity and patient-flow pilot",
                "expansion_offer": "enterprise healthcare operations intelligence platform",
                "first_action": "run patient-flow backtest",
                "second_action": "test operations workflow adoption",
            },
            "financial_market_intelligence": {
                "what_is_new": "the synthesis of hidden credit, liquidity, and market stress signals into a workflow-ready institutional intelligence layer",
                "what_is_not_new": "market data, risk analytics, and research tools exist separately",
                "novel_combination": "proprietary signal discovery plus regime analysis plus institutional workflow delivery",
                "non_obvious_pattern": "risk repricing signals may be detectable before consensus research or broad market reaction",
                "why_others_may_miss_it": "incumbents may sell data access rather than automated hidden-signal synthesis",
                "primary_mechanism": "convert fragmented market signals into early risk and repricing intelligence",
                "value_creation_path": "earlier risk detection, better research prioritization, and portfolio decision support",
                "breakthrough_unlock": "validated regime backtesting and institutional workflow adoption",
                "market_pressure_interpretation": "market participants face constant pressure to detect risk before repricing",
                "synthesis_summary": "The breakthrough is the hidden-signal layer connecting market data, credit/liquidity stress, and institutional workflow.",
                "non_linear_insight": "the value is not more data; it is earlier interpretation of weak signals",
                "historical_analogues": [{"analogue": "Bloomberg terminal ecosystem", "similarity": "embedded data and analytics into financial workflows", "difference": "this layer focuses on automated hidden-signal synthesis"}],
                "falsifiers": [{"falsifier": "Signals do not outperform obvious market indicators.", "test": "Backtest against historical regimes and consensus benchmarks.", "failure_signal": "Signals add no timing, accuracy, or workflow advantage.", "severity": "critical"}],
                "validate_signal_objective": "Prove signals detect risk or repricing before consensus.",
                "validate_signal_evidence": ["regime backtest", "signal precision report", "false-positive review"],
                "validate_buyer_objective": "Prove institutional buyers need the signal and will use it.",
                "validate_buyer_evidence": ["risk desk interviews", "research workflow feedback", "budget-owner validation"],
                "validate_workflow_objective": "Prove fit with research, risk, and portfolio workflows.",
                "validate_workflow_evidence": ["dashboard usage", "research workflow test", "analyst feedback"],
                "validate_moat_objective": "Prove signal history and benchmark data compound.",
                "validate_moat_evidence": ["signal dataset", "benchmark library", "model governance trail"],
                "validate_economic_objective": "Prove research efficiency or risk-detection ROI.",
                "validate_economic_evidence": ["signal ROI model", "risk avoidance case", "research efficiency case"],
                "portfolio_role": "financial signal intelligence platform candidate",
                "recommended_artifacts": ["regime backtest", "signal precision memo", "institutional workflow appendix"],
                "commercial_motion": "institutional signal pilot to platform subscription",
                "first_offer": "focused signal intelligence pilot",
                "expansion_offer": "institutional market intelligence platform",
                "first_action": "run regime and signal backtest",
                "second_action": "test institutional workflow adoption",
            },
            "industrial_supply_chain": {
                "what_is_new": "the synthesis of supplier dependency, shortage forecasting, procurement countermeasures, and workflow integration",
                "what_is_not_new": "ERP, supply-chain planning, and procurement tools exist separately",
                "novel_combination": "supplier-risk graph plus shortage prediction plus procurement action layer",
                "non_obvious_pattern": "supplier dependencies can reveal production failure before conventional planning alerts",
                "why_others_may_miss_it": "planning systems may optimize known workflows without discovering hidden dependency risk",
                "primary_mechanism": "convert supplier and disruption signals into early procurement and production countermeasures",
                "value_creation_path": "avoided shortages, reduced disruption, better procurement prioritization, and resilience benchmarks",
                "breakthrough_unlock": "validated disruption backtesting and procurement workflow adoption",
                "market_pressure_interpretation": "manufacturers face persistent supply volatility and supplier dependency risk",
                "synthesis_summary": "The breakthrough is the early-warning layer connecting supplier dependencies, shortage forecasts, and procurement workflow.",
                "non_linear_insight": "the value is not planning automation; it is hidden supplier-risk discovery before disruption",
                "historical_analogues": [{"analogue": "credit bureau risk infrastructure", "similarity": "turned distributed risk signals into decision infrastructure", "difference": "supplier risk adds operational, timing, and dependency graph dynamics"}],
                "falsifiers": [{"falsifier": "Shortage signals are not early or accurate enough to change procurement action.", "test": "Backtest against historical disruptions.", "failure_signal": "Signals are too late, too noisy, or not actionable.", "severity": "critical"}],
                "validate_signal_objective": "Prove supplier and shortage signals are predictive.",
                "validate_signal_evidence": ["disruption backtest", "shortage forecast precision", "supplier-risk event study"],
                "validate_buyer_objective": "Prove procurement teams feel urgent budget-worthy pain.",
                "validate_buyer_evidence": ["procurement interviews", "supplier-risk examples", "production disruption cases"],
                "validate_workflow_objective": "Prove fit with procurement and planning workflows.",
                "validate_workflow_evidence": ["ERP integration test", "operator workflow notes", "recommendation review"],
                "validate_moat_objective": "Prove supplier data loops and workflow integration compound.",
                "validate_moat_evidence": ["supplier graph", "shortage benchmark", "workflow footprint"],
                "validate_economic_objective": "Prove avoided disruption and procurement efficiency.",
                "validate_economic_evidence": ["avoided disruption model", "shortage cost estimate", "procurement efficiency case"],
                "portfolio_role": "industrial resilience platform candidate",
                "recommended_artifacts": ["disruption backtest", "supplier-risk graph appendix", "procurement ROI memo"],
                "commercial_motion": "procurement pilot to enterprise resilience platform",
                "first_offer": "supplier-risk and shortage forecasting pilot",
                "expansion_offer": "enterprise industrial resilience intelligence platform",
                "first_action": "run supplier-risk backtest",
                "second_action": "test procurement workflow adoption",
            },
            "energy_infrastructure": {
                "what_is_new": "the synthesis of grid events, asset risk, demand pressure, bottleneck forecasting, and resilience planning",
                "what_is_not_new": "grid monitoring, asset management, and utility planning tools exist separately",
                "novel_combination": "asset-risk intelligence plus demand forecasts plus resilience planning workflow",
                "non_obvious_pattern": "infrastructure bottlenecks may become visible in weak signals before operational failure",
                "why_others_may_miss_it": "utility systems may monitor infrastructure without synthesizing investment and resilience priorities",
                "primary_mechanism": "convert grid, asset, and demand signals into resilience investment and planning intelligence",
                "value_creation_path": "better asset prioritization, earlier bottleneck detection, and improved resilience planning",
                "breakthrough_unlock": "validated grid-event backtesting and utility workflow adoption",
                "market_pressure_interpretation": "utilities face demand growth, modernization pressure, and infrastructure constraints",
                "synthesis_summary": "The breakthrough is the resilience intelligence layer connecting grid events, asset risk, and planning decisions.",
                "non_linear_insight": "the value is not more grid monitoring; it is earlier capital and resilience prioritization",
                "historical_analogues": [{"analogue": "predictive maintenance platforms", "similarity": "used asset data to anticipate failure", "difference": "grid resilience adds system-level bottleneck and planning complexity"}],
                "falsifiers": [{"falsifier": "Grid and asset signals do not improve planning decisions.", "test": "Backtest against historical grid events and asset-risk outcomes.", "failure_signal": "Signals do not change investment or resilience planning.", "severity": "critical"}],
                "validate_signal_objective": "Prove grid and asset-risk signals are predictive.",
                "validate_signal_evidence": ["grid event backtest", "asset-risk calibration", "demand forecast accuracy"],
                "validate_buyer_objective": "Prove utility planners need the intelligence and can act on it.",
                "validate_buyer_evidence": ["utility interviews", "planning use cases", "asset-risk pain evidence"],
                "validate_workflow_objective": "Prove fit with utility planning workflows.",
                "validate_workflow_evidence": ["planning workflow test", "operator review", "resilience dashboard usage"],
                "validate_moat_objective": "Prove grid-event data loops and planning workflow footprint compound.",
                "validate_moat_evidence": ["grid event dataset", "asset-risk benchmark", "planning workflow footprint"],
                "validate_economic_objective": "Prove resilience investment value or avoided outage risk.",
                "validate_economic_evidence": ["resilience ROI model", "asset-risk prioritization case", "planning efficiency estimate"],
                "portfolio_role": "energy infrastructure intelligence platform candidate",
                "recommended_artifacts": ["grid-event backtest", "asset-risk appendix", "resilience planning memo"],
                "commercial_motion": "utility planning pilot to infrastructure intelligence platform",
                "first_offer": "grid bottleneck and resilience planning pilot",
                "expansion_offer": "enterprise energy infrastructure intelligence platform",
                "first_action": "run grid-event backtest",
                "second_action": "test utility planning workflow adoption",
            },
        }

        default = {
            "what_is_new": "the synthesis of weak signals, opportunity gaps, workflow context, and portfolio-ready recommendations",
            "what_is_not_new": "search, analytics, dashboards, and strategy workflows exist separately",
            "novel_combination": "automated opportunity discovery plus validation and design routing",
            "non_obvious_pattern": "valuable opportunities can emerge from signal combinations that are not visible through keyword search",
            "why_others_may_miss_it": "teams may search for known terms rather than synthesizing hidden cross-domain patterns",
            "primary_mechanism": "convert fragmented signals into validated opportunity and design pathways",
            "value_creation_path": "faster opportunity discovery, better validation, and portfolio-ready packaging",
            "breakthrough_unlock": "validated historical examples and buyer workflow adoption",
            "market_pressure_interpretation": "organizations face pressure to find non-obvious opportunities faster",
            "synthesis_summary": "The breakthrough is the opportunity intelligence layer connecting signals, gaps, validation, design, and portfolio packaging.",
            "non_linear_insight": "the value is not search; it is synthesis of hidden patterns into buildable opportunities",
            "historical_analogues": [{"analogue": "enterprise search platforms", "similarity": "made knowledge easier to access", "difference": "Claire synthesizes opportunity pathways instead of returning documents"}],
            "falsifiers": [{"falsifier": "The system does not find non-obvious opportunities beyond manual search.", "test": "Compare output against expert research baselines.", "failure_signal": "Outputs are obvious, generic, or already known.", "severity": "critical"}],
            "validate_signal_objective": "Prove the system finds non-obvious patterns.",
            "validate_signal_evidence": ["historical opportunity benchmark", "expert review", "false-positive analysis"],
            "validate_buyer_objective": "Prove strategy or innovation teams need the workflow.",
            "validate_buyer_evidence": ["buyer interviews", "workflow pain examples", "budget-owner validation"],
            "validate_workflow_objective": "Prove fit with discovery, design, and portfolio workflows.",
            "validate_workflow_evidence": ["workflow test", "artifact review", "user acceptance"],
            "validate_moat_objective": "Prove signal history and workflow data loops compound.",
            "validate_moat_evidence": ["signal dataset", "taxonomy", "workflow footprint"],
            "validate_economic_objective": "Prove time savings or opportunity quality improvement.",
            "validate_economic_evidence": ["time savings", "opportunity quality score", "portfolio value case"],
            "portfolio_role": "cross-sector opportunity platform candidate",
            "recommended_artifacts": ["historical benchmark", "opportunity thesis", "workflow validation memo"],
            "commercial_motion": "focused discovery pilot to enterprise platform subscription",
            "first_offer": "opportunity discovery pilot",
            "expansion_offer": "enterprise opportunity intelligence platform",
            "first_action": "run historical opportunity benchmark",
            "second_action": "test buyer workflow adoption",
        }
        return profiles.get(sector, default)

    def _synthesis_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []
        if signals["opportunity_score"] >= 0.80:
            drivers.append("exceptional opportunity discovery score")
        if signals["breakthrough_score"] >= 0.85:
            drivers.append("high existing breakthrough score")
        if signals["category_creation_score"] >= 0.78:
            drivers.append("category/platform formation signal")
        if signals["buyer_pull_score"] >= 0.78:
            drivers.append("strong buyer pull")
        if signals["timing_pressure_score"] >= 0.70:
            drivers.append("active timing pressure")
        if signals["moat_score"] >= 0.75:
            drivers.append("strong defensibility signal")
        if signals["value_capture_score"] >= 0.75:
            drivers.append("strong value capture")
        if signals["hidden_signal_term_count"] > 0:
            drivers.append("input describes hidden or early signals")
        return drivers or ["baseline opportunity and innovation signals"]

    def _signal_combination(self, signals: Dict[str, Any]) -> List[str]:
        return [
            f"market gap confidence {signals['market_gap_confidence']:.4f}",
            f"opportunity score {signals['opportunity_score']:.4f}",
            f"buyer pull {signals['buyer_pull_score']:.4f}",
            f"category creation {signals['category_creation_score']:.4f}",
            f"timing pressure {signals['timing_pressure_score']:.4f}",
            f"moat score {signals['moat_score']:.4f}",
            f"value capture {signals['value_capture_score']:.4f}",
        ]

    def _mechanism_type(self, signals: Dict[str, Any]) -> str:
        if signals["formation_type"] == "platform_layer" and signals["primary_moat"] == "data_advantage":
            return "platform_plus_data_moat"
        if signals["primary_moat"] == "workflow_lock_in":
            return "workflow_lock_in_breakthrough"
        if signals["timing_pressure_score"] >= 0.75:
            return "timing_window_breakthrough"
        if signals["category_creation_score"] >= 0.78:
            return "category_creation_breakthrough"
        return "applied_intelligence_breakthrough"

    def _synthesis_risk(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        risks = []
        if signals["blocker_level"] == "conditional":
            risks.append("conditional blocker may delay or discount the breakthrough")
        if signals["moat_score"] < 0.70:
            risks.append("defensibility may be weaker than the opportunity thesis implies")
        if signals["buyer_roi_score"] < 0.70:
            risks.append("buyer ROI still needs stronger quantification")
        if signals["commercial_risk_score"] >= 0.42:
            risks.append("commercial execution may be harder than signal strength suggests")
        level = "high" if len(risks) >= 3 else "moderate" if risks else "low"
        return {"level": level, "risks": risks or ["no major deterministic synthesis risk surfaced"]}

    def _commercial_risk_note(self, signals: Dict[str, Any]) -> str:
        if signals["blocker_level"] == "conditional":
            return "Commercialization should start as controlled advisory validation until blocker mitigation is documented."
        if signals["commercial_risk_score"] >= 0.42:
            return "Commercialization should explicitly test procurement, implementation, and budget-owner friction."
        return "Commercialization can proceed through focused validation and paid pilot packaging."

    def _confidence(self, signals: Dict[str, Any], synthesis_score: Dict[str, Any]) -> float:
        return round(self._bounded(
            0.20
            + synthesis_score.get("score", 0.0) * 0.18
            + signals["opportunity_score"] * 0.10
            + signals["breakthrough_score"] * 0.10
            + signals["market_gap_confidence"] * 0.08
            + signals["category_creation_score"] * 0.07
            + signals["buyer_pull_score"] * 0.07
            + signals["moat_score"] * 0.06
            + signals["value_capture_score"] * 0.05
            - signals["risk_score"] * 0.025
        ), 4)

    def _domain_for_sector(self, sector: str, fallback: str) -> str:
        return {
            "climate_insurance": "insurance",
            "defense_autonomy": "technology",
            "healthcare_operations": "healthcare",
            "industrial_supply_chain": "industrial",
            "energy_infrastructure": "energy",
            "financial_market_intelligence": "finance",
        }.get(sector, fallback or "general")

    def _sector_label(self, sector: str) -> str:
        return str(sector or "general").replace("_", " ")

    def _pretty(self, value: Any) -> str:
        return str(value or "").replace("_", " ").replace("-", " ")

    def _count_terms(self, text: str, terms: List[str]) -> int:
        return sum(1 for term in terms if term.lower() in text)

    def _bounded(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))

    def _nested(self, obj: Dict[str, Any], *path: str) -> float:
        cur: Any = obj
        for key in path:
            if not isinstance(cur, dict):
                return 0.0
            cur = cur.get(key, 0.0)
        try:
            return float(cur or 0.0)
        except Exception:
            return 0.0

    def _nested_text(self, obj: Dict[str, Any], *path: str) -> str:
        cur: Any = obj
        for key in path:
            if not isinstance(cur, dict):
                return ""
            cur = cur.get(key, "")
        return str(cur or "")
