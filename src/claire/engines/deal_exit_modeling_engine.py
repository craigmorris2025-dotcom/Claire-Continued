"""
Deal Exit Modeling Engine — evaluates exit readiness, acquirer fit,
valuation logic, deal paths, diligence requirements, and negotiation levers.

Purpose:
- Activate Claire Stage 21: Deal / Exit Modeling
- Convert the opportunity, moat, risk, business model, and acquirer outputs
  into a structured deal-readiness and exit-strategy profile.

This version is deterministic/local. Later versions can connect to M&A
comparables, buyer acquisition history, valuation multiples, public-market
data, private transaction datasets, and corporate-development intelligence.
"""

from typing import Any, Dict, List, Optional


class DealExitModelingEngine:
    """
    Deterministic deal / exit modeling analyzer.
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
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        business_model: Optional[Dict[str, Any]] = None,
        acquirer_matches: Optional[List[Dict[str, Any]]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        scores = scores or {}
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        business_model = business_model or {}
        acquirer_matches = acquirer_matches or []
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            scores=scores,
            domain=domain,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            moat=moat,
            risk_regulation=risk_regulation,
            business_model=business_model,
            acquirer_matches=acquirer_matches,
            connector_sources=connector_sources,
        )

        buyer_universe = self._buyer_universe(signals, acquirer_matches, market_gap)
        strategic_fit = self._strategic_fit(signals, buyer_universe)
        exit_readiness = self._exit_readiness(signals, strategic_fit)
        valuation_logic = self._valuation_logic(signals, strategic_fit)
        deal_paths = self._deal_paths(signals, buyer_universe)
        diligence_requirements = self._diligence_requirements(signals)
        risk_adjustments = self._risk_adjustments(signals)
        negotiation_levers = self._negotiation_levers(signals, buyer_universe)

        return {
            "status": "success",
            "domain": domain,
            "sector": signals["sector"],
            "exit_readiness": exit_readiness,
            "buyer_universe": buyer_universe,
            "strategic_fit": strategic_fit,
            "valuation_logic": valuation_logic,
            "deal_paths": deal_paths,
            "diligence_requirements": diligence_requirements,
            "risk_adjustments": risk_adjustments,
            "negotiation_levers": negotiation_levers,
            "exit_narrative": self._exit_narrative(signals, buyer_universe, strategic_fit, valuation_logic),
            "deal_exit_thesis": self._deal_exit_thesis(signals, exit_readiness, strategic_fit, valuation_logic),
            "recommended_next_actions": self._recommended_next_actions(signals, exit_readiness),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, strategic_fit, exit_readiness),
        }

    # =========================
    # SIGNALS
    # =========================
    def _signals(
        self,
        text: str,
        keywords: List[str],
        scores: Dict[str, Any],
        domain: str,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        business_model: Dict[str, Any],
        acquirer_matches: List[Dict[str, Any]],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        combined = f"{text} {' '.join(keywords).lower()}"

        sector = market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general"
        market = connector_sources.get("market", {}) if isinstance(connector_sources, dict) else {}
        financial = connector_sources.get("financial", {}) if isinstance(connector_sources, dict) else {}

        buyer_pull_score = self._get(market_formation, "buyer_pull.score")
        category_score = self._get(market_formation, "category_creation_score.score")
        timing_score = self._get(trend_trajectory, "timing_pressure.score")
        momentum_score = self._get(trend_trajectory, "market_momentum.score")
        moat_score = self._get(moat, "moat_type.moat_score")
        copy_risk_score = self._get(moat, "copy_risk.score")
        primary_moat = self._get_text(moat, "moat_type.primary_moat")
        risk_score = self._get(risk_regulation, "risk_profile.score")
        blocker_level = self._get_text(risk_regulation, "blocker_assessment.blocker_level") or "unknown"
        value_capture_score = self._get(business_model, "value_capture.score")
        buyer_roi_score = self._get(business_model, "buyer_roi.score")
        commercial_risk_score = self._get(business_model, "commercial_risk.score")
        revenue_model = self._get_text(business_model, "revenue_model.primary_model")

        match_scores = []
        for match in acquirer_matches:
            try:
                match_scores.append(float(match.get("match_score", 0.0) or 0.0))
            except Exception:
                pass

        top_acquirer_score = max(match_scores, default=0.0)
        avg_top_5_score = sum(sorted(match_scores, reverse=True)[:5]) / max(1, min(5, len(match_scores)))

        strategic_terms = [
            "platform",
            "enterprise",
            "subscription",
            "workflow",
            "erp",
            "procurement",
            "integration",
            "benchmark",
            "module",
            "data",
            "risk",
            "resilience",
            "automation",
            "intelligence",
            "api",
        ]

        exit_terms = [
            "acquirer",
            "acquisition",
            "exit",
            "strategic buyer",
            "partner",
            "enterprise license",
            "platform contract",
            "corporate development",
            "valuation",
        ]

        defensibility_terms = [
            "proprietary",
            "workflow",
            "lock-in",
            "dataset",
            "benchmark",
            "integration",
            "network",
            "moat",
            "sticky",
        ]

        def count_terms(terms: List[str]) -> int:
            return sum(1 for term in terms if term.lower() in combined)

        return {
            "domain": domain,
            "sector": sector,
            "portfolio_score": float(scores.get("portfolio_score", 0.0) or 0.0),
            "breakthrough_score": float(scores.get("breakthrough_score", 0.0) or 0.0),
            "viability_score": float(scores.get("viability_score", 0.0) or 0.0),
            "feasibility_score": float(scores.get("feasibility_score", 0.0) or 0.0),
            "acquisition_score": float(scores.get("acquisition_score", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "buyer_pull_score": buyer_pull_score,
            "category_creation_score": category_score,
            "timing_pressure": timing_score,
            "market_momentum": momentum_score,
            "moat_score": moat_score,
            "copy_risk_score": copy_risk_score,
            "primary_moat": primary_moat,
            "risk_score": risk_score,
            "blocker_level": blocker_level,
            "revenue_model": revenue_model,
            "value_capture_score": value_capture_score,
            "buyer_roi_score": buyer_roi_score,
            "commercial_risk_score": commercial_risk_score,
            "acquirer_count": len(acquirer_matches),
            "top_acquirer_score": top_acquirer_score,
            "avg_top_5_acquirer_score": avg_top_5_score,
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "acquirer_category_count": len(market_gap.get("acquirer_categories", [])) if isinstance(market_gap, dict) else 0,
            "strategic_term_count": count_terms(strategic_terms),
            "exit_term_count": count_terms(exit_terms),
            "defensibility_term_count": count_terms(defensibility_terms),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
        }

    # =========================
    # OUTPUT BUILDERS
    # =========================
    def _buyer_universe(
        self,
        signals: Dict[str, Any],
        acquirer_matches: List[Dict[str, Any]],
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        if signals["acquirer_count"] >= 8 and signals["top_acquirer_score"] >= 0.90:
            depth = "deep"
        elif signals["acquirer_count"] >= 4:
            depth = "moderate"
        else:
            depth = "thin"

        categories = market_gap.get("acquirer_categories", []) if isinstance(market_gap, dict) else []

        return {
            "depth": depth,
            "acquirer_count": signals["acquirer_count"],
            "top_match_score": round(signals["top_acquirer_score"], 4),
            "average_top_5_score": round(signals["avg_top_5_acquirer_score"], 4),
            "acquirer_categories": categories,
            "buyer_types": self._buyer_types(signals, categories),
            "top_matches": acquirer_matches[:10],
        }

    def _strategic_fit(self, signals: Dict[str, Any], buyer_universe: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.18
            + signals["acquisition_score"] * 0.15
            + signals["top_acquirer_score"] * 0.13
            + signals["avg_top_5_acquirer_score"] * 0.08
            + signals["buyer_pull_score"] * 0.11
            + signals["category_creation_score"] * 0.10
            + signals["value_capture_score"] * 0.10
            + signals["buyer_roi_score"] * 0.07
            + signals["moat_score"] * 0.08
            + min(0.06, signals["acquirer_count"] * 0.006)
            - signals["commercial_risk_score"] * 0.04
        )

        if score >= 0.78:
            level = "strong"
        elif score >= 0.60:
            level = "moderate"
        else:
            level = "early"

        return {
            "level": level,
            "score": round(score, 4),
            "fit_drivers": self._fit_drivers(signals, buyer_universe),
            "strategic_rationale": self._strategic_rationale(signals, buyer_universe),
        }

    def _exit_readiness(self, signals: Dict[str, Any], strategic_fit: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.16
            + signals["portfolio_score"] * 0.14
            + strategic_fit.get("score", 0.0) * 0.15
            + signals["value_capture_score"] * 0.11
            + signals["buyer_roi_score"] * 0.10
            + signals["moat_score"] * 0.09
            + signals["top_acquirer_score"] * 0.08
            + (1 - signals["copy_risk_score"]) * 0.06
            + min(0.05, signals["acquirer_count"] * 0.005)
            - signals["risk_score"] * 0.04
            - signals["commercial_risk_score"] * 0.04
            - (0.06 if signals["blocker_level"] == "conditional" else 0.0)
        )

        if signals["blocker_level"] == "conditional":
            state = "exit_candidate_with_conditions"
        elif score >= 0.80:
            state = "exit_ready"
        elif score >= 0.64:
            state = "exit_candidate"
        else:
            state = "needs_validation"

        return {
            "state": state,
            "score": round(score, 4),
            "readiness_drivers": self._readiness_drivers(signals),
            "missing_proof": self._missing_proof(signals),
        }

    def _valuation_logic(self, signals: Dict[str, Any], strategic_fit: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.20
            + signals["value_capture_score"] * 0.17
            + signals["buyer_roi_score"] * 0.13
            + signals["moat_score"] * 0.11
            + strategic_fit.get("score", 0.0) * 0.11
            + signals["category_creation_score"] * 0.09
            + signals["portfolio_score"] * 0.09
            + signals["top_acquirer_score"] * 0.07
            - signals["risk_score"] * 0.035
            - signals["commercial_risk_score"] * 0.035
        )

        if score >= 0.78:
            strength = "premium_strategic"
        elif score >= 0.62:
            strength = "strategic_with_validation"
        else:
            strength = "early_option_value"

        return {
            "valuation_signal": {
                "strength": strength,
                "score": round(score, 4),
            },
            "primary_value_drivers": self._valuation_drivers(signals),
            "valuation_methods": self._valuation_methods(signals),
            "upside_cases": self._upside_cases(signals),
            "discount_factors": self._discount_factors(signals),
        }

    def _deal_paths(self, signals: Dict[str, Any], buyer_universe: Dict[str, Any]) -> List[Dict[str, Any]]:
        paths = [
            {
                "path": "strategic acquisition",
                "fit": self._path_fit_score(signals, 0.18, "strategic"),
                "best_for": "ERP, industrial software, automation, supply-chain, or data platforms seeking category expansion",
                "trigger": "validated enterprise pilots, strong ROI proof, and defensible workflow/data position",
                "priority": "high",
            },
            {
                "path": "commercial partnership to acquisition",
                "fit": self._path_fit_score(signals, 0.12, "partnership"),
                "best_for": "strategic buyers who need proof before full corporate-development action",
                "trigger": "partner integration, channel validation, and repeated buyer demand",
                "priority": "high" if signals["blocker_level"] == "conditional" else "medium",
            },
            {
                "path": "platform licensing / OEM",
                "fit": self._path_fit_score(signals, 0.08, "licensing"),
                "best_for": "platforms that want embedded intelligence without full acquisition first",
                "trigger": "stable APIs, integration reliability, and defensible modules",
                "priority": "medium",
            },
            {
                "path": "growth financing before exit",
                "fit": self._path_fit_score(signals, 0.04, "financing"),
                "best_for": "scaling enterprise adoption before strategic exit",
                "trigger": "validated retention, module expansion, and repeatable sales motion",
                "priority": "medium",
            },
        ]

        return sorted(paths, key=lambda item: item["fit"], reverse=True)

    def _diligence_requirements(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        requirements = [
            {
                "requirement": "customer ROI evidence",
                "why": "Buyers need proof that the system reduces disruption, cost, risk, or cycle time.",
                "priority": "high",
            },
            {
                "requirement": "technical architecture and integration review",
                "why": "Strategic buyers will review scalability, APIs, ERP/planning-system integration, and maintainability.",
                "priority": "high",
            },
            {
                "requirement": "model performance validation",
                "why": "Forecasting and recommendation quality must be proven with backtests and pilots.",
                "priority": "high",
            },
            {
                "requirement": "data rights and governance review",
                "why": "Data-loop defensibility depends on clear rights, lineage, permissions, and controls.",
                "priority": "high",
            },
            {
                "requirement": "commercial model validation",
                "why": "Enterprise subscription pricing must be supported by willingness-to-pay and expansion proof.",
                "priority": "high",
            },
        ]

        if signals["blocker_level"] == "conditional":
            requirements.append({
                "requirement": "human-review and deployment-control evidence",
                "why": "Conditional blocker must be resolved or framed as a manageable deployment requirement.",
                "priority": "critical",
            })

        if signals["primary_moat"] in {"workflow_lock_in", "integration_depth"}:
            requirements.append({
                "requirement": "workflow stickiness evidence",
                "why": "The strongest deal argument depends on embedded operational use and switching costs.",
                "priority": "high",
            })

        if signals["copy_risk_score"] > 0.35:
            requirements.append({
                "requirement": "differentiation and copy-risk defense",
                "why": "Strategic buyers will discount generic features without proprietary data or workflow depth.",
                "priority": "medium",
            })

        return self._dedupe_dicts(requirements, "requirement")

    def _risk_adjustments(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        adjustments = []

        if signals["blocker_level"] == "conditional":
            adjustments.append({
                "adjustment": "conditional deployment discount",
                "impact": "Strategic buyers may require risk controls, advisory mode, and human-review validation before premium valuation.",
                "severity": "medium",
                "mitigation": "Package blocker mitigation as completed diligence evidence.",
            })

        if signals["moat_score"] < 0.78:
            adjustments.append({
                "adjustment": "moat maturity discount",
                "impact": "Moderate moat may reduce premium unless data loops and workflow dependency are proven.",
                "severity": "medium",
                "mitigation": "Validate repeat usage, proprietary benchmarks, and integration depth.",
            })

        if signals["commercial_risk_score"] >= 0.42:
            adjustments.append({
                "adjustment": "commercial execution discount",
                "impact": "Long sales cycles or procurement friction may reduce near-term deal value.",
                "severity": "medium",
                "mitigation": "Show paid pilot conversion and enterprise expansion path.",
            })

        if signals["acquirer_count"] < 4:
            adjustments.append({
                "adjustment": "thin buyer universe discount",
                "impact": "Limited acquirer universe can weaken deal tension.",
                "severity": "high",
                "mitigation": "Expand buyer map across adjacent strategic categories.",
            })

        if not adjustments:
            adjustments.append({
                "adjustment": "no major deterministic deal discount surfaced",
                "impact": "Maintain evidence discipline and validate with live market data.",
                "severity": "low",
                "mitigation": "Continue acquirer research and diligence preparation.",
            })

        return adjustments

    def _negotiation_levers(self, signals: Dict[str, Any], buyer_universe: Dict[str, Any]) -> List[Dict[str, Any]]:
        levers = [
            {
                "lever": "strong buyer pain and ROI",
                "use": "Anchor valuation to avoided disruption, shortage reduction, and procurement efficiency.",
                "priority": "high",
            },
            {
                "lever": "platform-layer category formation",
                "use": "Frame the opportunity as a category wedge rather than a feature acquisition.",
                "priority": "high",
            },
            {
                "lever": "workflow lock-in and data loops",
                "use": "Position defensibility around embedded operational workflow and compounding data advantage.",
                "priority": "high",
            },
            {
                "lever": "multi-acquirer tension",
                "use": "Use ERP, industrial automation, supply-chain software, and cloud data platform categories to create strategic tension.",
                "priority": "medium" if buyer_universe.get("depth") != "deep" else "high",
            },
        ]

        if signals["blocker_level"] == "conditional":
            levers.append({
                "lever": "risk-control readiness",
                "use": "Convert the human-review blocker into diligence strength by showing advisory-mode controls.",
                "priority": "medium",
            })

        if signals["revenue_model"] == "enterprise_subscription":
            levers.append({
                "lever": "recurring revenue path",
                "use": "Emphasize annual platform subscriptions, module expansion, and account growth.",
                "priority": "high",
            })

        return levers

    # =========================
    # TEXT HELPERS
    # =========================
    def _buyer_types(self, signals: Dict[str, Any], categories: List[str]) -> List[Dict[str, Any]]:
        buyer_types = []
        category_text = " ".join(categories).lower()

        if "erp" in category_text or signals["sector"] == "industrial_supply_chain":
            buyer_types.append({
                "type": "ERP / enterprise application platforms",
                "strategic_reason": "can embed predictive intelligence into planning, procurement, and operations workflows",
                "priority": "high",
            })

        if "automation" in category_text or "industrial" in category_text:
            buyer_types.append({
                "type": "industrial automation and industrial software companies",
                "strategic_reason": "can extend factory and operations intelligence into supplier and bottleneck prediction",
                "priority": "high",
            })

        if "supply" in category_text:
            buyer_types.append({
                "type": "supply-chain planning and execution platforms",
                "strategic_reason": "can add early-warning shortage and supplier-risk intelligence to existing planning suites",
                "priority": "high",
            })

        if "cloud" in category_text or "data" in category_text:
            buyer_types.append({
                "type": "cloud data and AI platforms",
                "strategic_reason": "can use the solution as a verticalized intelligence layer",
                "priority": "medium",
            })

        if not buyer_types:
            buyer_types.append({
                "type": "strategic technology buyers",
                "strategic_reason": "can acquire the opportunity for product expansion and data advantage",
                "priority": "medium",
            })

        return buyer_types

    def _fit_drivers(self, signals: Dict[str, Any], buyer_universe: Dict[str, Any]) -> List[str]:
        drivers = []

        if signals["acquirer_count"] >= 8:
            drivers.append("large acquirer universe")

        if signals["top_acquirer_score"] >= 0.90:
            drivers.append("high top-acquirer match score")

        if signals["buyer_pull_score"] >= 0.80:
            drivers.append("strong buyer pull")

        if signals["value_capture_score"] >= 0.80:
            drivers.append("strong value capture")

        if signals["buyer_roi_score"] >= 0.80:
            drivers.append("high buyer ROI")

        if signals["moat_score"] >= 0.70:
            drivers.append("defensible workflow/data position")

        if signals["category_creation_score"] >= 0.80:
            drivers.append("platform/category creation potential")

        if signals["blocker_level"] == "conditional":
            drivers.append("deal requires deployment-control proof")

        return drivers or ["strategic fit requires more validation"]

    def _strategic_rationale(self, signals: Dict[str, Any], buyer_universe: Dict[str, Any]) -> str:
        sector = signals.get("sector", "target sector").replace("_", " ")
        return (
            f"{sector} has {buyer_universe.get('depth')} strategic-buyer coverage, "
            f"top acquirer score of {signals.get('top_acquirer_score'):.4f}, "
            f"buyer pull of {signals.get('buyer_pull_score'):.4f}, and value capture of "
            f"{signals.get('value_capture_score'):.4f}."
        )

    def _readiness_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = [
            "portfolio score available",
            "acquirer matching available",
            "business model available",
            "risk/regulation profile available",
        ]

        if signals["value_capture_score"] >= 0.80:
            drivers.append("strong value capture")

        if signals["buyer_roi_score"] >= 0.80:
            drivers.append("high buyer ROI")

        if signals["top_acquirer_score"] >= 0.90:
            drivers.append("strong top acquirer fit")

        if signals["blocker_level"] == "conditional":
            drivers.append("readiness is conditional on blocker mitigation")

        return drivers

    def _missing_proof(self, signals: Dict[str, Any]) -> List[str]:
        missing = []

        if signals["blocker_level"] == "conditional":
            missing.append("documented mitigation of human-review / deployment-control blocker")

        if signals["moat_score"] < 0.78:
            missing.append("stronger evidence of proprietary data loops and workflow switching costs")

        if signals["buyer_roi_score"] < 0.85:
            missing.append("quantified buyer ROI case")

        if signals["acquirer_count"] < 8:
            missing.append("expanded acquirer universe and buyer mapping")

        if not missing:
            missing.append("live market comparables and buyer-specific acquisition rationale")

        return missing

    def _valuation_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = [
            "strategic buyer fit",
            "enterprise subscription potential",
            "strong value capture",
            "buyer ROI",
            "platform/category formation",
        ]

        if signals["primary_moat"]:
            drivers.append(f"primary moat: {signals['primary_moat']}")

        if signals["sector"] == "industrial_supply_chain":
            drivers.extend([
                "industrial resilience urgency",
                "supplier-risk and shortage intelligence",
                "ERP / workflow integration potential",
            ])

        return list(dict.fromkeys(drivers))

    def _valuation_methods(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "method": "strategic acquisition premium",
                "use_case": "best when acquirer product roadmap or category gap is directly addressed",
                "priority": "high",
            },
            {
                "method": "ARR / recurring revenue multiple",
                "use_case": "best once enterprise subscription revenue is validated",
                "priority": "high" if signals["revenue_model"] == "enterprise_subscription" else "medium",
            },
            {
                "method": "ROI-based strategic value",
                "use_case": "best when buyer can quantify avoided disruption or operational savings",
                "priority": "high",
            },
            {
                "method": "technology and data-asset value",
                "use_case": "best when proprietary datasets, benchmarks, and integrations are proven",
                "priority": "medium",
            },
        ]

    def _upside_cases(self, signals: Dict[str, Any]) -> List[str]:
        cases = [
            "paid pilots convert to recurring enterprise subscriptions",
            "modules expand across procurement, supplier risk, and operations workflows",
            "proprietary benchmarks become a premium data product",
            "strategic buyer uses acquisition to fill category gap",
        ]

        if signals["acquirer_count"] >= 8:
            cases.append("multiple strategic buyer categories create deal tension")

        return cases

    def _discount_factors(self, signals: Dict[str, Any]) -> List[str]:
        factors = []

        if signals["blocker_level"] == "conditional":
            factors.append("conditional deployment blocker")

        if signals["moat_score"] < 0.78:
            factors.append("moat still moderate rather than strong")

        if signals["commercial_risk_score"] >= 0.30:
            factors.append("enterprise sales and implementation burden")

        if signals["risk_score"] >= 0.45:
            factors.append("operational risk review required")

        return factors or ["no major deterministic valuation discount surfaced"]

    def _path_fit_score(self, signals: Dict[str, Any], base_bonus: float, path_type: str) -> float:
        score = self._bounded(
            0.18
            + base_bonus
            + signals["acquisition_score"] * 0.13
            + signals["top_acquirer_score"] * 0.11
            + signals["value_capture_score"] * 0.09
            + signals["buyer_roi_score"] * 0.08
            + signals["moat_score"] * 0.08
            - signals["commercial_risk_score"] * 0.04
        )

        if path_type == "partnership" and signals["blocker_level"] == "conditional":
            score = self._bounded(score + 0.05)

        if path_type == "strategic" and signals["blocker_level"] == "conditional":
            score = self._bounded(score - 0.03)

        if path_type == "licensing" and signals["revenue_model"] == "enterprise_subscription":
            score = self._bounded(score + 0.02)

        return round(score, 4)

    def _exit_narrative(
        self,
        signals: Dict[str, Any],
        buyer_universe: Dict[str, Any],
        strategic_fit: Dict[str, Any],
        valuation_logic: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "one_liner": (
                f"A {signals.get('sector', 'target sector').replace('_', ' ')} opportunity with "
                f"{strategic_fit.get('level')} strategic fit, {buyer_universe.get('depth')} buyer coverage, "
                f"and {valuation_logic.get('valuation_signal', {}).get('strength')} valuation signal."
            ),
            "acquirer_pitch": (
                "Acquire or partner to own a predictive intelligence layer that can extend enterprise workflows, "
                "reduce operational risk, deepen data advantage, and create platform/module expansion."
            ),
            "deal_story": (
                "The deal story should lead with validated buyer pain, measurable ROI, workflow embedding, "
                "proprietary data loops, and a clear path from advisory pilots to enterprise platform expansion."
            ),
        }

    def _recommended_next_actions(
        self,
        signals: Dict[str, Any],
        exit_readiness: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions = [
            {
                "action": "build acquirer-specific strategic rationale",
                "purpose": "translate Claire output into buyer-specific deal logic",
                "priority": "high",
            },
            {
                "action": "prepare diligence evidence pack",
                "purpose": "organize ROI proof, technical architecture, data rights, model validation, and risk controls",
                "priority": "high",
            },
            {
                "action": "model pilot-to-enterprise conversion economics",
                "purpose": "support valuation and commercial readiness with concrete revenue milestones",
                "priority": "high",
            },
            {
                "action": "map deal path options",
                "purpose": "compare acquisition, commercial partnership, OEM/licensing, and growth-financing paths",
                "priority": "medium",
            },
        ]

        if signals["blocker_level"] == "conditional":
            actions.append({
                "action": "resolve deployment-control blocker before outreach",
                "purpose": "prevent human-review and operational-risk questions from weakening deal leverage",
                "priority": "critical",
            })

        if exit_readiness.get("state") != "exit_ready":
            actions.append({
                "action": "close missing proof points",
                "purpose": "move from candidate-with-conditions to exit-ready package",
                "priority": "high",
            })

        return actions

    def _deal_exit_thesis(
        self,
        signals: Dict[str, Any],
        exit_readiness: Dict[str, Any],
        strategic_fit: Dict[str, Any],
        valuation_logic: Dict[str, Any],
    ) -> str:
        sector = signals.get("sector", "target sector").replace("_", " ")
        return (
            f"{sector} is a {exit_readiness.get('state')} with {strategic_fit.get('level')} strategic fit "
            f"and {valuation_logic.get('valuation_signal', {}).get('strength')} valuation signal. "
            f"The strongest route is strategic acquisition or partnership-to-acquisition, supported by enterprise subscription potential, "
            f"strong value capture, buyer ROI, and workflow/data defensibility."
        )

    # =========================
    # HELPERS
    # =========================
    def _bounded(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))

    def _confidence(
        self,
        signals: Dict[str, Any],
        strategic_fit: Dict[str, Any],
        exit_readiness: Dict[str, Any],
    ) -> float:
        return round(
            self._bounded(
                0.22
                + signals["portfolio_score"] * 0.11
                + strategic_fit.get("score", 0.0) * 0.13
                + exit_readiness.get("score", 0.0) * 0.11
                + signals["top_acquirer_score"] * 0.09
                + signals["value_capture_score"] * 0.10
                + signals["buyer_roi_score"] * 0.08
                + signals["moat_score"] * 0.07
                - signals["risk_score"] * 0.03
                - signals["commercial_risk_score"] * 0.03
            ),
            4,
        )

    def _get(self, obj: Dict[str, Any], path: str, default: float = 0.0) -> float:
        cur = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict):
                return default
            cur = cur.get(part)
        try:
            return float(cur or default)
        except Exception:
            return default

    def _get_text(self, obj: Dict[str, Any], path: str, default: str = "") -> str:
        cur = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict):
                return default
            cur = cur.get(part)
        return str(cur or default)

    def _dedupe_dicts(self, items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        deduped = {}
        for item in items:
            deduped[item.get(key, "")] = item
        return list(deduped.values())
