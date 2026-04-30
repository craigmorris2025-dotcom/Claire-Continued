"""
Market Gap Engine — detects sector gaps, industry bottlenecks,
needed solutions, buyer segments, and strategic pressure signals.

Purpose:
- Move Claire beyond keyword scoring
- Identify what is missing in a market / sector / industry
- Translate gaps into needed solution classes
- Feed design, portfolio, and later acquirer discovery
"""

from typing import Any, Dict, List, Optional


class MarketGapEngine:
    """
    Deterministic market / sector gap analyzer.

    This is not a search engine.
    It maps input signals into:
    - sector profile
    - market gap
    - needed solution
    - buyer segment
    - strategic pressure
    - design implications
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        connector_sources = connector_sources or {}

        profile = self._detect_profile(text=text, keywords=keywords)
        pressure = self._strategic_pressure(
            text=text,
            profile=profile,
            connector_sources=connector_sources,
        )

        return {
            "status": "success",
            "domain": domain,
            "sector": profile["sector"],
            "industry_context": profile["industry_context"],
            "gap_type": profile["gap_type"],
            "market_gap": profile["market_gap"],
            "needed_solution": profile["needed_solution"],
            "solution_class": profile["solution_class"],
            "buyer_segments": profile["buyer_segments"],
            "strategic_pressure": pressure,
            "design_implications": profile["design_implications"],
            "portfolio_relevance": self._portfolio_relevance(profile, pressure),
            "acquirer_categories": profile["acquirer_categories"],
            "confidence": self._confidence(profile, pressure),
        }

    # =========================
    # PROFILE DETECTION
    # =========================
    def _detect_profile(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        profiles = self._profiles()

        best_name = "general_market_intelligence"
        best_score = 0

        keyword_text = " ".join(keywords).lower()
        combined = f"{text} {keyword_text}"

        for name, profile in profiles.items():
            score = 0

            for trigger in profile["triggers"]:
                if trigger in combined:
                    score += 2 if " " in trigger else 1

            for strong_trigger in profile.get("strong_triggers", []):
                if strong_trigger in combined:
                    score += 3

            if score > best_score:
                best_score = score
                best_name = name

        selected = dict(profiles[best_name])
        selected["profile"] = best_name
        selected["match_strength"] = best_score

        return selected

    def _profiles(self) -> Dict[str, Dict[str, Any]]:
        return {
            "industrial_supply_chain": {
                "sector": "industrial_supply_chain",
                "industry_context": "manufacturing, logistics, supplier networks, industrial operations",
                "triggers": [
                    "supply",
                    "chain",
                    "supply chain",
                    "supplier",
                    "suppliers",
                    "manufacturing",
                    "component",
                    "components",
                    "shortage",
                    "shortages",
                    "bottleneck",
                    "bottlenecks",
                    "logistics",
                    "resilience",
                ],
                "strong_triggers": [
                    "component shortages",
                    "supplier risk",
                    "manufacturing resilience",
                    "supply chain intelligence",
                ],
                "gap_type": "visibility / resilience / bottleneck detection",
                "market_gap": "Industrial operators lack early-warning intelligence for supplier risk, component shortages, and hidden bottlenecks.",
                "needed_solution": "Predictive supply-chain intelligence that detects bottlenecks, maps supplier exposure, forecasts shortages, and recommends resilience actions.",
                "solution_class": "predictive industrial intelligence platform",
                "buyer_segments": [
                    "manufacturers",
                    "logistics networks",
                    "industrial operators",
                    "procurement teams",
                    "supply chain risk teams",
                ],
                "design_implications": [
                    "supplier-risk graph",
                    "shortage forecasting model",
                    "bottleneck detection engine",
                    "resilience recommendation layer",
                    "operations dashboard",
                ],
                "acquirer_categories": [
                    "industrial software",
                    "ERP platforms",
                    "automation companies",
                    "supply-chain platforms",
                    "cloud data platforms",
                ],
            },
            "financial_market_intelligence": {
                "sector": "financial_market_intelligence",
                "industry_context": "capital markets, credit, liquidity, institutional finance, risk intelligence",
                "triggers": [
                    "financial",
                    "market",
                    "liquidity",
                    "credit",
                    "stress",
                    "sector rotations",
                    "capital",
                    "reprices",
                    "institutional",
                    "risk",
                    "opportunities",
                ],
                "strong_triggers": [
                    "hidden liquidity gaps",
                    "credit stress signals",
                    "institutional capital",
                    "market intelligence",
                ],
                "gap_type": "hidden signal / repricing opportunity",
                "market_gap": "Financial markets contain weak signals that appear before capital reprices risk, liquidity, and sector rotation.",
                "needed_solution": "Signal intelligence system that detects hidden liquidity gaps, credit stress, and overlooked repricing opportunities.",
                "solution_class": "financial signal intelligence platform",
                "buyer_segments": [
                    "asset managers",
                    "hedge funds",
                    "credit funds",
                    "risk teams",
                    "institutional research desks",
                ],
                "design_implications": [
                    "market signal ingestion",
                    "historical regime modeling",
                    "credit stress detector",
                    "liquidity gap model",
                    "opportunity ranking engine",
                ],
                "acquirer_categories": [
                    "financial data platforms",
                    "risk analytics companies",
                    "market intelligence providers",
                    "asset-management technology platforms",
                ],
            },
            "healthcare_operations": {
                "sector": "healthcare_operations",
                "industry_context": "hospital operations, care delivery, staffing, capacity management",
                "triggers": [
                    "health",
                    "healthcare",
                    "clinical",
                    "hospital",
                    "patient",
                    "care",
                    "staffing",
                    "capacity",
                    "outcomes",
                    "operations",
                ],
                "strong_triggers": [
                    "hospital capacity gaps",
                    "care delivery bottlenecks",
                    "staffing shortages",
                    "patient outcomes",
                ],
                "gap_type": "capacity / operations / care delivery bottleneck",
                "market_gap": "Healthcare operators often react to capacity and staffing issues after patient risk has already increased.",
                "needed_solution": "Predictive clinical operations platform that forecasts capacity gaps, staffing shortages, and care bottlenecks before outcomes degrade.",
                "solution_class": "healthcare operations intelligence platform",
                "buyer_segments": [
                    "hospital systems",
                    "clinical operations teams",
                    "care coordination teams",
                    "healthcare administrators",
                ],
                "design_implications": [
                    "capacity forecasting model",
                    "staffing risk detector",
                    "care bottleneck mapper",
                    "patient-flow intelligence layer",
                    "operations command dashboard",
                ],
                "acquirer_categories": [
                    "healthcare software platforms",
                    "hospital IT companies",
                    "clinical analytics providers",
                    "healthcare operations vendors",
                ],
            },
            "energy_infrastructure": {
                "sector": "energy_infrastructure",
                "industry_context": "utilities, grid operations, energy infrastructure, regional power demand",
                "triggers": [
                    "energy",
                    "grid",
                    "power",
                    "utilities",
                    "transformer",
                    "transmission",
                    "demand",
                    "instability",
                    "infrastructure",
                    "resilience",
                ],
                "strong_triggers": [
                    "grid instability patterns",
                    "regional power demand gaps",
                    "transmission bottlenecks",
                    "energy infrastructure",
                ],
                "gap_type": "infrastructure resilience / demand forecasting / bottleneck detection",
                "market_gap": "Utilities need earlier detection of grid instability, demand gaps, and infrastructure bottlenecks.",
                "needed_solution": "AI-enabled infrastructure intelligence platform that forecasts demand, detects grid instability, and recommends resilience upgrades.",
                "solution_class": "energy infrastructure resilience platform",
                "buyer_segments": [
                    "utilities",
                    "grid operators",
                    "energy infrastructure companies",
                    "regional planning authorities",
                ],
                "design_implications": [
                    "grid signal ingestion",
                    "demand forecasting model",
                    "infrastructure bottleneck detector",
                    "resilience planning engine",
                    "utility dashboard",
                ],
                "acquirer_categories": [
                    "energy software companies",
                    "industrial automation companies",
                    "utility technology vendors",
                    "infrastructure analytics providers",
                ],
            },
            "defense_autonomy": {
                "sector": "defense_autonomy",
                "industry_context": "defense, autonomous systems, drones, battlefield intelligence",
                "triggers": [
                    "defense",
                    "battlefield",
                    "drone",
                    "drones",
                    "swarm",
                    "autonomous",
                    "sensor",
                    "fusion",
                    "edge",
                    "mission",
                ],
                "strong_triggers": [
                    "autonomous swarm",
                    "sensor fusion",
                    "battlefield learning",
                    "drone defense",
                ],
                "gap_type": "mission autonomy / low-latency decision / distributed coordination",
                "market_gap": "Defense operators need resilient autonomous systems capable of acting under degraded communications and fast-changing mission conditions.",
                "needed_solution": "Distributed autonomous decision platform for drones, sensors, and battlefield intelligence systems.",
                "solution_class": "autonomous defense intelligence platform",
                "buyer_segments": [
                    "defense primes",
                    "defense technology companies",
                    "government agencies",
                    "military operators",
                ],
                "design_implications": [
                    "edge runtime",
                    "sensor fusion layer",
                    "autonomous decision engine",
                    "mission-context isolation",
                    "human override framework",
                ],
                "acquirer_categories": [
                    "defense primes",
                    "defense technology companies",
                    "aerospace companies",
                    "government technology providers",
                ],
            },
            "general_market_intelligence": {
                "sector": "general_market_intelligence",
                "industry_context": "cross-sector market intelligence and opportunity discovery",
                "triggers": [
                    "market",
                    "industry",
                    "sector",
                    "gap",
                    "gaps",
                    "demand",
                    "trend",
                    "historical",
                    "opportunity",
                    "needed",
                    "solution",
                ],
                "strong_triggers": [
                    "industry gaps",
                    "market trajectories",
                    "unmet enterprise demand",
                    "needed solutions",
                ],
                "gap_type": "cross-sector opportunity / unmet demand / inefficient market structure",
                "market_gap": "Many industries contain unmet demand and inefficient workflows that are visible only through cross-signal trend analysis.",
                "needed_solution": "Market intelligence engine that detects sector gaps, ranks needed solutions, and identifies timing-based opportunities.",
                "solution_class": "cross-sector opportunity intelligence platform",
                "buyer_segments": [
                    "corporate strategy teams",
                    "venture studios",
                    "private equity teams",
                    "innovation groups",
                    "product strategy teams",
                ],
                "design_implications": [
                    "trend ingestion",
                    "gap detection model",
                    "needed-solution mapper",
                    "opportunity scoring layer",
                    "portfolio prioritization dashboard",
                ],
                "acquirer_categories": [
                    "enterprise software companies",
                    "strategy platforms",
                    "data intelligence companies",
                    "innovation platforms",
                ],
            },
        }

    # =========================
    # SCORING / PRESSURE
    # =========================
    def _strategic_pressure(
        self,
        text: str,
        profile: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        market = connector_sources.get("market", {})
        patent = connector_sources.get("patent", {})
        financial = connector_sources.get("financial", {})

        pressure_score = 0.45

        if profile.get("match_strength", 0) >= 4:
            pressure_score += 0.15

        if "shortage" in text or "bottleneck" in text or "gap" in text:
            pressure_score += 0.10

        if "regulatory" in text or "risk" in text or "resilience" in text:
            pressure_score += 0.08

        pressure_score += min(0.10, float(market.get("growth", 0.0)) * 0.25)
        pressure_score += min(0.10, float(patent.get("activity", 0.0)) * 0.10)
        pressure_score += min(0.06, float(financial.get("health", 0.0)) * 0.05)

        pressure_score = round(min(0.95, pressure_score), 4)

        if pressure_score >= 0.75:
            level = "high"
        elif pressure_score >= 0.55:
            level = "moderate"
        else:
            level = "emerging"

        return {
            "level": level,
            "score": pressure_score,
            "drivers": self._pressure_drivers(text, profile),
        }

    def _pressure_drivers(self, text: str, profile: Dict[str, Any]) -> List[str]:
        drivers = []

        if "shortage" in text or "shortages" in text:
            drivers.append("shortage exposure")

        if "bottleneck" in text or "bottlenecks" in text:
            drivers.append("operational bottlenecks")

        if "risk" in text:
            drivers.append("risk concentration")

        if "regulatory" in text:
            drivers.append("regulatory pressure")

        if "resilience" in text:
            drivers.append("resilience requirement")

        if "demand" in text:
            drivers.append("demand pressure")

        if not drivers:
            drivers.append(profile.get("gap_type", "market pressure"))

        return drivers

    def _portfolio_relevance(
        self,
        profile: Dict[str, Any],
        pressure: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = pressure.get("score", 0.0)

        if score >= 0.75:
            priority = "high"
        elif score >= 0.55:
            priority = "medium"
        else:
            priority = "watchlist"

        return {
            "priority": priority,
            "why_it_matters": profile["market_gap"],
            "portfolio_angle": profile["needed_solution"],
        }

    def _confidence(
        self,
        profile: Dict[str, Any],
        pressure: Dict[str, Any],
    ) -> float:
        match_strength = min(1.0, profile.get("match_strength", 0) / 8.0)
        pressure_score = pressure.get("score", 0.0)

        return round((match_strength * 0.55) + (pressure_score * 0.45), 4)
