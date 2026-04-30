"""
Moat Defensibility Engine — evaluates how defensible an opportunity is.

Purpose:
- Activate Claire Stage 11: Moat / Defensibility
- Identify the dominant moat type and supporting moat layers
- Estimate copy risk, compounding assets, vulnerabilities, and recommended
  actions to strengthen defensibility

This version is deterministic/local. Later versions can plug into patent search,
competitive landscape, proprietary datasets, customer data, switching-cost
analysis, integration depth, and live market intelligence.
"""

from typing import Any, Dict, List, Optional


class MoatDefensibilityEngine:
    """
    Deterministic moat and defensibility analyzer.
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        market_formation: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            connector_sources=connector_sources,
        )

        dimensions = self._defensibility_dimensions(signals, market_gap, market_formation)
        moat_type = self._moat_type(signals, dimensions)
        copy_risk = self._copy_risk(signals, dimensions)
        compounding_assets = self._compounding_assets(signals, market_gap, market_formation)
        vulnerabilities = self._vulnerabilities(signals, dimensions, copy_risk)
        strengthening_actions = self._strengthening_actions(signals, moat_type, vulnerabilities)

        return {
            "status": "success",
            "domain": domain,
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
            "moat_type": moat_type,
            "defensibility_dimensions": dimensions,
            "copy_risk": copy_risk,
            "compounding_assets": compounding_assets,
            "vulnerabilities": vulnerabilities,
            "moat_strengthening_actions": strengthening_actions,
            "strategic_defensibility_thesis": self._defensibility_thesis(
                moat_type=moat_type,
                copy_risk=copy_risk,
                market_gap=market_gap,
                market_formation=market_formation,
            ),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, dimensions),
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
        market_formation: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        combined = f"{text} {' '.join(keywords).lower()}"

        market = connector_sources.get("market", {})
        patent = connector_sources.get("patent", {})
        financial = connector_sources.get("financial", {})

        pressure = market_gap.get("strategic_pressure", {}) if isinstance(market_gap, dict) else {}
        pressure_score = pressure.get("score", 0.0) if isinstance(pressure, dict) else 0.0

        trend_inevitability = (
            trend_trajectory.get("inevitability_score", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )
        trend_momentum = (
            trend_trajectory.get("market_momentum", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )
        timing_pressure = (
            trend_trajectory.get("timing_pressure", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )

        category_score = (
            market_formation.get("category_creation_score", {}).get("score", 0.0)
            if isinstance(market_formation, dict)
            else 0.0
        )
        buyer_pull_score = (
            market_formation.get("buyer_pull", {}).get("score", 0.0)
            if isinstance(market_formation, dict)
            else 0.0
        )

        formation_type = (
            market_formation.get("formation_type", {}).get("type", "")
            if isinstance(market_formation, dict)
            else ""
        )

        integration_terms = [
            "erp",
            "integration",
            "workflow",
            "planning-system",
            "planning system",
            "procurement",
            "operations",
            "command layer",
            "system of record",
            "dashboard",
            "api",
        ]

        data_moat_terms = [
            "data",
            "historical",
            "benchmark",
            "supplier",
            "graph",
            "signals",
            "forecasting",
            "model",
            "maps",
            "detects",
            "predicts",
            "risk taxonomy",
            "dataset",
        ]

        network_terms = [
            "network",
            "supplier",
            "suppliers",
            "marketplace",
            "ecosystem",
            "partner",
            "partners",
            "logistics",
            "business networks",
        ]

        ip_terms = [
            "patent",
            "novelty",
            "novel",
            "proprietary",
            "algorithm",
            "model",
            "engine",
            "architecture",
        ]

        switching_terms = [
            "workflow",
            "operations",
            "procurement",
            "planning",
            "system",
            "dashboard",
            "command",
            "integration",
            "embedded",
        ]

        speed_terms = [
            "urgent",
            "near-term",
            "near_term",
            "accelerating",
            "fast",
            "early",
            "first",
            "timing",
            "window",
        ]

        commodity_terms = [
            "generic",
            "simple",
            "basic",
            "dashboard only",
            "search",
            "reporting",
            "thin layer",
        ]

        def count_terms(terms: List[str]) -> int:
            return sum(1 for term in terms if term.lower() in combined)

        return {
            "integration_term_count": count_terms(integration_terms),
            "data_moat_term_count": count_terms(data_moat_terms),
            "network_term_count": count_terms(network_terms),
            "ip_term_count": count_terms(ip_terms),
            "switching_term_count": count_terms(switching_terms),
            "speed_term_count": count_terms(speed_terms),
            "commodity_term_count": count_terms(commodity_terms),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": float(pressure_score or 0.0),
            "trend_inevitability": float(trend_inevitability or 0.0),
            "trend_momentum": float(trend_momentum or 0.0),
            "timing_pressure": float(timing_pressure or 0.0),
            "category_creation_score": float(category_score or 0.0),
            "buyer_pull_score": float(buyer_pull_score or 0.0),
            "formation_type": formation_type,
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "acquirer_category_count": len(market_gap.get("acquirer_categories", [])) if isinstance(market_gap, dict) else 0,
            "ecosystem_requirement_count": len(market_formation.get("ecosystem_requirements", [])) if isinstance(market_formation, dict) else 0,
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
        }

    # =========================
    # OUTPUTS
    # =========================
    def _defensibility_dimensions(
        self,
        signals: Dict[str, Any],
        market_gap: Dict[str, Any],
        market_formation: Dict[str, Any],
    ) -> Dict[str, Any]:
        data_advantage = self._score_dimension(
            base=0.24,
            terms=signals["data_moat_term_count"],
            term_weight=0.035,
            primary=signals["market_gap_confidence"],
            primary_weight=0.18,
            secondary=signals["patent_novelty"],
            secondary_weight=0.12,
            cap=0.96,
        )

        workflow_lock_in = self._score_dimension(
            base=0.20,
            terms=signals["switching_term_count"] + signals["integration_term_count"],
            term_weight=0.025,
            primary=signals["buyer_pull_score"],
            primary_weight=0.18,
            secondary=signals["strategic_pressure_score"],
            secondary_weight=0.14,
            cap=0.95,
        )

        integration_depth = self._score_dimension(
            base=0.18,
            terms=signals["integration_term_count"],
            term_weight=0.04,
            primary=signals["ecosystem_requirement_count"] / 10.0,
            primary_weight=0.20,
            secondary=signals["buyer_pull_score"],
            secondary_weight=0.12,
            cap=0.95,
        )

        network_effects = self._score_dimension(
            base=0.14,
            terms=signals["network_term_count"],
            term_weight=0.035,
            primary=signals["buyer_segment_count"] / 6.0,
            primary_weight=0.16,
            secondary=signals["acquirer_category_count"] / 6.0,
            secondary_weight=0.10,
            cap=0.90,
        )

        ip_position = self._score_dimension(
            base=0.18,
            terms=signals["ip_term_count"],
            term_weight=0.025,
            primary=signals["patent_activity"],
            primary_weight=0.16,
            secondary=signals["patent_novelty"],
            secondary_weight=0.18,
            cap=0.94,
        )

        category_position = self._score_dimension(
            base=0.20,
            terms=signals["speed_term_count"],
            term_weight=0.025,
            primary=signals["category_creation_score"],
            primary_weight=0.22,
            secondary=signals["trend_inevitability"],
            secondary_weight=0.16,
            cap=0.96,
        )

        speed_advantage = self._score_dimension(
            base=0.18,
            terms=signals["speed_term_count"],
            term_weight=0.03,
            primary=signals["timing_pressure"],
            primary_weight=0.18,
            secondary=signals["trend_momentum"],
            secondary_weight=0.14,
            cap=0.92,
        )

        dimensions = {
            "data_advantage": self._dimension_payload(data_advantage, "proprietary data, signal history, taxonomies, and learned models"),
            "workflow_lock_in": self._dimension_payload(workflow_lock_in, "embedding into recurring buyer workflows"),
            "integration_depth": self._dimension_payload(integration_depth, "depth of integration into systems of record and operational tools"),
            "network_effects": self._dimension_payload(network_effects, "value expansion across users, suppliers, partners, or ecosystem participants"),
            "ip_position": self._dimension_payload(ip_position, "technical novelty, protected methods, and algorithmic differentiation"),
            "category_position": self._dimension_payload(category_position, "ability to define and own a market/category narrative"),
            "speed_advantage": self._dimension_payload(speed_advantage, "timing, execution speed, and early market capture"),
        }

        return dimensions

    def _moat_type(self, signals: Dict[str, Any], dimensions: Dict[str, Any]) -> Dict[str, Any]:
        scores = {name: payload["score"] for name, payload in dimensions.items()}
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)

        primary = ranked[0][0]
        secondaries = [name for name, score in ranked[1:4] if score >= 0.62]

        weighted_score = min(
            0.97,
            ranked[0][1] * 0.36
            + ranked[1][1] * 0.22
            + ranked[2][1] * 0.16
            + signals["category_creation_score"] * 0.10
            + signals["buyer_pull_score"] * 0.08
            + signals["trend_inevitability"] * 0.08
        )

        if weighted_score >= 0.82:
            strength = "strong"
        elif weighted_score >= 0.65:
            strength = "moderate"
        elif weighted_score >= 0.48:
            strength = "emerging"
        else:
            strength = "weak"

        return {
            "primary_moat": primary,
            "secondary_moats": secondaries,
            "moat_score": round(weighted_score, 4),
            "strength": strength,
            "ranked_dimensions": [
                {"dimension": name, "score": round(score, 4)}
                for name, score in ranked
            ],
            "rationale": self._moat_rationale(primary, secondaries, signals),
        }

    def _copy_risk(self, signals: Dict[str, Any], dimensions: Dict[str, Any]) -> Dict[str, Any]:
        average_dimension = sum(payload["score"] for payload in dimensions.values()) / max(1, len(dimensions))

        risk = min(
            0.94,
            0.54
            - average_dimension * 0.28
            - signals["integration_term_count"] * 0.015
            - signals["data_moat_term_count"] * 0.010
            + signals["commodity_term_count"] * 0.08
            + signals["market_volatility"] * 0.10
            + signals["financial_risk"] * 0.08
        )

        risk = max(0.08, risk)

        if risk >= 0.62:
            level = "high"
        elif risk >= 0.42:
            level = "moderate"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(risk, 4),
            "copy_vectors": self._copy_vectors(signals, dimensions),
        }

    def _compounding_assets(
        self,
        signals: Dict[str, Any],
        market_gap: Dict[str, Any],
        market_formation: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        assets = []

        sector = signals.get("sector", "general")

        if signals["data_moat_term_count"] > 0 or sector == "industrial_supply_chain":
            assets.append({
                "asset": "proprietary operational dataset",
                "why_it_compounds": "Each run can improve shortage, bottleneck, supplier-risk, and resilience models.",
                "priority": "high",
            })

        if signals["integration_term_count"] > 0:
            assets.append({
                "asset": "workflow integration footprint",
                "why_it_compounds": "Operational embedding increases switching costs and improves context quality.",
                "priority": "high",
            })

        if signals["network_term_count"] > 0:
            assets.append({
                "asset": "ecosystem graph",
                "why_it_compounds": "Supplier, buyer, partner, or operational-network relationships become more valuable as coverage expands.",
                "priority": "medium",
            })

        if signals["category_creation_score"] >= 0.75:
            assets.append({
                "asset": "category narrative and positioning",
                "why_it_compounds": "Early category framing can shape buyer expectations and strategic acquirer perception.",
                "priority": "medium",
            })

        if signals["patent_novelty"] >= 0.55:
            assets.append({
                "asset": "technical novelty layer",
                "why_it_compounds": "Novel methods can support IP, differentiation, or proprietary implementation paths.",
                "priority": "medium",
            })

        if not assets:
            assets.append({
                "asset": "validated buyer insight",
                "why_it_compounds": "Repeated buyer validation can create sharper product and positioning decisions.",
                "priority": "medium",
            })

        return assets

    def _vulnerabilities(
        self,
        signals: Dict[str, Any],
        dimensions: Dict[str, Any],
        copy_risk: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if dimensions["data_advantage"]["score"] < 0.65:
            vulnerabilities.append({
                "vulnerability": "data advantage not yet deep enough",
                "impact": "competitors may replicate surface-level outputs",
                "severity": "medium",
            })

        if dimensions["integration_depth"]["score"] < 0.62:
            vulnerabilities.append({
                "vulnerability": "integration moat is not yet proven",
                "impact": "solution may remain a replaceable analytics layer",
                "severity": "medium",
            })

        if dimensions["network_effects"]["score"] < 0.55:
            vulnerabilities.append({
                "vulnerability": "network effects are weak or indirect",
                "impact": "value may not compound quickly across ecosystem participants",
                "severity": "low",
            })

        if signals["commodity_term_count"] > 0 or copy_risk.get("level") == "high":
            vulnerabilities.append({
                "vulnerability": "copy risk from generic AI/platform competitors",
                "impact": "large incumbents could imitate features if no proprietary data or workflow depth exists",
                "severity": "high" if copy_risk.get("level") == "high" else "medium",
            })

        if not vulnerabilities:
            vulnerabilities.append({
                "vulnerability": "no major moat vulnerability surfaced in deterministic analysis",
                "impact": "continue validation against live competitors and buyer workflows",
                "severity": "low",
            })

        return vulnerabilities

    def _strengthening_actions(
        self,
        signals: Dict[str, Any],
        moat_type: Dict[str, Any],
        vulnerabilities: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        actions = [
            {
                "action": "build proprietary data loops",
                "purpose": "ensure every customer interaction improves prediction, recommendations, and risk intelligence",
                "priority": "high",
            },
            {
                "action": "embed into operational workflow",
                "purpose": "increase switching costs and make the system part of recurring decisions",
                "priority": "high",
            },
            {
                "action": "define category narrative early",
                "purpose": "shape market language around the platform-layer opportunity",
                "priority": "medium",
            },
        ]

        primary = moat_type.get("primary_moat")

        if primary == "integration_depth":
            actions.append({
                "action": "prioritize ERP / system-of-record integrations",
                "purpose": "turn product usage into infrastructure dependency",
                "priority": "high",
            })

        if primary == "data_advantage":
            actions.append({
                "action": "create benchmark datasets and taxonomies",
                "purpose": "make the intelligence layer hard to recreate without proprietary signal history",
                "priority": "high",
            })

        if primary == "network_effects":
            actions.append({
                "action": "map multi-sided ecosystem participation",
                "purpose": "increase value as more suppliers, buyers, partners, or operators join",
                "priority": "medium",
            })

        if any(v.get("severity") == "high" for v in vulnerabilities):
            actions.append({
                "action": "de-risk direct imitation",
                "purpose": "identify which features are commodity and wrap them with data, workflow, and integration advantages",
                "priority": "high",
            })

        return actions

    def _defensibility_thesis(
        self,
        moat_type: Dict[str, Any],
        copy_risk: Dict[str, Any],
        market_gap: Dict[str, Any],
        market_formation: Dict[str, Any],
    ) -> str:
        sector = market_gap.get("sector", "target sector") if isinstance(market_gap, dict) else "target sector"
        primary = moat_type.get("primary_moat", "emerging moat")
        strength = moat_type.get("strength", "emerging")
        risk = copy_risk.get("level", "unknown")

        formation = (
            market_formation.get("formation_type", {}).get("type", "market opportunity")
            if isinstance(market_formation, dict)
            else "market opportunity"
        )

        return (
            f"{sector} shows a {strength} defensibility profile led by {primary}. "
            f"The opportunity is forming as a {formation}, with {risk} copy risk. "
            f"Defensibility should be strengthened through proprietary data loops, workflow embedding, "
            f"and integration depth."
        )

    # =========================
    # HELPERS
    # =========================
    def _score_dimension(
        self,
        base: float,
        terms: int,
        term_weight: float,
        primary: float,
        primary_weight: float,
        secondary: float,
        secondary_weight: float,
        cap: float,
    ) -> float:
        return round(
            min(
                cap,
                base
                + min(0.20, terms * term_weight)
                + min(0.25, primary * primary_weight)
                + min(0.20, secondary * secondary_weight),
            ),
            4,
        )

    def _dimension_payload(self, score: float, description: str) -> Dict[str, Any]:
        if score >= 0.78:
            level = "strong"
        elif score >= 0.62:
            level = "moderate"
        elif score >= 0.45:
            level = "emerging"
        else:
            level = "weak"

        return {
            "level": level,
            "score": score,
            "description": description,
        }

    def _moat_rationale(
        self,
        primary: str,
        secondaries: List[str],
        signals: Dict[str, Any],
    ) -> List[str]:
        rationale = [f"primary moat signal: {primary}"]

        if secondaries:
            rationale.append(f"supporting moat layers: {', '.join(secondaries)}")

        if signals["market_gap_confidence"] >= 0.75:
            rationale.append("high-confidence market gap supports defensibility")

        if signals["category_creation_score"] >= 0.75:
            rationale.append("category creation strengthens market position")

        if signals["buyer_pull_score"] >= 0.75:
            rationale.append("strong buyer pull supports workflow embedding")

        if signals["patent_novelty"] >= 0.55:
            rationale.append("technical novelty supports differentiation")

        return rationale

    def _copy_vectors(self, signals: Dict[str, Any], dimensions: Dict[str, Any]) -> List[str]:
        vectors = []

        if dimensions["data_advantage"]["score"] < 0.65:
            vectors.append("generic AI competitors could imitate surface-level analytics")

        if dimensions["integration_depth"]["score"] < 0.62:
            vectors.append("incumbent platforms could bundle similar features")

        if dimensions["ip_position"]["score"] < 0.60:
            vectors.append("technical implementation may be copied without stronger IP or proprietary process")

        if signals["category_creation_score"] >= 0.75:
            vectors.append("category attractiveness may invite fast followers")

        if not vectors:
            vectors.append("copy risk appears limited if proprietary data and workflow depth are executed")

        return vectors

    def _confidence(self, signals: Dict[str, Any], dimensions: Dict[str, Any]) -> float:
        dimension_avg = sum(payload["score"] for payload in dimensions.values()) / max(1, len(dimensions))

        return round(
            min(
                0.96,
                0.24
                + dimension_avg * 0.30
                + signals["market_gap_confidence"] * 0.16
                + signals["category_creation_score"] * 0.12
                + signals["buyer_pull_score"] * 0.08
                + signals["patent_activity"] * 0.06
            ),
            4,
        )
