"""
Productization Path Engine — dedicated Stage 13 engine for Claire.

v5.25:
- Converts productization path from design-output partial status into a real engine.
- Synthesizes opportunity, breakthrough, technical feasibility, market formation,
  moat, risk, business model, and design blueprint outputs into a productization
  plan.
- Produces pilot strategy, launch posture, packaging, roadmap, evidence gates,
  GTM readiness, launch risks, and product requirements.
"""

from typing import Any, Dict, List, Optional


class ProductizationPathEngine:
    """Deterministic productization and pilot-path analyzer."""

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
        technical_feasibility: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        business_model: Optional[Dict[str, Any]] = None,
        design_output: Optional[Dict[str, Any]] = None,
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
        technical_feasibility = technical_feasibility or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        business_model = business_model or {}
        design_output = design_output or {}
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
            technical_feasibility=technical_feasibility,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            design_output=design_output,
            connector_sources=connector_sources,
        )

        productization_score = self._productization_score(signals)
        classification = self._classification(signals, productization_score)
        pilot_strategy = self._pilot_strategy(signals, classification)
        packaging_strategy = self._packaging_strategy(signals, classification)
        roadmap = self._roadmap(signals, classification)
        evidence_gates = self._evidence_gates(signals, classification)
        gtm = self._gtm_readiness(signals, classification)
        launch_controls = self._launch_controls(signals, classification)
        launch_risks = self._launch_risks(signals)
        product_requirements = self._product_requirements(signals)

        return {
            "status": "success",
            "domain": signals["domain"],
            "sector": signals["sector"],
            "productization_score": productization_score,
            "productization_classification": classification,
            "pilot_strategy": pilot_strategy,
            "packaging_strategy": packaging_strategy,
            "productization_roadmap": roadmap,
            "evidence_gates": evidence_gates,
            "go_to_market_readiness": gtm,
            "launch_controls": launch_controls,
            "launch_risks": launch_risks,
            "product_requirements": product_requirements,
            "prototype_to_product_path": self._prototype_to_product_path(signals, classification),
            "product_metrics": self._product_metrics(signals),
            "recommended_next_actions": self._recommended_next_actions(signals, classification),
            "productization_thesis": self._thesis(signals, classification, productization_score),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, productization_score),
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
        technical_feasibility: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        design_output: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector = market_gap.get("sector", "general_intelligence") if isinstance(market_gap, dict) else "general_intelligence"
        domain = self._domain_for_sector(sector, domain)
        profile = self._sector_profile(sector)

        combined = f"{text.lower()} {' '.join([str(k).lower() for k in keywords])}"

        workflow_terms = self._count_terms(combined, [
            "workflow", "review", "operator", "underwriter", "clinical", "portfolio",
            "planning", "command", "procurement", "dashboard", "console"
        ])
        product_terms = self._count_terms(combined, [
            "platform", "product", "module", "pilot", "enterprise", "subscription",
            "api", "dashboard", "workflow", "integration", "launch"
        ])
        validation_terms = self._count_terms(combined, [
            "backtest", "validation", "pilot", "evidence", "accuracy", "audit",
            "scenario", "simulation", "proof", "review"
        ])

        market = connector_sources.get("market", {}) if isinstance(connector_sources, dict) else {}
        patent = connector_sources.get("patent", {}) if isinstance(connector_sources, dict) else {}
        financial = connector_sources.get("financial", {}) if isinstance(connector_sources, dict) else {}

        design_modules = design_output.get("architecture_blueprint", {}).get("modules", []) if isinstance(design_output, dict) else []
        design_flows = design_output.get("data_flows", []) if isinstance(design_output, dict) else []
        implementation_phases = design_output.get("implementation_phases", []) if isinstance(design_output, dict) else []

        return {
            "domain": domain,
            "sector": sector,
            "sector_label": profile["label"],
            "workflow_term_count": workflow_terms,
            "product_term_count": product_terms,
            "validation_term_count": validation_terms,
            "analysis_score": float(scores.get("analysis_score", 0.0) or 0.0),
            "breakthrough_score": float(scores.get("breakthrough_score", 0.0) or 0.0),
            "portfolio_score": float(scores.get("portfolio_score", 0.0) or 0.0),
            "feasibility_score": float(scores.get("feasibility_score", 0.0) or 0.0),
            "buildability_score": float(scores.get("buildability_score", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": self._nested(market_gap, "strategic_pressure", "score"),
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "needed_solution": market_gap.get("needed_solution", profile["needed_solution"]) if isinstance(market_gap, dict) else profile["needed_solution"],
            "solution_class": market_gap.get("solution_class", profile["solution_class"]) if isinstance(market_gap, dict) else profile["solution_class"],
            "timing_pressure_score": self._nested(trend_trajectory, "timing_pressure", "score"),
            "strategic_window": self._nested_text(trend_trajectory, "strategic_window", "window"),
            "formation_type": self._nested_text(market_formation, "formation_type", "type"),
            "market_stage": self._nested_text(market_formation, "market_stage", "stage"),
            "category_creation_score": self._nested(market_formation, "category_creation_score", "score"),
            "buyer_pull_score": self._nested(market_formation, "buyer_pull", "score"),
            "opportunity_score": self._nested(opportunity_discovery, "opportunity_score", "score"),
            "opportunity_priority_score": self._nested(opportunity_discovery, "priority_assessment", "score"),
            "validation_urgency_score": self._nested(opportunity_discovery, "validation_urgency", "score"),
            "opportunity_type": self._nested_text(opportunity_discovery, "opportunity_type", "type"),
            "breakthrough_synthesis_score": self._nested(breakthrough_synthesis, "breakthrough_synthesis_score", "score"),
            "breakthrough_classification": self._nested_text(breakthrough_synthesis, "breakthrough_classification", "classification"),
            "breakthrough_readiness_modifier": self._nested_text(breakthrough_synthesis, "breakthrough_classification", "readiness_modifier"),
            "technical_feasibility_score": self._nested(technical_feasibility, "technical_feasibility_score", "score"),
            "technical_feasibility_level": self._nested_text(technical_feasibility, "technical_feasibility_score", "level"),
            "technical_state": self._nested_text(technical_feasibility, "feasibility_classification", "state"),
            "technical_readiness_modifier": self._nested_text(technical_feasibility, "feasibility_classification", "readiness_modifier"),
            "deployment_posture": self._nested_text(technical_feasibility, "feasibility_classification", "deployment_posture"),
            "architecture_readiness_score": self._nested(technical_feasibility, "architecture_readiness", "score"),
            "integration_readiness_score": self._nested(technical_feasibility, "integration_readiness", "score"),
            "data_readiness_score": self._nested(technical_feasibility, "data_readiness", "score"),
            "validation_burden_score": self._nested(technical_feasibility, "validation_burden", "score"),
            "diligence_readiness_score": self._nested(technical_feasibility, "diligence_readiness", "score"),
            "moat_score": self._nested(moat, "moat_type", "moat_score"),
            "moat_strength": self._nested_text(moat, "moat_type", "strength"),
            "primary_moat": self._nested_text(moat, "moat_type", "primary_moat"),
            "copy_risk_score": self._nested(moat, "copy_risk", "score"),
            "risk_score": self._nested(risk_regulation, "risk_profile", "score"),
            "risk_level": self._nested_text(risk_regulation, "risk_profile", "level"),
            "regulatory_exposure_score": self._nested(risk_regulation, "regulation_profile", "score"),
            "blocker_level": self._nested_text(risk_regulation, "blocker_assessment", "blocker_level") or "unknown",
            "value_capture_score": self._nested(business_model, "value_capture", "score"),
            "value_capture_strength": self._nested_text(business_model, "value_capture", "strength"),
            "buyer_roi_score": self._nested(business_model, "buyer_roi", "score"),
            "buyer_roi_strength": self._nested_text(business_model, "buyer_roi", "roi_strength"),
            "commercial_risk_score": self._nested(business_model, "commercial_risk", "score"),
            "commercial_risk_level": self._nested_text(business_model, "commercial_risk", "level"),
            "revenue_model": self._nested_text(business_model, "revenue_model", "primary_model"),
            "design_success": design_output.get("status") == "success" if isinstance(design_output, dict) else False,
            "design_module_count": len(design_modules) if isinstance(design_modules, list) else 0,
            "design_flow_count": len(design_flows) if isinstance(design_flows, list) else 0,
            "implementation_phase_count": len(implementation_phases) if isinstance(implementation_phases, list) else 0,
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
        }

    # =========================
    # SCORING / CLASSIFICATION
    # =========================
    def _productization_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.12
            + signals["technical_feasibility_score"] * 0.120
            + signals["architecture_readiness_score"] * 0.070
            + signals["integration_readiness_score"] * 0.055
            + signals["data_readiness_score"] * 0.045
            + signals["opportunity_score"] * 0.085
            + signals["buyer_pull_score"] * 0.075
            + signals["category_creation_score"] * 0.060
            + signals["value_capture_score"] * 0.070
            + signals["buyer_roi_score"] * 0.045
            + signals["portfolio_score"] * 0.045
            + signals["moat_score"] * 0.040
            + (0.045 if signals["design_success"] else 0.0)
            + min(0.045, signals["implementation_phase_count"] * 0.007)
            + min(0.025, signals["product_term_count"] * 0.004)
            + min(0.025, signals["workflow_term_count"] * 0.004)
            - signals["risk_score"] * 0.018
            - signals["commercial_risk_score"] * 0.020
            - (0.040 if signals["blocker_level"] == "conditional" else 0.0)
            - (0.030 if signals["data_readiness_score"] and signals["data_readiness_score"] < 0.48 else 0.0)
        )

        level = "launch_ready" if score >= 0.78 else "pilot_ready" if score >= 0.64 else "validation_ready" if score >= 0.50 else "research_ready"

        return {
            "level": level,
            "score": round(score, 4),
            "drivers": self._score_drivers(signals),
        }

    def _classification(self, signals: Dict[str, Any], productization_score: Dict[str, Any]) -> Dict[str, Any]:
        score = productization_score.get("score", 0.0)

        if score >= 0.78:
            state = "product_ready"
        elif score >= 0.64:
            state = "pilot_ready"
        elif score >= 0.50:
            state = "validation_ready"
        else:
            state = "research_only"

        if signals["blocker_level"] == "conditional" or signals["technical_readiness_modifier"] == "control_gated":
            readiness_modifier = "control_gated"
            launch_posture = "advisory_or_shadow_mode_before_automation"
            recommended_motion = "controlled validation pilot"
        elif signals["data_readiness_score"] and signals["data_readiness_score"] < 0.50:
            readiness_modifier = "data_limited"
            launch_posture = "data_foundation_before_pilot"
            recommended_motion = "data-readiness validation sprint"
        elif signals["buyer_roi_score"] < 0.62:
            readiness_modifier = "roi_unproven"
            launch_posture = "paid pilot_with_roi_instrumentation"
            recommended_motion = "ROI-instrumented design-partner pilot"
        else:
            readiness_modifier = "standard"
            launch_posture = "design_partner_pilot_to_enterprise_rollout"
            recommended_motion = "design-partner pilot"

        return {
            "state": state,
            "readiness_modifier": readiness_modifier,
            "recommended_motion": recommended_motion,
            "launch_posture": launch_posture,
            "score_used": round(score, 4),
        }

    # =========================
    # OUTPUT BUILDERS
    # =========================
    def _pilot_strategy(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "pilot_type": profile["pilot_type"],
            "pilot_scope": profile["pilot_scope"],
            "first_user": profile["first_user"],
            "pilot_mode": classification["launch_posture"],
            "pilot_duration": "30_to_60_days" if classification["readiness_modifier"] != "control_gated" else "60_to_90_days_control_gated",
            "success_metrics": profile["success_metrics"],
            "pilot_exit_criteria": profile["pilot_exit_criteria"],
        }

    def _packaging_strategy(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        packages = [
            {
                "package": "Validation Sprint",
                "purpose": "prove the critical assumption before broad product build",
                "contents": profile["validation_sprint_contents"],
                "when_to_sell": "before paid pilot if evidence is weak",
            },
            {
                "package": "Controlled Pilot",
                "purpose": "test workflow adoption, ROI, and operational controls with a design partner",
                "contents": profile["controlled_pilot_contents"],
                "when_to_sell": "after buyer pain and technical feasibility are credible",
            },
            {
                "package": "Enterprise Platform",
                "purpose": "convert validated pilot usage into recurring platform deployment",
                "contents": profile["enterprise_platform_contents"],
                "when_to_sell": "after pilot success and security/compliance review",
            },
            {
                "package": "Expansion Modules",
                "purpose": "expand from wedge workflow into platform-level account growth",
                "contents": profile["expansion_modules"],
                "when_to_sell": "after the first recurring workflow is embedded",
            },
        ]

        return {
            "primary_package": "Controlled Pilot" if classification["state"] in {"pilot_ready", "product_ready"} else "Validation Sprint",
            "pricing_anchor": profile["pricing_anchor"],
            "packaging_sequence": packages,
            "buyer_commitment_needed": profile["buyer_commitment_needed"],
        }

    def _roadmap(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        profile = self._sector_profile(signals["sector"])
        roadmap = [
            {
                "phase": 1,
                "name": "Product proof contract",
                "objective": "Lock the target user, workflow, input/output contract, evidence gates, and no-go criteria.",
                "deliverables": ["target workflow", "I/O contract", "evidence gates", "no-go criteria"],
                "priority": "critical",
            },
            {
                "phase": 2,
                "name": "Validation sprint",
                "objective": profile["validation_objective"],
                "deliverables": profile["validation_deliverables"],
                "priority": "critical",
            },
            {
                "phase": 3,
                "name": "Pilot product slice",
                "objective": profile["pilot_objective"],
                "deliverables": profile["pilot_deliverables"],
                "priority": "high",
            },
            {
                "phase": 4,
                "name": "Workflow integration",
                "objective": profile["workflow_objective"],
                "deliverables": profile["workflow_deliverables"],
                "priority": "high",
            },
            {
                "phase": 5,
                "name": "Commercial packaging",
                "objective": "Turn the pilot into a repeatable commercial offer with pricing, ROI, support model, and rollout path.",
                "deliverables": ["pilot package", "pricing model", "ROI scorecard", "support model", "expansion plan"],
                "priority": "high",
            },
            {
                "phase": 6,
                "name": "Enterprise readiness",
                "objective": "Prepare the product for enterprise deployment, diligence, and strategic-buyer review.",
                "deliverables": ["security review", "architecture review", "data-rights packet", "risk register", "buyer proof pack"],
                "priority": "high",
            },
        ]

        if classification["readiness_modifier"] == "control_gated":
            roadmap.insert(3, {
                "phase": 4,
                "name": "Control-gated launch review",
                "objective": "Prove controls, human-review gates, allowed-use boundaries, and auditability before pilot expansion.",
                "deliverables": ["control plan", "human-review workflow", "allowed-use policy", "audit replay", "deployment constraints"],
                "priority": "critical",
            })
            for idx, item in enumerate(roadmap, start=1):
                item["phase"] = idx

        return roadmap

    def _evidence_gates(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        profile = self._sector_profile(signals["sector"])
        gates = [
            {
                "gate": "buyer pain gate",
                "pass_condition": profile["buyer_pain_gate"],
                "failure_condition": "buyer agrees the problem exists but will not allocate budget, data, or workflow access",
                "priority": "critical",
            },
            {
                "gate": "technical proof gate",
                "pass_condition": profile["technical_proof_gate"],
                "failure_condition": "prototype cannot generate reliable outputs under realistic constraints",
                "priority": "critical",
            },
            {
                "gate": "workflow adoption gate",
                "pass_condition": profile["workflow_gate"],
                "failure_condition": "users treat output as optional analysis instead of recurring workflow support",
                "priority": "high",
            },
            {
                "gate": "ROI gate",
                "pass_condition": profile["roi_gate"],
                "failure_condition": "impact cannot be quantified or tied to buyer value",
                "priority": "high",
            },
            {
                "gate": "defensibility gate",
                "pass_condition": profile["moat_gate"],
                "failure_condition": "incumbents can copy the feature without proprietary data, integration, or workflow history",
                "priority": "medium",
            },
        ]

        if classification["readiness_modifier"] == "control_gated":
            gates.insert(2, {
                "gate": "control gate",
                "pass_condition": "human-review, allowed-use, deployment boundary, and audit evidence are documented and accepted",
                "failure_condition": "controls make the product too slow, risky, or hard to adopt",
                "priority": "critical",
            })

        return gates

    def _gtm_readiness(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.14
            + signals["buyer_pull_score"] * 0.145
            + signals["value_capture_score"] * 0.120
            + signals["buyer_roi_score"] * 0.100
            + signals["productization_score"] * 0.140 if "productization_score" in signals else 0.0
        )

        # The expression above cannot reference a later value, so recompute from available indicators.
        score = self._bounded(
            0.14
            + signals["buyer_pull_score"] * 0.150
            + signals["value_capture_score"] * 0.120
            + signals["buyer_roi_score"] * 0.095
            + signals["category_creation_score"] * 0.070
            + signals["opportunity_score"] * 0.070
            + signals["commercial_risk_score"] * -0.035
            - (0.035 if classification["readiness_modifier"] == "control_gated" else 0.0)
        )

        level = "ready" if score >= 0.74 else "pilot_ready" if score >= 0.60 else "needs_validation"

        return {
            "level": level,
            "score": round(score, 4),
            "recommended_motion": classification["recommended_motion"],
            "first_customer_profile": self._sector_profile(signals["sector"])["first_customer_profile"],
            "sales_risks": self._sector_profile(signals["sector"])["sales_risks"],
        }

    def _launch_controls(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        controls = list(profile["launch_controls"])

        if classification["readiness_modifier"] == "control_gated":
            controls.extend([
                "documented blocker mitigation plan",
                "human-review gate before operational use",
                "advisory or shadow-mode launch before automation",
                "audit evidence retained for all recommendations",
                "explicit allowed-use and restricted-use policy",
            ])

        return {
            "control_level": "strict" if classification["readiness_modifier"] == "control_gated" else "standard",
            "launch_mode": classification["launch_posture"],
            "controls": list(dict.fromkeys(controls)),
        }

    def _launch_risks(self, signals: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        risks = list(profile["launch_risks"])

        if signals["data_readiness_score"] and signals["data_readiness_score"] < 0.50:
            risks.append({
                "risk": "data readiness gap",
                "impact": "pilot may not produce defensible product evidence without stronger datasets or feedback loops",
                "severity": "high",
                "mitigation": "run a data-foundation sprint before launch",
            })

        if signals["buyer_roi_score"] < 0.62:
            risks.append({
                "risk": "ROI proof gap",
                "impact": "buyers may like the product but hesitate to expand without quantified value",
                "severity": "medium",
                "mitigation": "instrument ROI metrics before the first pilot",
            })

        if signals["blocker_level"] == "conditional":
            risks.append({
                "risk": "control-gated deployment",
                "impact": "deployment must remain constrained until controls and review workflows are accepted",
                "severity": "high",
                "mitigation": "launch in advisory/shadow mode with documented controls",
            })

        return risks

    def _product_requirements(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "must_have": profile["must_have"],
            "should_have": profile["should_have"],
            "later_modules": profile["later_modules"],
            "non_functional_requirements": profile["non_functional_requirements"],
        }

    def _prototype_to_product_path(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "current_state": signals["technical_state"] or "technical_validation_needed",
            "next_state": "controlled_pilot" if classification["state"] in {"pilot_ready", "product_ready"} else "validation_sprint",
            "product_wedge": profile["product_wedge"],
            "expansion_path": profile["expansion_path"],
            "enterprise_conversion_trigger": profile["enterprise_conversion_trigger"],
        }

    def _product_metrics(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "adoption_metrics": profile["adoption_metrics"],
            "quality_metrics": profile["quality_metrics"],
            "business_metrics": profile["business_metrics"],
            "risk_metrics": profile["risk_metrics"],
        }

    def _recommended_next_actions(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        actions = [
            {
                "action": profile["first_action"],
                "purpose": "turn the opportunity into a concrete pilotable product slice",
                "priority": "critical",
            },
            {
                "action": profile["second_action"],
                "purpose": "produce product evidence for buyer validation and binder packaging",
                "priority": "critical",
            },
            {
                "action": "instrument pilot metrics before launch",
                "purpose": "make ROI, adoption, quality, and risk evidence measurable from the first pilot",
                "priority": "high",
            },
            {
                "action": "define enterprise conversion criteria",
                "purpose": "prevent the pilot from becoming custom services without platform expansion",
                "priority": "high",
            },
        ]

        if classification["readiness_modifier"] == "control_gated":
            actions.insert(2, {
                "action": "complete control-gated launch plan",
                "purpose": "resolve deployment controls before the product is framed as launch-ready",
                "priority": "critical",
            })

        return actions

    def _thesis(self, signals: Dict[str, Any], classification: Dict[str, Any], productization_score: Dict[str, Any]) -> str:
        return (
            f"{signals['sector_label']} is {classification.get('state')} with "
            f"{productization_score.get('level')} productization strength and a score of "
            f"{productization_score.get('score')}. The recommended motion is "
            f"{classification.get('recommended_motion')} with launch posture "
            f"{classification.get('launch_posture')}. Productization should focus on a narrow product wedge, "
            f"measurable buyer value, workflow adoption, and evidence gates before enterprise expansion."
        )

    # =========================
    # SECTOR PROFILES
    # =========================
    def _sector_profile(self, sector: str) -> Dict[str, Any]:
        profiles = {
            "defense_autonomy": {
                "label": "defense autonomy",
                "needed_solution": "controlled mission intelligence product",
                "solution_class": "secure mission intelligence platform",
                "pilot_type": "secure mission simulation and review pilot",
                "pilot_scope": "one mission simulation use case with operator review, authorization state, and audit trace",
                "first_user": "mission operators and secure command review stakeholders",
                "success_metrics": ["operator acceptance", "scenario coverage", "recommendation precision", "override trace completeness", "time-to-decision improvement"],
                "pilot_exit_criteria": ["operator workflow accepted", "allowed-use policy approved", "audit replay completed", "mission simulation results reviewed"],
                "validation_sprint_contents": ["mission use case definition", "scenario set", "operator review script", "allowed-use boundary"],
                "controlled_pilot_contents": ["simulation harness", "secure review console", "authorization state machine", "audit trail", "shadow-mode comparison"],
                "enterprise_platform_contents": ["secure command adapter", "mission context ingestion", "coordination risk model", "human authorization layer", "mission audit service"],
                "expansion_modules": ["additional mission scenarios", "sensor/context integrations", "program-level reporting", "workflow analytics"],
                "pricing_anchor": "paid secure validation pilot followed by annual platform license",
                "buyer_commitment_needed": "mission scenario access, operator review time, secure workflow constraints, and sponsor ownership",
                "validation_objective": "Prove mission recommendations can be reviewed safely in simulation or shadow mode.",
                "validation_deliverables": ["simulation validation memo", "operator feedback notes", "allowed-use policy", "audit-trace sample"],
                "pilot_objective": "Build a controlled mission-intelligence product slice with human authorization.",
                "pilot_deliverables": ["review console", "authorization workflow", "mission audit log", "pilot scorecard"],
                "workflow_objective": "Embed advisory outputs into secure command review without automating operational decisions.",
                "workflow_deliverables": ["secure command workflow map", "operator review procedure", "override logging", "deployment boundary"],
                "buyer_pain_gate": "mission stakeholders confirm the system improves reviewable mission decisions enough to sponsor a pilot",
                "technical_proof_gate": "simulation outputs and recommendation confidence are usable under defined mission constraints",
                "workflow_gate": "operators can review, accept, reject, and override recommendations in a repeatable workflow",
                "roi_gate": "pilot shows time-to-decision improvement, mission-risk reduction, or coordination-quality improvement",
                "moat_gate": "simulation data, review history, and secure workflow integration produce a proprietary evidence loop",
                "first_customer_profile": "defense program, defense prime, or mission technology team with a controlled simulation environment",
                "sales_risks": ["security review", "operator trust", "classified/restricted environments", "long procurement cycles"],
                "launch_controls": ["restricted access environment", "human authorization gate", "mission-use audit log", "secure deployment boundary"],
                "launch_risks": [
                    {"risk": "operator trust gap", "impact": "users may reject outputs if rationale and controls are weak", "severity": "high", "mitigation": "run operator review sessions and preserve override logs"},
                    {"risk": "simulation-to-reality gap", "impact": "simulation success may not translate to operational conditions", "severity": "high", "mitigation": "validate across scenario families and remain in shadow mode"},
                ],
                "must_have": ["mission_context_ingestion", "mission_simulation_engine", "secure review console", "human authorization gate", "mission audit log"],
                "should_have": ["coordination risk scoring", "explainable recommendation trace", "allowed-use policy manager", "operator feedback loop"],
                "later_modules": ["multi-scenario library", "program reporting", "sensor integration expansion", "cross-unit benchmark layer"],
                "non_functional_requirements": ["secure deployment boundary", "auditability", "low-latency review where needed", "role-based authorization"],
                "product_wedge": "mission simulation and secure review console",
                "expansion_path": ["secure review pilot", "mission audit layer", "coordination risk model", "program expansion", "enterprise secure mission intelligence platform"],
                "enterprise_conversion_trigger": "operator acceptance, auditability, and measurable time-to-decision improvement across repeated scenarios",
                "adoption_metrics": ["active operator reviewers", "review sessions completed", "override/acceptance rate", "repeat usage"],
                "quality_metrics": ["recommendation precision", "scenario coverage", "false-positive/false-negative review", "explanation completeness"],
                "business_metrics": ["pilot conversion", "program expansion interest", "sponsor renewal signal", "time-to-decision value"],
                "risk_metrics": ["control exceptions", "unauthorized-use attempts", "audit replay completeness", "override reasons"],
                "first_action": "define the mission simulation product wedge",
                "second_action": "prototype secure review console with authorization and audit trace",
            },
            "climate_insurance": {
                "label": "climate insurance",
                "needed_solution": "underwriting-grade climate risk intelligence product",
                "solution_class": "climate insurance risk intelligence platform",
                "pilot_type": "climate exposure and repricing pilot",
                "pilot_scope": "one region/peril/portfolio pilot with weather-loss backtesting and underwriter review",
                "first_user": "underwriting and portfolio risk teams",
                "success_metrics": ["repricing signal accuracy", "underwriter adoption", "exposure benchmark usefulness", "risk-transfer recommendation quality"],
                "pilot_exit_criteria": ["weather-loss backtest accepted", "underwriter workflow validated", "ROI case quantified", "data rights confirmed"],
                "validation_sprint_contents": ["weather-loss backtest", "exposure schema", "peril taxonomy", "underwriter interview pack"],
                "controlled_pilot_contents": ["exposure model", "repricing detector", "underwriter review console", "scenario report"],
                "enterprise_platform_contents": ["continuous exposure monitoring", "catastrophe scenario service", "risk-transfer module", "benchmark dataset"],
                "expansion_modules": ["new perils", "new regions", "broker/reinsurer reporting", "portfolio benchmark products"],
                "pricing_anchor": "paid underwriting pilot followed by enterprise subscription plus benchmark modules",
                "buyer_commitment_needed": "portfolio sample, underwriting workflow access, loss-history examples, and review time",
                "validation_objective": "Prove climate-loss and exposure signals improve underwriting or repricing decisions.",
                "validation_deliverables": ["weather-loss backtest", "repricing signal report", "exposure benchmark memo"],
                "pilot_objective": "Build an underwriter-ready review workflow for exposure and repricing pressure.",
                "pilot_deliverables": ["underwriter console", "scenario model", "pricing-impact audit log", "pilot scorecard"],
                "workflow_objective": "Embed outputs into underwriting review and portfolio steering.",
                "workflow_deliverables": ["workflow map", "review queue", "pricing-impact evidence", "underwriter acceptance notes"],
                "buyer_pain_gate": "underwriters confirm recurring pain around climate exposure, repricing, or withdrawal decisions",
                "technical_proof_gate": "backtests show signals are timely and actionable",
                "workflow_gate": "underwriters use the review output in a repeatable decision workflow",
                "roi_gate": "pilot quantifies avoided loss exposure, pricing improvement, or portfolio risk reduction",
                "moat_gate": "climate-loss data, exposure benchmarks, and workflow feedback create a proprietary loop",
                "first_customer_profile": "carrier, reinsurer, broker, or risk team with exposure/loss data and underwriting review need",
                "sales_risks": ["data access", "actuarial review", "model trust", "workflow friction"],
                "launch_controls": ["underwriter review required", "model confidence thresholds", "pricing-impact audit log", "scenario versioning"],
                "launch_risks": [
                    {"risk": "model trust gap", "impact": "underwriters may distrust black-box climate outputs", "severity": "high", "mitigation": "make scenarios explainable and backtested"},
                ],
                "must_have": ["weather_loss_ingestion", "exposure_modeling_service", "repricing_detector", "underwriter_review_console", "audit trail"],
                "should_have": ["catastrophe scenarios", "portfolio concentration reports", "risk-transfer recommendations"],
                "later_modules": ["broker reports", "reinsurer modules", "regional benchmark packs"],
                "non_functional_requirements": ["data lineage", "model versioning", "auditability", "role-based permissions"],
                "product_wedge": "underwriting repricing and climate exposure review",
                "expansion_path": ["underwriting pilot", "exposure benchmarks", "catastrophe modules", "risk-transfer workflow", "enterprise platform"],
                "enterprise_conversion_trigger": "underwriter adoption plus measurable repricing or exposure-management value",
                "adoption_metrics": ["underwriter users", "reviewed portfolios", "repeat usage", "reports exported"],
                "quality_metrics": ["backtest precision", "scenario calibration", "false-positive review", "confidence threshold performance"],
                "business_metrics": ["pilot conversion", "module expansion", "benchmark subscription interest", "risk-transfer value"],
                "risk_metrics": ["model exceptions", "pricing-impact audit completeness", "scenario versioning", "data lineage coverage"],
                "first_action": "define underwriting pilot wedge",
                "second_action": "run weather-loss backtest and underwriter workflow test",
            },
        }

        default = {
            "label": str(sector or "general").replace("_", " "),
            "needed_solution": "validated intelligence product",
            "solution_class": "opportunity intelligence platform",
            "pilot_type": "focused design-partner pilot",
            "pilot_scope": "one high-pain buyer workflow with measurable output, review, and ROI instrumentation",
            "first_user": "target workflow owner",
            "success_metrics": ["workflow adoption", "recommendation quality", "time savings", "ROI signal"],
            "pilot_exit_criteria": ["workflow accepted", "ROI baseline quantified", "technical risks logged", "buyer expansion path defined"],
            "validation_sprint_contents": ["buyer interviews", "historical examples", "workflow map", "data sample"],
            "controlled_pilot_contents": ["workflow prototype", "evidence trace", "pilot scorecard", "ROI instrumentation"],
            "enterprise_platform_contents": ["continuous monitoring", "workflow dashboard", "data integrations", "audit trail"],
            "expansion_modules": ["additional workflows", "benchmark data", "API access", "reporting modules"],
            "pricing_anchor": "paid validation pilot followed by annual enterprise subscription",
            "buyer_commitment_needed": "workflow access, data sample, review time, and sponsor ownership",
            "validation_objective": "Prove the system improves a repeatable buyer workflow.",
            "validation_deliverables": ["validation report", "workflow map", "pilot scorecard", "ROI baseline"],
            "pilot_objective": "Build a narrow product slice that proves value and repeat usage.",
            "pilot_deliverables": ["prototype", "review workflow", "metrics dashboard", "evidence pack"],
            "workflow_objective": "Embed outputs into the buyer workflow.",
            "workflow_deliverables": ["workflow integration", "review notes", "usage analytics", "feedback loop"],
            "buyer_pain_gate": "buyer validates urgency, budget owner, and repeat workflow need",
            "technical_proof_gate": "prototype produces reliable and explainable outputs",
            "workflow_gate": "users repeatedly use the product in the target workflow",
            "roi_gate": "pilot quantifies time savings, risk reduction, revenue, or cost impact",
            "moat_gate": "data loops or workflow integrations create increasing advantage",
            "first_customer_profile": "design partner with high pain and access to relevant data/workflow",
            "sales_risks": ["budget owner ambiguity", "data access", "workflow friction"],
            "launch_controls": ["audit logging", "human review", "data lineage", "role-based permissions"],
            "launch_risks": [
                {"risk": "workflow adoption gap", "impact": "pilot may become a demo instead of recurring product use", "severity": "medium", "mitigation": "focus on one repeatable workflow and instrument usage"},
            ],
            "must_have": ["ingestion", "analysis engine", "review workflow", "evidence trace", "metrics"],
            "should_have": ["dashboard", "benchmarks", "export", "API"],
            "later_modules": ["workflow expansion", "benchmark products", "integrations"],
            "non_functional_requirements": ["reliability", "auditability", "permissions", "monitoring"],
            "product_wedge": "focused workflow intelligence pilot",
            "expansion_path": ["validation sprint", "pilot", "workflow expansion", "enterprise platform"],
            "enterprise_conversion_trigger": "repeat usage, measurable ROI, and clear expansion demand",
            "adoption_metrics": ["active users", "repeat usage", "workflow completion", "feedback events"],
            "quality_metrics": ["accuracy", "precision", "false-positive review", "explanation quality"],
            "business_metrics": ["pilot conversion", "ARR path", "expansion interest", "ROI evidence"],
            "risk_metrics": ["model exceptions", "audit completeness", "data quality", "review overrides"],
            "first_action": "define the product wedge and pilot scope",
            "second_action": "prototype the target workflow and evidence gates",
        }

        # Reuse default with sector labels for sectors not yet specialized in this engine.
        if sector in {"healthcare_operations", "financial_market_intelligence", "industrial_supply_chain", "energy_infrastructure"}:
            custom = dict(default)
            custom["label"] = str(sector).replace("_", " ")
            custom["product_wedge"] = {
                "healthcare_operations": "capacity and patient-flow operations pilot",
                "financial_market_intelligence": "institutional signal intelligence pilot",
                "industrial_supply_chain": "supplier-risk and shortage forecasting pilot",
                "energy_infrastructure": "grid bottleneck and resilience planning pilot",
            }.get(sector, default["product_wedge"])
            custom["pilot_type"] = custom["product_wedge"]
            custom["first_action"] = f"define the {custom['product_wedge']}"
            custom["second_action"] = "prototype the target workflow with ROI and evidence gates"
            return custom

        return profiles.get(sector, default)

    # =========================
    # HELPERS
    # =========================
    def _score_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []
        if signals["technical_feasibility_score"] >= 0.64:
            drivers.append("technical feasibility supports a pilot path")
        if signals["design_success"]:
            drivers.append("system design blueprint is available")
        if signals["buyer_pull_score"] >= 0.78:
            drivers.append("strong buyer pull")
        if signals["category_creation_score"] >= 0.78:
            drivers.append("platform/category formation signal")
        if signals["value_capture_score"] >= 0.70:
            drivers.append("value capture potential")
        if signals["buyer_roi_score"] < 0.62:
            drivers.append("buyer ROI still needs proof")
        if signals["data_readiness_score"] and signals["data_readiness_score"] < 0.50:
            drivers.append("data readiness requires focused validation")
        if signals["blocker_level"] == "conditional":
            drivers.append("conditional blocker requires control-gated launch")
        return drivers or ["baseline productization indicators"]

    def _confidence(self, signals: Dict[str, Any], productization_score: Dict[str, Any]) -> float:
        return round(self._bounded(
            0.20
            + productization_score.get("score", 0.0) * 0.16
            + signals["technical_feasibility_score"] * 0.10
            + signals["opportunity_score"] * 0.08
            + signals["buyer_pull_score"] * 0.07
            + signals["value_capture_score"] * 0.06
            + signals["portfolio_score"] * 0.06
            + signals["market_gap_confidence"] * 0.05
            + (0.04 if signals["design_success"] else 0.0)
            - signals["risk_score"] * 0.02
            - signals["commercial_risk_score"] * 0.02
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
