"""
Portfolio Binder Builder — assembles Claire outputs into a structured
portfolio / binder package.

Purpose:
- Convert pipeline intelligence into a reusable strategic artifact
- Package breakthrough, trend, market formation, moat, market gap, design,
  feasibility, and acquirer logic
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


class PortfolioBinderBuilder:
    """
    Builds a structured portfolio binder from a completed Claire pipeline run.
    """

    def build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not context:
            return {
                "status": "binder_failed",
                "error": "No binder context provided.",
            }

        scores = context.get("scores", {})
        domain = context.get("domain", "general")
        keywords = context.get("keywords", [])
        market_gap = context.get("market_gap", {})
        trend_trajectory = context.get("trend_trajectory", {})
        market_formation = context.get("market_formation", {})
        moat = context.get("moat", {})
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
            scores=scores,
        )

        sections = [
            self._section_executive_thesis(executive_thesis, scores),
            self._section_trend_trajectory(trend_trajectory),
            self._section_market_formation(market_formation),
            self._section_moat_defensibility(moat),
            self._section_market_gap(market_gap),
            self._section_needed_solution(market_gap),
            self._section_breakthrough(scores, signal_trace),
            self._section_design_blueprint(system_design, design_output),
            self._section_technical_specs(design_output),
            self._section_implementation_plan(design_output),
            self._section_feasibility(scores, design_output),
            self._section_strategic_positioning(market_gap, trend_trajectory, market_formation, moat, scores),
            self._section_acquirer_logic(acquirer_matches, market_gap),
            self._section_phase_log(phase_log),
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
            "readiness": self._readiness(scores=scores, design_output=design_output),
            "sections": sections,
            "artifact_manifest": self._artifact_manifest(sections),
            "export_targets": ["json", "markdown", "pdf", "docx"],
            "next_actions": self._next_actions(scores, market_gap, trend_trajectory, market_formation, moat, design_output),
        }

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
        scores: Dict[str, Any],
    ) -> str:
        market_gap_text = market_gap.get("market_gap", "A meaningful market gap was identified.")
        needed_solution = market_gap.get("needed_solution", "A needed solution was identified.")
        solution_class = market_gap.get("solution_class", "validated intelligence platform")

        breakthrough = scores.get("breakthrough_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)

        trend_direction = trend_trajectory.get("trend_direction", {}).get("direction")
        strategic_window = trend_trajectory.get("strategic_window", {}).get("window")

        trend_sentence = ""
        if trend_direction and strategic_window:
            article = "an" if str(trend_direction)[0].lower() in {"a", "e", "i", "o", "u"} else "a"
            trend_sentence = (
                f"Trajectory analysis shows {article} {trend_direction} pattern with a "
                f"{self._pretty_token(strategic_window)} strategic window. "
            )

        formation_sentence = ""
        if isinstance(market_formation, dict) and market_formation.get("status") == "success":
            formation_type = market_formation.get("formation_type", {}).get("type")
            market_stage = market_formation.get("market_stage", {}).get("stage")
            buyer_pull = market_formation.get("buyer_pull", {}).get("strength")
            if formation_type and market_stage:
                formation_sentence = (
                    f"Market formation analysis classifies this as {self._pretty_token(formation_type)} "
                    f"at the {self._pretty_token(market_stage)} stage with {buyer_pull} buyer pull. "
                )

        moat_sentence = ""
        if isinstance(moat, dict) and moat.get("status") == "success":
            moat_type = moat.get("moat_type", {})
            primary = moat_type.get("primary_moat")
            strength = moat_type.get("strength")
            copy_risk = moat.get("copy_risk", {}).get("level")
            if primary and strength:
                moat_sentence = (
                    f"Moat analysis shows a {strength} defensibility profile led by "
                    f"{self._pretty_token(primary)}, with {copy_risk} copy risk. "
                )

        return (
            f"Claire identified a {solution_class} opportunity. "
            f"{market_gap_text} "
            f"The needed solution is: {needed_solution} "
            f"{trend_sentence}"
            f"{formation_sentence}"
            f"{moat_sentence}"
            f"The opportunity produced a breakthrough score of {breakthrough:.4f} "
            f"and portfolio confidence of {portfolio:.4f}, indicating a candidate suitable "
            f"for blueprinting, validation, and portfolio packaging."
        )

    def _readiness(self, scores: Dict[str, Any], design_output: Dict[str, Any]) -> Dict[str, Any]:
        breakthrough = scores.get("breakthrough_score", 0.0)
        feasibility = scores.get("feasibility_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)

        design_ready = design_output.get("status") == "success"
        artifact_status = (
            design_output.get("portfolio_artifacts", {}).get("artifact_status")
            if isinstance(design_output, dict)
            else None
        )

        if design_ready and breakthrough >= 0.85 and feasibility >= 0.75 and portfolio >= 0.80:
            state = "binder_ready"
        elif design_ready and portfolio >= 0.70:
            state = "binder_candidate"
        else:
            state = "needs_more_validation"

        return {
            "state": state,
            "design_ready": design_ready,
            "artifact_status": artifact_status,
            "breakthrough_score": breakthrough,
            "feasibility_score": feasibility,
            "portfolio_score": portfolio,
        }

    def _section_executive_thesis(self, executive_thesis: str, scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": "executive_thesis",
            "title": "Executive Thesis",
            "include": True,
            "content": {
                "summary": executive_thesis,
                "key_scores": {
                    "breakthrough": scores.get("breakthrough_score", 0.0),
                    "feasibility": scores.get("feasibility_score", 0.0),
                    "portfolio": scores.get("portfolio_score", 0.0),
                    "confidence": scores.get("_confidence", 0.0),
                },
            },
        }

    def _section_trend_trajectory(self, trend_trajectory: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(trend_trajectory, dict) or trend_trajectory.get("status") != "success":
            return {"id": "trend_trajectory", "title": "Trend + Trajectory", "include": False, "content": {}}

        return {
            "id": "trend_trajectory",
            "title": "Trend + Trajectory",
            "include": True,
            "content": {
                "trend_direction": trend_trajectory.get("trend_direction"),
                "historical_trajectory": trend_trajectory.get("historical_trajectory"),
                "adoption_curve_position": trend_trajectory.get("adoption_curve_position"),
                "inflection_signals": trend_trajectory.get("inflection_signals"),
                "timing_pressure": trend_trajectory.get("timing_pressure"),
                "market_momentum": trend_trajectory.get("market_momentum"),
                "inevitability_score": trend_trajectory.get("inevitability_score"),
                "strategic_window": trend_trajectory.get("strategic_window"),
                "trajectory_risk": trend_trajectory.get("trajectory_risk"),
                "confidence": trend_trajectory.get("confidence"),
            },
        }

    def _section_market_formation(self, market_formation: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(market_formation, dict) or market_formation.get("status") != "success":
            return {"id": "market_formation", "title": "Market Formation", "include": False, "content": {}}

        return {
            "id": "market_formation",
            "title": "Market Formation",
            "include": True,
            "content": {
                "formation_type": market_formation.get("formation_type"),
                "market_stage": market_formation.get("market_stage"),
                "category_creation_score": market_formation.get("category_creation_score"),
                "buyer_pull": market_formation.get("buyer_pull"),
                "adoption_path": market_formation.get("adoption_path"),
                "ecosystem_requirements": market_formation.get("ecosystem_requirements"),
                "market_entry_strategy": market_formation.get("market_entry_strategy"),
                "formation_risk": market_formation.get("formation_risk"),
                "formation_thesis": market_formation.get("formation_thesis"),
                "confidence": market_formation.get("confidence"),
            },
        }

    def _section_moat_defensibility(self, moat: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(moat, dict) or moat.get("status") != "success":
            return {"id": "moat_defensibility", "title": "Moat / Defensibility", "include": False, "content": {}}

        return {
            "id": "moat_defensibility",
            "title": "Moat / Defensibility",
            "include": True,
            "content": {
                "moat_type": moat.get("moat_type"),
                "defensibility_dimensions": moat.get("defensibility_dimensions"),
                "copy_risk": moat.get("copy_risk"),
                "compounding_assets": moat.get("compounding_assets"),
                "vulnerabilities": moat.get("vulnerabilities"),
                "moat_strengthening_actions": moat.get("moat_strengthening_actions"),
                "strategic_defensibility_thesis": moat.get("strategic_defensibility_thesis"),
                "confidence": moat.get("confidence"),
            },
        }

    def _section_market_gap(self, market_gap: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(market_gap, dict) or market_gap.get("status") != "success":
            return {"id": "market_gap", "title": "Detected Market / Sector Gap", "include": False, "content": {}}

        return {
            "id": "market_gap",
            "title": "Detected Market / Sector Gap",
            "include": True,
            "content": {
                "sector": market_gap.get("sector"),
                "industry_context": market_gap.get("industry_context"),
                "gap_type": market_gap.get("gap_type"),
                "market_gap": market_gap.get("market_gap"),
                "strategic_pressure": market_gap.get("strategic_pressure"),
                "confidence": market_gap.get("confidence"),
            },
        }

    def _section_needed_solution(self, market_gap: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(market_gap, dict) or market_gap.get("status") != "success":
            return {"id": "needed_solution", "title": "Needed Solution", "include": False, "content": {}}

        return {
            "id": "needed_solution",
            "title": "Needed Solution",
            "include": True,
            "content": {
                "needed_solution": market_gap.get("needed_solution"),
                "solution_class": market_gap.get("solution_class"),
                "buyer_segments": market_gap.get("buyer_segments", []),
                "portfolio_relevance": market_gap.get("portfolio_relevance", {}),
            },
        }

    def _section_breakthrough(self, scores: Dict[str, Any], signal_trace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": "breakthrough_analysis",
            "title": "Breakthrough Analysis",
            "include": True,
            "content": {
                "breakthrough_score": scores.get("breakthrough_score", 0.0),
                "innovation_score": scores.get("innovation_score", 0.0),
                "signal_trace": signal_trace,
                "interpretation": self._breakthrough_interpretation(scores, signal_trace),
            },
        }

    def _section_design_blueprint(self, system_design: Dict[str, Any], design_output: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(design_output, dict) or design_output.get("status") != "success":
            return {"id": "design_blueprint", "title": "Breakthrough Design Blueprint", "include": False, "content": {}}

        return {
            "id": "design_blueprint",
            "title": "Breakthrough Design Blueprint",
            "include": True,
            "content": {
                "system_design": system_design,
                "architecture": design_output.get("architecture"),
                "architecture_blueprint": design_output.get("architecture_blueprint", {}),
                "data_flows": design_output.get("data_flows", []),
            },
        }

    def _section_technical_specs(self, design_output: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(design_output, dict) or design_output.get("status") != "success":
            return {"id": "technical_specs", "title": "Technical Specifications", "include": False, "content": {}}

        return {"id": "technical_specs", "title": "Technical Specifications", "include": True, "content": design_output.get("technical_specs", {})}

    def _section_implementation_plan(self, design_output: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(design_output, dict) or design_output.get("status") != "success":
            return {"id": "implementation_plan", "title": "Implementation Plan", "include": False, "content": {}}

        return {"id": "implementation_plan", "title": "Implementation Plan", "include": True, "content": {"phases": design_output.get("implementation_phases", [])}}

    def _section_feasibility(self, scores: Dict[str, Any], design_output: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": "feasibility_and_risk",
            "title": "Feasibility and Risk",
            "include": True,
            "content": {
                "feasibility_score": scores.get("feasibility_score", 0.0),
                "buildability_score": scores.get("buildability_score", 0.0),
                "viability_score": scores.get("viability_score", 0.0),
                "readiness": design_output.get("readiness", {}) if isinstance(design_output, dict) else {},
                "risk_notes": self._risk_notes(scores=scores, design_output=design_output),
            },
        }

    def _section_strategic_positioning(
        self,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "id": "strategic_positioning",
            "title": "Strategic Positioning",
            "include": True,
            "content": {
                "positioning": self._positioning_statement(market_gap, trend_trajectory, market_formation, moat),
                "portfolio_score": scores.get("portfolio_score", 0.0),
                "matching_score": scores.get("matching_score", 0.0),
                "acquisition_score": scores.get("acquisition_score", 0.0),
            },
        }

    def _section_acquirer_logic(self, acquirer_matches: List[Dict[str, Any]], market_gap: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": "acquirer_partner_logic",
            "title": "Acquirer / Partner Logic",
            "include": True,
            "content": {
                "acquirer_categories": market_gap.get("acquirer_categories", []) if isinstance(market_gap, dict) else [],
                "top_matches": acquirer_matches[:8],
                "logic": "Candidates are ranked using market-gap sector, acquirer categories, buyer segments, solution class, focus overlap, and strategic pressure.",
            },
        }

    def _section_phase_log(self, phase_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "id": "pipeline_phase_log",
            "title": "Pipeline Phase Log",
            "include": True,
            "content": {"phases": phase_log},
        }

    def _breakthrough_interpretation(self, scores: Dict[str, Any], signal_trace: Dict[str, Any]) -> str:
        breakthrough = scores.get("breakthrough_score", 0.0)
        spike = signal_trace.get("breakthrough_spike", 0.0)
        pressure = signal_trace.get("market_pressure_score", 0.0)
        inevitability = signal_trace.get("trajectory_inevitability", 0.0)
        category = signal_trace.get("category_creation_score", 0.0)
        buyer_pull = signal_trace.get("buyer_pull_score", 0.0)
        moat_score = signal_trace.get("moat_score", 0.0)

        if breakthrough >= 0.9:
            level = "high-conviction breakthrough"
        elif breakthrough >= 0.75:
            level = "promising breakthrough candidate"
        else:
            level = "early-stage opportunity"

        return (
            f"This run is classified as a {level}. "
            f"Breakthrough spike contribution was {spike:.4f}; "
            f"market pressure contribution was {pressure:.4f}; "
            f"trajectory inevitability was {inevitability:.4f}; "
            f"category creation was {category:.4f}; "
            f"buyer pull was {buyer_pull:.4f}; "
            f"moat score was {moat_score:.4f}."
        )

    def _risk_notes(self, scores: Dict[str, Any], design_output: Dict[str, Any]) -> List[str]:
        notes = []
        feasibility = scores.get("feasibility_score", 0.0)
        buildability = scores.get("buildability_score", 0.0)

        if feasibility < 0.7:
            notes.append("Feasibility requires additional validation.")

        if buildability < 0.7:
            notes.append("Buildability requires implementation de-risking.")

        readiness = design_output.get("readiness", {}) if isinstance(design_output, dict) else {}
        if readiness.get("state") == "ready_for_blueprint":
            notes.append("Technical blueprint readiness is strong.")

        if not notes:
            notes.append("No major feasibility blockers surfaced in this deterministic run.")

        return notes

    def _positioning_statement(
        self,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
    ) -> str:
        if not isinstance(market_gap, dict) or market_gap.get("status") != "success":
            return "Opportunity requires additional market-gap validation."

        sector = self._pretty_token(market_gap.get("sector", "target sector"))
        needed_solution = market_gap.get("needed_solution", "needed solution")
        buyer_segments = market_gap.get("buyer_segments", [])
        buyers = ", ".join(buyer_segments[:3]) if buyer_segments else "strategic buyers"

        trend_sentence = ""
        if isinstance(trend_trajectory, dict) and trend_trajectory.get("status") == "success":
            direction = trend_trajectory.get("trend_direction", {}).get("direction")
            window = trend_trajectory.get("strategic_window", {}).get("window")
            if direction and window:
                trend_sentence = f" The trend trajectory is {direction}, with a {self._pretty_token(window)} strategic window."

        formation_sentence = ""
        if isinstance(market_formation, dict) and market_formation.get("status") == "success":
            formation_type = market_formation.get("formation_type", {}).get("type")
            market_stage = market_formation.get("market_stage", {}).get("stage")
            if formation_type and market_stage:
                formation_sentence = f" Market formation profile: {self._pretty_token(formation_type)} at {self._pretty_token(market_stage)} stage."

        moat_sentence = ""
        if isinstance(moat, dict) and moat.get("status") == "success":
            primary = moat.get("moat_type", {}).get("primary_moat")
            strength = moat.get("moat_type", {}).get("strength")
            if primary and strength:
                moat_sentence = f" Defensibility is {strength}, led by {self._pretty_token(primary)}."

        return (
            f"This opportunity is positioned in {sector}. "
            f"It addresses the needed solution: {needed_solution} "
            f"Primary buyer segments include {buyers}."
            f"{trend_sentence}"
            f"{formation_sentence}"
            f"{moat_sentence}"
        )

    def _artifact_manifest(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "order": idx,
                "section_id": section.get("id"),
                "title": section.get("title"),
                "status": "ready",
            }
            for idx, section in enumerate(sections, start=1)
        ]

    def _next_actions(
        self,
        scores: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        design_output: Dict[str, Any],
    ) -> List[str]:
        actions = [
            "Review market gap and needed solution thesis.",
            "Validate buyer segments and strategic pressure assumptions.",
            "Review trend trajectory, timing pressure, and strategic window.",
            "Review market formation type, buyer pull, and adoption path.",
            "Review moat, copy risk, vulnerabilities, and strengthening actions.",
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

        return actions

    def _pretty_token(self, value: str) -> str:
        return str(value or "").replace("_", " ").replace("-", " ")
