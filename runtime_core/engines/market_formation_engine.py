"""
Market Formation Engine — determines whether a discovered opportunity is merely
a product idea, an expanding category, or an emerging market layer.

Purpose:
- Activate Claire Stage 10: Market Formation Analysis
- Translate trend + market-gap intelligence into category formation logic
- Identify buyer pull, adoption path, ecosystem requirements, market entry
  strategy, and formation risk

This version is deterministic/local. Later versions can plug into live datasets,
TAM/SAM/SOM models, funding history, analyst reports, adoption curves, and
competitive landscapes.
"""

from typing import Any, Dict, List, Optional


class MarketFormationEngine:
    """
    Deterministic market formation analyzer.
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            connector_sources=connector_sources,
        )

        formation_type = self._formation_type(signals, market_gap)
        market_stage = self._market_stage(signals, trend_trajectory)

        category_creation = self._category_creation_score(signals)
        buyer_pull = self._buyer_pull(signals, market_gap)
        adoption_path = self._adoption_path(signals, market_gap, trend_trajectory)
        ecosystem_requirements = self._ecosystem_requirements(signals, market_gap)
        formation_risk = self._formation_risk(signals)
        entry_strategy = self._market_entry_strategy(
            formation_type=formation_type,
            market_stage=market_stage,
            buyer_pull=buyer_pull,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
        )

        return {
            "status": "success",
            "domain": domain,
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
            "formation_type": formation_type,
            "market_stage": market_stage,
            "category_creation_score": category_creation,
            "buyer_pull": buyer_pull,
            "adoption_path": adoption_path,
            "ecosystem_requirements": ecosystem_requirements,
            "market_entry_strategy": entry_strategy,
            "formation_risk": formation_risk,
            "formation_thesis": self._formation_thesis(
                formation_type=formation_type,
                market_stage=market_stage,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                buyer_pull=buyer_pull,
            ),
            "evidence_signals": signals,
            "confidence": self._confidence(signals),
        }

    # =========================
    # SIGNALS
    # =========================
    def _signals(
        self,
        text: str,
        keywords: List[str],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        keyword_blob = " ".join(keywords).lower()
        combined = f"{text} {keyword_blob}"

        market = connector_sources.get("market", {})
        patent = connector_sources.get("patent", {})
        financial = connector_sources.get("financial", {})

        pressure = market_gap.get("strategic_pressure", {}) if isinstance(market_gap, dict) else {}
        pressure_score = pressure.get("score", 0.0) if isinstance(pressure, dict) else 0.0

        trend_direction = trend_trajectory.get("trend_direction", {}) if isinstance(trend_trajectory, dict) else {}
        timing = trend_trajectory.get("timing_pressure", {}) if isinstance(trend_trajectory, dict) else {}
        momentum = trend_trajectory.get("market_momentum", {}) if isinstance(trend_trajectory, dict) else {}
        inevitability = trend_trajectory.get("inevitability_score", {}) if isinstance(trend_trajectory, dict) else {}
        strategic_window = trend_trajectory.get("strategic_window", {}) if isinstance(trend_trajectory, dict) else {}

        category_terms = [
            "platform",
            "system",
            "engine",
            "intelligence",
            "infrastructure",
            "network",
            "marketplace",
            "operating system",
            "command center",
            "system of record",
            "workflow",
        ]

        buyer_pull_terms = [
            "shortage",
            "bottleneck",
            "risk",
            "resilience",
            "capacity",
            "demand",
            "cost",
            "compliance",
            "staffing",
            "liquidity",
            "instability",
            "forecast",
            "predict",
        ]

        ecosystem_terms = [
            "supplier",
            "procurement",
            "manufacturer",
            "logistics",
            "operators",
            "utilities",
            "hospital",
            "asset managers",
            "credit",
            "data",
            "cloud",
            "ERP",
            "automation",
        ]

        wedge_terms = [
            "detects",
            "predicts",
            "maps",
            "forecasts",
            "recommends",
            "identifies",
            "ranks",
            "monitors",
        ]

        def count_terms(terms: List[str]) -> int:
            return sum(1 for term in terms if term.lower() in combined)

        return {
            "category_term_count": count_terms(category_terms),
            "buyer_pull_term_count": count_terms(buyer_pull_terms),
            "ecosystem_term_count": count_terms(ecosystem_terms),
            "wedge_term_count": count_terms(wedge_terms),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": float(pressure_score or 0.0),
            "trend_direction_score": float(trend_direction.get("score", 0.0) or 0.0),
            "timing_pressure_score": float(timing.get("score", 0.0) or 0.0),
            "market_momentum_score": float(momentum.get("score", 0.0) or 0.0),
            "inevitability_score": float(inevitability.get("score", 0.0) or 0.0),
            "strategic_window_score": float(strategic_window.get("score", 0.0) or 0.0),
            "strategic_window": strategic_window.get("window", "unknown"),
            "adoption_position": (
                trend_trajectory.get("adoption_curve_position", {}).get("position", "unknown")
                if isinstance(trend_trajectory, dict)
                else "unknown"
            ),
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "acquirer_category_count": len(market_gap.get("acquirer_categories", [])) if isinstance(market_gap, dict) else 0,
        }

    # =========================
    # OUTPUTS
    # =========================
    def _formation_type(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> Dict[str, Any]:
        sector = signals.get("sector", "general")
        solution_class = market_gap.get("solution_class", "") if isinstance(market_gap, dict) else ""

        platform_score = self._platform_layer_score(signals)
        category_score = self._category_creation_score(signals)["score"]
        ecosystem_score = self._ecosystem_score(signals)

        if platform_score >= 0.78 and ecosystem_score >= 0.55:
            formation = "platform_layer"
        elif category_score >= 0.78 and signals["buyer_pull_term_count"] >= 2:
            formation = "category_expansion"
        elif "infrastructure" in solution_class or sector in {"energy_infrastructure", "defense_autonomy"}:
            formation = "infrastructure_layer"
        elif signals["wedge_term_count"] >= 2:
            formation = "workflow_wedge"
        else:
            formation = "productized_solution"

        return {
            "type": formation,
            "score": round(max(platform_score, category_score, ecosystem_score), 4),
            "sector": sector,
            "rationale": self._formation_type_rationale(formation, signals),
        }

    def _market_stage(
        self,
        signals: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
    ) -> Dict[str, Any]:
        adoption = signals.get("adoption_position", "unknown")
        timing = signals.get("timing_pressure_score", 0.0)
        inevitability = signals.get("inevitability_score", 0.0)

        if adoption in {"early_majority_transition"} or (timing >= 0.82 and inevitability >= 0.82):
            stage = "early_majority_transition"
        elif adoption in {"early_adoption", "rapid_emergence"}:
            stage = "early_adoption"
        elif adoption in {"emerging_market"}:
            stage = "emerging_market"
        elif adoption in {"pre_market_signal"}:
            stage = "pre_market_signal"
        else:
            stage = "formation_unclear"

        return {
            "stage": stage,
            "source_adoption_position": adoption,
            "timing_pressure": round(timing, 4),
            "inevitability": round(inevitability, 4),
        }

    def _category_creation_score(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = min(
            0.96,
            0.22
            + signals["market_gap_confidence"] * 0.20
            + signals["strategic_pressure_score"] * 0.20
            + signals["inevitability_score"] * 0.18
            + signals["market_momentum_score"] * 0.12
            + min(0.12, signals["category_term_count"] * 0.03)
            + min(0.08, signals["buyer_pull_term_count"] * 0.02)
            + min(0.06, signals["ecosystem_term_count"] * 0.015)
        )

        if score >= 0.82:
            level = "high"
        elif score >= 0.65:
            level = "moderate"
        elif score >= 0.48:
            level = "emerging"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(score, 4),
            "drivers": self._category_drivers(signals),
        }

    def _buyer_pull(
        self,
        signals: Dict[str, Any],
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = min(
            0.96,
            0.20
            + signals["strategic_pressure_score"] * 0.28
            + signals["market_gap_confidence"] * 0.18
            + signals["timing_pressure_score"] * 0.16
            + min(0.14, signals["buyer_pull_term_count"] * 0.035)
            + min(0.08, signals["buyer_segment_count"] * 0.015)
        )

        if score >= 0.80:
            strength = "strong"
        elif score >= 0.62:
            strength = "moderate"
        else:
            strength = "weak_or_unproven"

        return {
            "strength": strength,
            "score": round(score, 4),
            "buyer_segments": market_gap.get("buyer_segments", []) if isinstance(market_gap, dict) else [],
            "pull_drivers": self._buyer_pull_drivers(signals, market_gap),
        }

    def _adoption_path(
        self,
        signals: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
    ) -> Dict[str, Any]:
        wedge = self._primary_wedge(signals, market_gap)
        expansion = self._expansion_path(signals, market_gap)
        stage = signals.get("adoption_position", "unknown")

        return {
            "entry_wedge": wedge,
            "adoption_stage": stage,
            "expansion_path": expansion,
            "recommended_motion": self._recommended_motion(signals),
            "scale_requirements": self._scale_requirements(signals, market_gap),
        }

    def _ecosystem_requirements(
        self,
        signals: Dict[str, Any],
        market_gap: Dict[str, Any],
    ) -> List[str]:
        requirements = [
            "validated buyer pain",
            "repeatable data ingestion path",
            "clear workflow integration point",
            "measurable ROI or risk-reduction case",
        ]

        sector = signals.get("sector", "")

        if sector == "industrial_supply_chain":
            requirements.extend([
                "supplier and procurement data access",
                "ERP / planning-system integration",
                "operational risk taxonomy",
                "shortage and bottleneck benchmark dataset",
            ])
        elif sector == "financial_market_intelligence":
            requirements.extend([
                "market data feeds",
                "historical regime datasets",
                "institutional research workflow integration",
                "risk-model validation process",
            ])
        elif sector == "healthcare_operations":
            requirements.extend([
                "hospital operations data access",
                "clinical workflow integration",
                "privacy and compliance review",
                "capacity and staffing validation dataset",
            ])
        elif sector == "energy_infrastructure":
            requirements.extend([
                "grid and demand signal access",
                "utility operations integration",
                "infrastructure asset taxonomy",
                "regional demand validation dataset",
            ])
        elif sector == "defense_autonomy":
            requirements.extend([
                "secure deployment pathway",
                "mission-simulation environment",
                "human override doctrine",
                "edge-operational validation",
            ])

        if signals["acquirer_category_count"] >= 3:
            requirements.append("strategic partner map")

        return sorted(list(dict.fromkeys(requirements)))

    def _market_entry_strategy(
        self,
        formation_type: Dict[str, Any],
        market_stage: Dict[str, Any],
        buyer_pull: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
    ) -> Dict[str, Any]:
        formation = formation_type.get("type", "productized_solution")
        stage = market_stage.get("stage", "formation_unclear")
        pull = buyer_pull.get("strength", "weak_or_unproven")

        if formation in {"platform_layer", "category_expansion"} and pull == "strong":
            strategy = "category-wedge with platform expansion"
        elif formation == "workflow_wedge":
            strategy = "workflow wedge into broader system layer"
        elif formation == "infrastructure_layer":
            strategy = "infrastructure integration with anchor customers"
        else:
            strategy = "focused product validation"

        return {
            "strategy": strategy,
            "market_stage": stage,
            "priority": "high" if pull == "strong" and stage in {"early_adoption", "early_majority_transition"} else "medium",
            "recommended_first_customers": buyer_pull.get("buyer_segments", [])[:3],
            "positioning_angle": self._positioning_angle(market_gap, trend_trajectory),
        }

    def _formation_risk(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        risk = min(
            0.92,
            0.18
            + signals["financial_risk"] * 0.22
            + signals["market_volatility"] * 0.18
            + max(0.0, 0.68 - signals["market_momentum_score"]) * 0.16
            + max(0.0, 0.72 - signals["buyer_pull_term_count"] * 0.16) * 0.10
        )

        if risk >= 0.62:
            level = "high"
        elif risk >= 0.42:
            level = "moderate"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(risk, 4),
            "risk_factors": self._risk_factors(signals),
        }

    def _formation_thesis(
        self,
        formation_type: Dict[str, Any],
        market_stage: Dict[str, Any],
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        buyer_pull: Dict[str, Any],
    ) -> str:
        sector = market_gap.get("sector", "target sector") if isinstance(market_gap, dict) else "target sector"
        needed = market_gap.get("needed_solution", "the needed solution") if isinstance(market_gap, dict) else "the needed solution"

        trend_direction = (
            trend_trajectory.get("trend_direction", {}).get("direction", "forming")
            if isinstance(trend_trajectory, dict)
            else "forming"
        )

        return (
            f"{sector} appears to be forming a {formation_type.get('type')} opportunity. "
            f"The market stage is {market_stage.get('stage')}; buyer pull is {buyer_pull.get('strength')}. "
            f"The trajectory is {trend_direction}, and the needed solution is: {needed}"
        )

    # =========================
    # SCORING HELPERS
    # =========================
    def _platform_layer_score(self, signals: Dict[str, Any]) -> float:
        return min(
            0.96,
            0.18
            + signals["category_term_count"] * 0.035
            + signals["ecosystem_term_count"] * 0.025
            + signals["buyer_segment_count"] * 0.025
            + signals["market_gap_confidence"] * 0.16
            + signals["inevitability_score"] * 0.18
            + signals["timing_pressure_score"] * 0.12
        )

    def _ecosystem_score(self, signals: Dict[str, Any]) -> float:
        return min(
            0.96,
            0.16
            + signals["ecosystem_term_count"] * 0.04
            + signals["buyer_segment_count"] * 0.03
            + signals["acquirer_category_count"] * 0.025
            + signals["market_gap_confidence"] * 0.12
            + signals["market_momentum_score"] * 0.12
        )

    def _confidence(self, signals: Dict[str, Any]) -> float:
        return round(
            min(
                0.96,
                0.24
                + signals["market_gap_confidence"] * 0.22
                + signals["strategic_pressure_score"] * 0.18
                + signals["inevitability_score"] * 0.16
                + signals["timing_pressure_score"] * 0.10
                + min(0.06, signals["buyer_segment_count"] * 0.012)
            ),
            4,
        )

    # =========================
    # TEXT HELPERS
    # =========================
    def _formation_type_rationale(self, formation: str, signals: Dict[str, Any]) -> List[str]:
        rationale = []

        if signals["category_term_count"] > 0:
            rationale.append("category/platform language present")

        if signals["buyer_pull_term_count"] > 0:
            rationale.append("buyer pain/pull signals present")

        if signals["market_gap_confidence"] >= 0.75:
            rationale.append("high-confidence market gap")

        if signals["inevitability_score"] >= 0.75:
            rationale.append("high inevitability trajectory")

        if signals["ecosystem_term_count"] > 0:
            rationale.append("ecosystem participants identifiable")

        if not rationale:
            rationale.append(f"defaulted to {formation}")

        return rationale

    def _category_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []

        if signals["market_gap_confidence"] >= 0.75:
            drivers.append("validated market gap")

        if signals["strategic_pressure_score"] >= 0.70:
            drivers.append("high strategic pressure")

        if signals["inevitability_score"] >= 0.75:
            drivers.append("high inevitability")

        if signals["market_momentum_score"] >= 0.65:
            drivers.append("market momentum")

        if signals["category_term_count"] > 0:
            drivers.append("category/platform language")

        if signals["buyer_pull_term_count"] > 0:
            drivers.append("buyer pain signals")

        return drivers or ["limited category formation evidence"]

    def _buyer_pull_drivers(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> List[str]:
        drivers = []

        pressure = market_gap.get("strategic_pressure", {}) if isinstance(market_gap, dict) else {}
        for driver in pressure.get("drivers", []) if isinstance(pressure, dict) else []:
            drivers.append(driver)

        if signals["timing_pressure_score"] >= 0.75:
            drivers.append("urgent timing pressure")

        if signals["buyer_segment_count"] >= 3:
            drivers.append("multiple buyer segments identified")

        if signals["buyer_pull_term_count"] >= 2:
            drivers.append("buyer pain language repeated")

        return sorted(list(dict.fromkeys(drivers))) or ["buyer pull requires validation"]

    def _primary_wedge(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> str:
        sector = signals.get("sector", "")

        if sector == "industrial_supply_chain":
            return "supplier-risk and shortage forecasting wedge"

        if sector == "financial_market_intelligence":
            return "hidden liquidity / credit-stress signal wedge"

        if sector == "healthcare_operations":
            return "capacity and staffing prediction wedge"

        if sector == "energy_infrastructure":
            return "grid instability and demand-gap forecasting wedge"

        if sector == "defense_autonomy":
            return "mission autonomy and sensor-fusion wedge"

        solution = market_gap.get("solution_class") if isinstance(market_gap, dict) else None
        return solution or "focused intelligence wedge"

    def _expansion_path(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> List[str]:
        sector = signals.get("sector", "")

        paths = {
            "industrial_supply_chain": [
                "supplier-risk graph",
                "shortage forecasting",
                "bottleneck recommendations",
                "procurement and planning command layer",
                "resilience operating system",
            ],
            "financial_market_intelligence": [
                "signal detection",
                "risk and liquidity models",
                "portfolio workflow integration",
                "institutional intelligence platform",
            ],
            "healthcare_operations": [
                "capacity forecasting",
                "staffing risk",
                "patient-flow operations",
                "clinical operations command layer",
            ],
            "energy_infrastructure": [
                "demand-gap forecasting",
                "grid bottleneck detection",
                "resilience planning",
                "utility operations intelligence",
            ],
            "defense_autonomy": [
                "sensor fusion",
                "autonomous decision support",
                "mission simulation",
                "distributed operational layer",
            ],
        }

        return paths.get(sector, ["focused wedge", "workflow expansion", "platform extension"])

    def _recommended_motion(self, signals: Dict[str, Any]) -> str:
        if signals["strategic_window"] == "now":
            return "anchor-customer validation immediately"
        if signals["strategic_window"] == "near_term":
            return "near-term pilot with high-pain buyer segment"
        if signals["buyer_pull_term_count"] >= 2:
            return "pain-driven discovery and pilot design"
        return "evidence gathering and customer discovery"

    def _scale_requirements(self, signals: Dict[str, Any], market_gap: Dict[str, Any]) -> List[str]:
        requirements = [
            "repeatable use case",
            "measurable buyer value",
            "validated implementation path",
        ]

        if signals["category_term_count"] >= 2:
            requirements.append("category narrative")

        if signals["ecosystem_term_count"] >= 2:
            requirements.append("ecosystem integration strategy")

        if signals["buyer_segment_count"] >= 3:
            requirements.append("segmented go-to-market motion")

        return requirements

    def _positioning_angle(
        self,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
    ) -> str:
        solution = market_gap.get("solution_class", "intelligence platform") if isinstance(market_gap, dict) else "intelligence platform"
        window = (
            trend_trajectory.get("strategic_window", {}).get("window", "forming")
            if isinstance(trend_trajectory, dict)
            else "forming"
        )

        return f"Position as a {solution} for a {window} market window."

    def _risk_factors(self, signals: Dict[str, Any]) -> List[str]:
        factors = []

        if signals["financial_risk"] >= 0.45:
            factors.append("financial risk")

        if signals["market_volatility"] >= 0.25:
            factors.append("market volatility")

        if signals["market_momentum_score"] < 0.60:
            factors.append("insufficient market momentum")

        if signals["buyer_pull_term_count"] < 2:
            factors.append("buyer pull needs further proof")

        if not factors:
            factors.append("no major formation risk surfaced")

        return factors
