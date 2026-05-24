"""
Market-Wide Needed Solution Search — public-facing opportunity discovery directions.

v5.40:
- Replaces exposed internal search phrasing with safe, user-facing discovery directions.
- Output is phrased as market needs and solution areas, not Claire's internal reasoning.
"""

from __future__ import annotations

from typing import Any, Dict, List


class OpportunitySearchSuggestions:
    """Generate public-facing market-wide needed-solution directions."""

    UNIVERSE_NEEDS = {
        "sp500_public": [
            "enterprise governance infrastructure",
            "margin-pressure automation",
            "resilience and risk intelligence",
            "operational command-center modernization",
            "strategic capability-gap detection",
        ],
        "djia_public": [
            "blue-chip workflow modernization",
            "legacy-system replacement",
            "enterprise resilience tooling",
            "executive risk visibility",
            "operational performance intelligence",
        ],
        "nasdaq_composite": [
            "AI infrastructure governance",
            "software platform efficiency",
            "data lineage and evaluation",
            "growth-company operating leverage",
            "technology adoption intelligence",
        ],
        "private_sector_establishments": [
            "vertical workflow automation",
            "local/regional compliance simplification",
            "labor productivity tooling",
            "operator-grade decision support",
            "private-market risk visibility",
        ],
        "federal_government": [
            "audit-ready mission workflow",
            "procurement modernization",
            "compliance reporting automation",
            "secure review and approval tooling",
            "public-sector operations intelligence",
        ],
        "defense_industrial_base": [
            "control-gated mission support",
            "supplier readiness intelligence",
            "secure coordination infrastructure",
            "critical infrastructure exposure monitoring",
            "program risk visibility",
        ],
        "custom_universe": [
            "workflow bottleneck reduction",
            "buyer pain discovery",
            "competitive differentiation",
            "market-timing intelligence",
            "strategic operating leverage",
        ],
    }

    DOMAIN_NEEDS = {
        "energy": ["grid reliability", "asset monitoring", "interconnection management", "load and demand operations"],
        "materials": ["traceability", "quality consistency", "supplier substitution", "production yield"],
        "industrials": ["maintenance planning", "supplier fragility", "factory throughput", "quality control"],
        "consumer_discretionary": ["demand forecasting", "inventory alignment", "customer journey optimization", "marketplace pressure"],
        "consumer_staples": ["retail execution", "supply assurance", "margin protection", "labeling compliance"],
        "health_care": ["patient flow", "capacity operations", "staffing coordination", "payer-provider workflow"],
        "financials": ["risk surveillance", "counterparty monitoring", "compliance operations", "portfolio exposure intelligence"],
        "information_technology": ["AI governance", "model evaluation", "inference cost management", "data lineage"],
        "communication_services": ["platform risk", "content operations", "audience signal intelligence", "network economics"],
        "utilities": ["asset reliability", "storm response", "grid operations", "regulatory reporting"],
        "real_estate": ["portfolio exposure", "tenant operations", "insurance pressure", "property risk visibility"],
        "government_defense": ["mission readiness", "secure review", "auditability", "compliance boundaries"],
        "cross_sector": ["workflow bottlenecks", "market gaps", "buyer pain", "strategic acquirer fit"],
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
        universe_needs = self.UNIVERSE_NEEDS.get(market_universe, self.UNIVERSE_NEEDS["custom_universe"])
        domain_needs = self.DOMAIN_NEEDS.get(industry_domain, self.DOMAIN_NEEDS["cross_sector"])
        signal = (signal or "").strip()

        directions: List[Dict[str, str]] = []
        for index in range(max(1, min(count, 10))):
            universe_need = universe_needs[index % len(universe_needs)]
            domain_need = domain_needs[index % len(domain_needs)]
            title = f"{domain_need.title()} for {market_universe.replace('_', ' ').title()}"
            needed_solution = f"A productized solution addressing {domain_need} and {universe_need} for {buyer_segment.replace('_', ' ')}."
            market_gap = f"Current workflows often lack integrated visibility, reviewability, and measurable ROI around {domain_need}."
            if signal:
                market_gap = f"{market_gap} User signal: {signal}"
            directions.append({
                "id": f"direction_{index + 1}",
                "title": title,
                "market_universe": market_universe,
                "industry_domain": industry_domain,
                "buyer_segment": buyer_segment,
                "objective": objective,
                "opportunity_direction": universe_need,
                "market_gap": market_gap,
                "needed_solution": needed_solution,
                "why_now": "Increasing operational complexity, compliance pressure, and competitive pressure create a timely opening.",
                "confidence_label": "directional",
            })

        return {
            "status": "success",
            "market_universe": market_universe,
            "industry_domain": industry_domain,
            "buyer_segment": buyer_segment,
            "objective": objective,
            "workflow": workflow,
            "direction_count": len(directions),
            "directions": directions,
        }
