"""
Patent Data Connector — innovation + patent intelligence
Fully self-contained (no backend dependency)
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("claire.connectors.patent")


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
# PATENT DATA
# =========================
PATENT_DATA = {
    "technology": {
        "density": 0.82,
        "novelty": 0.65,
        "cliff_risk": 0.08
    },
    "finance": {
        "density": 0.55,
        "novelty": 0.50,
        "cliff_risk": 0.12
    },
    "healthcare": {
        "density": 0.73,
        "novelty": 0.68,
        "cliff_risk": 0.22
    }
}


# =========================
# CONNECTOR
# =========================
class PatentConnector(BaseConnector):

    def get_name(self) -> str:
        return "patent"

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
        if sector not in PATENT_DATA:
            sector = "technology"

        data = PATENT_DATA[sector]

        density = data["density"]
        novelty = data["novelty"]
        risk = data["cliff_risk"]

        # Core outputs your pipeline uses
        activity = round(density * 0.7 + novelty * 0.3, 4)
        novelty_score = round(novelty * (1 - risk), 4)

        logger.info(f"Patent fallback: sector={sector}, activity={activity}, novelty={novelty_score}")

        return {
            "activity": activity,
            "novelty": novelty_score
        }
