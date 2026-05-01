"""
Opportunity Search Suggestions — deterministic search/query guidance for Claire.

v5.39:
- Generates market-universe-specific opportunity suggestions.
- Keeps suggestions local and deterministic; connected/hybrid modes can later use them as live-feed query seeds.
"""

from __future__ import annotations

from typing import Any, Dict, List


class OpportunitySearchSuggestions:
    """Generate market-universe and industry-specific search suggestions."""

    UNIVERSE_TERMS = {
        "sp500_public": ["large-cap capability gap", "public-company margin pressure", "enterprise workflow bottleneck", "strategic acquirer gap", "industry modernization pressure"],
        "djia_public": ["blue-chip transformation gap", "legacy workflow pressure", "enterprise operating constraint", "resilience investment need", "strategic modernization gap"],
        "nasdaq_composite": ["growth-company disruption signal", "AI infrastructure pressure", "software platform gap", "biotech or data workflow friction", "technology adoption timing"],
        "private_sector_establishments": ["underserved private operator pain", "local/regional workflow bottleneck", "compliance burden", "labor productivity gap", "vertical software wedge"],
        "federal_government": ["agency mission bottleneck", "procurement modernization need", "compliance reporting burden", "public-sector workflow gap", "auditability requirement"],
        "defense_industrial_base": ["mission support gap", "control-gated autonomy need", "secure coordination bottleneck", "supplier readiness risk", "critical infrastructure exposure"],
        "custom_universe": ["user-defined buyer pain", "custom portfolio gap", "strategic wedge", "competitor weakness", "market timing signal"],
    }

    DOMAIN_TERMS = {
        "energy": ["grid resilience", "asset monitoring", "interconnection backlog", "demand response"],
        "materials": ["supply substitution", "quality traceability", "production yield", "raw material risk"],
        "industrials": ["maintenance bottleneck", "supplier fragility", "factory throughput", "quality escape"],
        "consumer_discretionary": ["demand forecasting", "consumer journey friction", "inventory mismatch", "marketplace pressure"],
        "consumer_staples": ["margin pressure", "supply assurance", "retail execution", "compliance labeling"],
        "health_care": ["patient flow", "clinical operations", "capacity constraints", "payer-provider friction"],
        "financials": ["risk signal", "counterparty stress", "compliance surveillance", "portfolio exposure"],
        "information_technology": ["agent governance", "model evaluation", "inference cost", "data lineage"],
        "communication_services": ["content operations", "network economics", "audience signal", "platform risk"],
        "utilities": ["asset reliability", "storm response", "grid operations", "regulatory reporting"],
        "real_estate": ["property exposure", "tenant operations", "portfolio risk", "insurance pressure"],
        "government_defense": ["mission readiness", "secure review", "auditability", "compliance boundary"],
        "cross_sector": ["workflow bottleneck", "buyer pain", "market gap", "strategic acquirer"],
    }

    def suggest(
        self,
        market_universe: str = "custom_universe",
        industry_domain: str = "cross_sector",
        buyer_segment: str = "enterprise_c_suite",
        objective: str = "discover_market_gaps",
        workflow: str = "discover",
        signal: str = "",
        count: int = 10,
    ) -> Dict[str, Any]:
        universe_terms = self.UNIVERSE_TERMS.get(market_universe, self.UNIVERSE_TERMS["custom_universe"])
        domain_terms = self.DOMAIN_TERMS.get(industry_domain, self.DOMAIN_TERMS["cross_sector"])
        signal = (signal or "").strip()

        patterns = [
            "find {objective} in {universe} around {domain_term} for {buyer_segment}",
            "identify urgent buyer pain where {universe_term} intersects with {domain_term}",
            "discover productizable gaps caused by {domain_term} and {universe_term}",
            "find acquirer-attractive capability gaps involving {domain_term}",
            "map regulatory, technical, and adoption blockers around {domain_term}",
            "generate a competitor-beating product wedge for {domain_term}",
            "find under-served buyers with budget and urgency around {universe_term}",
            "identify proof paths and pilot designs for {domain_term}",
            "find market timing signals that make {domain_term} urgent now",
            "generate adjacent opportunity spaces related to {domain_term}",
        ]

        suggestions: List[Dict[str, str]] = []
        for index, pattern in enumerate(patterns):
            domain_term = domain_terms[index % len(domain_terms)]
            universe_term = universe_terms[index % len(universe_terms)]
            query = pattern.format(
                objective=objective.replace("_", " "),
                universe=market_universe.replace("_", " "),
                industry=industry_domain.replace("_", " "),
                buyer_segment=buyer_segment.replace("_", " "),
                domain_term=domain_term,
                universe_term=universe_term,
            )
            if signal:
                query = f"{query}; user signal: {signal}"
            suggestions.append({
                "id": f"suggest_{index + 1}",
                "query": query,
                "workflow": workflow,
                "market_universe": market_universe,
                "industry_domain": industry_domain,
                "buyer_segment": buyer_segment,
                "objective": objective,
                "domain_term": domain_term,
                "universe_term": universe_term,
            })

        return {
            "status": "success",
            "market_universe": market_universe,
            "industry_domain": industry_domain,
            "buyer_segment": buyer_segment,
            "objective": objective,
            "workflow": workflow,
            "signal": signal,
            "suggestions": suggestions[:max(1, min(count, len(suggestions)))],
        }
