"""
Market Data Connector — sector-adaptive market intelligence.
Fully self-contained (no backend dependencies)
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("claire.connectors.market")


# =========================
# BASE CONNECTOR (LOCAL)
# =========================
class BaseConnector:
    def _safe_fetch(self, query: Dict[str, Any], mode: str = "connected") -> Dict[str, Any]:
        try:
            if mode == "connected":
                live = self._live_fetch(query)
                if live:
                    return live
        except Exception as e:
            logger.warning(f"Live fetch failed: {e}")

        return self.fallback(query)

    def _live_fetch(self, query: Dict[str, Any]) -> Dict[str, Any]:
        return None

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:
        return {}


# =========================
# SECTOR DATA
# =========================
SECTOR_DATA = {
    "technology": {
        "growth_rate": 0.12,
        "volatility": 0.18,
        "market_drivers": [
            "AI adoption",
            "cloud expansion",
            "cybersecurity demand"
        ]
    },
    "finance": {
        "growth_rate": 0.07,
        "volatility": 0.16,
        "market_drivers": [
            "fintech expansion",
            "digital banking",
            "real-time payments"
        ]
    },
    "healthcare": {
        "growth_rate": 0.09,
        "volatility": 0.14,
        "market_drivers": [
            "aging population",
            "biotech innovation",
            "AI diagnostics"
        ]
    }
}


# =========================
# DOMAIN MAPPING
# =========================
def _domain_to_sector(domain: str) -> str:
    mapping = {
        "technology": "technology",
        "finance": "finance",
        "healthcare": "healthcare",
    }
    return mapping.get(domain.lower(), "technology")


# =========================
# CONNECTOR
# =========================
class MarketConnector(BaseConnector):

    def get_name(self) -> str:
        return "market"

    def fetch(self, query: Any, mode: str = "connected") -> Dict[str, Any]:

        # Normalize input
        if isinstance(query, str):
            query = {
                "domain": "technology",
                "keywords": query.split()
            }

        return self._safe_fetch(query, mode)

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:

        sector = _domain_to_sector(query.get("domain", "technology"))
        data = SECTOR_DATA.get(sector, SECTOR_DATA["technology"])

        keywords = query.get("keywords", [])

        # simple driver alignment
        hits = 0
        for driver in data["market_drivers"]:
            for kw in keywords:
                if kw.lower() in driver.lower():
                    hits += 1

        alignment = min(1.0, hits / max(len(data["market_drivers"]), 1))

        result = {
            "growth": data["growth_rate"],
            "volatility": data["volatility"],
            "alignment": alignment
        }

        return result
