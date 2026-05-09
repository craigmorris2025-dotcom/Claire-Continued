"""
Financial Data Connector — valuation + financial health intelligence
Fully self-contained (no backend dependency)
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("claire.connectors.financial")


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
# FINANCIAL DATA
# =========================
FINANCIAL_DATA = {
    "technology": {
        "gross_margin": 0.72,
        "rd_spend": 0.18,
        "debt_equity": 0.35,
        "valuation_signal": 0.65
    },
    "finance": {
        "gross_margin": 0.45,
        "rd_spend": 0.10,
        "debt_equity": 0.70,
        "valuation_signal": 0.60
    },
    "healthcare": {
        "gross_margin": 0.65,
        "rd_spend": 0.22,
        "debt_equity": 0.42,
        "valuation_signal": 0.68
    }
}


# =========================
# CONNECTOR
# =========================
class FinancialConnector(BaseConnector):

    def get_name(self) -> str:
        return "financial"

    def fetch(self, query: Any, mode: str = "connected") -> Dict[str, Any]:

        # Normalize input (pipeline sends string)
        if isinstance(query, str):
            query = {
                "domain": "technology",
                "keywords": query.split()
            }

        return self._safe_fetch(query, mode)

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:

        sector = query.get("domain", "technology").lower()
        if sector not in FINANCIAL_DATA:
            sector = "technology"

        data = FINANCIAL_DATA[sector]

        margin = data["gross_margin"]
        rd = data["rd_spend"]
        leverage = data["debt_equity"]
        valuation = data["valuation_signal"]

        # Core outputs your pipeline uses
        health = round((margin * 0.5 + rd * 0.2 + valuation * 0.3), 4)
        risk = round(leverage * 0.7 + (1 - valuation) * 0.3, 4)

        logger.info(f"Financial fallback: sector={sector}, health={health}, risk={risk}")

        return {
            "health": health,
            "risk": risk
        }
