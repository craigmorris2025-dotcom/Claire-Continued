"""
Market Universe Taxonomy — industry-standard launcher terminology for Claire.

v5.39:
- Separates market universe, industry/domain, buyer segment, and opportunity objective.
- Keeps Claire's internal routing sectors available as downstream routing hints.
- Prepared for future connected/hybrid live-feed universes.
"""

from __future__ import annotations

from typing import Any, Dict, List


class MarketUniverseTaxonomy:
    """Deterministic taxonomy used by the dashboard and opportunity command library."""

    def market_universes(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "sp500_public",
                "name": "S&P 500 public-company universe",
                "coverage_label": "S&P 500 coverage universe",
                "coverage_count_label": "503 companies / securities coverage target",
                "category": "public_markets",
                "description": "Large-cap U.S. public-company discovery universe for strategic gaps, acquirer fit, and industry pressure mapping.",
                "future_live_feed_role": "public-company intelligence, filings, news, market pressure, acquirer capability gaps",
            },
            {
                "id": "djia_public",
                "name": "Dow Jones Industrial Average blue-chip universe",
                "coverage_label": "DJIA coverage universe",
                "coverage_count_label": "30 companies",
                "category": "public_markets",
                "description": "Blue-chip company universe for enterprise, industrial, financial, healthcare, and infrastructure capability-gap discovery.",
                "future_live_feed_role": "blue-chip strategic movement, acquisition logic, market pressure, competitor positioning",
            },
            {
                "id": "nasdaq_composite",
                "name": "NASDAQ Composite public-growth universe",
                "coverage_label": "NASDAQ Composite coverage universe",
                "coverage_count_label": "3,300 companies coverage target",
                "category": "public_markets",
                "description": "Technology, growth, software, AI, biotech, and market-disruption discovery universe.",
                "future_live_feed_role": "technology trajectory, product launches, venture-like public-company signals, competitive gaps",
            },
            {
                "id": "private_sector_establishments",
                "name": "Private-sector establishments universe",
                "coverage_label": "Private-sector establishment coverage",
                "coverage_count_label": "7.88 million establishments coverage target",
                "category": "private_markets",
                "description": "Private-sector opportunity discovery universe for workflow bottlenecks, compliance pain, local/regional market gaps, and vertical software wedges.",
                "future_live_feed_role": "private-market discovery, NAICS-style segmentation, regional clusters, underserved buyer pools",
            },
            {
                "id": "federal_government",
                "name": "Federal / government buyer universe",
                "coverage_label": "Federal and public-sector buyer coverage",
                "coverage_count_label": "agency and program coverage target",
                "category": "government",
                "description": "Government, federal, public-sector, procurement, compliance, and mission-support opportunity universe.",
                "future_live_feed_role": "procurement signals, compliance changes, agency pain points, mission requirements",
            },
            {
                "id": "defense_industrial_base",
                "name": "Defense industrial base universe",
                "coverage_label": "Defense and critical mission ecosystem",
                "coverage_count_label": "prime, integrator, supplier, and program coverage target",
                "category": "defense_critical",
                "description": "Defense, national security, mission support, critical infrastructure, and control-gated autonomy opportunity universe.",
                "future_live_feed_role": "program pressure, mission gaps, secure systems, control-gated productization",
            },
            {
                "id": "custom_universe",
                "name": "Custom user-defined universe",
                "coverage_label": "Custom coverage",
                "coverage_count_label": "user-defined",
                "category": "custom",
                "description": "User-defined universe for founder theses, customer lists, strategic portfolios, local markets, or specialized domains.",
                "future_live_feed_role": "user-defined connected/hybrid feed target",
            },
        ]

    def industry_domains(self) -> List[Dict[str, Any]]:
        return [
            {"id": "energy", "name": "Energy", "classification": "GICS-style"},
            {"id": "materials", "name": "Materials", "classification": "GICS-style"},
            {"id": "industrials", "name": "Industrials", "classification": "GICS-style"},
            {"id": "consumer_discretionary", "name": "Consumer Discretionary", "classification": "GICS-style"},
            {"id": "consumer_staples", "name": "Consumer Staples", "classification": "GICS-style"},
            {"id": "health_care", "name": "Health Care", "classification": "GICS-style"},
            {"id": "financials", "name": "Financials", "classification": "GICS-style"},
            {"id": "information_technology", "name": "Information Technology", "classification": "GICS-style"},
            {"id": "communication_services", "name": "Communication Services", "classification": "GICS-style"},
            {"id": "utilities", "name": "Utilities", "classification": "GICS-style"},
            {"id": "real_estate", "name": "Real Estate", "classification": "GICS-style"},
            {"id": "government_defense", "name": "Government / Defense", "classification": "public-sector"},
            {"id": "cross_sector", "name": "Cross-Sector / Multi-Industry", "classification": "cross-market"},
        ]

    def buyer_segments(self) -> List[Dict[str, Any]]:
        return [
            {"id": "enterprise_c_suite", "name": "Enterprise C-suite / strategy leaders"},
            {"id": "business_unit_owner", "name": "Business unit owners"},
            {"id": "operations_leader", "name": "Operations leaders"},
            {"id": "compliance_risk", "name": "Compliance / risk leaders"},
            {"id": "product_innovation", "name": "Product / innovation leaders"},
            {"id": "corporate_development", "name": "Corporate development / M&A teams"},
            {"id": "federal_agency", "name": "Federal agency buyers"},
            {"id": "defense_program", "name": "Defense program sponsors"},
            {"id": "private_market_operator", "name": "Private-market operators"},
            {"id": "investor_acquirer", "name": "Investors / strategic acquirers"},
        ]

    def opportunity_objectives(self) -> List[Dict[str, Any]]:
        return [
            {"id": "discover_market_gaps", "name": "Discover market gaps"},
            {"id": "find_acquirer_gaps", "name": "Find acquirer capability gaps"},
            {"id": "find_regulatory_openings", "name": "Find regulatory openings"},
            {"id": "find_workflow_bottlenecks", "name": "Find workflow bottlenecks"},
            {"id": "beat_competitors", "name": "Beat direct competitors"},
            {"id": "generate_adjacent_opportunities", "name": "Generate adjacent opportunities"},
            {"id": "optimize_described_project", "name": "Optimize described project"},
            {"id": "build_pilot_path", "name": "Build pilot / proof path"},
        ]

    def internal_routing_hints(self) -> List[Dict[str, Any]]:
        return [
            {"id": "defense_autonomy", "name": "Defense Autonomy"},
            {"id": "climate_insurance", "name": "Climate Insurance"},
            {"id": "healthcare_operations", "name": "Healthcare Operations"},
            {"id": "industrial_supply_chain", "name": "Industrial Supply Chain"},
            {"id": "energy_infrastructure", "name": "Energy Infrastructure"},
            {"id": "financial_intelligence", "name": "Financial Intelligence"},
            {"id": "regulatory_technology", "name": "Regulatory Technology"},
            {"id": "ai_infrastructure", "name": "AI Infrastructure"},
            {"id": "cross_sector", "name": "Cross-Sector"},
        ]

    def catalog(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "market_universes": self.market_universes(),
            "industry_domains": self.industry_domains(),
            "buyer_segments": self.buyer_segments(),
            "opportunity_objectives": self.opportunity_objectives(),
            "internal_routing_hints": self.internal_routing_hints(),
        }
