"""
Technical Feasibility Engine — dedicated Stage 9 engine for Claire.

v5.24:
- Converts Stage 9 from score-only feasibility into a dedicated technical
  feasibility engine.
- Evaluates architecture readiness, implementation complexity, integration
  readiness, data readiness, validation burden, deployment controls, and
  blocker burn-down.
- Produces sector-aware technical feasibility language for climate insurance,
  defense autonomy, healthcare operations, financial market intelligence,
  industrial supply chain, energy infrastructure, and general intelligence.
"""

from typing import Any, Dict, List, Optional


class TechnicalFeasibilityEngine:
    """
    Deterministic technical feasibility analyzer.

    This engine does not replace the orchestrator's numeric feasibility score.
    It explains what must be true technically for the opportunity to become
    buildable, deployable, and diligence-ready.
    """

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
        breakthrough_synthesis: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        business_model: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = text or ""
        keywords = keywords or []
        scores = scores or {}
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        opportunity_discovery = opportunity_discovery or {}
        breakthrough_synthesis = breakthrough_synthesis or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        business_model = business_model or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            domain=domain,
            scores=scores,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            opportunity_discovery=opportunity_discovery,
            breakthrough_synthesis=breakthrough_synthesis,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            connector_sources=connector_sources,
        )

        feasibility = self._technical_feasibility_score(signals)
        classification = self._classification(signals, feasibility)
        architecture = self._architecture_readiness(signals)
        implementation = self._implementation_complexity(signals)
        integration = self._integration_readiness(signals)
        data = self._data_readiness(signals)
        validation = self._validation_burden(signals)
        controls = self._deployment_controls(signals)
        risks = self._technical_risks(signals, classification)
        roadmap = self._feasibility_roadmap(signals, classification)

        return {
            "status": "success",
            "domain": signals["domain"],
            "sector": signals["sector"],
            "technical_feasibility_score": feasibility,
            "feasibility_classification": classification,
            "architecture_readiness": architecture,
            "implementation_complexity": implementation,
            "integration_readiness": integration,
            "data_readiness": data,
            "validation_burden": validation,
            "deployment_controls": controls,
            "technical_risks": risks,
            "blocker_burndown_plan": self._blocker_burndown_plan(signals, classification),
            "feasibility_roadmap": roadmap,
            "prototype_plan": self._prototype_plan(signals, classification),
            "diligence_readiness": self._diligence_readiness(signals, feasibility, risks),
            "recommended_next_actions": self._recommended_next_actions(signals, classification, risks),
            "technical_feasibility_thesis": self._technical_feasibility_thesis(signals, feasibility, classification),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, feasibility),
        }

    # =========================
    # SIGNALS
    # =========================
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
        breakthrough_synthesis: Dict[str, Any],
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

        architecture_terms = self._count_terms(combined, [
            "platform", "architecture", "system", "engine", "module", "api", "integration", "workflow", "service"
        ])
        data_terms = self._count_terms(combined, [
            "data", "dataset", "sensor", "claims", "weather", "exposure", "simulation", "market", "patient", "supplier", "grid"
        ])
        model_terms = self._count_terms(combined, [
            "model", "forecast", "prediction", "scenario", "simulation", "risk score", "detector", "recommendation"
        ])
        security_terms = self._count_terms(combined, [
            "secure", "audit", "authorization", "governance", "compliance", "privacy", "encrypted", "restricted", "override"
        ])
        complexity_terms = self._count_terms(combined, [
            "real-time", "real time", "edge", "autonomous", "mission", "clinical", "regulated", "critical", "low-latency", "low latency"
        ])

        return {
            "domain": domain,
            "sector": sector,
            "architecture_term_count": architecture_terms,
            "data_term_count": data_terms,
            "model_term_count": model_terms,
            "security_term_count": security_terms,
            "complexity_term_count": complexity_terms,
            "analysis_score": float(scores.get("analysis_score", 0.0) or 0.0),
            "discovery_score": float(scores.get("discovery_score", 0.0) or 0.0),
            "breakthrough_score": float(scores.get("breakthrough_score", 0.0) or 0.0),
            "breakthrough_synthesis_score": float(scores.get("breakthrough_synthesis_score", 0.0) or 0.0),
            "innovation_score": float(scores.get("innovation_score", 0.0) or 0.0),
            "viability_score": float(scores.get("viability_score", 0.0) or 0.0),
            "buildability_score": float(scores.get("buildability_score", 0.0) or 0.0),
            "feasibility_score": float(scores.get("feasibility_score", 0.0) or 0.0),
            "portfolio_score": float(scores.get("portfolio_score", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": self._nested(market_gap, "strategic_pressure", "score"),
            "design_implication_count": len(market_gap.get("design_implications", [])) if isinstance(market_gap, dict) else 0,
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "timing_pressure_score": self._nested(trend_trajectory, "timing_pressure", "score"),
            "market_momentum_score": self._nested(trend_trajectory, "market_momentum", "score"),
            "formation_type": self._nested_text(market_formation, "formation_type", "type"),
            "market_stage": self._nested_text(market_formation, "market_stage", "stage"),
            "category_creation_score": self._nested(market_formation, "category_creation_score", "score"),
            "buyer_pull_score": self._nested(market_formation, "buyer_pull", "score"),
            "ecosystem_requirement_count": len(market_formation.get("ecosystem_requirements", [])) if isinstance(market_formation, dict) else 0,
            "opportunity_score": self._nested(opportunity_discovery, "opportunity_score", "score"),
            "opportunity_priority_score": self._nested(opportunity_discovery, "priority_assessment", "score"),
            "validation_urgency_score": self._nested(opportunity_discovery, "validation_urgency", "score"),
            "breakthrough_classification": self._nested_text(breakthrough_synthesis, "breakthrough_classification", "classification"),
            "breakthrough_readiness_modifier": self._nested_text(breakthrough_synthesis, "breakthrough_classification", "readiness_modifier"),
            "novelty_score": self._nested(breakthrough_synthesis, "novelty_assessment", "score"),
            "non_obviousness_score": self._nested(breakthrough_synthesis, "non_obviousness", "score"),
            "mechanism_score": self._nested(breakthrough_synthesis, "breakthrough_mechanism", "mechanism_score"),
            "moat_score": self._nested(moat, "moat_type", "moat_score"),
            "primary_moat": self._nested_text(moat, "moat_type", "primary_moat"),
            "copy_risk_score": self._nested(moat, "copy_risk", "score"),
            "risk_score": self._nested(risk_regulation, "risk_profile", "score"),
            "risk_level": self._nested_text(risk_regulation, "risk_profile", "level"),
            "regulatory_exposure_score": self._nested(risk_regulation, "regulation_profile", "score"),
            "regulatory_exposure": self._nested_text(risk_regulation, "regulation_profile", "exposure"),
            "blocker_level": self._nested_text(risk_regulation, "blocker_assessment", "blocker_level") or "unknown",
            "compliance_requirement_count": len(risk_regulation.get("compliance_requirements", [])) if isinstance(risk_regulation, dict) else 0,
            "deployment_constraint_count": len(risk_regulation.get("deployment_constraints", [])) if isinstance(risk_regulation, dict) else 0,
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

    # =========================
    # CORE ASSESSMENTS
    # =========================
    def _technical_feasibility_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        sector_adjustment = self._sector_profile(signals["sector"])["feasibility_adjustment"]
        blocker_penalty = 0.060 if signals["blocker_level"] == "conditional" else 0.025 if signals["blocker_level"] == "manageable" else 0.0
        complexity_penalty = min(0.065, signals["complexity_term_count"] * 0.010)
        control_credit = min(0.050, signals["security_term_count"] * 0.008 + signals["compliance_requirement_count"] * 0.004)

        score = self._bounded(
            0.15
            + signals["feasibility_score"] * 0.180
            + signals["buildability_score"] * 0.145
            + signals["viability_score"] * 0.080
            + signals["market_gap_confidence"] * 0.070
            + signals["opportunity_score"] * 0.060
            + signals["breakthrough_synthesis_score"] * 0.055
            + signals["mechanism_score"] * 0.040
            + signals["moat_score"] * 0.045
            + (1.0 - signals["copy_risk_score"]) * 0.020
            + signals["architecture_term_count"] * 0.006
            + signals["data_term_count"] * 0.006
            + signals["model_term_count"] * 0.006
            + control_credit
            + sector_adjustment
            - signals["risk_score"] * 0.030
            - signals["regulatory_exposure_score"] * 0.018
            - signals["commercial_risk_score"] * 0.018
            - blocker_penalty
            - complexity_penalty
        )

        level = "high" if score >= 0.78 else "moderate" if score >= 0.62 else "early" if score >= 0.48 else "weak"
        return {
            "level": level,
            "score": round(score, 4),
            "drivers": self._feasibility_drivers(signals),
        }

    def _classification(self, signals: Dict[str, Any], feasibility: Dict[str, Any]) -> Dict[str, Any]:
        score = feasibility.get("score", 0.0)
        if signals["blocker_level"] == "conditional":
            if score >= 0.72:
                state = "technically_feasible_with_controls"
            elif score >= 0.58:
                state = "conditionally_feasible"
            else:
                state = "needs_control_burndown"
            modifier = "control_gated"
        elif score >= 0.78:
            state = "technically_feasible"
            modifier = "clear_to_prototype"
        elif score >= 0.62:
            state = "feasible_with_validation"
            modifier = "prototype_before_scale"
        elif score >= 0.48:
            state = "early_feasibility"
            modifier = "research_before_build"
        else:
            state = "not_yet_feasible"
            modifier = "major_unknowns"

        return {
            "state": state,
            "readiness_modifier": modifier,
            "prototype_recommendation": self._prototype_recommendation(state),
            "deployment_posture": self._deployment_posture(signals, state),
            "score_used": round(score, 4),
        }

    def _architecture_readiness(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.22
            + signals["buildability_score"] * 0.16
            + signals["architecture_term_count"] * 0.020
            + signals["design_implication_count"] * 0.020
            + signals["ecosystem_requirement_count"] * 0.008
            + profile["architecture_adjustment"]
            - signals["complexity_term_count"] * 0.008
        )
        return {
            "level": self._level(score),
            "score": round(score, 4),
            "recommended_architecture": profile["recommended_architecture"],
            "required_components": profile["required_components"],
            "architecture_notes": profile["architecture_notes"],
        }

    def _implementation_complexity(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.22
            + signals["complexity_term_count"] * 0.035
            + signals["regulatory_exposure_score"] * 0.10
            + signals["deployment_constraint_count"] * 0.015
            + signals["ecosystem_requirement_count"] * 0.012
            + profile["complexity_adjustment"]
            - signals["buildability_score"] * 0.060
        )
        level = "high" if score >= 0.68 else "moderate" if score >= 0.45 else "low"
        return {
            "level": level,
            "score": round(score, 4),
            "complexity_drivers": profile["complexity_drivers"],
            "implementation_notes": profile["implementation_notes"],
        }

    def _integration_readiness(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.18
            + signals["architecture_term_count"] * 0.016
            + signals["market_gap_confidence"] * 0.080
            + signals["buyer_pull_score"] * 0.070
            + signals["moat_score"] * 0.065
            + signals["ecosystem_requirement_count"] * 0.010
            + profile["integration_adjustment"]
            - signals["complexity_term_count"] * 0.006
        )
        return {
            "level": self._level(score),
            "score": round(score, 4),
            "integration_points": profile["integration_points"],
            "integration_risks": profile["integration_risks"],
        }

    def _data_readiness(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.16
            + signals["data_term_count"] * 0.020
            + signals["model_term_count"] * 0.014
            + signals["market_gap_confidence"] * 0.060
            + signals["patent_activity"] * 0.035
            + signals["moat_score"] * 0.055
            + profile["data_adjustment"]
        )
        return {
            "level": self._level(score),
            "score": round(score, 4),
            "required_datasets": profile["required_datasets"],
            "data_gaps": profile["data_gaps"],
            "data_rights_notes": profile["data_rights_notes"],
        }

    def _validation_burden(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        score = self._bounded(
            0.20
            + signals["risk_score"] * 0.090
            + signals["regulatory_exposure_score"] * 0.080
            + signals["complexity_term_count"] * 0.018
            + signals["deployment_constraint_count"] * 0.018
            + profile["validation_adjustment"]
            - signals["feasibility_score"] * 0.050
        )
        level = "high" if score >= 0.64 else "moderate" if score >= 0.42 else "low"
        return {
            "level": level,
            "score": round(score, 4),
            "validation_requirements": profile["validation_requirements"],
            "minimum_evidence_pack": profile["minimum_evidence_pack"],
        }

    def _deployment_controls(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        controls = list(profile["deployment_controls"])
        if signals["blocker_level"] == "conditional":
            controls.extend([
                "documented blocker mitigation plan",
                "human-review gate before operational use",
                "advisory or shadow-mode launch before automation",
                "audit evidence retained for all recommendations",
            ])
        return {
            "control_level": "strict" if signals["blocker_level"] == "conditional" or signals["regulatory_exposure_score"] >= 0.55 else "standard",
            "controls": self._dedupe(controls),
            "deployment_mode": profile["deployment_mode"] if signals["blocker_level"] != "conditional" else profile["controlled_deployment_mode"],
        }

    def _technical_risks(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        risks = list(profile["technical_risks"])
        if signals["blocker_level"] == "conditional":
            risks.append({
                "risk": "conditional deployment blocker",
                "impact": "deployment cannot be treated as fully build-ready until controls, allowed-use boundaries, and review gates are proven",
                "severity": "high",
                "mitigation": "run blocker burn-down before pilot expansion",
            })
        if signals["buyer_roi_score"] < 0.65:
            risks.append({
                "risk": "ROI instrumentation gap",
                "impact": "technical success may not translate into buyer or deal readiness without measurable impact evidence",
                "severity": "medium",
                "mitigation": "instrument pilot metrics before launch",
            })
        if signals["moat_score"] < 0.70:
            risks.append({
                "risk": "defensibility implementation gap",
                "impact": "the build may be technically possible but not technically differentiated enough for premium strategic value",
                "severity": "medium",
                "mitigation": "capture proprietary data loops, integration depth, and workflow telemetry during pilot",
            })
        return risks

    def _blocker_burndown_plan(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        if signals["blocker_level"] != "conditional":
            return [{
                "step": "monitor controls",
                "objective": "keep deployment controls proportional to risk",
                "evidence_required": "standard audit log and model monitoring evidence",
                "priority": "medium",
            }]

        return [
            {
                "step": "define allowed-use boundary",
                "objective": profile["allowed_use_objective"],
                "evidence_required": "written allowed-use / restricted-use policy",
                "priority": "critical",
            },
            {
                "step": "prove human-review workflow",
                "objective": profile["human_review_objective"],
                "evidence_required": "review-console test, authorization log, and operator acceptance notes",
                "priority": "critical",
            },
            {
                "step": "run shadow-mode validation",
                "objective": profile["shadow_mode_objective"],
                "evidence_required": "shadow-mode comparison against human decisions and failure-mode review",
                "priority": "critical",
            },
            {
                "step": "package audit evidence",
                "objective": "make controls reviewable by buyer, diligence, and compliance stakeholders",
                "evidence_required": "trace logs, versioned assumptions, source lineage, and decision evidence",
                "priority": "high",
            },
        ]

    def _feasibility_roadmap(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        profile = self._sector_profile(signals["sector"])
        roadmap = [
            {"phase": 1, "name": "Feasibility contract", "objective": "Lock input/output contracts, scoring schema, evidence trace, and no-go criteria.", "deliverables": ["I/O contracts", "schema tests", "no-go criteria", "trace requirements"], "priority": "critical"},
            {"phase": 2, "name": "Data foundation", "objective": profile["data_foundation_objective"], "deliverables": profile["data_foundation_deliverables"], "priority": "critical"},
            {"phase": 3, "name": "Model validation", "objective": profile["model_validation_objective"], "deliverables": profile["model_validation_deliverables"], "priority": "high"},
            {"phase": 4, "name": "Workflow prototype", "objective": profile["workflow_prototype_objective"], "deliverables": profile["workflow_prototype_deliverables"], "priority": "high"},
            {"phase": 5, "name": "Control and audit layer", "objective": profile["control_layer_objective"], "deliverables": profile["control_layer_deliverables"], "priority": "critical" if signals["blocker_level"] == "conditional" else "high"},
            {"phase": 6, "name": "Pilot readiness review", "objective": "Decide whether the system can move into controlled pilot, binder export, or deal diligence.", "deliverables": ["pilot scorecard", "risk register", "evidence pack", "go/no-go memo"], "priority": "high"},
        ]
        return roadmap

    def _prototype_plan(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "prototype_type": profile["prototype_type"],
            "prototype_scope": profile["prototype_scope"],
            "success_metrics": profile["prototype_success_metrics"],
            "recommended_mode": "shadow_mode_or_advisory" if signals["blocker_level"] == "conditional" else profile["prototype_mode"],
        }

    def _diligence_readiness(self, signals: Dict[str, Any], feasibility: Dict[str, Any], risks: List[Dict[str, str]]) -> Dict[str, Any]:
        score = self._bounded(
            feasibility.get("score", 0.0) * 0.52
            + signals["portfolio_score"] * 0.16
            + signals["moat_score"] * 0.10
            + signals["buyer_roi_score"] * 0.08
            + (1.0 - signals["risk_score"]) * 0.07
            - (0.08 if signals["blocker_level"] == "conditional" else 0.0)
        )
        state = "diligence_ready_with_controls" if score >= 0.72 and signals["blocker_level"] == "conditional" else "diligence_ready" if score >= 0.74 else "pilot_evidence_needed" if score >= 0.58 else "not_diligence_ready"
        return {
            "state": state,
            "score": round(score, 4),
            "critical_open_items": [risk["risk"] for risk in risks if risk.get("severity") in {"critical", "high"}],
        }

    def _recommended_next_actions(self, signals: Dict[str, Any], classification: Dict[str, Any], risks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        actions = [
            {"action": profile["first_action"], "purpose": "prove the highest-leverage technical assumption", "priority": "critical"},
            {"action": profile["second_action"], "purpose": "convert feasibility into pilot-ready evidence", "priority": "high"},
            {"action": "instrument pilot metrics", "purpose": "connect technical performance to ROI, workflow adoption, and diligence evidence", "priority": "high"},
            {"action": "create technical risk register", "purpose": "track failure modes, controls, owners, and mitigation evidence", "priority": "high"},
        ]
        if signals["blocker_level"] == "conditional":
            actions.insert(1, {"action": "complete control-gated deployment plan", "purpose": "resolve conditional blocker before broader build or commercialization", "priority": "critical"})
        return actions

    def _technical_feasibility_thesis(self, signals: Dict[str, Any], feasibility: Dict[str, Any], classification: Dict[str, Any]) -> str:
        sector = self._pretty(signals["sector"])
        return (
            f"{sector} is {classification.get('state')} with {feasibility.get('level')} technical feasibility "
            f"and a score of {feasibility.get('score')}. The build should proceed through "
            f"{classification.get('deployment_posture')}, with the main technical proof centered on "
            f"data readiness, integration depth, validation quality, and deployment controls."
        )

    # =========================
    # SECTOR PROFILES
    # =========================
    def _sector_profile(self, sector: str) -> Dict[str, Any]:
        profiles = {
            "defense_autonomy": {
                "feasibility_adjustment": -0.020,
                "architecture_adjustment": 0.045,
                "complexity_adjustment": 0.140,
                "integration_adjustment": 0.055,
                "data_adjustment": 0.035,
                "validation_adjustment": 0.130,
                "recommended_architecture": "secure modular mission-intelligence architecture with simulation, review, authorization, and audit layers",
                "required_components": ["mission_context_ingestion", "mission_simulation_engine", "coordination_risk_model", "secure_command_adapter", "human_override_layer", "mission_audit_service"],
                "architecture_notes": "Defense/autonomy feasibility depends on simulation fidelity, secure command integration, authorization state, allowed-use enforcement, and audit traceability.",
                "complexity_drivers": ["secure mission context", "simulation fidelity", "low-latency constraints", "human authorization", "allowed-use boundaries"],
                "implementation_notes": "Start in advisory/shadow mode. Avoid operational automation until mission-use controls and operator review are validated.",
                "integration_points": ["secure command workflow", "mission simulation environment", "sensor/context ingestion", "authorization and audit systems"],
                "integration_risks": ["classified or restricted environments", "operator trust", "secure deployment boundary", "command workflow fit"],
                "required_datasets": ["mission simulation scenarios", "sensor/context records", "operator review history", "allowed-use and override logs"],
                "data_gaps": ["scenario coverage", "operator feedback labels", "deployment context lineage", "review outcome history"],
                "data_rights_notes": "Data rights must distinguish simulation data, mission context, operator feedback, and restricted deployment records.",
                "validation_requirements": ["mission simulation validation", "operator review", "secure command integration test", "allowed-use policy review", "audit trace replay"],
                "minimum_evidence_pack": ["simulation report", "operator review notes", "authorization workflow map", "audit logs", "restricted-use policy"],
                "deployment_controls": ["restricted access environment", "human authorization gate", "allowed-use policy", "mission-use audit log", "secure deployment boundary"],
                "deployment_mode": "controlled secure pilot",
                "controlled_deployment_mode": "advisory shadow-mode pilot with human authorization",
                "technical_risks": [
                    {"risk": "simulation-to-reality gap", "impact": "mission simulation may not generalize to operational conditions", "severity": "high", "mitigation": "validate across scenario families and operator review"},
                    {"risk": "operator trust gap", "impact": "users may reject recommendations if rationale and controls are weak", "severity": "high", "mitigation": "use explainable outputs, review workflows, and override logging"},
                ],
                "allowed_use_objective": "define where mission-intelligence recommendations can and cannot be used",
                "human_review_objective": "prove operators can review, accept, reject, and override recommendations",
                "shadow_mode_objective": "compare system recommendations against operator decisions without automating outcomes",
                "data_foundation_objective": "Establish authorized mission context, simulation, sensor, and review-control data foundations.",
                "data_foundation_deliverables": ["mission context schema", "simulation scenario set", "allowed-use metadata", "operator review event schema"],
                "model_validation_objective": "Validate mission simulation, coordination-risk scoring, and recommendation confidence.",
                "model_validation_deliverables": ["simulation validation memo", "coordination-risk model report", "false-positive / false-negative review"],
                "workflow_prototype_objective": "Prototype secure command review and authorization flow.",
                "workflow_prototype_deliverables": ["review console mock", "authorization state machine", "operator acceptance notes"],
                "control_layer_objective": "Prove allowed-use enforcement, human authorization, and auditability.",
                "control_layer_deliverables": ["allowed-use policy", "human authorization gate", "audit replay", "secure deployment checklist"],
                "prototype_type": "secure mission simulation and review prototype",
                "prototype_scope": "one mission simulation use case with operator review, authorization state, and audit trace",
                "prototype_success_metrics": ["operator acceptance", "scenario coverage", "recommendation precision", "override trace completeness", "time-to-decision improvement"],
                "prototype_mode": "controlled_pilot",
                "first_action": "build mission simulation feasibility harness",
                "second_action": "prototype secure command review and authorization workflow",
            },
            "climate_insurance": {
                "feasibility_adjustment": 0.020,
                "architecture_adjustment": 0.040,
                "complexity_adjustment": 0.075,
                "integration_adjustment": 0.045,
                "data_adjustment": 0.070,
                "validation_adjustment": 0.090,
                "recommended_architecture": "underwriting-grade climate risk architecture with weather-loss ingestion, exposure modeling, scenario analysis, and underwriter review",
                "required_components": ["weather_loss_ingestion", "exposure_modeling_service", "catastrophe_scenario_engine", "underwriting_repricing_detector", "risk_transfer_recommendation_layer", "underwriter_review_console"],
                "architecture_notes": "Climate-insurance feasibility depends on loss-history quality, exposure data lineage, scenario calibration, and underwriter workflow fit.",
                "complexity_drivers": ["weather-loss data quality", "exposure normalization", "scenario calibration", "underwriting workflow integration"],
                "implementation_notes": "Start with historical weather-loss and repricing backtests before operational workflow deployment.",
                "integration_points": ["underwriting workbench", "policy systems", "exposure databases", "catastrophe models", "risk-transfer workflow"],
                "integration_risks": ["data lineage", "pricing impact trust", "model calibration", "actuarial review"],
                "required_datasets": ["weather loss history", "property exposure data", "claims context", "pricing and repricing history", "catastrophe scenario assumptions"],
                "data_gaps": ["loss normalization", "geospatial exposure completeness", "repricing outcome labels", "scenario calibration history"],
                "data_rights_notes": "Data rights must cover exposure records, loss history, benchmark generation, and workflow feedback capture.",
                "validation_requirements": ["weather-loss backtest", "repricing signal validation", "catastrophe scenario calibration", "underwriter workflow acceptance"],
                "minimum_evidence_pack": ["loss backtest", "repricing precision report", "exposure benchmark appendix", "underwriter review notes"],
                "deployment_controls": ["underwriter approval gate", "actuarial model review", "pricing impact audit log", "scenario versioning"],
                "deployment_mode": "underwriter-reviewed advisory pilot",
                "controlled_deployment_mode": "underwriter-reviewed advisory pilot",
                "technical_risks": [{"risk": "loss-signal noise", "impact": "weather-loss signals may be too noisy for underwriting action", "severity": "high", "mitigation": "validate with historical repricing and loss outcomes"}],
                "allowed_use_objective": "define how outputs may support underwriting and risk-transfer decisions",
                "human_review_objective": "prove underwriters can review evidence and confidence before action",
                "shadow_mode_objective": "compare recommendations against historical underwriter decisions",
                "data_foundation_objective": "Establish weather-loss, exposure, claims-context, and pricing-history data foundations.",
                "data_foundation_deliverables": ["weather-loss connector", "exposure schema", "repricing event labels", "scenario input contract"],
                "model_validation_objective": "Validate exposure, repricing, and catastrophe scenario models.",
                "model_validation_deliverables": ["loss backtest", "repricing precision report", "scenario calibration memo"],
                "workflow_prototype_objective": "Prototype underwriter review and risk-transfer workflow.",
                "workflow_prototype_deliverables": ["underwriter review console", "pricing impact log", "risk-transfer recommendation test"],
                "control_layer_objective": "Prove model governance, scenario versioning, and pricing-impact auditability.",
                "control_layer_deliverables": ["model governance checklist", "scenario version log", "pricing audit trail"],
                "prototype_type": "climate exposure and repricing backtest prototype",
                "prototype_scope": "one peril/region portfolio with weather-loss backtesting and underwriter review",
                "prototype_success_metrics": ["repricing precision", "underwriter acceptance", "exposure coverage", "scenario calibration", "risk-transfer value"],
                "prototype_mode": "advisory_pilot",
                "first_action": "build weather-loss and repricing backtest",
                "second_action": "prototype underwriter review console",
            },
        }

        default = {
            "feasibility_adjustment": 0.000,
            "architecture_adjustment": 0.020,
            "complexity_adjustment": 0.050,
            "integration_adjustment": 0.025,
            "data_adjustment": 0.030,
            "validation_adjustment": 0.060,
            "recommended_architecture": "modular intelligence platform with ingestion, analysis, decision, review, and audit layers",
            "required_components": ["ingestion", "semantic_processing", "analysis_engines", "decision_layer", "review_console", "audit_service"],
            "architecture_notes": "Feasibility depends on stable contracts, data quality, explainability, and workflow adoption.",
            "complexity_drivers": ["data quality", "model validation", "workflow fit", "integration depth"],
            "implementation_notes": "Start with controlled advisory prototype before operational deployment.",
            "integration_points": ["source systems", "workflow dashboard", "API layer", "audit/logging service"],
            "integration_risks": ["source data availability", "workflow adoption", "model trust"],
            "required_datasets": ["historical events", "source metadata", "user feedback", "outcome labels"],
            "data_gaps": ["outcome labels", "source lineage", "feedback-loop capture"],
            "data_rights_notes": "Confirm rights to use source data, derived benchmarks, and workflow feedback.",
            "validation_requirements": ["historical backtest", "pilot acceptance test", "false-positive / false-negative analysis", "audit review"],
            "minimum_evidence_pack": ["backtest", "pilot metrics", "risk register", "audit log"],
            "deployment_controls": ["role-based access", "audit logging", "human review", "confidence thresholds"],
            "deployment_mode": "controlled advisory pilot",
            "controlled_deployment_mode": "controlled advisory pilot with explicit review gates",
            "technical_risks": [{"risk": "model validation gap", "impact": "recommendations may be technically plausible but insufficiently proven", "severity": "medium", "mitigation": "run historical backtests and pilot acceptance testing"}],
            "allowed_use_objective": "define allowed and restricted use cases",
            "human_review_objective": "prove users can review and override recommendations",
            "shadow_mode_objective": "compare outputs to human decisions before automation",
            "data_foundation_objective": "Establish source, outcome, lineage, and feedback data foundations.",
            "data_foundation_deliverables": ["source schema", "lineage map", "outcome label set", "feedback capture plan"],
            "model_validation_objective": "Validate model quality, recommendation reliability, and failure modes.",
            "model_validation_deliverables": ["backtest report", "precision review", "failure-mode analysis"],
            "workflow_prototype_objective": "Prototype user workflow and review experience.",
            "workflow_prototype_deliverables": ["review workflow", "pilot dashboard", "user acceptance notes"],
            "control_layer_objective": "Prove traceability, auditability, and review controls.",
            "control_layer_deliverables": ["audit log", "confidence thresholds", "review policy"],
            "prototype_type": "controlled intelligence prototype",
            "prototype_scope": "one high-value workflow with historical validation and user review",
            "prototype_success_metrics": ["accuracy", "false-positive rate", "workflow adoption", "time savings", "ROI signal"],
            "prototype_mode": "advisory_pilot",
            "first_action": "define prototype data and validation contract",
            "second_action": "run historical backtest and workflow acceptance test",
        }
        return profiles.get(sector, default)

    # =========================
    # HELPERS
    # =========================
    def _feasibility_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []
        if signals["feasibility_score"] >= 0.70:
            drivers.append("strong orchestrator feasibility score")
        if signals["buildability_score"] >= 0.70:
            drivers.append("strong buildability score")
        if signals["market_gap_confidence"] >= 0.80:
            drivers.append("high-confidence market gap")
        if signals["architecture_term_count"] >= 3:
            drivers.append("architecture and integration language present")
        if signals["data_term_count"] >= 3:
            drivers.append("data foundation language present")
        if signals["security_term_count"] >= 2:
            drivers.append("control and audit language present")
        if signals["blocker_level"] == "conditional":
            drivers.append("conditional blocker requires control-gated deployment")
        return drivers or ["baseline feasibility and buildability signals"]

    def _prototype_recommendation(self, state: str) -> str:
        if state in {"technically_feasible", "technically_feasible_with_controls"}:
            return "build_controlled_prototype"
        if state in {"feasible_with_validation", "conditionally_feasible"}:
            return "build_validation_prototype_first"
        if state == "needs_control_burndown":
            return "burn_down_controls_before_prototype"
        return "research_before_prototype"

    def _deployment_posture(self, signals: Dict[str, Any], state: str) -> str:
        if signals["blocker_level"] == "conditional":
            return "advisory_or_shadow_mode_with_controls"
        if state == "technically_feasible":
            return "controlled_pilot"
        if state == "feasible_with_validation":
            return "validation_pilot"
        return "research_validation"

    def _level(self, score: float) -> str:
        if score >= 0.75:
            return "strong"
        if score >= 0.58:
            return "moderate"
        if score >= 0.42:
            return "emerging"
        return "weak"

    def _confidence(self, signals: Dict[str, Any], feasibility: Dict[str, Any]) -> float:
        return round(self._bounded(
            0.22
            + feasibility.get("score", 0.0) * 0.16
            + signals["feasibility_score"] * 0.11
            + signals["buildability_score"] * 0.10
            + signals["market_gap_confidence"] * 0.08
            + signals["breakthrough_synthesis_score"] * 0.06
            + signals["opportunity_score"] * 0.06
            + signals["moat_score"] * 0.05
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

    def _dedupe(self, values: List[str]) -> List[str]:
        return list(dict.fromkeys([str(v) for v in values if v]))
