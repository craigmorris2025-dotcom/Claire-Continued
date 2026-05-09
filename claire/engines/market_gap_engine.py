"""
Market Gap Engine — sector-aware gap, needed-solution, buyer, and acquirer-category mapping.

Regex sector routing hotfix:
- Uses plain normalized word/phrase matching instead of regex word boundaries.
- Forces upstream domain == "insurance" into climate_insurance.
- Prevents false generic routing for climate insurance inputs.
"""

from typing import Any, Dict, List, Optional


class MarketGapEngine:
    """
    Deterministic market / sector / industry gap mapper.
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = text or ""
        keywords = keywords or []
        connector_sources = connector_sources or {}

        sector = self._detect_sector(text=text, domain=domain, keywords=keywords)
        profile = self._sector_profile(sector)

        market = connector_sources.get("market", {})
        patent = connector_sources.get("patent", {})
        financial = connector_sources.get("financial", {})

        pressure = self._strategic_pressure(
            text=text,
            keywords=keywords,
            sector=sector,
            market=market,
            financial=financial,
        )

        confidence = self._confidence(
            text=text,
            keywords=keywords,
            sector=sector,
            pressure_score=pressure["score"],
            patent_activity=float(patent.get("activity", 0.0) or 0.0),
        )

        return {
            "status": "success",
            "domain": self._domain_for_sector(sector, domain),
            "sector": sector,
            "industry_context": profile["industry_context"],
            "gap_type": profile["gap_type"],
            "market_gap": profile["market_gap"],
            "needed_solution": profile["needed_solution"],
            "solution_class": profile["solution_class"],
            "buyer_segments": profile["buyer_segments"],
            "strategic_pressure": pressure,
            "design_implications": profile["design_implications"],
            "portfolio_relevance": {
                "priority": "high" if confidence >= 0.70 else "medium",
                "why_it_matters": profile["market_gap"],
                "portfolio_angle": profile["needed_solution"],
            },
            "acquirer_categories": profile["acquirer_categories"],
            "confidence": confidence,
        }

    # =========================
    # PLAIN-TEXT ROUTING HELPERS
    # =========================
    def _normalize_text(self, text: str) -> str:
        chars = []
        for ch in (text or "").lower():
            if ch.isalnum():
                chars.append(ch)
            else:
                chars.append(" ")
        return " ".join("".join(chars).split())

    def _routing_view(self, text: str, keywords: Optional[List[str]] = None) -> str:
        return self._normalize_text(f"{text or ''} {' '.join(keywords or [])}")

    def _contains_word(self, routing_text: str, word: str) -> bool:
        return word.lower() in routing_text.split()

    def _contains_phrase(self, routing_text: str, phrase: str) -> bool:
        phrase = self._normalize_text(phrase).strip()
        return f" {phrase} " in f" {routing_text} "

    def _has_any_words(self, routing_text: str, words: List[str]) -> bool:
        return any(self._contains_word(routing_text, word) for word in words)

    def _has_any_phrases(self, routing_text: str, phrases: List[str]) -> bool:
        return any(self._contains_phrase(routing_text, phrase) for phrase in phrases)

    # =========================
    # SECTOR DETECTION
    # =========================
    def _detect_sector(self, text: str, domain: str, keywords: List[str]) -> str:
        routing = self._routing_view(text, keywords)
        domain = (domain or "").lower()

        # Critical hotfix: if the upstream router already identified insurance,
        # do not fall back to general_intelligence.
        if domain == "insurance":
            return "climate_insurance"

        if self._has_any_phrases(routing, [
            "climate insurance",
            "weather losses",
            "historical weather losses",
            "climate exposure",
            "regional climate exposure",
            "property risk",
            "property and infrastructure risk",
            "risk concentration",
            "risk transfer",
            "risk transfer countermeasures",
            "premium repricing",
            "insurance repricing",
            "market withdrawal",
            "catastrophe model",
            "cat model",
            "exposure benchmark",
            "exposure benchmarks",
        ]) or self._has_any_words(routing, [
            "insurance",
            "insurer",
            "insurers",
            "reinsurance",
            "reinsurer",
            "reinsurers",
            "underwriting",
            "underwriter",
            "underwriters",
            "catastrophe",
            "actuarial",
            "claims",
            "policyholder",
            "broker",
            "brokers",
        ]):
            return "climate_insurance"

        if self._has_any_phrases(routing, [
            "secure command",
            "command system",
            "command systems",
            "battlefield sensor",
            "battlefield sensors",
            "mission risk",
            "mission countermeasure",
            "mission countermeasures",
            "drone coordination",
            "border security",
        ]) or self._has_any_words(routing, [
            "defense",
            "military",
            "battlefield",
            "mission",
            "drone",
            "drones",
            "uav",
            "surveillance",
            "autonomy",
            "autonomous",
        ]):
            return "defense_autonomy"

        if self._has_any_phrases(routing, [
            "health system",
            "health systems",
            "patient flow",
            "patient flow bottlenecks",
            "care delivery",
            "staffing shortage",
            "staffing shortages",
            "clinical workflow",
            "hospital capacity",
        ]) or self._has_any_words(routing, [
            "healthcare",
            "hospital",
            "hospitals",
            "patient",
            "patients",
            "clinical",
            "medical",
            "clinician",
            "clinicians",
        ]):
            return "healthcare_operations"

        if self._has_any_phrases(routing, [
            "supply chain",
            "component shortage",
            "component shortages",
            "planning system",
            "planning systems",
            "production failure",
            "production failures",
            "supplier dependency",
            "supplier dependencies",
        ]) or self._has_any_words(routing, [
            "manufacturing",
            "industrial",
            "supplier",
            "suppliers",
            "erp",
            "procurement",
            "production",
            "factory",
            "factories",
        ]):
            return "industrial_supply_chain"

        if self._has_any_phrases(routing, [
            "power grid",
            "power system",
            "power systems",
            "power demand",
            "electric infrastructure",
            "grid instability",
            "transmission bottleneck",
            "transmission bottlenecks",
            "utility operations",
        ]) or self._has_any_words(routing, [
            "energy",
            "grid",
            "utility",
            "utilities",
            "transmission",
        ]):
            return "energy_infrastructure"

        if self._has_any_phrases(routing, [
            "capital market",
            "capital markets",
            "asset manager",
            "asset managers",
            "institutional research",
            "financial market",
            "financial markets",
            "market intelligence",
            "credit stress",
            "liquidity deterioration",
        ]) or self._has_any_words(routing, [
            "finance",
            "financial",
            "credit",
            "liquidity",
            "portfolio",
            "portfolios",
            "asset",
            "assets",
            "equities",
            "bonds",
        ]):
            return "financial_market_intelligence"

        return "general_intelligence"

    # =========================
    # SECTOR PROFILES
    # =========================
    def _sector_profile(self, sector: str) -> Dict[str, Any]:
        profiles = {
            "climate_insurance": {
                "industry_context": "insurance, reinsurance, underwriting, catastrophe risk, property exposure, climate risk transfer",
                "gap_type": "climate exposure / underwriting repricing / market withdrawal",
                "market_gap": "Insurers and reinsurers face accelerating climate exposure, property-risk concentration, pricing uncertainty, and withdrawal pressure before underwriting systems fully adapt.",
                "needed_solution": "Climate insurance risk intelligence platform that detects exposure concentration, forecasts repricing pressure, and supports underwriting, risk-transfer, and portfolio countermeasures.",
                "solution_class": "climate insurance risk intelligence platform",
                "buyer_segments": [
                    "insurers",
                    "reinsurers",
                    "underwriting teams",
                    "catastrophe-risk teams",
                    "property risk carriers",
                    "insurance brokers",
                    "public risk pools",
                ],
                "design_implications": [
                    "weather loss ingestion",
                    "property exposure model",
                    "catastrophe scenario engine",
                    "underwriting repricing detector",
                    "market withdrawal risk map",
                    "risk-transfer recommendation layer",
                ],
                "acquirer_categories": [
                    "insurance analytics platforms",
                    "catastrophe modeling companies",
                    "reinsurers",
                    "risk data providers",
                    "climate risk intelligence companies",
                    "insurance core software platforms",
                    "insurance brokers",
                ],
            },
            "defense_autonomy": {
                "industry_context": "defense technology, autonomous systems, mission intelligence, secure command, aerospace",
                "gap_type": "mission autonomy / low-latency decision / distributed coordination",
                "market_gap": "Defense operators need secure, human-reviewed autonomy and mission intelligence under contested, low-latency conditions.",
                "needed_solution": "Distributed autonomous decision platform with secure command integration, simulation data, auditability, and human override controls.",
                "solution_class": "distributed autonomous decision platform",
                "buyer_segments": [
                    "defense primes",
                    "defense technology companies",
                    "aerospace programs",
                    "government mission teams",
                ],
                "design_implications": [
                    "secure command integration",
                    "mission simulation datasets",
                    "human override layer",
                    "edge decision engine",
                    "audit trail",
                ],
                "acquirer_categories": [
                    "defense primes",
                    "defense technology companies",
                    "aerospace companies",
                    "secure command platforms",
                ],
            },
            "healthcare_operations": {
                "industry_context": "health systems, hospital operations, patient flow, staffing, clinical operations",
                "gap_type": "capacity / staffing / patient-flow bottleneck",
                "market_gap": "Health systems struggle to predict capacity and staffing bottlenecks before they degrade patient-flow and operational performance.",
                "needed_solution": "Healthcare operations intelligence platform that forecasts patient-flow bottlenecks, staffing gaps, and capacity risk while preserving auditability and privacy controls.",
                "solution_class": "healthcare operations intelligence platform",
                "buyer_segments": [
                    "health systems",
                    "hospital operations teams",
                    "capacity command centers",
                    "workforce planning teams",
                ],
                "design_implications": [
                    "patient-flow model",
                    "capacity forecast engine",
                    "staffing-risk detector",
                    "privacy controls",
                    "clinical workflow review layer",
                ],
                "acquirer_categories": [
                    "healthcare software platforms",
                    "hospital operations platforms",
                    "EHR ecosystem companies",
                    "healthcare analytics companies",
                ],
            },
            "industrial_supply_chain": {
                "industry_context": "manufacturing, procurement, suppliers, ERP, planning systems, industrial resilience",
                "gap_type": "component shortage / supplier dependency / production bottleneck",
                "market_gap": "Manufacturers lack early-warning intelligence for component shortages, supplier dependency failures, and production bottlenecks.",
                "needed_solution": "Industrial resilience intelligence platform that maps supplier dependencies, forecasts shortages, and recommends procurement and manufacturing countermeasures.",
                "solution_class": "industrial resilience intelligence platform",
                "buyer_segments": [
                    "manufacturers",
                    "procurement teams",
                    "supply-chain leaders",
                    "operations planning teams",
                ],
                "design_implications": [
                    "supplier graph",
                    "shortage forecast engine",
                    "ERP integration",
                    "procurement recommendation layer",
                    "production risk dashboard",
                ],
                "acquirer_categories": [
                    "ERP platforms",
                    "supply-chain software companies",
                    "industrial automation companies",
                    "procurement platforms",
                ],
            },
            "energy_infrastructure": {
                "industry_context": "grid infrastructure, utilities, transmission, power systems, energy resilience",
                "gap_type": "grid instability / demand pressure / infrastructure bottleneck",
                "market_gap": "Utilities and infrastructure operators need better early-warning intelligence for grid instability, demand pressure, and transmission bottlenecks.",
                "needed_solution": "Energy infrastructure intelligence platform that forecasts grid bottlenecks, maps utility asset risk, and recommends resilience investments.",
                "solution_class": "energy infrastructure intelligence platform",
                "buyer_segments": [
                    "utilities",
                    "grid operators",
                    "energy infrastructure owners",
                    "transmission planners",
                ],
                "design_implications": [
                    "grid data ingestion",
                    "asset-risk model",
                    "demand forecast engine",
                    "transmission bottleneck map",
                    "resilience planning module",
                ],
                "acquirer_categories": [
                    "utility software companies",
                    "grid technology companies",
                    "energy management platforms",
                    "infrastructure analytics providers",
                ],
            },
            "financial_market_intelligence": {
                "industry_context": "capital markets, credit, liquidity, institutional finance, risk intelligence",
                "gap_type": "hidden signal / repricing opportunity",
                "market_gap": "Financial markets contain weak signals that appear before capital reprices risk, liquidity, and sector rotation.",
                "needed_solution": "Financial signal intelligence platform that detects hidden liquidity gaps, credit stress, and overlooked repricing opportunities.",
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
            "general_intelligence": {
                "industry_context": "cross-sector intelligence, opportunity discovery, strategic analysis",
                "gap_type": "knowledge / decision / opportunity gap",
                "market_gap": "Organizations lack integrated systems for detecting weak signals, synthesizing opportunities, and converting them into validated designs.",
                "needed_solution": "Cross-sector opportunity intelligence platform that maps signals, gaps, opportunities, designs, and strategic outcomes.",
                "solution_class": "opportunity intelligence platform",
                "buyer_segments": [
                    "strategy teams",
                    "innovation groups",
                    "corporate development teams",
                    "research organizations",
                ],
                "design_implications": [
                    "signal ingestion",
                    "gap detection",
                    "opportunity ranking",
                    "design synthesis",
                    "portfolio packaging",
                ],
                "acquirer_categories": [
                    "data intelligence platforms",
                    "enterprise AI platforms",
                    "research platforms",
                    "strategy software companies",
                ],
            },
        }
        return profiles.get(sector, profiles["general_intelligence"])

    # =========================
    # SCORING
    # =========================
    def _strategic_pressure(
        self,
        text: str,
        keywords: List[str],
        sector: str,
        market: Dict[str, Any],
        financial: Dict[str, Any],
    ) -> Dict[str, Any]:
        routing = self._routing_view(text, keywords)

        pressure_terms = {
            "climate_insurance": [
                "accelerating",
                "climate exposure",
                "weather losses",
                "repricing",
                "market withdrawal",
                "losses",
                "risk concentration",
                "risk transfer",
                "underwriting",
                "catastrophe",
            ],
            "defense_autonomy": [
                "contested",
                "mission",
                "secure",
                "real time",
                "human override",
                "battlefield",
                "drone",
            ],
            "healthcare_operations": [
                "shortage",
                "capacity",
                "patient flow",
                "staffing",
                "hospital",
            ],
            "industrial_supply_chain": [
                "shortage",
                "bottleneck",
                "supplier",
                "production failure",
                "procurement",
            ],
            "energy_infrastructure": [
                "grid",
                "demand",
                "transmission",
                "resilience",
                "utility",
            ],
            "financial_market_intelligence": [
                "credit",
                "liquidity",
                "repricing",
                "risk",
                "portfolio",
            ],
        }

        drivers = []
        for term in pressure_terms.get(sector, []):
            if " " in term:
                matched = self._contains_phrase(routing, term)
            else:
                matched = self._contains_word(routing, term)
            if matched:
                drivers.append(term)

        base = 0.34 + min(0.26, len(drivers) * 0.050)
        base += float(market.get("volatility", 0.0) or 0.0) * 0.12
        base += float(financial.get("risk", 0.0) or 0.0) * 0.08

        if sector == "climate_insurance":
            base += 0.12
        elif sector in {"defense_autonomy", "healthcare_operations"}:
            base += 0.08
        elif sector in {"energy_infrastructure", "financial_market_intelligence"}:
            base += 0.06
        elif sector == "industrial_supply_chain":
            base += 0.05

        score = round(min(0.94, base), 4)
        level = "high" if score >= 0.70 else "moderate" if score >= 0.48 else "low"

        return {
            "level": level,
            "score": score,
            "drivers": drivers or ["sector need", "market uncertainty"],
        }

    def _confidence(
        self,
        text: str,
        keywords: List[str],
        sector: str,
        pressure_score: float,
        patent_activity: float,
    ) -> float:
        routing = self._routing_view(text, keywords)

        sector_terms = {
            "climate_insurance": [
                "insurance",
                "climate",
                "weather",
                "underwriting",
                "reinsurance",
                "exposure",
                "repricing",
                "losses",
                "catastrophe",
                "risk transfer",
            ],
            "defense_autonomy": [
                "defense",
                "mission",
                "drone",
                "secure",
                "autonomous",
                "command",
            ],
            "healthcare_operations": [
                "healthcare",
                "hospital",
                "patient",
                "capacity",
                "staffing",
            ],
            "industrial_supply_chain": [
                "supply",
                "manufacturing",
                "supplier",
                "procurement",
                "erp",
            ],
            "energy_infrastructure": [
                "energy",
                "grid",
                "utility",
                "transmission",
                "power grid",
            ],
            "financial_market_intelligence": [
                "financial",
                "credit",
                "liquidity",
                "capital",
                "portfolio",
            ],
        }

        hits = 0
        for term in sector_terms.get(sector, []):
            if " " in term:
                hits += 1 if self._contains_phrase(routing, term) else 0
            else:
                hits += 1 if self._contains_word(routing, term) else 0

        base = 0.32 + hits * 0.060 + pressure_score * 0.24 + patent_activity * 0.10

        if sector == "climate_insurance":
            base += 0.06

        return round(min(0.94, base), 4)

    def _domain_for_sector(self, sector: str, fallback: str) -> str:
        return {
            "climate_insurance": "insurance",
            "defense_autonomy": "technology",
            "healthcare_operations": "healthcare",
            "industrial_supply_chain": "industrial",
            "energy_infrastructure": "energy",
            "financial_market_intelligence": "finance",
        }.get(sector, fallback or "general")
