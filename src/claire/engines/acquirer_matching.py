"""
Acquirer Matching Engine — market-gap-aware strategic acquirer discovery.

This engine ranks likely strategic acquirers using:
- market_gap sector
- acquirer categories
- buyer segments
- needed solution class
- keyword overlap with exact-token matching
- strategic pressure
- domain fit

Important:
This is still deterministic and local. It is not yet live web discovery.
It replaces the earlier keyword-only placeholder matcher.
"""

import re
from typing import Any, Dict, List, Optional, Set


class AcquirerMatchingEngine:
    """
    Market-gap-aware acquirer matcher.

    Public API:
        match(keywords, domain="technology", market_gap=None)
    """

    def match(
        self,
        keywords: List[str],
        domain: str = "technology",
        market_gap: Optional[Dict[str, Any]] = None,
        limit: int = 12,
    ) -> List[Dict[str, Any]]:
        keywords = keywords or []
        market_gap = market_gap or {}

        context = self._build_context(
            keywords=keywords,
            domain=domain,
            market_gap=market_gap,
        )

        candidates = self._candidate_pool(context=context)

        results = []
        for candidate in candidates:
            score_detail = self._score_candidate(
                candidate=candidate,
                context=context,
            )

            result = {
                "name": candidate["name"],
                "ticker": candidate.get("ticker", "UNKNOWN"),
                "type": candidate.get("type", "strategic"),
                "sector": candidate.get("sector", "unknown"),
                "match_score": round(score_detail["score"], 4),
                "matched_signals": score_detail["matched_signals"],
                "rationale": score_detail["rationale"],
                "fit_dimensions": score_detail["fit_dimensions"],
                "focus": candidate.get("focus", []),
            }
            results.append(result)

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:limit]

    # =========================
    # CONTEXT
    # =========================
    def _build_context(
        self,
        keywords: List[str],
        domain: str,
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector = market_gap.get("sector", "")
        solution_class = market_gap.get("solution_class", "")
        needed_solution = market_gap.get("needed_solution", "")
        acquirer_categories = market_gap.get("acquirer_categories", [])
        buyer_segments = market_gap.get("buyer_segments", [])
        industry_context = market_gap.get("industry_context", "")

        strategic_pressure = market_gap.get("strategic_pressure", {})
        pressure_score = strategic_pressure.get("score", 0.0) if isinstance(strategic_pressure, dict) else 0.0

        text_blob = " ".join([
            domain or "",
            sector or "",
            solution_class or "",
            needed_solution or "",
            industry_context or "",
            " ".join(keywords),
            " ".join(acquirer_categories),
            " ".join(buyer_segments),
        ])

        return {
            "domain": domain or "general",
            "sector": sector,
            "solution_class": solution_class,
            "needed_solution": needed_solution,
            "acquirer_categories": acquirer_categories,
            "buyer_segments": buyer_segments,
            "industry_context": industry_context,
            "pressure_score": pressure_score,
            "tokens": self._tokens(text_blob),
            "phrases": self._phrases(text_blob),
            "raw_keywords": keywords,
        }

    def _tokens(self, value: str) -> Set[str]:
        value = (value or "").lower()
        return set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", value))

    def _phrases(self, value: str) -> Set[str]:
        value = (value or "").lower()
        cleaned = re.sub(r"[^a-z0-9\-\s/]", " ", value)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        phrases = set()
        words = cleaned.split()

        for size in (2, 3, 4):
            for i in range(0, max(0, len(words) - size + 1)):
                phrases.add(" ".join(words[i:i + size]))

        return phrases

    # =========================
    # CANDIDATES
    # =========================
    def _candidate_pool(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        sector = context.get("sector") or "general_market_intelligence"

        pools = self._sector_candidate_pools()

        candidates = []
        candidates.extend(pools.get(sector, []))

        # Add general strategic tech/data candidates for all non-empty contexts.
        candidates.extend(pools.get("general_market_intelligence", []))

        # If domain is energy/finance/healthcare/technology, add domain-adjacent pool.
        domain = context.get("domain", "")
        if domain == "energy":
            candidates.extend(pools.get("energy_infrastructure", []))
        elif domain == "finance":
            candidates.extend(pools.get("financial_market_intelligence", []))
        elif domain == "healthcare":
            candidates.extend(pools.get("healthcare_operations", []))
        elif domain == "technology" and sector != "defense_autonomy":
            candidates.extend(pools.get("enterprise_ai_platforms", []))

        # Deduplicate by name.
        deduped = {}
        for candidate in candidates:
            deduped[candidate["name"]] = candidate

        return list(deduped.values())

    def _sector_candidate_pools(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "industrial_supply_chain": [
                {
                    "name": "SAP",
                    "ticker": "SAP",
                    "type": "strategic",
                    "sector": "enterprise software / ERP",
                    "categories": ["ERP platforms", "industrial software", "supply-chain platforms"],
                    "focus": ["ERP", "supply chain", "procurement", "manufacturing operations", "business networks"],
                    "base_fit": 0.82,
                },
                {
                    "name": "Oracle",
                    "ticker": "ORCL",
                    "type": "strategic",
                    "sector": "enterprise software / cloud",
                    "categories": ["ERP platforms", "cloud data platforms", "supply-chain platforms"],
                    "focus": ["ERP", "supply chain planning", "cloud applications", "procurement", "enterprise data"],
                    "base_fit": 0.79,
                },
                {
                    "name": "Siemens",
                    "ticker": "SIEGY",
                    "type": "strategic",
                    "sector": "industrial automation / digital industries",
                    "categories": ["industrial software", "automation companies"],
                    "focus": ["industrial automation", "digital twin", "manufacturing", "factory operations", "industrial data"],
                    "base_fit": 0.84,
                },
                {
                    "name": "Schneider Electric",
                    "ticker": "SBGSY",
                    "type": "strategic",
                    "sector": "energy management / industrial automation",
                    "categories": ["industrial software", "automation companies", "energy software companies"],
                    "focus": ["industrial automation", "energy management", "resilience", "operations", "supply continuity"],
                    "base_fit": 0.80,
                },
                {
                    "name": "Rockwell Automation",
                    "ticker": "ROK",
                    "type": "strategic",
                    "sector": "industrial automation",
                    "categories": ["automation companies", "industrial software"],
                    "focus": ["factory automation", "manufacturing intelligence", "industrial operations", "connected enterprise"],
                    "base_fit": 0.81,
                },
                {
                    "name": "Honeywell",
                    "ticker": "HON",
                    "type": "strategic",
                    "sector": "industrial technology / automation",
                    "categories": ["automation companies", "industrial software"],
                    "focus": ["industrial operations", "automation", "supply resilience", "sensors", "operational intelligence"],
                    "base_fit": 0.78,
                },
                {
                    "name": "Kinaxis",
                    "ticker": "KXSCF",
                    "type": "strategic",
                    "sector": "supply chain planning software",
                    "categories": ["supply-chain platforms"],
                    "focus": ["supply chain planning", "concurrent planning", "shortage detection", "supplier risk", "resilience"],
                    "base_fit": 0.86,
                },
                {
                    "name": "Manhattan Associates",
                    "ticker": "MANH",
                    "type": "strategic",
                    "sector": "supply chain commerce software",
                    "categories": ["supply-chain platforms"],
                    "focus": ["supply chain execution", "logistics", "warehouse management", "transportation", "inventory"],
                    "base_fit": 0.76,
                },
                {
                    "name": "Dassault Systemes",
                    "ticker": "DASTY",
                    "type": "strategic",
                    "sector": "industrial software / digital twin",
                    "categories": ["industrial software"],
                    "focus": ["digital twin", "manufacturing design", "simulation", "industrial systems", "product lifecycle"],
                    "base_fit": 0.77,
                },
            ],
            "financial_market_intelligence": [
                {
                    "name": "Bloomberg",
                    "ticker": "PRIVATE",
                    "type": "strategic",
                    "sector": "financial data / market intelligence",
                    "categories": ["financial data platforms", "market intelligence providers"],
                    "focus": ["market data", "financial analytics", "risk signals", "liquidity intelligence", "institutional research"],
                    "base_fit": 0.87,
                },
                {
                    "name": "S&P Global",
                    "ticker": "SPGI",
                    "type": "strategic",
                    "sector": "financial information / credit analytics",
                    "categories": ["financial data platforms", "risk analytics companies"],
                    "focus": ["credit analytics", "market intelligence", "risk data", "sector analysis", "financial benchmarks"],
                    "base_fit": 0.84,
                },
                {
                    "name": "MSCI",
                    "ticker": "MSCI",
                    "type": "strategic",
                    "sector": "investment analytics / risk",
                    "categories": ["risk analytics companies", "asset-management technology platforms"],
                    "focus": ["portfolio analytics", "risk modeling", "factor signals", "institutional investment tools"],
                    "base_fit": 0.80,
                },
                {
                    "name": "FactSet",
                    "ticker": "FDS",
                    "type": "strategic",
                    "sector": "financial data / analytics",
                    "categories": ["financial data platforms"],
                    "focus": ["financial data", "analytics", "portfolio intelligence", "research workflow", "market signals"],
                    "base_fit": 0.79,
                },
                {
                    "name": "BlackRock Aladdin",
                    "ticker": "BLK",
                    "type": "strategic",
                    "sector": "asset management technology",
                    "categories": ["asset-management technology platforms", "risk analytics companies"],
                    "focus": ["risk analytics", "portfolio management", "institutional capital", "market risk", "investment operations"],
                    "base_fit": 0.82,
                },
            ],
            "healthcare_operations": [
                {
                    "name": "Epic Systems",
                    "ticker": "PRIVATE",
                    "type": "strategic",
                    "sector": "healthcare software",
                    "categories": ["healthcare software platforms", "hospital IT companies"],
                    "focus": ["hospital software", "clinical workflow", "patient records", "care coordination", "operations"],
                    "base_fit": 0.84,
                },
                {
                    "name": "Oracle Health",
                    "ticker": "ORCL",
                    "type": "strategic",
                    "sector": "healthcare IT / cloud",
                    "categories": ["healthcare software platforms", "hospital IT companies"],
                    "focus": ["clinical systems", "hospital operations", "health data", "care delivery", "cloud healthcare"],
                    "base_fit": 0.80,
                },
                {
                    "name": "GE HealthCare",
                    "ticker": "GEHC",
                    "type": "strategic",
                    "sector": "healthcare technology",
                    "categories": ["clinical analytics providers", "healthcare operations vendors"],
                    "focus": ["clinical operations", "hospital capacity", "imaging workflow", "care delivery", "operational analytics"],
                    "base_fit": 0.78,
                },
                {
                    "name": "Philips Healthcare",
                    "ticker": "PHG",
                    "type": "strategic",
                    "sector": "health technology",
                    "categories": ["clinical analytics providers", "healthcare operations vendors"],
                    "focus": ["patient monitoring", "care operations", "hospital workflow", "clinical intelligence"],
                    "base_fit": 0.77,
                },
                {
                    "name": "Health Catalyst",
                    "ticker": "HCAT",
                    "type": "strategic",
                    "sector": "healthcare analytics",
                    "categories": ["clinical analytics providers"],
                    "focus": ["healthcare analytics", "care improvement", "population health", "operational insights"],
                    "base_fit": 0.76,
                },
            ],
            "energy_infrastructure": [
                {
                    "name": "Schneider Electric",
                    "ticker": "SBGSY",
                    "type": "strategic",
                    "sector": "energy management / automation",
                    "categories": ["energy software companies", "industrial automation companies"],
                    "focus": ["grid operations", "energy management", "resilience", "automation", "infrastructure monitoring"],
                    "base_fit": 0.84,
                },
                {
                    "name": "Siemens Energy",
                    "ticker": "SMNEY",
                    "type": "strategic",
                    "sector": "energy infrastructure",
                    "categories": ["utility technology vendors", "infrastructure analytics providers"],
                    "focus": ["grid infrastructure", "transmission", "energy systems", "power demand", "grid resilience"],
                    "base_fit": 0.83,
                },
                {
                    "name": "GE Vernova",
                    "ticker": "GEV",
                    "type": "strategic",
                    "sector": "energy technology",
                    "categories": ["utility technology vendors", "energy software companies"],
                    "focus": ["grid software", "power systems", "utilities", "transmission", "energy resilience"],
                    "base_fit": 0.81,
                },
                {
                    "name": "Hitachi Energy",
                    "ticker": "HTHIY",
                    "type": "strategic",
                    "sector": "grid technology",
                    "categories": ["utility technology vendors", "infrastructure analytics providers"],
                    "focus": ["grid automation", "transformers", "transmission", "power infrastructure", "grid stability"],
                    "base_fit": 0.82,
                },
                {
                    "name": "Itron",
                    "ticker": "ITRI",
                    "type": "strategic",
                    "sector": "utility intelligence",
                    "categories": ["utility technology vendors", "energy software companies"],
                    "focus": ["utility data", "metering", "grid intelligence", "demand forecasting", "energy analytics"],
                    "base_fit": 0.77,
                },
            ],
            "defense_autonomy": [
                {
                    "name": "Anduril",
                    "ticker": "PRIVATE",
                    "type": "strategic",
                    "sector": "defense technology",
                    "categories": ["defense technology companies"],
                    "focus": ["autonomous defense", "drones", "AI", "border security", "mission autonomy"],
                    "base_fit": 0.90,
                },
                {
                    "name": "Lockheed Martin",
                    "ticker": "LMT",
                    "type": "strategic",
                    "sector": "defense",
                    "categories": ["defense primes", "aerospace companies"],
                    "focus": ["autonomous systems", "drones", "sensor fusion", "battlefield intelligence", "mission systems"],
                    "base_fit": 0.86,
                },
                {
                    "name": "Northrop Grumman",
                    "ticker": "NOC",
                    "type": "strategic",
                    "sector": "defense",
                    "categories": ["defense primes", "aerospace companies"],
                    "focus": ["aerospace", "autonomous platforms", "surveillance", "command systems", "defense autonomy"],
                    "base_fit": 0.84,
                },
                {
                    "name": "RTX",
                    "ticker": "RTX",
                    "type": "strategic",
                    "sector": "defense",
                    "categories": ["defense primes"],
                    "focus": ["sensors", "missiles", "defense systems", "edge computing", "mission systems"],
                    "base_fit": 0.80,
                },
                {
                    "name": "Palantir",
                    "ticker": "PLTR",
                    "type": "strategic",
                    "sector": "data / defense software",
                    "categories": ["government technology providers", "defense technology companies"],
                    "focus": ["battlefield intelligence", "AI", "data fusion", "decision systems", "mission software"],
                    "base_fit": 0.82,
                },
            ],
            "enterprise_ai_platforms": [
                {
                    "name": "Microsoft",
                    "ticker": "MSFT",
                    "type": "strategic",
                    "sector": "cloud / enterprise AI",
                    "categories": ["cloud data platforms", "enterprise software companies"],
                    "focus": ["enterprise AI", "cloud platforms", "data intelligence", "developer tools", "business applications"],
                    "base_fit": 0.75,
                },
                {
                    "name": "Amazon Web Services",
                    "ticker": "AMZN",
                    "type": "strategic",
                    "sector": "cloud infrastructure / AI",
                    "categories": ["cloud data platforms"],
                    "focus": ["cloud infrastructure", "AI services", "data platforms", "industrial cloud", "marketplace"],
                    "base_fit": 0.74,
                },
                {
                    "name": "Google Cloud",
                    "ticker": "GOOGL",
                    "type": "strategic",
                    "sector": "cloud / AI / data",
                    "categories": ["cloud data platforms", "data intelligence companies"],
                    "focus": ["AI", "data analytics", "cloud platforms", "machine learning", "enterprise intelligence"],
                    "base_fit": 0.74,
                },
                {
                    "name": "Snowflake",
                    "ticker": "SNOW",
                    "type": "strategic",
                    "sector": "cloud data platform",
                    "categories": ["cloud data platforms", "data intelligence companies"],
                    "focus": ["data cloud", "analytics", "enterprise data", "data sharing", "AI data"],
                    "base_fit": 0.73,
                },
                {
                    "name": "ServiceNow",
                    "ticker": "NOW",
                    "type": "strategic",
                    "sector": "enterprise workflow software",
                    "categories": ["enterprise software companies", "strategy platforms"],
                    "focus": ["workflow automation", "enterprise operations", "AI agents", "business process intelligence"],
                    "base_fit": 0.72,
                },
            ],
            "general_market_intelligence": [
                {
                    "name": "Palantir",
                    "ticker": "PLTR",
                    "type": "strategic",
                    "sector": "data intelligence",
                    "categories": ["data intelligence companies", "enterprise software companies"],
                    "focus": ["ontology", "data integration", "decision intelligence", "operational AI", "enterprise analytics"],
                    "base_fit": 0.76,
                },
                {
                    "name": "Databricks",
                    "ticker": "PRIVATE",
                    "type": "strategic",
                    "sector": "data / AI platform",
                    "categories": ["data intelligence companies", "cloud data platforms"],
                    "focus": ["data intelligence", "lakehouse", "AI", "analytics", "machine learning"],
                    "base_fit": 0.75,
                },
                {
                    "name": "Salesforce",
                    "ticker": "CRM",
                    "type": "strategic",
                    "sector": "enterprise software / customer data",
                    "categories": ["enterprise software companies"],
                    "focus": ["customer intelligence", "enterprise AI", "workflow", "market demand", "business data"],
                    "base_fit": 0.70,
                },
            ],
        }

    # =========================
    # SCORING
    # =========================
    def _score_candidate(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = float(candidate.get("base_fit", 0.5))
        matched_signals = []
        rationale = []
        fit_dimensions = {}

        context_tokens = context["tokens"]
        context_phrases = context["phrases"]

        candidate_categories = [c.lower() for c in candidate.get("categories", [])]
        candidate_focus = [f.lower() for f in candidate.get("focus", [])]
        candidate_sector = candidate.get("sector", "").lower()

        # Category alignment from market_gap.acquirer_categories.
        requested_categories = [c.lower() for c in context.get("acquirer_categories", [])]
        category_matches = sorted(set(candidate_categories).intersection(set(requested_categories)))

        if category_matches:
            boost = min(0.12, len(category_matches) * 0.04)
            score += boost
            matched_signals.extend(category_matches)
            rationale.append("matches market-gap acquirer category")
            fit_dimensions["category_alignment"] = round(boost, 4)
        else:
            fit_dimensions["category_alignment"] = 0.0

        # Focus matching with exact-token and exact-phrase logic.
        focus_matches = []
        for focus in candidate_focus:
            focus_tokens = self._tokens(focus)
            focus_phrases = self._phrases(focus)

            exact_token_overlap = focus_tokens.intersection(context_tokens)
            phrase_overlap = focus_phrases.intersection(context_phrases)

            # Ignore weak generic AI-only overlap unless supported by another signal.
            filtered_tokens = {
                token for token in exact_token_overlap
                if token not in {"ai", "platform", "data", "system", "systems"}
            }

            if filtered_tokens or phrase_overlap:
                focus_matches.append(focus)
                matched_signals.extend(sorted(filtered_tokens))
                matched_signals.extend(sorted(phrase_overlap))

        focus_matches = sorted(set(focus_matches))
        if focus_matches:
            boost = min(0.14, len(focus_matches) * 0.025)
            score += boost
            rationale.append("focus areas match opportunity requirements")
            fit_dimensions["focus_alignment"] = round(boost, 4)
        else:
            fit_dimensions["focus_alignment"] = 0.0

        # Sector fit.
        sector = (context.get("sector") or "").lower()
        if sector and sector.replace("_", " ") in candidate_sector:
            score += 0.05
            rationale.append("candidate sector directly matches market-gap sector")
            fit_dimensions["sector_fit"] = 0.05
        elif sector:
            sector_tokens = self._tokens(sector.replace("_", " "))
            candidate_sector_tokens = self._tokens(candidate_sector)
            overlap = sector_tokens.intersection(candidate_sector_tokens)
            if overlap:
                score += 0.03
                rationale.append("candidate sector overlaps market-gap sector")
                fit_dimensions["sector_fit"] = 0.03
            else:
                fit_dimensions["sector_fit"] = 0.0
        else:
            fit_dimensions["sector_fit"] = 0.0

        # Buyer segment fit.
        buyer_blob = " ".join(context.get("buyer_segments", []))
        buyer_tokens = self._tokens(buyer_blob)
        candidate_blob = " ".join(candidate.get("focus", []) + candidate.get("categories", []))
        candidate_tokens = self._tokens(candidate_blob)

        buyer_overlap = buyer_tokens.intersection(candidate_tokens)
        buyer_overlap = {
            token for token in buyer_overlap
            if token not in {"teams", "companies", "platforms", "software"}
        }

        if buyer_overlap:
            boost = min(0.06, len(buyer_overlap) * 0.02)
            score += boost
            matched_signals.extend(sorted(buyer_overlap))
            rationale.append("candidate likely sells into relevant buyer segment")
            fit_dimensions["buyer_segment_fit"] = round(boost, 4)
        else:
            fit_dimensions["buyer_segment_fit"] = 0.0

        # Strategic pressure.
        pressure_score = float(context.get("pressure_score", 0.0) or 0.0)
        pressure_boost = min(0.04, pressure_score * 0.04)
        score += pressure_boost
        fit_dimensions["strategic_pressure"] = round(pressure_boost, 4)

        if pressure_boost >= 0.03:
            rationale.append("high strategic pressure increases acquisition relevance")

        score = max(0.0, min(0.98, score))

        if not rationale:
            rationale.append("general strategic adjacency")

        matched_signals = sorted({
            signal for signal in matched_signals
            if signal and len(signal) > 1
        })

        return {
            "score": score,
            "matched_signals": matched_signals[:12],
            "rationale": rationale,
            "fit_dimensions": fit_dimensions,
        }
