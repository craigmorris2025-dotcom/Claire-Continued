
"""
Portfolio Binder Builder — assembles Claire outputs into a structured portfolio / binder package.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


class PortfolioBinderBuilder:
    """Builds a structured portfolio binder from a completed Claire pipeline run."""

    def build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not context:
            return {"status": "binder_failed", "error": "No binder context provided."}

        scores = context.get("scores", {})
        domain = context.get("domain", "general")
        keywords = context.get("keywords", [])
        market_gap = context.get("market_gap", {})
        trend_trajectory = context.get("trend_trajectory", {})
        market_formation = context.get("market_formation", {})
        moat = context.get("moat", {})
        risk_regulation = context.get("risk_regulation", {})
        business_model = context.get("business_model", {})
        opportunity_discovery = context.get("opportunity_discovery", {})
        breakthrough_synthesis = context.get("breakthrough_synthesis", {})
        technical_feasibility = context.get("technical_feasibility", {})
        productization_path = context.get("productization_path", {})
        deal_exit_modeling = context.get("deal_exit_modeling", {})
        system_design = context.get("system_design", {})
        design_output = context.get("design_output", {})
        acquirer_matches = context.get("acquirer_matches", [])
        signal_trace = context.get("signal_trace", {})
        phase_log = context.get("phase_log", [])

        title = self._title(domain=domain, market_gap=market_gap, design_output=design_output)
        executive_thesis = self._executive_thesis(
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            opportunity_discovery=opportunity_discovery,
            breakthrough_synthesis=breakthrough_synthesis,
            technical_feasibility=technical_feasibility,
            productization_path=productization_path,
            deal_exit_modeling=deal_exit_modeling,
            scores=scores,
        )

        sections = [
            self._section("executive_thesis", "Executive Thesis", {"summary": executive_thesis, "key_scores": self._key_scores(scores)}),
            self._section("trend_trajectory", "Trend + Trajectory", trend_trajectory, trend_trajectory.get("status") == "success"),
            self._section("market_formation", "Market Formation", market_formation, market_formation.get("status") == "success"),
            self._section("opportunity_discovery", "Opportunity Discovery", opportunity_discovery, opportunity_discovery.get("status") == "success"),
            self._section("breakthrough_synthesis", "Breakthrough Synthesis", breakthrough_synthesis, breakthrough_synthesis.get("status") == "success"),
            self._section("technical_feasibility", "Technical Feasibility", technical_feasibility, technical_feasibility.get("status") == "success"),
            self._section("productization_path", "Productization Path", productization_path, productization_path.get("status") == "success"),
            self._section("moat_defensibility", "Moat / Defensibility", moat, moat.get("status") == "success"),
            self._section("risk_regulation", "Risk / Regulation / Compliance", risk_regulation, risk_regulation.get("status") == "success"),
            self._section("business_model", "Business Model + Value Capture", business_model, business_model.get("status") == "success"),
            self._section("deal_exit_modeling", "Deal / Exit Modeling", deal_exit_modeling, deal_exit_modeling.get("status") == "success"),
            self._section("market_gap", "Detected Market / Sector Gap", market_gap, market_gap.get("status") == "success"),
            self._section("needed_solution", "Needed Solution", {
                "needed_solution": market_gap.get("needed_solution"),
                "solution_class": market_gap.get("solution_class"),
                "buyer_segments": market_gap.get("buyer_segments", []),
                "portfolio_relevance": market_gap.get("portfolio_relevance", {}),
            }, market_gap.get("status") == "success"),
            self._section("breakthrough_analysis", "Breakthrough Analysis", {
                "breakthrough_score": scores.get("breakthrough_score", 0.0),
                "innovation_score": scores.get("innovation_score", 0.0),
                "signal_trace": signal_trace,
                "interpretation": self._breakthrough_interpretation(scores, signal_trace),
            }),
            self._section("design_blueprint", "Breakthrough Design Blueprint", {
                "system_design": system_design,
                "architecture": design_output.get("architecture"),
                "architecture_blueprint": design_output.get("architecture_blueprint", {}),
                "data_flows": design_output.get("data_flows", []),
            }, design_output.get("status") == "success"),
            self._section("technical_specs", "Technical Specifications", design_output.get("technical_specs", {}), design_output.get("status") == "success"),
            self._section("implementation_plan", "Implementation Plan", {"phases": design_output.get("implementation_phases", [])}, design_output.get("status") == "success"),
            self._section("feasibility_and_risk", "Feasibility and Risk", {
                "feasibility_score": scores.get("feasibility_score", 0.0),
                "buildability_score": scores.get("buildability_score", 0.0),
                "viability_score": scores.get("viability_score", 0.0),
                "readiness": design_output.get("readiness", {}) if isinstance(design_output, dict) else {},
                "risk_blocker_level": risk_regulation.get("blocker_assessment", {}).get("blocker_level"),
                "commercial_risk": business_model.get("commercial_risk", {}).get("level"),
                "exit_readiness": deal_exit_modeling.get("exit_readiness", {}).get("state"),
                "strategic_fit": deal_exit_modeling.get("strategic_fit", {}).get("level"),
                "technical_feasibility": technical_feasibility,
                "technical_feasibility_score": technical_feasibility.get("technical_feasibility_score", {}) if isinstance(technical_feasibility, dict) else {},
                "feasibility_classification": technical_feasibility.get("feasibility_classification", {}) if isinstance(technical_feasibility, dict) else {},
                "risk_notes": self._risk_notes(scores, design_output, risk_regulation, business_model, deal_exit_modeling),
            }),
            self._section("strategic_positioning", "Strategic Positioning", {
                "positioning": self._positioning_statement(
                    market_gap,
                    trend_trajectory,
                    market_formation,
                    moat,
                    risk_regulation,
                    business_model,
                    deal_exit_modeling,
                ),
                "portfolio_score": scores.get("portfolio_score", 0.0),
                "matching_score": scores.get("matching_score", 0.0),
                "acquisition_score": scores.get("acquisition_score", 0.0),
            }),
            self._section("acquirer_partner_logic", "Acquirer / Partner Logic", {
                "acquirer_categories": market_gap.get("acquirer_categories", []) if isinstance(market_gap, dict) else [],
                "top_matches": acquirer_matches[:8],
                "logic": "Candidates are ranked using market-gap sector, acquirer categories, buyer segments, solution class, focus overlap, and strategic pressure.",
            }),
            self._section("pipeline_phase_log", "Pipeline Phase Log", {"phases": phase_log}),
        ]

        sections = [section for section in sections if section.get("include", True)]

        return {
            "status": "success",
            "binder_type": "portfolio_intelligence_binder",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "domain": domain,
            "keywords": keywords,
            "executive_thesis": executive_thesis,
            "readiness": self._readiness(scores, design_output, risk_regulation, business_model, deal_exit_modeling, productization_path),
            "sections": sections,
            "artifact_manifest": self._artifact_manifest(sections),
            "export_targets": ["json", "markdown", "pdf", "docx"],
            "next_actions": self._next_actions(scores, market_gap, trend_trajectory, market_formation, moat, risk_regulation, business_model, deal_exit_modeling, design_output),
        }

    def _section(self, section_id: str, title: str, content: Dict[str, Any], include: bool = True) -> Dict[str, Any]:
        return {"id": section_id, "title": title, "include": include, "content": content}

    def _title(self, domain: str, market_gap: Dict[str, Any], design_output: Dict[str, Any]) -> str:
        solution_class = market_gap.get("solution_class") if isinstance(market_gap, dict) else None
        system_type = design_output.get("system_type") if isinstance(design_output, dict) else None

        if solution_class:
            return f"Claire Portfolio Binder — {solution_class.title()}"

        if system_type:
            return f"Claire Portfolio Binder — {system_type.replace('_', ' ').title()}"

        return f"Claire Portfolio Binder — {domain.title()} Opportunity"

    def _executive_thesis(
        self,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        opportunity_discovery: Dict[str, Any],
        breakthrough_synthesis: Dict[str, Any],
        technical_feasibility: Dict[str, Any],
        productization_path: Dict[str, Any],
        deal_exit_modeling: Dict[str, Any],
        scores: Dict[str, Any],
    ) -> str:
        market_gap_text = market_gap.get("market_gap", "A meaningful market gap was identified.")
        needed_solution = market_gap.get("needed_solution", "A needed solution was identified.")
        solution_class = market_gap.get("solution_class", "validated intelligence platform")
        breakthrough = scores.get("breakthrough_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)

        parts = [
            f"Claire identified a {solution_class} opportunity.",
            market_gap_text,
            f"The needed solution is: {needed_solution}",
        ]

        direction = trend_trajectory.get("trend_direction", {}).get("direction")
        window = trend_trajectory.get("strategic_window", {}).get("window")
        opportunity_level = opportunity_discovery.get("opportunity_score", {}).get("level")
        opportunity_type = opportunity_discovery.get("opportunity_type", {}).get("label")
        opportunity_priority = opportunity_discovery.get("priority_assessment", {}).get("priority")
        validation_urgency = opportunity_discovery.get("validation_urgency", {}).get("level")
        if opportunity_discovery.get("status") == "success":
            parts.append(
                f"Opportunity discovery classifies this as a {opportunity_level} {self._pretty(opportunity_type)} "
                f"with {opportunity_priority} priority and {validation_urgency} validation urgency."
            )

        if breakthrough_synthesis.get("status") == "success":
            synthesis_level = breakthrough_synthesis.get("breakthrough_synthesis_score", {}).get("level")
            classification = breakthrough_synthesis.get("breakthrough_classification", {}).get("classification")
            non_obviousness = breakthrough_synthesis.get("non_obviousness", {}).get("level")
            parts.append(
                f"Breakthrough synthesis classifies this as {self._pretty(classification)} "
                f"with {synthesis_level} synthesis strength and {non_obviousness} non-obviousness."
            )

        if technical_feasibility.get("status") == "success":
            feasibility_level = technical_feasibility.get("technical_feasibility_score", {}).get("level")
            feasibility_state = technical_feasibility.get("feasibility_classification", {}).get("state")
            deployment_posture = technical_feasibility.get("feasibility_classification", {}).get("deployment_posture")
            parts.append(
                f"Technical feasibility classifies this as {self._pretty(feasibility_state)} "
                f"with {feasibility_level} feasibility and {self._pretty(deployment_posture)} deployment posture."
            )

        if productization_path.get("status") == "success":
            product_state = productization_path.get("productization_classification", {}).get("state")
            product_level = productization_path.get("productization_score", {}).get("level")
            launch_posture = productization_path.get("productization_classification", {}).get("launch_posture")
            pilot_type = productization_path.get("pilot_strategy", {}).get("pilot_type")
            parts.append(
                f"Productization path classifies this as {self._pretty(product_state)} "
                f"with {product_level} productization strength, {self._pretty(launch_posture)} launch posture, "
                f"and a {pilot_type}."
            )

        if direction and window:
            article = "an" if str(direction)[0].lower() in {"a", "e", "i", "o", "u"} else "a"
            parts.append(f"Trajectory analysis shows {article} {self._pretty(direction)} pattern with a {self._pretty(window)} strategic window.")

        formation = market_formation.get("formation_type", {}).get("type")
        stage = market_formation.get("market_stage", {}).get("stage")
        pull = market_formation.get("buyer_pull", {}).get("strength")
        if formation and stage:
            parts.append(f"Market formation analysis classifies this as {self._pretty(formation)} at the {self._pretty(stage)} stage with {pull} buyer pull.")

        primary_moat = moat.get("moat_type", {}).get("primary_moat")
        moat_strength = moat.get("moat_type", {}).get("strength")
        copy_risk = moat.get("copy_risk", {}).get("level")
        if primary_moat and moat_strength:
            parts.append(f"Moat analysis shows a {moat_strength} defensibility profile led by {self._pretty(primary_moat)}, with {copy_risk} copy risk.")

        risk_level = risk_regulation.get("risk_profile", {}).get("level")
        exposure = risk_regulation.get("regulation_profile", {}).get("exposure")
        blocker = risk_regulation.get("blocker_assessment", {}).get("blocker_level")
        if risk_level and exposure:
            parts.append(f"Risk/regulation analysis shows {risk_level} operational/compliance risk, {exposure} regulatory exposure, and a {blocker} blocker profile.")

        revenue = business_model.get("revenue_model", {}).get("primary_model")
        value_capture = business_model.get("value_capture", {}).get("strength")
        buyer_roi = business_model.get("buyer_roi", {}).get("roi_strength")
        commercial_risk = business_model.get("commercial_risk", {}).get("level")
        if revenue:
            parts.append(f"Business model analysis supports {self._pretty(revenue)} with {value_capture} value capture, {buyer_roi} buyer ROI, and {commercial_risk} commercial risk.")

        exit_state = deal_exit_modeling.get("exit_readiness", {}).get("state")
        strategic_fit = deal_exit_modeling.get("strategic_fit", {}).get("level")
        valuation_signal = deal_exit_modeling.get("valuation_logic", {}).get("valuation_signal", {}).get("strength")
        if exit_state:
            parts.append(
                f"Deal/exit modeling classifies this as {self._pretty(exit_state)} with "
                f"{strategic_fit} strategic fit and a {self._pretty(valuation_signal)} valuation signal."
            )

        parts.append(
            f"The opportunity produced a breakthrough score of {breakthrough:.4f} and portfolio confidence of {portfolio:.4f}, "
            "indicating a candidate suitable for blueprinting, validation, portfolio packaging, and deal-readiness preparation."
        )

        return " ".join(parts)

    def _readiness(
        self,
        scores: Dict[str, Any],
        design_output: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        deal_exit_modeling: Dict[str, Any],
        productization_path: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        breakthrough = scores.get("breakthrough_score", 0.0)
        feasibility = scores.get("feasibility_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)

        design_ready = design_output.get("status") == "success"
        artifact_status = (
            design_output.get("portfolio_artifacts", {}).get("artifact_status")
            if isinstance(design_output, dict)
            else None
        )

        blocker_level = risk_regulation.get("blocker_assessment", {}).get("blocker_level") if isinstance(risk_regulation, dict) else None
        value_capture = business_model.get("value_capture", {}).get("strength") if isinstance(business_model, dict) else None
        commercial_risk = business_model.get("commercial_risk", {}).get("level") if isinstance(business_model, dict) else None
        exit_state = deal_exit_modeling.get("exit_readiness", {}).get("state") if isinstance(deal_exit_modeling, dict) else None
        strategic_fit = deal_exit_modeling.get("strategic_fit", {}).get("level") if isinstance(deal_exit_modeling, dict) else None
        productization_path = productization_path or {}
        productization_state = productization_path.get("productization_classification", {}).get("state") if isinstance(productization_path, dict) else None
        launch_posture = productization_path.get("productization_classification", {}).get("launch_posture") if isinstance(productization_path, dict) else None

        if exit_state == "exit_ready" and blocker_level != "conditional":
            state = "deal_ready_binder"
        elif exit_state:
            state = "deal_candidate_with_conditions"
        elif blocker_level == "conditional":
            state = "binder_candidate_with_conditions"
        elif commercial_risk == "high":
            state = "commercial_validation_needed"
        elif design_ready and breakthrough >= 0.85 and feasibility >= 0.75 and portfolio >= 0.80:
            state = "binder_ready"
        elif design_ready and portfolio >= 0.70:
            state = "binder_candidate"
        else:
            state = "needs_more_validation"

        return {
            "state": state,
            "design_ready": design_ready,
            "artifact_status": artifact_status,
            "risk_blocker_level": blocker_level,
            "value_capture": value_capture,
            "commercial_risk": commercial_risk,
            "exit_state": exit_state,
            "strategic_fit": strategic_fit,
            "productization_state": productization_state,
            "launch_posture": launch_posture,
            "productization_score": scores.get("productization_score", 0.0),
            "breakthrough_score": breakthrough,
            "feasibility_score": feasibility,
            "portfolio_score": portfolio,
        }

    def _key_scores(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "breakthrough": scores.get("breakthrough_score", 0.0),
            "feasibility": scores.get("feasibility_score", 0.0),
            "portfolio": scores.get("portfolio_score", 0.0),
            "productization": scores.get("productization_score", 0.0),
            "confidence": scores.get("_confidence", 0.0),
        }

    def _breakthrough_interpretation(self, scores: Dict[str, Any], signal_trace: Dict[str, Any]) -> str:
        breakthrough = scores.get("breakthrough_score", 0.0)
        level = "high-conviction breakthrough" if breakthrough >= 0.9 else "promising breakthrough candidate" if breakthrough >= 0.75 else "early-stage opportunity"

        return (
            f"This run is classified as a {level}. "
            f"Breakthrough spike contribution was {signal_trace.get('breakthrough_spike', 0.0):.4f}; "
            f"market pressure contribution was {signal_trace.get('market_pressure_score', 0.0):.4f}; "
            f"trajectory inevitability was {signal_trace.get('trajectory_inevitability', 0.0):.4f}; "
            f"category creation was {signal_trace.get('category_creation_score', 0.0):.4f}; "
            f"buyer pull was {signal_trace.get('buyer_pull_score', 0.0):.4f}; "
            f"moat score was {signal_trace.get('moat_score', 0.0):.4f}; "
            f"risk score was {signal_trace.get('risk_score', 0.0):.4f}; "
            f"value capture was {signal_trace.get('value_capture_score', 0.0):.4f}; "
            f"buyer ROI was {signal_trace.get('buyer_roi_score', 0.0):.4f}."
        )

    def _risk_notes(
        self,
        scores: Dict[str, Any],
        design_output: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        deal_exit_modeling: Dict[str, Any],
    ) -> List[str]:
        notes = []
        if scores.get("feasibility_score", 0.0) < 0.7:
            notes.append("Feasibility requires additional validation.")
        if scores.get("buildability_score", 0.0) < 0.7:
            notes.append("Buildability requires implementation de-risking.")

        readiness = design_output.get("readiness", {}) if isinstance(design_output, dict) else {}
        if readiness.get("state") == "ready_for_blueprint":
            notes.append("Technical blueprint readiness is strong.")

        if isinstance(risk_regulation, dict) and risk_regulation.get("status") == "success":
            risk_level = risk_regulation.get("risk_profile", {}).get("level")
            blocker = risk_regulation.get("blocker_assessment", {}).get("blocker_level")
            notes.append(f"Risk/regulation profile is {risk_level}; blocker level is {blocker}.")

        if isinstance(business_model, dict) and business_model.get("status") == "success":
            commercial_risk = business_model.get("commercial_risk", {}).get("level")
            value_capture = business_model.get("value_capture", {}).get("strength")
            notes.append(f"Business model profile shows {value_capture} value capture and {commercial_risk} commercial risk.")

        if isinstance(deal_exit_modeling, dict) and deal_exit_modeling.get("status") == "success":
            exit_state = deal_exit_modeling.get("exit_readiness", {}).get("state")
            strategic_fit = deal_exit_modeling.get("strategic_fit", {}).get("level")
            notes.append(f"Deal/exit model shows {exit_state} with {strategic_fit} strategic fit.")

        if not notes:
            notes.append("No major feasibility blockers surfaced in this deterministic run.")

        return notes

    def _positioning_statement(
        self,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        deal_exit_modeling: Dict[str, Any],
    ) -> str:
        if not isinstance(market_gap, dict) or market_gap.get("status") != "success":
            return "Opportunity requires additional market-gap validation."

        sector = self._pretty(market_gap.get("sector", "target sector"))
        needed_solution = market_gap.get("needed_solution", "needed solution")
        buyer_segments = market_gap.get("buyer_segments", [])
        buyers = ", ".join(buyer_segments[:3]) if buyer_segments else "strategic buyers"

        parts = [
            f"This opportunity is positioned in {sector}.",
            f"It addresses the needed solution: {needed_solution}",
            f"Primary buyer segments include {buyers}.",
        ]

        direction = trend_trajectory.get("trend_direction", {}).get("direction")
        window = trend_trajectory.get("strategic_window", {}).get("window")
        if direction and window:
            parts.append(f"The trend trajectory is {self._pretty(direction)}, with a {self._pretty(window)} strategic window.")

        formation = market_formation.get("formation_type", {}).get("type")
        stage = market_formation.get("market_stage", {}).get("stage")
        if formation and stage:
            parts.append(f"Market formation profile: {self._pretty(formation)} at {self._pretty(stage)} stage.")

        primary_moat = moat.get("moat_type", {}).get("primary_moat")
        moat_strength = moat.get("moat_type", {}).get("strength")
        if primary_moat and moat_strength:
            parts.append(f"Defensibility is {moat_strength}, led by {self._pretty(primary_moat)}.")

        risk = risk_regulation.get("risk_profile", {}).get("level")
        exposure = risk_regulation.get("regulation_profile", {}).get("exposure")
        blocker = risk_regulation.get("blocker_assessment", {}).get("blocker_level")
        if risk:
            parts.append(f"Risk profile is {risk}, regulatory exposure is {exposure}, and blocker level is {blocker}.")

        revenue = business_model.get("revenue_model", {}).get("primary_model")
        value = business_model.get("value_capture", {}).get("strength")
        if revenue:
            parts.append(f"Business model fit is {self._pretty(revenue)} with {value} value capture.")

        exit_state = deal_exit_modeling.get("exit_readiness", {}).get("state")
        strategic_fit = deal_exit_modeling.get("strategic_fit", {}).get("level")
        valuation_signal = deal_exit_modeling.get("valuation_logic", {}).get("valuation_signal", {}).get("strength")
        if exit_state:
            parts.append(
                f"Deal/exit position is {self._pretty(exit_state)} with {strategic_fit} strategic fit "
                f"and {self._pretty(valuation_signal)} valuation signal."
            )

        return " ".join(parts)

    def _artifact_manifest(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {"order": idx, "section_id": section.get("id"), "title": section.get("title"), "status": "ready"}
            for idx, section in enumerate(sections, start=1)
        ]

    def _next_actions(
        self,
        scores: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        deal_exit_modeling: Dict[str, Any],
        design_output: Dict[str, Any],
    ) -> List[str]:
        actions = [
            "Review market gap and needed solution thesis.",
            "Validate buyer segments and strategic pressure assumptions.",
            "Review trend trajectory, timing pressure, and strategic window.",
            "Review market formation type, buyer pull, and adoption path.",
            "Review moat, copy risk, vulnerabilities, and strengthening actions.",
            "Review risk/regulation profile, deployment constraints, blockers, and mitigation actions.",
            "Review business model, pricing, buyer ROI, value capture, and commercial risk.",
            "Review deal/exit readiness, strategic fit, valuation logic, and diligence requirements.",
            "Review technical blueprint and implementation phases.",
        ]

        if scores.get("portfolio_score", 0.0) >= 0.80:
            actions.append("Prepare portfolio binder export.")

        if design_output.get("readiness", {}).get("state") == "ready_for_blueprint":
            actions.append("Begin prototype and feasibility validation planning.")

        if isinstance(market_gap, dict) and market_gap.get("acquirer_categories"):
            actions.append("Run deeper acquirer/partner discovery using market-gap categories.")

        if isinstance(trend_trajectory, dict) and trend_trajectory.get("strategic_window", {}).get("window") in {"now", "near_term"}:
            actions.append("Prioritize validation while the strategic timing window is active.")

        if isinstance(market_formation, dict) and market_formation.get("buyer_pull", {}).get("strength") == "strong":
            actions.append("Design anchor-customer validation around the strongest buyer-pull segment.")

        if isinstance(moat, dict) and moat.get("status") == "success":
            actions.append("Prioritize moat strengthening through proprietary data loops and workflow integration.")

        if isinstance(risk_regulation, dict) and risk_regulation.get("status") == "success":
            blocker = risk_regulation.get("blocker_assessment", {}).get("blocker_level")
            if blocker == "conditional":
                actions.append("Resolve risk/regulation blockers before go-to-market packaging.")
            else:
                actions.append("Proceed with advisory-mode validation, auditability, and sector-specific compliance review.")

        if isinstance(business_model, dict) and business_model.get("status") == "success":
            actions.append("Package a paid advisory pilot with ROI metrics and enterprise conversion path.")
            if business_model.get("commercial_risk", {}).get("level") != "low":
                actions.append("Map procurement friction and commercial-risk burn-down before scaling.")

        if isinstance(deal_exit_modeling, dict) and deal_exit_modeling.get("status") == "success":
            actions.append("Build acquirer-specific strategic rationale and diligence evidence pack.")
            if deal_exit_modeling.get("exit_readiness", {}).get("state") != "exit_ready":
                actions.append("Close deal-readiness proof gaps before outreach.")

        return actions

    def _pretty(self, value: str) -> str:
        return str(value or "").replace("_", " ").replace("-", " ")
