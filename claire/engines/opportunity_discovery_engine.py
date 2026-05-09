"""
Opportunity Discovery Engine — dedicated Stage 7 engine for Claire.

v5.21:
- Converts Stage 7 from contextual/partial into a real engine.
- Synthesizes market gap, needed solution, trend trajectory, market formation,
  moat, risk/regulation, and business model outputs into a structured
  opportunity thesis.
- Produces opportunity score, opportunity type, discovery vectors, wedge logic,
  validation roadmap, evidence gaps, and next actions.
- Uses sector-aware language for climate insurance, defense autonomy,
  healthcare operations, financial market intelligence, industrial supply chain,
  energy infrastructure, and general intelligence opportunities.
"""

from typing import Any, Dict, List, Optional


class OpportunityDiscoveryEngine:
    """
    Deterministic opportunity discovery analyzer.

    This engine does not replace market-gap detection. It sits after the gap /
    needed-solution layer and asks:

    - Is this a true opportunity or just a known need?
    - Where is the wedge?
    - Why now?
    - Which buyer pain should be validated first?
    - What must be proven before breakthrough synthesis, design, binder, and deal
      packaging should be trusted?
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        market_formation: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        business_model: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = text or ""
        keywords = keywords or []
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        business_model = business_model or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            domain=domain,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            connector_sources=connector_sources,
        )

        opportunity_score = self._opportunity_score(signals)
        opportunity_type = self._opportunity_type(signals)
        discovery_vector = self._discovery_vector(signals, opportunity_type)
        opportunity_map = self._opportunity_map(signals, market_gap, trend_trajectory, market_formation)
        priority = self._priority_assessment(signals, opportunity_score)
        validation_urgency = self._validation_urgency(signals, priority)
        whitespace = self._whitespace_map(signals, market_gap)
        hypotheses = self._opportunity_hypotheses(signals, market_gap)
        validation_roadmap = self._validation_roadmap(signals, priority)
        evidence_gaps = self._evidence_gaps(signals)
        next_actions = self._recommended_next_actions(signals, priority, validation_urgency)

        return {
            "status": "success",
            "domain": signals["domain"],
            "sector": signals["sector"],
            "opportunity_score": opportunity_score,
            "opportunity_type": opportunity_type,
            "discovery_vector": discovery_vector,
            "opportunity_map": opportunity_map,
            "priority_assessment": priority,
            "validation_urgency": validation_urgency,
            "whitespace_map": whitespace,
            "opportunity_hypotheses": hypotheses,
            "validation_roadmap": validation_roadmap,
            "evidence_gaps": evidence_gaps,
            "recommended_next_actions": next_actions,
            "opportunity_thesis": self._opportunity_thesis(signals, opportunity_score, opportunity_type, priority),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, opportunity_score),
        }

    # =========================
    # SIGNALS
    # =========================
    def _signals(
        self,
        text: str,
        keywords: List[str],
        domain: str,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
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

        pain_terms = self._count_terms(combined, [
            "gap",
            "shortage",
            "loss",
            "losses",
            "risk",
            "bottleneck",
            "withdrawal",
            "repricing",
            "capacity",
            "exposure",
            "stress",
            "disruption",
            "urgent",
            "accelerating",
        ])

        wedge_terms = self._count_terms(combined, [
            "platform",
            "workflow",
            "module",
            "pilot",
            "wedge",
            "benchmark",
            "intelligence",
            "decision",
            "recommendation",
            "detector",
            "engine",
        ])

        proof_terms = self._count_terms(combined, [
            "backtest",
            "validation",
            "validated",
            "historical",
            "pilot",
            "accuracy",
            "evidence",
            "model",
            "scenario",
            "audit",
        ])

        return {
            "domain": domain,
            "sector": sector,
            "input_pain_term_count": pain_terms,
            "input_wedge_term_count": wedge_terms,
            "input_proof_term_count": proof_terms,
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": self._nested(market_gap, "strategic_pressure", "score"),
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "acquirer_category_count": len(market_gap.get("acquirer_categories", [])) if isinstance(market_gap, dict) else 0,
            "trend_direction": self._nested_text(trend_trajectory, "trend_direction", "direction"),
            "trend_direction_score": self._nested(trend_trajectory, "trend_direction", "score"),
            "timing_pressure_score": self._nested(trend_trajectory, "timing_pressure", "score"),
            "market_momentum_score": self._nested(trend_trajectory, "market_momentum", "score"),
            "inevitability_score": self._nested(trend_trajectory, "inevitability_score", "score"),
            "strategic_window": self._nested_text(trend_trajectory, "strategic_window", "window"),
            "formation_type": self._nested_text(market_formation, "formation_type", "type"),
            "formation_type_score": self._nested(market_formation, "formation_type", "score"),
            "market_stage": self._nested_text(market_formation, "market_stage", "stage"),
            "category_creation_score": self._nested(market_formation, "category_creation_score", "score"),
            "buyer_pull_score": self._nested(market_formation, "buyer_pull", "score"),
            "buyer_pull_strength": self._nested_text(market_formation, "buyer_pull", "strength"),
            "ecosystem_requirement_count": len(market_formation.get("ecosystem_requirements", [])) if isinstance(market_formation, dict) else 0,
            "moat_score": self._nested(moat, "moat_type", "moat_score"),
            "moat_strength": self._nested_text(moat, "moat_type", "strength"),
            "primary_moat": self._nested_text(moat, "moat_type", "primary_moat"),
            "copy_risk_score": self._nested(moat, "copy_risk", "score"),
            "copy_risk_level": self._nested_text(moat, "copy_risk", "level"),
            "risk_score": self._nested(risk_regulation, "risk_profile", "score"),
            "risk_level": self._nested_text(risk_regulation, "risk_profile", "level"),
            "regulatory_exposure_score": self._nested(risk_regulation, "regulation_profile", "score"),
            "regulatory_exposure": self._nested_text(risk_regulation, "regulation_profile", "exposure"),
            "blocker_level": self._nested_text(risk_regulation, "blocker_assessment", "blocker_level") or "unknown",
            "revenue_model": self._nested_text(business_model, "revenue_model", "primary_model"),
            "value_capture_score": self._nested(business_model, "value_capture", "score"),
            "value_capture_strength": self._nested_text(business_model, "value_capture", "strength"),
            "buyer_roi_score": self._nested(business_model, "buyer_roi", "score"),
            "buyer_roi_strength": self._nested_text(business_model, "buyer_roi", "roi_strength"),
            "commercial_risk_score": self._nested(business_model, "commercial_risk", "score"),
            "commercial_risk_level": self._nested_text(business_model, "commercial_risk", "level"),
        }

    # =========================
    # CORE OUTPUTS
    # =========================
    def _opportunity_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.16
            + signals["market_gap_confidence"] * 0.145
            + signals["strategic_pressure_score"] * 0.105
            + signals["buyer_pull_score"] * 0.115
            + signals["category_creation_score"] * 0.090
            + signals["timing_pressure_score"] * 0.065
            + signals["inevitability_score"] * 0.060
            + signals["market_momentum_score"] * 0.055
            + signals["moat_score"] * 0.080
            + (1.0 - signals["copy_risk_score"]) * 0.035
            + signals["value_capture_score"] * 0.055
            + signals["buyer_roi_score"] * 0.035
            + min(0.055, signals["buyer_segment_count"] * 0.007)
            + min(0.035, signals["input_pain_term_count"] * 0.006)
            + min(0.030, signals["input_wedge_term_count"] * 0.005)
            - signals["risk_score"] * 0.025
            - signals["commercial_risk_score"] * 0.020
            - (0.045 if signals["blocker_level"] == "conditional" else 0.0)
        )

        level = "exceptional" if score >= 0.84 else "strong" if score >= 0.72 else "moderate" if score >= 0.56 else "early"

        return {
            "level": level,
            "score": round(score, 4),
            "drivers": self._score_drivers(signals),
        }

    def _opportunity_type(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        sector = signals["sector"]

        if signals["formation_type"] == "platform_layer" and signals["category_creation_score"] >= 0.78:
            typ = "platform_wedge"
        elif signals["primary_moat"] == "data_advantage" and signals["moat_score"] >= 0.70:
            typ = "data_moat_opportunity"
        elif signals["buyer_pull_score"] >= 0.80 and signals["strategic_pressure_score"] >= 0.70:
            typ = "urgent_buyer_pain_opportunity"
        elif signals["timing_pressure_score"] >= 0.72:
            typ = "timing_window_opportunity"
        else:
            typ = "validated_gap_opportunity"

        sector_label = self._sector_label(sector)

        rationale = [
            f"sector detected as {sector_label}",
            f"formation type is {signals['formation_type'] or 'unknown'}",
            f"buyer pull score is {signals['buyer_pull_score']:.4f}",
            f"strategic pressure score is {signals['strategic_pressure_score']:.4f}",
            f"moat score is {signals['moat_score']:.4f}",
        ]

        return {
            "type": typ,
            "sector": sector,
            "label": self._pretty(typ),
            "rationale": rationale,
        }

    def _discovery_vector(self, signals: Dict[str, Any], opportunity_type: Dict[str, Any]) -> Dict[str, Any]:
        sector_profile = self._sector_profile(signals["sector"])

        primary = sector_profile["primary_vector"]

        secondary = [
            "buyer-pain validation",
            "workflow wedge validation",
            "proprietary data-loop validation",
        ]

        if signals["timing_pressure_score"] >= 0.70:
            secondary.append("timing-window capture")

        if signals["category_creation_score"] >= 0.78:
            secondary.append("category creation")

        if signals["blocker_level"] == "conditional":
            secondary.append("risk blocker burn-down")

        return {
            "primary_vector": primary,
            "secondary_vectors": list(dict.fromkeys(secondary)),
            "opportunity_type": opportunity_type.get("type"),
            "best_entry_wedge": sector_profile["entry_wedge"],
            "expansion_path": sector_profile["expansion_path"],
        }

    def _opportunity_map(
        self,
        signals: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector_profile = self._sector_profile(signals["sector"])

        return {
            "target_gap": market_gap.get("gap_type") or sector_profile["target_gap"],
            "unmet_need": market_gap.get("needed_solution") or sector_profile["unmet_need"],
            "solution_class": market_gap.get("solution_class") or sector_profile["solution_class"],
            "first_buyer_segment": self._first_item(market_gap.get("buyer_segments", []), sector_profile["first_buyer_segment"]),
            "buyer_pain": sector_profile["buyer_pain"],
            "why_now": self._why_now(signals, trend_trajectory),
            "entry_wedge": sector_profile["entry_wedge"],
            "proof_to_unlock": sector_profile["proof_to_unlock"],
            "scale_path": market_formation.get("adoption_path", {}).get("expansion_path") or sector_profile["expansion_path"],
        }

    def _priority_assessment(self, signals: Dict[str, Any], opportunity_score: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            opportunity_score["score"] * 0.52
            + signals["timing_pressure_score"] * 0.14
            + signals["buyer_pull_score"] * 0.12
            + signals["category_creation_score"] * 0.08
            + signals["market_gap_confidence"] * 0.08
            - signals["risk_score"] * 0.025
            - (0.04 if signals["blocker_level"] == "conditional" else 0.0)
        )

        priority = "immediate" if score >= 0.82 else "high" if score >= 0.70 else "medium" if score >= 0.55 else "watch"

        return {
            "priority": priority,
            "score": round(score, 4),
            "drivers": self._priority_drivers(signals),
        }

    def _validation_urgency(self, signals: Dict[str, Any], priority: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.18
            + signals["timing_pressure_score"] * 0.22
            + signals["strategic_pressure_score"] * 0.16
            + signals["buyer_pull_score"] * 0.13
            + signals["market_momentum_score"] * 0.08
            + (0.08 if priority["priority"] in {"immediate", "high"} else 0.0)
            + (0.04 if signals["blocker_level"] == "conditional" else 0.0)
        )

        level = "urgent" if score >= 0.78 else "high" if score >= 0.65 else "moderate" if score >= 0.48 else "low"

        return {
            "level": level,
            "score": round(score, 4),
            "recommended_validation_window": "now_to_30_days" if level == "urgent" else "30_to_60_days" if level == "high" else "60_to_90_days",
            "why": self._validation_urgency_why(signals, level),
        }

    def _whitespace_map(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> Dict[str, Any]:
        sector_profile = self._sector_profile(signals["sector"])

        return {
            "white_space_area": sector_profile["white_space_area"],
            "underserved_buyers": market_gap.get("buyer_segments", [])[:4] if isinstance(market_gap, dict) else [],
            "incumbent_blind_spot": sector_profile["incumbent_blind_spot"],
            "hidden_gap": sector_profile["hidden_gap"],
            "category_language": sector_profile["category_language"],
        }

    def _opportunity_hypotheses(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        sector_profile = self._sector_profile(signals["sector"])
        hypotheses = []

        for idx, hypothesis in enumerate(sector_profile["hypotheses"], start=1):
            hypotheses.append({
                "id": f"H{idx}",
                "hypothesis": hypothesis["hypothesis"],
                "validation_method": hypothesis["validation_method"],
                "success_signal": hypothesis["success_signal"],
                "priority": hypothesis.get("priority", "high"),
            })

        if signals["buyer_pull_score"] >= 0.80:
            hypotheses.append({
                "id": f"H{len(hypotheses) + 1}",
                "hypothesis": "High buyer pull indicates a near-term design-partner path may exist.",
                "validation_method": "Interview target buyers and test pilot willingness around the entry wedge.",
                "success_signal": "Multiple buyers validate budget owner, urgency, and pilot criteria.",
                "priority": "high",
            })

        if signals["moat_score"] >= 0.75:
            hypotheses.append({
                "id": f"H{len(hypotheses) + 1}",
                "hypothesis": "The opportunity can become defensible if proprietary data loops are established early.",
                "validation_method": "Define data rights, feedback-loop capture, and benchmark products during pilot design.",
                "success_signal": "Pilot produces reusable data assets and workflow-specific feedback loops.",
                "priority": "high",
            })

        return hypotheses

    def _validation_roadmap(self, signals: Dict[str, Any], priority: Dict[str, Any]) -> List[Dict[str, Any]]:
        sector_profile = self._sector_profile(signals["sector"])

        roadmap = [
            {
                "step": 1,
                "name": "Buyer pain confirmation",
                "objective": sector_profile["buyer_validation_objective"],
                "evidence_required": sector_profile["buyer_validation_evidence"],
                "priority": "critical" if priority["priority"] in {"immediate", "high"} else "high",
            },
            {
                "step": 2,
                "name": "Historical evidence test",
                "objective": sector_profile["historical_validation_objective"],
                "evidence_required": sector_profile["historical_validation_evidence"],
                "priority": "high",
            },
            {
                "step": 3,
                "name": "Workflow wedge test",
                "objective": sector_profile["workflow_validation_objective"],
                "evidence_required": sector_profile["workflow_validation_evidence"],
                "priority": "high",
            },
            {
                "step": 4,
                "name": "Economic value test",
                "objective": sector_profile["economic_validation_objective"],
                "evidence_required": sector_profile["economic_validation_evidence"],
                "priority": "high",
            },
            {
                "step": 5,
                "name": "Defensibility test",
                "objective": sector_profile["defensibility_validation_objective"],
                "evidence_required": sector_profile["defensibility_validation_evidence"],
                "priority": "medium",
            },
        ]

        if signals["blocker_level"] == "conditional":
            roadmap.insert(3, {
                "step": 4,
                "name": "Blocker burn-down",
                "objective": "Resolve deployment, compliance, governance, or human-review blockers before scaling the opportunity.",
                "evidence_required": ["blocker mitigation plan", "review controls", "approval policy", "audit evidence"],
                "priority": "critical",
            })
            for idx, item in enumerate(roadmap, start=1):
                item["step"] = idx

        return roadmap

    def _evidence_gaps(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        sector_profile = self._sector_profile(signals["sector"])
        gaps = []

        if signals["buyer_roi_score"] < 0.72:
            gaps.append({
                "gap": "buyer ROI proof",
                "why_it_matters": "The opportunity needs quantified economic proof before deal or enterprise packaging should be treated as mature.",
                "suggested_evidence": sector_profile["roi_evidence"],
                "priority": "high",
            })

        if signals["moat_score"] < 0.78:
            gaps.append({
                "gap": "defensibility proof",
                "why_it_matters": "The opportunity needs stronger proof that incumbents cannot easily copy visible features.",
                "suggested_evidence": sector_profile["moat_evidence"],
                "priority": "medium",
            })

        if signals["category_creation_score"] < 0.75:
            gaps.append({
                "gap": "category narrative proof",
                "why_it_matters": "The opportunity may be interpreted as a feature unless the category wedge is made explicit.",
                "suggested_evidence": ["category language test", "buyer narrative feedback", "competitive category map"],
                "priority": "medium",
            })

        if signals["blocker_level"] == "conditional":
            gaps.append({
                "gap": "deployment blocker proof",
                "why_it_matters": "The opportunity should not advance to aggressive commercialization until blockers are framed and mitigated.",
                "suggested_evidence": ["control plan", "human-review policy", "compliance review", "deployment constraints"],
                "priority": "critical",
            })

        return gaps or [{
            "gap": "live buyer validation",
            "why_it_matters": "The opportunity is strong enough to test, but buyer conversations and pilot evidence are still needed.",
            "suggested_evidence": sector_profile["buyer_validation_evidence"],
            "priority": "medium",
        }]

    def _recommended_next_actions(
        self,
        signals: Dict[str, Any],
        priority: Dict[str, Any],
        validation_urgency: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        sector_profile = self._sector_profile(signals["sector"])

        actions = [
            {
                "action": sector_profile["first_action"],
                "purpose": "turn the discovered opportunity into a validated buyer-backed thesis",
                "priority": "critical" if priority["priority"] in {"immediate", "high"} else "high",
            },
            {
                "action": sector_profile["second_action"],
                "purpose": "produce evidence for breakthrough synthesis, technical design, and binder packaging",
                "priority": "high",
            },
            {
                "action": "define no-go criteria",
                "purpose": "prevent false positives by deciding what evidence would invalidate the opportunity",
                "priority": "high",
            },
            {
                "action": "package opportunity thesis for portfolio binder",
                "purpose": "make the opportunity legible for design, acquirer, and deal-readiness workflows",
                "priority": "medium",
            },
        ]

        if validation_urgency["level"] in {"urgent", "high"}:
            actions.insert(2, {
                "action": "start validation immediately",
                "purpose": f"timing window is {signals['strategic_window'] or 'active'} and validation urgency is {validation_urgency['level']}",
                "priority": "critical" if validation_urgency["level"] == "urgent" else "high",
            })

        return actions

    # =========================
    # THESIS / SECTOR PROFILES
    # =========================
    def _opportunity_thesis(
        self,
        signals: Dict[str, Any],
        opportunity_score: Dict[str, Any],
        opportunity_type: Dict[str, Any],
        priority: Dict[str, Any],
    ) -> str:
        sector = self._sector_label(signals["sector"])
        typ = self._pretty(opportunity_type.get("type", "opportunity"))
        window = self._pretty(signals.get("strategic_window") or "active")
        moat = self._pretty(signals.get("primary_moat") or "unknown")
        return (
            f"{sector} is showing a {opportunity_score.get('level')} {typ} with "
            f"{priority.get('priority')} priority. The strongest signals are buyer pull "
            f"({signals['buyer_pull_score']:.4f}), strategic pressure "
            f"({signals['strategic_pressure_score']:.4f}), category creation "
            f"({signals['category_creation_score']:.4f}), and a {window} timing window. "
            f"The current defensibility path is led by {moat}; next proof should focus on "
            f"buyer pain, workflow wedge, ROI, and proprietary data-loop validation."
        )

    def _sector_profile(self, sector: str) -> Dict[str, Any]:
        profiles = {
            "climate_insurance": {
                "primary_vector": "climate exposure and underwriting repricing opportunity",
                "target_gap": "climate exposure / underwriting repricing / market withdrawal",
                "unmet_need": "climate insurance risk intelligence platform",
                "solution_class": "climate insurance risk intelligence platform",
                "first_buyer_segment": "underwriting teams",
                "buyer_pain": "insurers and reinsurers need earlier detection of climate exposure concentration, repricing pressure, and market-withdrawal risk",
                "entry_wedge": "climate exposure and underwriting repricing pilot",
                "expansion_path": ["weather-loss backtesting", "exposure benchmarks", "catastrophe scenario modules", "risk-transfer planning", "enterprise risk platform"],
                "proof_to_unlock": "weather-loss backtesting, repricing accuracy, underwriter workflow adoption, and quantified avoided loss exposure",
                "white_space_area": "underwriting-grade climate exposure intelligence between catastrophe modeling, property data, and insurance workflow systems",
                "incumbent_blind_spot": "incumbents may model catastrophe risk but not translate emerging exposure concentration into underwriting workflow and market-withdrawal countermeasures fast enough",
                "hidden_gap": "climate losses can reprice local underwriting markets before insurers have a unified exposure, pricing, and risk-transfer decision layer",
                "category_language": "climate insurance risk intelligence",
                "buyer_validation_objective": "Confirm underwriters, reinsurers, and risk teams feel acute pressure around climate exposure, repricing, and withdrawal decisions.",
                "buyer_validation_evidence": ["underwriter interviews", "reinsurer feedback", "pricing pain evidence", "portfolio exposure examples"],
                "historical_validation_objective": "Backtest climate exposure and repricing signals against historical weather losses and market responses.",
                "historical_validation_evidence": ["weather-loss backtest", "repricing signal precision", "exposure concentration study", "market-withdrawal examples"],
                "workflow_validation_objective": "Confirm the system can fit into underwriting review and portfolio steering workflows.",
                "workflow_validation_evidence": ["underwriter review console test", "workflow acceptance notes", "decision audit trail", "pilot usage logs"],
                "economic_validation_objective": "Quantify underwriting precision, avoided loss exposure, risk-transfer improvement, or portfolio concentration reduction.",
                "economic_validation_evidence": ["ROI model", "pricing improvement case", "avoided loss exposure estimate", "risk-transfer planning improvement"],
                "defensibility_validation_objective": "Prove climate-loss data, exposure benchmarks, and underwriting feedback loops create compounding advantage.",
                "defensibility_validation_evidence": ["data-rights plan", "benchmark product design", "feedback-loop capture plan", "scenario model history"],
                "roi_evidence": ["avoided loss exposure model", "repricing accuracy backtest", "underwriting time savings", "portfolio concentration risk reduction"],
                "moat_evidence": ["climate-loss dataset", "exposure benchmark dataset", "underwriting workflow footprint", "catastrophe scenario model history"],
                "first_action": "run underwriting pain interviews",
                "second_action": "backtest weather-loss and repricing signals",
                "hypotheses": [
                    {
                        "hypothesis": "Underwriters will value a climate exposure intelligence layer if it improves repricing confidence before losses are fully reflected in legacy models.",
                        "validation_method": "Run underwriter interviews and show historical examples of repricing pressure.",
                        "success_signal": "Underwriters identify repeatable decision moments and pilot-worthy workflows.",
                        "priority": "high",
                    },
                    {
                        "hypothesis": "Climate exposure benchmarks can become a premium data product if they are tied to underwriting and reinsurance decisions.",
                        "validation_method": "Test benchmark outputs with carriers, reinsurers, and brokers.",
                        "success_signal": "Buyers request recurring benchmark access or portfolio comparisons.",
                        "priority": "high",
                    },
                ],
            },
            "defense_autonomy": {
                "primary_vector": "mission autonomy and secure command opportunity",
                "target_gap": "mission autonomy / low-latency decision / distributed coordination",
                "unmet_need": "distributed autonomous decision platform",
                "solution_class": "distributed autonomous decision platform",
                "first_buyer_segment": "defense technology programs",
                "buyer_pain": "mission teams need secure, human-reviewed autonomy and coordination under contested conditions",
                "entry_wedge": "mission simulation and secure review pilot",
                "expansion_path": ["simulation validation", "secure command adapter", "human-review controls", "mission audit layer", "program expansion"],
                "proof_to_unlock": "mission simulation performance, secure integration, human-review evidence, and allowed-use policy",
                "white_space_area": "human-reviewed mission intelligence between autonomous platforms, sensors, and secure command workflows",
                "incumbent_blind_spot": "incumbents may build platforms but lack a flexible decision-intelligence layer across simulation, review, and mission evidence",
                "hidden_gap": "mission teams need coordination intelligence that is explainable and governable before full autonomy",
                "category_language": "secure autonomous mission intelligence",
                "buyer_validation_objective": "Confirm mission teams and defense technology buyers need reviewable autonomy coordination.",
                "buyer_validation_evidence": ["mission stakeholder interviews", "simulation use case map", "secure workflow constraints"],
                "historical_validation_objective": "Validate decision logic against simulated or historical mission scenarios.",
                "historical_validation_evidence": ["simulation test", "scenario performance report", "mission review notes"],
                "workflow_validation_objective": "Confirm secure command review and authorization workflows.",
                "workflow_validation_evidence": ["review console test", "authorization workflow map", "audit trail"],
                "economic_validation_objective": "Quantify faster mission planning, reduced coordination failures, or improved situational response.",
                "economic_validation_evidence": ["time-to-decision model", "mission risk reduction estimate", "operator feedback"],
                "defensibility_validation_objective": "Prove simulation data, secure integration, and review logs create defensibility.",
                "defensibility_validation_evidence": ["mission simulation dataset", "secure workflow integration", "audit history"],
                "roi_evidence": ["time-to-decision model", "mission risk reduction", "simulation performance gain"],
                "moat_evidence": ["mission simulation dataset", "secure command workflow footprint", "review and override history"],
                "first_action": "define mission simulation use case",
                "second_action": "validate secure review and human-authorization workflow",
                "hypotheses": [
                    {
                        "hypothesis": "Mission teams will adopt autonomy support faster when it is framed as reviewable mission intelligence instead of full automation.",
                        "validation_method": "Run scenario reviews with operators and security stakeholders.",
                        "success_signal": "Operators accept the review workflow and identify mission-critical use cases.",
                        "priority": "high",
                    },
                ],
            },
            "healthcare_operations": {
                "primary_vector": "capacity and patient-flow operations opportunity",
                "target_gap": "capacity / staffing / patient-flow bottleneck",
                "unmet_need": "healthcare operations intelligence platform",
                "solution_class": "healthcare operations intelligence platform",
                "first_buyer_segment": "hospital operations teams",
                "buyer_pain": "health systems need earlier capacity, staffing, and patient-flow intelligence",
                "entry_wedge": "capacity and patient-flow pilot",
                "expansion_path": ["capacity forecast", "staffing-risk module", "department benchmarks", "command center workflow", "enterprise health-system rollout"],
                "proof_to_unlock": "historical patient-flow backtesting, capacity forecast accuracy, workflow adoption, and staffing impact",
                "white_space_area": "operational decision intelligence between EHR data, staffing systems, and command-center workflows",
                "incumbent_blind_spot": "large health IT systems often store the data but do not expose fast operational foresight across capacity and staffing pressure",
                "hidden_gap": "patient-flow bottlenecks become visible too late for proactive staffing and capacity countermeasures",
                "category_language": "healthcare operations intelligence",
                "buyer_validation_objective": "Confirm operations leaders feel urgent pain around capacity, staffing, and flow decisions.",
                "buyer_validation_evidence": ["operations interviews", "capacity incident examples", "staffing pain evidence"],
                "historical_validation_objective": "Backtest capacity and patient-flow forecasts against historical operations data.",
                "historical_validation_evidence": ["patient-flow backtest", "capacity forecast report", "staffing-risk precision"],
                "workflow_validation_objective": "Confirm fit with command-center, staffing, and operations workflows.",
                "workflow_validation_evidence": ["workflow test", "operator feedback", "review console usage"],
                "economic_validation_objective": "Quantify throughput, staffing efficiency, wait-time reduction, or capacity utilization improvement.",
                "economic_validation_evidence": ["capacity ROI model", "staffing efficiency case", "throughput lift estimate"],
                "defensibility_validation_objective": "Prove capacity data loops and hospital workflow embedding create defensibility.",
                "defensibility_validation_evidence": ["patient-flow dataset", "capacity benchmark", "workflow footprint"],
                "roi_evidence": ["throughput lift", "wait-time reduction", "staffing efficiency", "capacity utilization"],
                "moat_evidence": ["capacity dataset", "patient-flow benchmarks", "hospital workflow footprint"],
                "first_action": "run hospital operations pain interviews",
                "second_action": "backtest patient-flow and capacity forecasts",
                "hypotheses": [
                    {
                        "hypothesis": "Hospital operations leaders will adopt forecasting tools if they predict capacity and staffing pressure early enough to act.",
                        "validation_method": "Test forecasts against historical flow and staffing data.",
                        "success_signal": "Operations teams identify actionable intervention windows.",
                        "priority": "high",
                    },
                ],
            },
            "financial_market_intelligence": {
                "primary_vector": "hidden market signal and repricing opportunity",
                "target_gap": "hidden signal / repricing opportunity",
                "unmet_need": "financial signal intelligence platform",
                "solution_class": "financial signal intelligence platform",
                "first_buyer_segment": "institutional research desks",
                "buyer_pain": "institutional buyers need earlier detection of credit, liquidity, risk, and repricing signals",
                "entry_wedge": "focused signal intelligence pilot",
                "expansion_path": ["historical regime backtest", "risk signal dashboard", "portfolio workflow module", "premium benchmark data", "institutional platform"],
                "proof_to_unlock": "historical regime backtesting, signal accuracy, workflow adoption, and economic value of earlier risk detection",
                "white_space_area": "proprietary weak-signal intelligence between market data, risk systems, and institutional workflows",
                "incumbent_blind_spot": "data platforms may provide data access but not automatically synthesize overlooked signal patterns into portfolio-ready intelligence",
                "hidden_gap": "risk repricing signals can exist before they become obvious in consensus research",
                "category_language": "financial signal intelligence",
                "buyer_validation_objective": "Confirm research, risk, and portfolio teams need earlier signal detection.",
                "buyer_validation_evidence": ["institutional interviews", "risk workflow map", "signal pain examples"],
                "historical_validation_objective": "Backtest signals against historical regimes and repricing events.",
                "historical_validation_evidence": ["regime backtest", "signal precision report", "false-positive review"],
                "workflow_validation_objective": "Confirm fit with research, risk, and portfolio workflows.",
                "workflow_validation_evidence": ["research workflow test", "risk dashboard usage", "analyst feedback"],
                "economic_validation_objective": "Quantify value from earlier risk detection or research prioritization.",
                "economic_validation_evidence": ["risk detection ROI", "research efficiency case", "portfolio signal case"],
                "defensibility_validation_objective": "Prove signal history and benchmark data create proprietary advantage.",
                "defensibility_validation_evidence": ["signal dataset", "benchmark library", "model governance trail"],
                "roi_evidence": ["signal precision", "portfolio risk avoidance", "research efficiency", "regime backtest value"],
                "moat_evidence": ["proprietary signal history", "risk benchmark library", "research workflow footprint"],
                "first_action": "run institutional buyer pain interviews",
                "second_action": "backtest signals against historical regimes",
                "hypotheses": [
                    {
                        "hypothesis": "Institutional buyers will pay for signal intelligence if it identifies risk or repricing before consensus awareness.",
                        "validation_method": "Backtest signals and present examples to research/risk teams.",
                        "success_signal": "Buyers request recurring monitoring or integration into research workflow.",
                        "priority": "high",
                    },
                ],
            },
            "industrial_supply_chain": {
                "primary_vector": "supplier-risk and shortage prediction opportunity",
                "target_gap": "component shortage / supplier dependency / production bottleneck",
                "unmet_need": "industrial resilience intelligence platform",
                "solution_class": "industrial resilience intelligence platform",
                "first_buyer_segment": "procurement teams",
                "buyer_pain": "manufacturers need earlier warning of supplier dependency risk, shortages, and production bottlenecks",
                "entry_wedge": "supplier-risk and shortage forecasting pilot",
                "expansion_path": ["supplier graph", "shortage forecast", "procurement recommendation", "ERP integration", "enterprise resilience platform"],
                "proof_to_unlock": "historical disruption backtesting, shortage forecast accuracy, workflow adoption, and avoided disruption value",
                "white_space_area": "predictive resilience layer between supplier data, ERP systems, and procurement workflows",
                "incumbent_blind_spot": "planning systems often manage workflows but do not discover hidden supplier-risk patterns early enough",
                "hidden_gap": "supplier dependency failures compound before procurement teams have enough lead time to respond",
                "category_language": "industrial resilience intelligence",
                "buyer_validation_objective": "Confirm procurement and operations leaders feel acute pain around shortages and supplier risk.",
                "buyer_validation_evidence": ["procurement interviews", "supplier-risk examples", "production disruption cases"],
                "historical_validation_objective": "Backtest supplier-risk and shortage signals against historical disruptions.",
                "historical_validation_evidence": ["disruption backtest", "shortage forecast precision", "supplier-risk event study"],
                "workflow_validation_objective": "Confirm fit with procurement, planning, and ERP workflows.",
                "workflow_validation_evidence": ["ERP integration test", "operator workflow notes", "procurement recommendation review"],
                "economic_validation_objective": "Quantify avoided shortages, reduced disruption, and procurement efficiency.",
                "economic_validation_evidence": ["avoided disruption model", "shortage cost estimate", "procurement efficiency case"],
                "defensibility_validation_objective": "Prove supplier data loops and workflow embedding create defensibility.",
                "defensibility_validation_evidence": ["supplier-risk graph", "shortage benchmark", "workflow integration footprint"],
                "roi_evidence": ["avoided disruption", "shortage cost reduction", "procurement efficiency", "forecast accuracy"],
                "moat_evidence": ["supplier graph", "shortage dataset", "ERP workflow footprint"],
                "first_action": "run procurement pain interviews",
                "second_action": "backtest supplier-risk and shortage signals",
                "hypotheses": [
                    {
                        "hypothesis": "Manufacturers will adopt early-warning supplier intelligence if it gives procurement enough time to avoid disruption.",
                        "validation_method": "Backtest shortage signals and validate recommendations with procurement teams.",
                        "success_signal": "Procurement teams identify specific actions they would have taken earlier.",
                        "priority": "high",
                    },
                ],
            },
            "energy_infrastructure": {
                "primary_vector": "grid bottleneck and resilience intelligence opportunity",
                "target_gap": "grid instability / demand pressure / infrastructure bottleneck",
                "unmet_need": "energy infrastructure intelligence platform",
                "solution_class": "energy infrastructure intelligence platform",
                "first_buyer_segment": "utilities",
                "buyer_pain": "utilities and infrastructure owners need earlier visibility into grid bottlenecks, demand pressure, and asset risk",
                "entry_wedge": "grid bottleneck and resilience planning pilot",
                "expansion_path": ["grid event backtest", "asset-risk model", "demand forecast", "resilience planning", "utility platform"],
                "proof_to_unlock": "grid-event backtesting, asset-risk calibration, utility workflow fit, and resilience planning value",
                "white_space_area": "predictive resilience layer between grid operations, asset data, and infrastructure planning",
                "incumbent_blind_spot": "infrastructure systems may monitor assets but not synthesize early bottleneck and resilience signals into planning decisions",
                "hidden_gap": "grid demand and asset-risk pressure can build before planning systems surface investment priorities",
                "category_language": "energy infrastructure intelligence",
                "buyer_validation_objective": "Confirm utility planners and infrastructure owners need early bottleneck and resilience intelligence.",
                "buyer_validation_evidence": ["utility interviews", "grid bottleneck examples", "asset-risk pain evidence"],
                "historical_validation_objective": "Backtest grid-event, demand, and asset-risk forecasts.",
                "historical_validation_evidence": ["grid event backtest", "asset-risk calibration", "demand forecast accuracy"],
                "workflow_validation_objective": "Confirm fit with utility planning and resilience workflows.",
                "workflow_validation_evidence": ["planning workflow test", "operator review", "resilience dashboard usage"],
                "economic_validation_objective": "Quantify resilience investment value, avoided outage risk, or planning efficiency.",
                "economic_validation_evidence": ["resilience ROI model", "asset-risk prioritization case", "planning efficiency estimate"],
                "defensibility_validation_objective": "Prove grid-event data loops and planning workflow embedding create defensibility.",
                "defensibility_validation_evidence": ["grid event dataset", "asset-risk benchmark", "planning workflow footprint"],
                "roi_evidence": ["resilience investment value", "avoided outage risk", "asset-risk prioritization", "planning efficiency"],
                "moat_evidence": ["grid event dataset", "asset-risk benchmark", "utility workflow footprint"],
                "first_action": "run utility planning pain interviews",
                "second_action": "backtest grid-event and asset-risk signals",
                "hypotheses": [
                    {
                        "hypothesis": "Utilities will adopt infrastructure intelligence if it improves resilience planning before grid pressure becomes operationally visible.",
                        "validation_method": "Backtest grid bottleneck signals and validate planning value with utility stakeholders.",
                        "success_signal": "Planners identify investment or operational decisions improved by the signal.",
                        "priority": "high",
                    },
                ],
            },
        }

        return profiles.get(sector, {
            "primary_vector": "cross-sector opportunity intelligence opportunity",
            "target_gap": "knowledge / decision / opportunity gap",
            "unmet_need": "opportunity intelligence platform",
            "solution_class": "opportunity intelligence platform",
            "first_buyer_segment": "strategy teams",
            "buyer_pain": "buyers need better weak-signal discovery, opportunity synthesis, and validation workflows",
            "entry_wedge": "focused opportunity intelligence pilot",
            "expansion_path": ["signal ingestion", "gap detection", "opportunity ranking", "design synthesis", "portfolio packaging"],
            "proof_to_unlock": "buyer pain validation, historical signal evidence, workflow fit, and ROI case",
            "white_space_area": "automated opportunity discovery between research, strategy, design, and portfolio workflows",
            "incumbent_blind_spot": "existing tools search known terms but do not synthesize hidden opportunity pathways across signals",
            "hidden_gap": "valuable opportunities can remain invisible when signals are fragmented across data, markets, and history",
            "category_language": "opportunity intelligence",
            "buyer_validation_objective": "Confirm strategy and innovation buyers need automated opportunity discovery.",
            "buyer_validation_evidence": ["buyer interviews", "workflow map", "strategy pain examples"],
            "historical_validation_objective": "Backtest discovery logic against historical opportunity patterns.",
            "historical_validation_evidence": ["historical opportunity examples", "signal trace", "discovery precision"],
            "workflow_validation_objective": "Confirm fit with strategy, research, design, and portfolio workflows.",
            "workflow_validation_evidence": ["workflow test", "user feedback", "artifact usage"],
            "economic_validation_objective": "Quantify speed, quality, and strategic value of opportunity discovery.",
            "economic_validation_evidence": ["time savings", "opportunity quality score", "portfolio value case"],
            "defensibility_validation_objective": "Prove proprietary signal history and workflow data loops create defensibility.",
            "defensibility_validation_evidence": ["signal dataset", "taxonomy", "workflow footprint"],
            "roi_evidence": ["time savings", "opportunity conversion", "better decision quality"],
            "moat_evidence": ["signal history", "opportunity taxonomy", "workflow data loops"],
            "first_action": "run buyer pain interviews",
            "second_action": "backtest opportunity discovery against historical examples",
            "hypotheses": [
                {
                    "hypothesis": "Strategy teams will adopt opportunity intelligence if it finds non-obvious opportunities faster than manual research.",
                    "validation_method": "Compare system output against a curated historical opportunity set.",
                    "success_signal": "System identifies useful gaps, wedges, or buyer hypotheses that manual search misses.",
                    "priority": "high",
                },
            ],
        })

    # =========================
    # SMALL HELPERS
    # =========================
    def _score_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []
        if signals["market_gap_confidence"] >= 0.80:
            drivers.append("high-confidence market gap")
        if signals["strategic_pressure_score"] >= 0.70:
            drivers.append("high strategic pressure")
        if signals["buyer_pull_score"] >= 0.78:
            drivers.append("strong buyer pull")
        if signals["category_creation_score"] >= 0.78:
            drivers.append("platform/category creation signal")
        if signals["timing_pressure_score"] >= 0.70:
            drivers.append("timing pressure")
        if signals["moat_score"] >= 0.70:
            drivers.append("defensible data/workflow position")
        if signals["value_capture_score"] >= 0.70:
            drivers.append("value capture potential")
        return drivers or ["baseline market gap and opportunity signals"]

    def _priority_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []
        if signals["strategic_window"]:
            drivers.append(f"strategic window: {signals['strategic_window']}")
        if signals["buyer_pull_score"] >= 0.78:
            drivers.append("buyer pull is strong")
        if signals["timing_pressure_score"] >= 0.70:
            drivers.append("validation window is time-sensitive")
        if signals["category_creation_score"] >= 0.78:
            drivers.append("category formation is active")
        if signals["blocker_level"] == "conditional":
            drivers.append("blocker mitigation must be validated early")
        return drivers or ["priority based on opportunity score and market-gap confidence"]

    def _why_now(self, signals: Dict[str, Any], trend_trajectory: Dict[str, Any]) -> str:
        direction = signals.get("trend_direction") or "emerging"
        window = signals.get("strategic_window") or "active"
        pressure = signals.get("strategic_pressure_score", 0.0)
        return (
            f"The trend is {self._pretty(direction)}, the strategic window is {self._pretty(window)}, "
            f"and strategic pressure is {pressure:.4f}. This suggests validation should happen before the opportunity becomes obvious to incumbents."
        )

    def _validation_urgency_why(self, signals: Dict[str, Any], level: str) -> str:
        if level in {"urgent", "high"}:
            return (
                f"Timing pressure ({signals['timing_pressure_score']:.4f}) and buyer pull "
                f"({signals['buyer_pull_score']:.4f}) indicate the opportunity should be validated quickly."
            )
        return "Signals support validation, but timing pressure is not yet extreme."

    def _confidence(self, signals: Dict[str, Any], opportunity_score: Dict[str, Any]) -> float:
        return round(self._bounded(
            0.22
            + opportunity_score["score"] * 0.16
            + signals["market_gap_confidence"] * 0.12
            + signals["buyer_pull_score"] * 0.10
            + signals["category_creation_score"] * 0.08
            + signals["moat_score"] * 0.07
            + signals["value_capture_score"] * 0.06
            + signals["timing_pressure_score"] * 0.05
            + min(0.05, signals["buyer_segment_count"] * 0.007)
            - signals["risk_score"] * 0.025
            - signals["commercial_risk_score"] * 0.020
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
        text = text or ""
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

    def _first_item(self, values: Any, fallback: str) -> str:
        if isinstance(values, list) and values:
            return str(values[0])
        return fallback
