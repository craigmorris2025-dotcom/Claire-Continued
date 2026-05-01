"""
Opportunity Search Suggestions — deterministic search/query guidance for Claire.

v5.38:
- Generates search and prompt suggestions for opportunity discovery.
- Keeps suggestions local and deterministic; connected/hybrid modes can later use them as query seeds.
"""

from __future__ import annotations

from typing import Any, Dict, List


class OpportunitySearchSuggestions:
    """Generate domain-specific search suggestions and exploration prompts."""

    SECTOR_TERMS = {
        "defense_autonomy": ["mission autonomy", "command review", "human authorization", "secure simulation", "auditability"],
        "climate_insurance": ["underwriting repricing", "catastrophe scenarios", "market withdrawal", "exposure concentration", "risk transfer"],
        "healthcare_operations": ["patient flow", "capacity command center", "staffing shortage", "boarding pressure", "discharge delay"],
        "industrial_supply_chain": ["supplier fragility", "inventory shock", "production bottleneck", "quality escape", "vendor risk"],
        "energy_infrastructure": ["grid resilience", "interconnection backlog", "asset monitoring", "demand response", "infrastructure permitting"],
        "financial_intelligence": ["risk signal", "portfolio exposure", "counterparty stress", "compliance surveillance", "market anomaly"],
        "regulatory_technology": ["compliance burden", "audit trail", "reporting workflow", "policy change", "regulated review"],
        "ai_infrastructure": ["model operations", "evaluation pipeline", "inference cost", "agent governance", "data lineage"],
        "cross_sector": ["workflow bottleneck", "compliance gate", "buyer pain", "market gap", "strategic acquirer"],
    }

    def suggest(
        self,
        sector: str = "cross_sector",
        workflow: str = "discover",
        signal: str = "",
        count: int = 10,
    ) -> Dict[str, Any]:
        terms = self.SECTOR_TERMS.get(sector, self.SECTOR_TERMS["cross_sector"])
        signal = (signal or "").strip()
        suggestions: List[Dict[str, str]] = []

        base_patterns = [
            "find non-obvious {sector} opportunities around {term}",
            "identify buyer pain where {term} creates urgent operational friction",
            "discover productizable gaps caused by {term}",
            "find acquirer-attractive capability gaps involving {term}",
            "map regulatory, technical, and adoption blockers around {term}",
            "generate a competitor-beating product wedge for {term}",
            "find under-served buyers with budget and urgency around {term}",
            "identify proof paths and pilot designs for {term}",
            "find market timing signals that make {term} urgent now",
            "generate adjacent opportunity spaces related to {term}",
        ]

        sector_label = sector.replace("_", " ")
        for index, pattern in enumerate(base_patterns):
            term = terms[index % len(terms)]
            query = pattern.format(sector=sector_label, term=term)
            if signal:
                query = f"{query}; user signal: {signal}"
            suggestions.append({
                "id": f"suggest_{index + 1}",
                "query": query,
                "workflow": workflow,
                "sector": sector,
                "term": term,
            })

        return {
            "status": "success",
            "sector": sector,
            "workflow": workflow,
            "signal": signal,
            "suggestions": suggestions[:max(1, min(count, len(suggestions)))],
        }
