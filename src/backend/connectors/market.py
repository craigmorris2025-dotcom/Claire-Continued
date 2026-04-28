"""
Market Data Connector — sector-adaptive market intelligence.
API-ready: override _live_fetch() to wire to Alpha Vantage, Yahoo Finance, etc.
"""
import hashlib
import logging
import time
from typing import Any, Dict, List
from backend.connectors.base import BaseConnector

logger = logging.getLogger("claire.connectors.market")

# Rich sector intelligence database
SECTOR_DATA = {
    "defense": {
        "sector_pe": 22.1, "growth_rate": 0.08, "volatility": 0.09,
        "total_market_cap_b": 890, "avg_deal_size_m": 2100,
        "yoy_ma_activity": 0.07, "median_enterprise_value_b": 45.2,
        "top_segments": ["C4ISR", "Space Systems", "Cyber Operations", "Autonomous"],
        "market_drivers": ["DoD budget growth", "JADC2 modernization", "AI/ML mandate",
                          "Space Force expansion", "Cyber defense urgency"],
        "headwinds": ["Sequestration risk", "Supply chain constraints", "Workforce clearance delays"],
        "recent_deals": [
            {"acquirer": "L3Harris", "target": "Aerojet Rocketdyne", "value_b": 4.7, "year": 2023},
            {"acquirer": "Northrop", "target": "Orbital ATK", "value_b": 9.2, "year": 2018},
            {"acquirer": "Raytheon", "target": "United Technologies", "value_b": 135.0, "year": 2020},
        ],
        "regulatory": {"itar_applicable": True, "cfius_review": "likely", "export_controls": "strict"},
        "talent_market": {"clearance_premium_pct": 0.25, "stem_demand": "critical", "attrition_rate": 0.08},
    },
    "technology": {
        "sector_pe": 28.5, "growth_rate": 0.12, "volatility": 0.18,
        "total_market_cap_b": 12400, "avg_deal_size_m": 850,
        "yoy_ma_activity": 0.15, "median_enterprise_value_b": 8.5,
        "top_segments": ["AI/ML", "Cloud Infrastructure", "Cybersecurity", "Edge Computing", "Quantum"],
        "market_drivers": ["Enterprise AI adoption", "Cloud migration", "Zero trust security",
                          "Edge/IoT expansion", "Quantum computing R&D"],
        "headwinds": ["Valuation compression", "Regulatory scrutiny", "Talent competition"],
        "recent_deals": [
            {"acquirer": "Microsoft", "target": "Activision Blizzard", "value_b": 68.7, "year": 2023},
            {"acquirer": "Broadcom", "target": "VMware", "value_b": 61.0, "year": 2023},
            {"acquirer": "Cisco", "target": "Splunk", "value_b": 28.0, "year": 2024},
        ],
        "regulatory": {"itar_applicable": False, "cfius_review": "possible", "export_controls": "moderate"},
        "talent_market": {"clearance_premium_pct": 0.0, "stem_demand": "high", "attrition_rate": 0.15},
    },
    "healthcare": {
        "sector_pe": 19.8, "growth_rate": 0.09, "volatility": 0.14,
        "total_market_cap_b": 6200, "avg_deal_size_m": 620,
        "yoy_ma_activity": 0.11, "median_enterprise_value_b": 12.1,
        "top_segments": ["Biotech", "Digital Health", "Diagnostics", "MedTech", "Genomics"],
        "market_drivers": ["Aging population", "Precision medicine", "Telehealth expansion",
                          "AI diagnostics", "Gene therapy breakthroughs"],
        "headwinds": ["Drug pricing pressure", "FDA approval timelines", "Reimbursement uncertainty"],
        "recent_deals": [
            {"acquirer": "Pfizer", "target": "Seagen", "value_b": 43.0, "year": 2023},
            {"acquirer": "Amgen", "target": "Horizon Therapeutics", "value_b": 27.8, "year": 2023},
        ],
        "regulatory": {"itar_applicable": False, "cfius_review": "unlikely", "export_controls": "minimal"},
        "talent_market": {"clearance_premium_pct": 0.0, "stem_demand": "high", "attrition_rate": 0.12},
    },
    "energy": {
        "sector_pe": 15.2, "growth_rate": 0.06, "volatility": 0.22,
        "total_market_cap_b": 4100, "avg_deal_size_m": 1200,
        "yoy_ma_activity": 0.09, "median_enterprise_value_b": 22.5,
        "top_segments": ["Renewables", "Grid Modernization", "Energy Storage", "Hydrogen", "Nuclear"],
        "market_drivers": ["IRA incentives", "Grid resilience mandate", "EV infrastructure",
                          "Corporate net-zero commitments", "Energy security"],
        "headwinds": ["Interest rate sensitivity", "Permitting delays", "Supply chain bottlenecks"],
        "recent_deals": [
            {"acquirer": "Brookfield", "target": "Origin Energy", "value_b": 10.8, "year": 2023},
        ],
        "regulatory": {"itar_applicable": False, "cfius_review": "possible", "export_controls": "moderate"},
        "talent_market": {"clearance_premium_pct": 0.0, "stem_demand": "moderate", "attrition_rate": 0.10},
    },
    "aerospace": {
        "sector_pe": 24.3, "growth_rate": 0.10, "volatility": 0.13,
        "total_market_cap_b": 520, "avg_deal_size_m": 1800,
        "yoy_ma_activity": 0.06, "median_enterprise_value_b": 35.0,
        "top_segments": ["Satellite", "Launch Services", "Avionics", "Propulsion", "Space Situational Awareness"],
        "market_drivers": ["Commercial space growth", "Mega-constellations", "Hypersonic development",
                          "Space domain awareness", "Reusable launch systems"],
        "headwinds": ["Launch cadence constraints", "Orbital debris", "Spectrum allocation"],
        "recent_deals": [],
        "regulatory": {"itar_applicable": True, "cfius_review": "likely", "export_controls": "strict"},
        "talent_market": {"clearance_premium_pct": 0.20, "stem_demand": "critical", "attrition_rate": 0.07},
    },
    "infrastructure": {
        "sector_pe": 18.0, "growth_rate": 0.05, "volatility": 0.10,
        "total_market_cap_b": 3200, "avg_deal_size_m": 900,
        "yoy_ma_activity": 0.08, "median_enterprise_value_b": 15.0,
        "top_segments": ["Smart Grid", "5G/Telecom", "Water Systems", "Transportation", "Smart Cities"],
        "market_drivers": ["Infrastructure bill funding", "5G rollout", "Climate resilience",
                          "Smart city initiatives", "Water infrastructure aging"],
        "headwinds": ["Labor shortages", "Material cost inflation", "Permitting complexity"],
        "recent_deals": [],
        "regulatory": {"itar_applicable": False, "cfius_review": "possible", "export_controls": "minimal"},
        "talent_market": {"clearance_premium_pct": 0.0, "stem_demand": "moderate", "attrition_rate": 0.11},
    },
    "finance": {
        "sector_pe": 14.5, "growth_rate": 0.07, "volatility": 0.16,
        "total_market_cap_b": 8900, "avg_deal_size_m": 1500,
        "yoy_ma_activity": 0.10, "median_enterprise_value_b": 28.0,
        "top_segments": ["Fintech", "InsurTech", "Digital Banking", "RegTech", "Payments"],
        "market_drivers": ["Digital transformation", "Open banking", "AI-driven underwriting",
                          "Real-time payments", "Embedded finance"],
        "headwinds": ["Rate environment", "Regulatory tightening", "Cybersecurity threats"],
        "recent_deals": [],
        "regulatory": {"itar_applicable": False, "cfius_review": "possible", "export_controls": "minimal"},
        "talent_market": {"clearance_premium_pct": 0.0, "stem_demand": "high", "attrition_rate": 0.14},
    },
    "government": {
        "sector_pe": 16.0, "growth_rate": 0.04, "volatility": 0.06,
        "total_market_cap_b": 450, "avg_deal_size_m": 500,
        "yoy_ma_activity": 0.05, "median_enterprise_value_b": 8.0,
        "top_segments": ["IT Modernization", "Cloud Migration", "Cybersecurity", "Data Analytics"],
        "market_drivers": ["Federal IT modernization mandate", "Zero trust implementation",
                          "Cloud-first policy", "AI executive order"],
        "headwinds": ["Continuing resolutions", "Protest risk", "Clearance backlogs"],
        "recent_deals": [],
        "regulatory": {"itar_applicable": False, "cfius_review": "unlikely", "export_controls": "moderate"},
        "talent_market": {"clearance_premium_pct": 0.20, "stem_demand": "critical", "attrition_rate": 0.09},
    },
}


