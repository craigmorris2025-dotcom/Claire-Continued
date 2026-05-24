"""
Strategic Positioning Engine — dedicated Stage 18 engine for Claire.

v5.26:
- Converts Strategic Positioning from a binder-derived partial into a real engine.
- Synthesizes market gap, opportunity, breakthrough, technical feasibility,
  productization, moat, risk, business model, deal/exit, acquirer matches, and
  design outputs into a positioning system.
- Produces category narrative, buyer narrative, acquirer narrative, competitive
  framing, risk framing, proof stack, messaging hierarchy, and strategic roadmap.
"""

from typing import Any, Dict, List, Optional


class StrategicPositioningEngine:
    """Deterministic strategic positioning analyzer."""

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
        productization_path: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        business_model: Optional[Dict[str, Any]] = None,
        deal_exit_modeling: Optional[Dict[str, Any]] = None,
        design_output: Optional[Dict[str, Any]] = None,
        acquirer_matches: Optional[List[Dict[str, Any]]] = None,
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
        productization_path = productization_path or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        business_model = business_model or {}
        deal_exit_modeling = deal_exit_modeling or {}
        design_output = design_output or {}
        acquirer_matches = acquirer_matches or []
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
            productization_path=productization_path,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            deal_exit_modeling=deal_exit_modeling,
            design_output=design_output,
            acquirer_matches=acquirer_matches,
            connector_sources=connector_sources,
        )

        positioning_score = self._positioning_score(signals)
        classification = self._classification(signals, positioning_score)

        return {
            "status": "success",
            "domain": signals["domain"],
            "sector": signals["sector"],
            "strategic_positioning_score": positioning_score,
            "positioning_classification": classification,
            "category_positioning": self._category_positioning(signals, classification),
            "buyer_positioning": self._buyer_positioning(signals, classification),
            "acquirer_positioning": self._acquirer_positioning(signals, classification),
            "competitive_positioning": self._competitive_positioning(signals),
            "risk_positioning": self._risk_positioning(signals, classification),
            "proof_stack": self._proof_stack(signals),
            "message_hierarchy": self._message_hierarchy(signals, classification),
            "sales_enablement": self._sales_enablement(signals, classification),
            "strategic_roadmap": self._strategic_roadmap(signals, classification),
            "positioning_risks": self._positioning_risks(signals),
            "recommended_next_actions": self._recommended_next_actions(signals, classification),
            "strategic_positioning_thesis": self._thesis(signals, classification, positioning_score),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, positioning_score),
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
        breakthrough_synthesis: Dict[str, Any],
        technical_feasibility: Dict[str, Any],
        productization_path: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        deal_exit_modeling: Dict[str, Any],
        design_output: Dict[str, Any],
        acquirer_matches: List[Dict[str, Any]],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector = market_gap.get("sector", "general_intelligence") if isinstance(market_gap, dict) else "general_intelligence"
        domain = self._domain_for_sector(sector, domain)
        profile = self._sector_profile(sector)
        combined = f"{text.lower()} {' '.join([str(k).lower() for k in keywords])}"

        category_terms = self._count_terms(combined, ["platform", "category", "market", "wedge", "ecosystem", "layer"])
        buyer_terms = self._count_terms(combined, ["buyer", "operator", "underwriter", "mission", "workflow", "pain", "urgent", "review"])
        proof_terms = self._count_terms(combined, ["proof", "pilot", "validation", "backtest", "audit", "simulation", "roi", "evidence"])
        differentiation_terms = self._count_terms(combined, ["moat", "defensible", "proprietary", "integration", "workflow", "benchmark", "data"])

        top_acquirer = acquirer_matches[0] if acquirer_matches else {}
        avg_top_5 = 0.0
        if acquirer_matches:
            top_scores = [float(m.get("match_score", 0.0) or 0.0) for m in acquirer_matches[:5]]
            avg_top_5 = sum(top_scores) / len(top_scores) if top_scores else 0.0

        design_modules = design_output.get("architecture_blueprint", {}).get("modules", []) if isinstance(design_output, dict) else []
        design_artifacts = design_output.get("portfolio_artifacts", {}).get("sector_appendices", []) if isinstance(design_output, dict) else []

        return {
            "domain": domain,
            "sector": sector,
            "sector_label": profile["label"],
            "category_term_count": category_terms,
            "buyer_term_count": buyer_terms,
            "proof_term_count": proof_terms,
            "differentiation_term_count": differentiation_terms,
            "breakthrough_score": float(scores.get("breakthrough_score", 0.0) or 0.0),
            "portfolio_score": float(scores.get("portfolio_score", 0.0) or 0.0),
            "productization_score": float(scores.get("productization_score", 0.0) or 0.0),
            "pilot_readiness_score": float(scores.get("pilot_readiness_score", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "gap_type": market_gap.get("gap_type", profile["gap_type"]),
            "market_gap_text": market_gap.get("market_gap", profile["market_gap"]),
            "needed_solution": market_gap.get("needed_solution", profile["needed_solution"]),
            "solution_class": market_gap.get("solution_class", profile["solution_class"]),
            "buyer_segments": market_gap.get("buyer_segments", []),
            "strategic_pressure_score": self._nested(market_gap, "strategic_pressure", "score"),
            "trend_direction": self._nested_text(trend_trajectory, "trend_direction", "direction"),
            "timing_pressure_score": self._nested(trend_trajectory, "timing_pressure", "score"),
            "strategic_window": self._nested_text(trend_trajectory, "strategic_window", "window"),
            "market_stage": self._nested_text(market_formation, "market_stage", "stage"),
            "formation_type": self._nested_text(market_formation, "formation_type", "type"),
            "category_creation_score": self._nested(market_formation, "category_creation_score", "score"),
            "buyer_pull_score": self._nested(market_formation, "buyer_pull", "score"),
            "buyer_pull_strength": self._nested_text(market_formation, "buyer_pull", "strength"),
            "opportunity_score": self._nested(opportunity_discovery, "opportunity_score", "score"),
            "opportunity_type": self._nested_text(opportunity_discovery, "opportunity_type", "type"),
            "opportunity_priority": self._nested_text(opportunity_discovery, "priority_assessment", "priority"),
            "breakthrough_synthesis_score": self._nested(breakthrough_synthesis, "breakthrough_synthesis_score", "score"),
            "breakthrough_classification": self._nested_text(breakthrough_synthesis, "breakthrough_classification", "classification"),
            "breakthrough_readiness_modifier": self._nested_text(breakthrough_synthesis, "breakthrough_classification", "readiness_modifier"),
            "non_obviousness_level": self._nested_text(breakthrough_synthesis, "non_obviousness", "level"),
            "technical_feasibility_score": self._nested(technical_feasibility, "technical_feasibility_score", "score"),
            "technical_state": self._nested_text(technical_feasibility, "feasibility_classification", "state"),
            "deployment_posture": self._nested_text(technical_feasibility, "feasibility_classification", "deployment_posture"),
            "productization_state": self._nested_text(productization_path, "productization_classification", "state"),
            "productization_modifier": self._nested_text(productization_path, "productization_classification", "readiness_modifier"),
            "launch_posture": self._nested_text(productization_path, "productization_classification", "launch_posture"),
            "pilot_type": self._nested_text(productization_path, "pilot_strategy", "pilot_type"),
            "gtm_readiness_score": self._nested(productization_path, "go_to_market_readiness", "score"),
            "gtm_readiness_level": self._nested_text(productization_path, "go_to_market_readiness", "level"),
            "moat_score": self._nested(moat, "moat_type", "moat_score"),
            "moat_strength": self._nested_text(moat, "moat_type", "strength"),
            "primary_moat": self._nested_text(moat, "moat_type", "primary_moat"),
            "copy_risk_score": self._nested(moat, "copy_risk", "score"),
            "risk_score": self._nested(risk_regulation, "risk_profile", "score"),
            "risk_level": self._nested_text(risk_regulation, "risk_profile", "level"),
            "regulatory_exposure": self._nested_text(risk_regulation, "regulation_profile", "exposure"),
            "regulatory_exposure_score": self._nested(risk_regulation, "regulation_profile", "score"),
            "blocker_level": self._nested_text(risk_regulation, "blocker_assessment", "blocker_level") or "unknown",
            "value_capture_score": self._nested(business_model, "value_capture", "score"),
            "value_capture_strength": self._nested_text(business_model, "value_capture", "strength"),
            "buyer_roi_score": self._nested(business_model, "buyer_roi", "score"),
            "buyer_roi_strength": self._nested_text(business_model, "buyer_roi", "roi_strength"),
            "revenue_model": self._nested_text(business_model, "revenue_model", "primary_model"),
            "commercial_risk_score": self._nested(business_model, "commercial_risk", "score"),
            "commercial_risk_level": self._nested_text(business_model, "commercial_risk", "level"),
            "exit_state": self._nested_text(deal_exit_modeling, "exit_readiness", "state"),
            "exit_readiness_score": self._nested(deal_exit_modeling, "exit_readiness", "score"),
            "strategic_fit_level": self._nested_text(deal_exit_modeling, "strategic_fit", "level"),
            "strategic_fit_score": self._nested(deal_exit_modeling, "strategic_fit", "score"),
            "valuation_signal": self._nested_text(deal_exit_modeling, "valuation_logic", "valuation_signal", "strength"),
            "valuation_signal_score": self._nested(deal_exit_modeling, "valuation_logic", "valuation_signal", "score"),
            "acquirer_count": len(acquirer_matches),
            "top_acquirer_name": top_acquirer.get("name", ""),
            "top_acquirer_score": float(top_acquirer.get("match_score", 0.0) or 0.0),
            "avg_top_5_acquirer_score": avg_top_5,
            "design_success": design_output.get("status") == "success" if isinstance(design_output, dict) else False,
            "design_module_count": len(design_modules) if isinstance(design_modules, list) else 0,
            "design_artifact_count": len(design_artifacts) if isinstance(design_artifacts, list) else 0,
        }

    def _positioning_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.12
            + signals["opportunity_score"] * 0.080
            + signals["breakthrough_synthesis_score"] * 0.085
            + signals["productization_score"] * 0.075
            + signals["strategic_fit_score"] * 0.085
            + signals["valuation_signal_score"] * 0.060
            + signals["market_gap_confidence"] * 0.060
            + signals["category_creation_score"] * 0.065
            + signals["buyer_pull_score"] * 0.070
            + signals["value_capture_score"] * 0.050
            + signals["moat_score"] * 0.045
            + (1.0 - signals["copy_risk_score"]) * 0.035
            + min(0.035, signals["category_term_count"] * 0.006)
            + min(0.035, signals["buyer_term_count"] * 0.006)
            + min(0.035, signals["proof_term_count"] * 0.006)
            + (0.045 if signals["design_success"] else 0.0)
            + min(0.030, signals["acquirer_count"] * 0.004)
            - signals["risk_score"] * 0.018
            - signals["commercial_risk_score"] * 0.020
            - (0.035 if signals["blocker_level"] == "conditional" else 0.0)
        )
        level = "category_defining" if score >= 0.78 else "strong" if score >= 0.64 else "emerging" if score >= 0.50 else "weak"
        return {"level": level, "score": round(score, 4), "drivers": self._positioning_drivers(signals)}

    def _classification(self, signals: Dict[str, Any], positioning_score: Dict[str, Any]) -> Dict[str, Any]:
        score = positioning_score.get("score", 0.0)
        if score >= 0.78:
            state = "category_positioned"
        elif score >= 0.64:
            state = "strategically_positioned"
        elif score >= 0.50:
            state = "positioning_candidate"
        else:
            state = "positioning_unproven"

        if signals["blocker_level"] == "conditional" or signals["productization_modifier"] == "control_gated":
            readiness_modifier = "control_gated_positioning"
            narrative_posture = "strategic_candidate_with_controls"
        elif signals["buyer_roi_score"] < 0.62:
            readiness_modifier = "roi_unproven"
            narrative_posture = "validation_first"
        elif signals["moat_score"] < 0.62:
            readiness_modifier = "defensibility_unproven"
            narrative_posture = "category_wedge_with_moat_proof_needed"
        else:
            readiness_modifier = "standard"
            narrative_posture = "category_leadership"

        return {
            "state": state,
            "readiness_modifier": readiness_modifier,
            "narrative_posture": narrative_posture,
            "recommended_positioning_motion": self._sector_profile(signals["sector"])["positioning_motion"],
            "score_used": round(score, 4),
        }

    def _category_positioning(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "category_name": profile["category_name"],
            "category_claim": profile["category_claim"],
            "positioning_angle": profile["positioning_angle"],
            "why_now": f"The trend is {self._pretty(signals['trend_direction'] or 'emerging')}, the strategic window is {self._pretty(signals['strategic_window'] or 'active')}, and category creation score is {signals['category_creation_score']:.4f}.",
            "category_maturity": signals["market_stage"] or "unknown",
            "narrative_posture": classification["narrative_posture"],
        }

    def _buyer_positioning(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "primary_buyer": self._first(signals["buyer_segments"], profile["primary_buyer"]),
            "buyer_pain_statement": profile["buyer_pain_statement"],
            "buyer_value_proposition": profile["buyer_value_proposition"],
            "first_offer": profile["first_offer"],
            "workflow_wedge": profile["workflow_wedge"],
            "economic_buyer_message": profile["economic_buyer_message"],
            "proof_needed_to_sell": profile["proof_needed_to_sell"],
        }

    def _acquirer_positioning(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "top_acquirer": signals["top_acquirer_name"] or "not_available",
            "top_acquirer_score": round(signals["top_acquirer_score"], 4),
            "buyer_universe_depth": "deep" if signals["acquirer_count"] >= 6 else "moderate" if signals["acquirer_count"] >= 3 else "thin",
            "strategic_fit": signals["strategic_fit_level"] or "unknown",
            "valuation_signal": signals["valuation_signal"] or "unknown",
            "acquirer_pitch": profile["acquirer_pitch"],
            "strategic_rationale": profile["strategic_rationale"],
            "deal_positioning_note": self._deal_positioning_note(signals),
        }

    def _competitive_positioning(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "competitive_frame": profile["competitive_frame"],
            "differentiation_claim": profile["differentiation_claim"],
            "incumbent_blind_spot": profile["incumbent_blind_spot"],
            "moat_message": self._moat_message(signals),
            "copy_risk_message": self._copy_risk_message(signals),
        }

    def _risk_positioning(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        risk_frame = "controls_as_advantage" if classification["readiness_modifier"] == "control_gated_positioning" else "standard_enterprise_risk_management"
        return {
            "risk_frame": risk_frame,
            "risk_level": signals["risk_level"] or "unknown",
            "regulatory_exposure": signals["regulatory_exposure"] or "unknown",
            "blocker_level": signals["blocker_level"],
            "control_narrative": profile["control_narrative"] if risk_frame == "controls_as_advantage" else "Position risk controls as enterprise trust, auditability, and repeatability.",
            "buyer_reassurance_points": profile["buyer_reassurance_points"],
        }

    def _proof_stack(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "already_supported": self._proof_supported(signals),
            "critical_missing_proof": profile["critical_missing_proof"],
            "proof_sequence": profile["proof_sequence"],
            "minimum_positioning_evidence_pack": profile["minimum_positioning_evidence_pack"],
        }

    def _message_hierarchy(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "one_liner": profile["one_liner"],
            "short_pitch": profile["short_pitch"],
            "long_pitch": profile["long_pitch"],
            "tagline_options": profile["tagline_options"],
            "do_not_say": profile["do_not_say"],
        }

    def _sales_enablement(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        profile = self._sector_profile(signals["sector"])
        return {
            "first_conversation_goal": profile["first_conversation_goal"],
            "discovery_questions": profile["discovery_questions"],
            "objection_handling": profile["objection_handling"],
            "pilot_close_message": profile["pilot_close_message"],
        }

    def _strategic_roadmap(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        profile = self._sector_profile(signals["sector"])
        roadmap = [
            {"phase": 1, "name": "Narrative lock", "objective": "Lock category name, buyer pain, wedge, and proof sequence.", "deliverables": ["category statement", "buyer pain memo", "wedge narrative", "proof map"], "priority": "critical"},
            {"phase": 2, "name": "Proof-backed positioning", "objective": profile["proof_objective"], "deliverables": profile["proof_deliverables"], "priority": "critical"},
            {"phase": 3, "name": "Buyer message test", "objective": profile["buyer_message_objective"], "deliverables": ["buyer call script", "objection log", "message resonance notes"], "priority": "high"},
            {"phase": 4, "name": "Acquirer narrative", "objective": profile["acquirer_message_objective"], "deliverables": ["acquirer-specific one-pagers", "strategic rationale", "deal proof gaps"], "priority": "high"},
            {"phase": 5, "name": "Binder-ready positioning", "objective": "Package the strategic narrative for portfolio, partner, and deal-review workflows.", "deliverables": ["positioning section", "proof appendix", "risk narrative", "pilot ask"], "priority": "high"},
        ]
        if classification["readiness_modifier"] == "control_gated_positioning":
            roadmap.insert(2, {"phase": 3, "name": "Control narrative validation", "objective": "Turn controls from a blocker into a trust and adoption narrative.", "deliverables": ["allowed-use statement", "human-review narrative", "audit proof", "deployment boundary"], "priority": "critical"})
            for idx, item in enumerate(roadmap, start=1):
                item["phase"] = idx
        return roadmap

    def _positioning_risks(self, signals: Dict[str, Any]) -> List[Dict[str, str]]:
        risks = []
        if signals["buyer_roi_score"] < 0.62:
            risks.append({"risk": "ROI narrative not yet quantified", "impact": "buyers and acquirers may see a strategic story but discount value capture", "severity": "high", "mitigation": "instrument ROI in the pilot proof stack"})
        if signals["moat_score"] < 0.70:
            risks.append({"risk": "defensibility narrative remains moderate", "impact": "strategic buyers may see copy risk unless workflow/data loops are proven", "severity": "medium", "mitigation": "position integration depth and proof of recurring workflow use"})
        if signals["blocker_level"] == "conditional":
            risks.append({"risk": "controls could overwhelm the narrative", "impact": "buyers may focus on deployment constraints instead of value", "severity": "high", "mitigation": "frame controls as the reason the category is deployable and trustworthy"})
        return risks or [{"risk": "message proof drift", "impact": "positioning can become generic if not tied to evidence", "severity": "medium", "mitigation": "tie every claim to a proof artifact"}]

    def _recommended_next_actions(self, signals: Dict[str, Any], classification: Dict[str, Any]) -> List[Dict[str, str]]:
        profile = self._sector_profile(signals["sector"])
        actions = [
            {"action": profile["first_action"], "purpose": "turn the strategy into a buyer-testable category narrative", "priority": "critical"},
            {"action": profile["second_action"], "purpose": "make the positioning defensible with product, pilot, and proof evidence", "priority": "critical"},
            {"action": "write acquirer-specific positioning one-pagers", "purpose": "connect Claire outputs to concrete strategic-buyer motivations", "priority": "high"},
            {"action": "instrument message tests during pilot discovery", "purpose": "learn which claims buyers repeat, challenge, or ignore", "priority": "high"},
        ]
        if classification["readiness_modifier"] == "control_gated_positioning":
            actions.insert(2, {"action": "validate control narrative", "purpose": "frame governance, human review, and auditability as product advantages instead of blockers", "priority": "critical"})
        return actions

    def _thesis(self, signals: Dict[str, Any], classification: Dict[str, Any], positioning_score: Dict[str, Any]) -> str:
        return (
            f"{signals['sector_label']} is {classification.get('state')} with {positioning_score.get('level')} "
            f"strategic positioning strength and a score of {positioning_score.get('score')}. The recommended posture is "
            f"{self._pretty(classification.get('narrative_posture'))}. The narrative should lead with the category wedge, "
            f"buyer pain, control-aware proof stack, pilot motion, and acquirer-ready strategic rationale."
        )

    def _sector_profile(self, sector: str) -> Dict[str, Any]:
        profiles = {
            "defense_autonomy": {
                "label": "defense autonomy",
                "gap_type": "mission autonomy / low-latency decision / distributed coordination",
                "market_gap": "Defense operators need secure, human-reviewed autonomy and mission intelligence under contested, low-latency conditions.",
                "needed_solution": "Distributed autonomous decision platform with secure command integration, simulation data, auditability, and human override controls.",
                "solution_class": "distributed autonomous decision platform",
                "category_name": "secure autonomous mission intelligence",
                "category_claim": "A governable mission-intelligence layer for simulation-backed, human-authorized autonomy support.",
                "positioning_angle": "not full autonomy; deployable autonomy with trust, authorization, simulation, and auditability",
                "positioning_motion": "control-gated category wedge to secure mission intelligence platform",
                "primary_buyer": "mission operators and secure command stakeholders",
                "buyer_pain_statement": "Mission teams need faster coordination intelligence without surrendering human authorization or secure command controls.",
                "buyer_value_proposition": "Improve mission review speed and coordination quality while preserving authorization, allowed-use boundaries, and audit evidence.",
                "first_offer": "secure mission simulation and review pilot",
                "workflow_wedge": "mission simulation, operator review, authorization state, and audit trace",
                "economic_buyer_message": "Start with a controlled validation pilot that measures time-to-decision, operator acceptance, and coordination-quality improvement.",
                "proof_needed_to_sell": ["mission simulation validation", "operator review acceptance", "allowed-use policy", "audit replay", "time-to-decision estimate"],
                "acquirer_pitch": "Own the reviewable decision layer between autonomous systems, sensor context, mission simulation, and secure command workflows.",
                "strategic_rationale": "Defense primes and defense-tech platforms can use this to make autonomy deployable through governance, review, and evidence rather than raw automation alone.",
                "competitive_frame": "sits between autonomous platforms, sensor fusion, command systems, and operator-review workflows",
                "differentiation_claim": "differentiated by secure workflow integration, simulation evidence, human authorization, and mission audit history",
                "incumbent_blind_spot": "incumbents may focus on platforms or algorithms while underbuilding the reviewable mission-decision layer",
                "control_narrative": "Controls are the product advantage: the system is positioned as autonomy that can be reviewed, authorized, audited, and constrained.",
                "buyer_reassurance_points": ["human authorization required", "advisory/shadow mode first", "allowed-use boundaries", "audit trail retained", "secure deployment boundary"],
                "critical_missing_proof": ["operator trust", "simulation-to-reality validation", "ROI/time-to-decision evidence", "secure workflow acceptance", "control plan approval"],
                "proof_sequence": ["simulation evidence", "operator review", "control validation", "workflow adoption", "ROI evidence", "defensibility evidence"],
                "minimum_positioning_evidence_pack": ["mission simulation memo", "operator review notes", "allowed-use policy", "audit trace sample", "pilot scorecard"],
                "one_liner": "A secure autonomous mission-intelligence layer for reviewable, simulation-backed, human-authorized decision support.",
                "short_pitch": "Claire positions this as deployable autonomy infrastructure: a mission-intelligence layer that connects simulation, sensor context, secure command review, authorization, and audit evidence.",
                "long_pitch": "The strategic opening is not full autonomy. It is the governable layer that lets mission teams evaluate autonomous recommendations in simulation or shadow mode, review them through secure command workflows, preserve human authorization, and build an evidence trail for controlled deployment.",
                "tagline_options": ["Deployable autonomy with human authority", "Mission intelligence you can review", "Autonomy that earns trust before automation"],
                "do_not_say": ["fully autonomous battlefield decisioning", "remove humans from mission decisions", "unrestricted operational automation"],
                "first_conversation_goal": "Confirm whether mission teams need reviewable autonomy support and what evidence would justify a controlled pilot.",
                "discovery_questions": ["Where do coordination decisions slow down today?", "Which mission scenarios can be simulated safely?", "What must remain human-authorized?", "What audit evidence would make this acceptable?", "What would prove time-to-decision value?"],
                "objection_handling": ["If autonomy risk is raised, position the pilot as advisory/shadow mode with human authorization.", "If simulation fidelity is challenged, lead with scenario-family validation and operator review.", "If procurement risk is raised, frame the first step as a controlled validation pilot."],
                "pilot_close_message": "The pilot does not automate mission decisions; it proves whether simulation-backed recommendations can be reviewed, authorized, audited, and tied to measurable mission-workflow value.",
                "proof_objective": "Prove the mission-intelligence layer is useful, reviewable, and control-ready.",
                "proof_deliverables": ["simulation memo", "operator review summary", "allowed-use policy", "audit trace", "time-to-decision baseline"],
                "buyer_message_objective": "Test whether buyers repeat the control-aware autonomy narrative and accept the pilot wedge.",
                "acquirer_message_objective": "Show strategic buyers why the reviewable mission-decision layer fills a category gap in their autonomy roadmaps.",
                "first_action": "lock the secure autonomous mission intelligence category narrative",
                "second_action": "build the control-aware proof stack for the mission simulation pilot",
            },
            "climate_insurance": {
                "label": "climate insurance",
                "gap_type": "climate exposure / underwriting repricing / market withdrawal",
                "market_gap": "Insurers need earlier visibility into climate exposure, repricing pressure, and market-withdrawal risk.",
                "needed_solution": "Climate insurance risk intelligence platform.",
                "solution_class": "climate insurance risk intelligence platform",
                "category_name": "climate insurance risk intelligence",
                "category_claim": "An underwriting-grade intelligence layer for climate exposure, repricing pressure, and risk-transfer decisions.",
                "positioning_angle": "not just climate analytics; underwriting decision infrastructure for climate-driven insurance markets",
                "positioning_motion": "underwriting wedge to enterprise climate risk platform",
                "primary_buyer": "underwriting and portfolio risk teams",
                "buyer_pain_statement": "Underwriters need earlier confidence on climate exposure concentration and repricing pressure.",
                "buyer_value_proposition": "Improve underwriting, pricing, portfolio steering, and risk-transfer decisions with backtested climate-loss and exposure intelligence.",
                "first_offer": "climate exposure and repricing pilot",
                "workflow_wedge": "underwriter review console with weather-loss backtesting and exposure benchmarks",
                "economic_buyer_message": "Start with one peril/region/portfolio pilot and quantify avoided loss exposure or pricing improvement.",
                "proof_needed_to_sell": ["weather-loss backtest", "repricing signal accuracy", "underwriter workflow adoption", "exposure benchmark value"],
                "acquirer_pitch": "Own the underwriting workflow layer between catastrophe models, exposure data, and risk-transfer decisions.",
                "strategic_rationale": "Insurance analytics, reinsurers, and workflow platforms can use this to own a strategic climate-risk decision layer.",
                "competitive_frame": "sits between catastrophe modeling, property data, underwriting workflow, and risk-transfer planning",
                "differentiation_claim": "differentiated by exposure benchmarks, repricing signals, underwriter workflow embedding, and scenario history",
                "incumbent_blind_spot": "incumbents may treat climate data and underwriting workflow as separate categories",
                "control_narrative": "Model governance, pricing audit logs, and underwriter review controls make the system deployable in regulated workflows.",
                "buyer_reassurance_points": ["underwriter review required", "pricing-impact audit log", "data lineage", "scenario versioning"],
                "critical_missing_proof": ["repricing accuracy", "underwriter adoption", "ROI", "data rights"],
                "proof_sequence": ["weather-loss backtest", "underwriter review", "ROI model", "benchmark validation", "enterprise expansion"],
                "minimum_positioning_evidence_pack": ["backtest memo", "exposure benchmark", "workflow demo", "ROI scorecard"],
                "one_liner": "Underwriting-grade climate risk intelligence for exposure, repricing, and risk-transfer decisions.",
                "short_pitch": "Claire positions this as the decision layer that turns climate-loss and exposure signals into underwriting workflow intelligence.",
                "long_pitch": "The strategic opening is the move from climate analytics to underwriting-grade decision infrastructure: backtested exposure intelligence, repricing signals, portfolio steering, and risk-transfer recommendations embedded into review workflows.",
                "tagline_options": ["Climate risk intelligence for underwriting decisions", "Reprice climate exposure before the market does", "From climate data to underwriting action"],
                "do_not_say": ["black-box pricing automation", "replace underwriters", "guaranteed climate-loss prediction"],
                "first_conversation_goal": "Confirm whether underwriters see recurring climate repricing pain and what proof would justify a pilot.",
                "discovery_questions": ["Which perils are hardest to price?", "Where does exposure concentration surprise you?", "What signals would change underwriting action?", "What does a useful backtest need to show?"],
                "objection_handling": ["If model trust is challenged, lead with backtests and transparent scenario versioning.", "If workflow friction is raised, position the console as review support, not automation."],
                "pilot_close_message": "The pilot proves whether backtested exposure and repricing signals improve underwriter review decisions in one focused portfolio.",
                "proof_objective": "Prove climate-loss signals and exposure benchmarks improve underwriting decisions.",
                "proof_deliverables": ["weather-loss backtest", "underwriter feedback", "exposure benchmark", "ROI estimate"],
                "buyer_message_objective": "Test whether buyers repeat the underwriting-grade climate intelligence narrative.",
                "acquirer_message_objective": "Show strategic buyers why the system owns the workflow layer between climate risk data and underwriting action.",
                "first_action": "lock the climate insurance risk intelligence narrative",
                "second_action": "build the underwriting proof stack for the climate exposure pilot",
            },
        }
        default = {
            "label": str(sector or "general").replace("_", " "),
            "gap_type": "strategic opportunity gap",
            "market_gap": "A meaningful strategic opportunity gap was identified.",
            "needed_solution": "Validated intelligence product.",
            "solution_class": "opportunity intelligence platform",
            "category_name": "opportunity intelligence",
            "category_claim": "A workflow intelligence layer for discovering, validating, and packaging non-obvious opportunities.",
            "positioning_angle": "not search; opportunity synthesis with validation and portfolio packaging",
            "positioning_motion": "focused workflow wedge to enterprise platform",
            "primary_buyer": "strategy and innovation teams",
            "buyer_pain_statement": "Teams need faster discovery, validation, and packaging of non-obvious opportunities.",
            "buyer_value_proposition": "Reduce research time and improve quality of opportunity validation, design, and portfolio decisions.",
            "first_offer": "focused opportunity validation pilot",
            "workflow_wedge": "one repeatable discovery-to-validation workflow",
            "economic_buyer_message": "Start with a paid pilot that measures speed, quality, and decision impact.",
            "proof_needed_to_sell": ["historical benchmark", "workflow adoption", "ROI baseline", "buyer acceptance"],
            "acquirer_pitch": "Own the opportunity-intelligence workflow across discovery, validation, design, and portfolio packaging.",
            "strategic_rationale": "Strategic buyers can use the system to expand into higher-value decision intelligence workflows.",
            "competitive_frame": "sits between research, analytics, strategy, design, and portfolio workflows",
            "differentiation_claim": "differentiated by synthesis, validation, workflow packaging, and reusable evidence traces",
            "incumbent_blind_spot": "incumbents may optimize search or dashboards while missing the opportunity synthesis workflow",
            "control_narrative": "Auditability and evidence traces make the system trustworthy for enterprise decisions.",
            "buyer_reassurance_points": ["human review", "evidence trace", "auditability", "clear no-go criteria"],
            "critical_missing_proof": ["buyer workflow fit", "ROI", "repeatability", "defensibility"],
            "proof_sequence": ["buyer pain", "historical benchmark", "workflow adoption", "ROI", "defensibility"],
            "minimum_positioning_evidence_pack": ["opportunity thesis", "workflow demo", "proof memo", "pilot scorecard"],
            "one_liner": "Opportunity intelligence that turns fragmented signals into validated, buildable, portfolio-ready opportunities.",
            "short_pitch": "Claire positions this as a workflow layer that discovers non-obvious opportunities and packages them for validation, design, portfolio, and deal-readiness workflows.",
            "long_pitch": "The strategic opening is the shift from passive research to active opportunity intelligence: detect gaps, synthesize breakthrough patterns, validate feasibility, define productization, and package the opportunity for buyers and strategic partners.",
            "tagline_options": ["From weak signals to validated opportunities", "Opportunity intelligence for strategic teams", "Discover, validate, and package what others miss"],
            "do_not_say": ["generic search tool", "fully automated strategy replacement", "guaranteed market prediction"],
            "first_conversation_goal": "Confirm the buyer's current opportunity discovery workflow and what proof would justify a pilot.",
            "discovery_questions": ["Where do opportunities get missed today?", "What evidence changes your decision?", "Which workflow should the pilot improve?", "How is ROI measured?"],
            "objection_handling": ["If outputs feel generic, narrow to one workflow and proof standard.", "If ROI is challenged, instrument time savings and decision quality from the start."],
            "pilot_close_message": "The pilot proves whether opportunity intelligence improves one repeatable workflow with measurable evidence.",
            "proof_objective": "Prove the strategic narrative is grounded in repeatable buyer value.",
            "proof_deliverables": ["buyer validation memo", "workflow scorecard", "proof stack", "ROI baseline"],
            "buyer_message_objective": "Test whether buyers understand and repeat the opportunity-intelligence category narrative.",
            "acquirer_message_objective": "Show strategic buyers where the workflow expands their product/category roadmap.",
            "first_action": "lock the category narrative and buyer wedge",
            "second_action": "build the proof stack for the focused pilot",
        }
        if sector in {"healthcare_operations", "financial_market_intelligence", "industrial_supply_chain", "energy_infrastructure"}:
            custom = dict(default)
            custom["label"] = str(sector).replace("_", " ")
            custom["category_name"] = {
                "healthcare_operations": "healthcare operations intelligence",
                "financial_market_intelligence": "financial signal intelligence",
                "industrial_supply_chain": "industrial resilience intelligence",
                "energy_infrastructure": "energy infrastructure intelligence",
            }.get(sector, default["category_name"])
            custom["first_offer"] = {
                "healthcare_operations": "capacity and patient-flow pilot",
                "financial_market_intelligence": "institutional signal intelligence pilot",
                "industrial_supply_chain": "supplier-risk and shortage forecasting pilot",
                "energy_infrastructure": "grid bottleneck and resilience planning pilot",
            }.get(sector, default["first_offer"])
            custom["positioning_angle"] = f"focused {custom['category_name']} wedge to enterprise platform"
            custom["one_liner"] = f"{custom['category_name'].title()} for high-pressure operational decisions."
            return custom
        return profiles.get(sector, default)

    def _positioning_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []
        if signals["category_creation_score"] >= 0.78:
            drivers.append("strong category-creation signal")
        if signals["buyer_pull_score"] >= 0.78:
            drivers.append("strong buyer pull")
        if signals["breakthrough_synthesis_score"] >= 0.78:
            drivers.append("breakthrough synthesis supports strategic narrative")
        if signals["productization_score"] >= 0.64:
            drivers.append("productization path supports pilotable positioning")
        if signals["strategic_fit_score"] >= 0.80:
            drivers.append("strong strategic-buyer fit")
        if signals["value_capture_score"] >= 0.70:
            drivers.append("value capture supports commercial message")
        if signals["blocker_level"] == "conditional":
            drivers.append("control-gated deployment must be part of positioning")
        return drivers or ["baseline strategic positioning signals"]

    def _proof_supported(self, signals: Dict[str, Any]) -> List[str]:
        proof = []
        if signals["market_gap_confidence"] >= 0.80:
            proof.append("validated market gap")
        if signals["buyer_pull_score"] >= 0.78:
            proof.append("strong buyer-pull signal")
        if signals["breakthrough_synthesis_score"] >= 0.78:
            proof.append("breakthrough synthesis narrative")
        if signals["technical_feasibility_score"] >= 0.60:
            proof.append("technical feasibility path")
        if signals["productization_score"] >= 0.60:
            proof.append("pilotable productization path")
        if signals["strategic_fit_score"] >= 0.80:
            proof.append("strategic acquirer fit")
        return proof or ["initial opportunity thesis"]

    def _deal_positioning_note(self, signals: Dict[str, Any]) -> str:
        if signals["exit_state"] and "conditions" in signals["exit_state"]:
            return "Position as a strategic candidate, but lead diligence with blocker mitigation, ROI proof, and defensibility evidence."
        if signals["strategic_fit_score"] >= 0.80:
            return "Position as a strategic roadmap-fit asset with buyer and platform expansion logic."
        return "Position as a validation-stage asset until proof stack and buyer evidence improve."

    def _moat_message(self, signals: Dict[str, Any]) -> str:
        moat = self._pretty(signals["primary_moat"] or "defensibility")
        if signals["moat_score"] >= 0.70:
            return f"Lead with {moat} as a compounding advantage."
        return f"Frame {moat} as the defensibility path, but acknowledge that proof must be strengthened."

    def _copy_risk_message(self, signals: Dict[str, Any]) -> str:
        if signals["copy_risk_score"] <= 0.30:
            return "Copy risk is low if integration depth, workflow embedding, and proof history are captured early."
        return "Copy risk must be reduced through proprietary data loops, workflow adoption, and buyer-specific integrations."

    def _confidence(self, signals: Dict[str, Any], positioning_score: Dict[str, Any]) -> float:
        return round(self._bounded(
            0.20
            + positioning_score.get("score", 0.0) * 0.16
            + signals["opportunity_score"] * 0.08
            + signals["breakthrough_synthesis_score"] * 0.08
            + signals["productization_score"] * 0.07
            + signals["strategic_fit_score"] * 0.07
            + signals["market_gap_confidence"] * 0.06
            + signals["buyer_pull_score"] * 0.06
            + signals["value_capture_score"] * 0.05
            + (0.03 if signals["design_success"] else 0.0)
            - signals["risk_score"] * 0.02
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

    def _first(self, values: Any, fallback: str) -> str:
        if isinstance(values, list) and values:
            return str(values[0])
        return fallback

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