def _domain_to_sector(domain: str) -> str:
    """Map semantic domain to closest market sector."""
    mapping = {
        "defense": "defense", "technology": "technology", "healthcare": "healthcare",
        "energy": "energy", "aerospace": "aerospace", "infrastructure": "infrastructure",
        "finance": "finance", "government": "government",
    }
    return mapping.get(domain.lower(), "technology")


class MarketConnector(BaseConnector):
    def get_name(self) -> str:
        return "market"

    def fetch(self, query: Dict[str, Any], mode: str = "connected") -> Dict[str, Any]:
        return self._safe_fetch(query, mode)

    def _live_fetch(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override this to call a real market data API.
        Example integration points:
          - Alpha Vantage: sector performance, company fundamentals
          - Yahoo Finance: real-time quotes, sector ETFs
          - FRED: macroeconomic indicators
          - PitchBook/CB Insights: M&A activity (requires license)

        To integrate, set CLAIRE_MARKET_API_KEY in .env and implement here.
        Return None to trigger fallback.
        """
        return None  # Will trigger fallback — wire API here when ready

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:
        sector = _domain_to_sector(query.get("sector", query.get("domain", "technology")))
        data = SECTOR_DATA.get(sector, SECTOR_DATA["technology"])

        # Dynamic adjustments based on query context
        keywords = query.get("keywords", [])
        result = dict(data)
        result["sector"] = sector
        result["query_domain"] = query.get("domain", sector)

        # Boost signals if query keywords align with market drivers
        driver_hits = 0
        for driver in data.get("market_drivers", []):
            for kw in keywords:
                if kw.lower() in driver.lower():
                    driver_hits += 1
        result["driver_alignment"] = min(1.0, driver_hits / max(len(data.get("market_drivers", [1])), 1))
        result["market_timing_signal"] = round(
            data["growth_rate"] * 2 + result["driver_alignment"] * 0.3, 4
        )

        logger.info(f"Market fallback: sector={sector}, drivers_hit={driver_hits}, "
                     f"timing={result['market_timing_signal']:.3f}")
        return {"connector": "market", "sector": sector, "data": result}
