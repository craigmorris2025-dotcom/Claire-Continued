"""
News Connector — sentiment + coverage signal
Fully self-contained (no backend dependencies)
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("claire.connectors.news")


# =========================
# BASE CONNECTOR (LOCAL)
# =========================
class BaseConnector:
    def _safe_fetch(self, query: Dict[str, Any], mode: str = "deterministic") -> Dict[str, Any]:
        try:
            if mode != "deterministic":
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
# CONNECTOR
# =========================
class NewsConnector(BaseConnector):

    def get_name(self) -> str:
        return "news"

    def fetch(self, query: Any, mode: str = "deterministic") -> Dict[str, Any]:

        # Normalize input (pipeline sends string)
        if isinstance(query, str):
            query = {
                "domain": "technology",
                "keywords": query.split()
            }

        return self._safe_fetch(query, mode)

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:

        keywords = query.get("keywords", [])
        domain = query.get("domain", "technology")

        # Simple deterministic signal generation
        keyword_strength = min(1.0, len(keywords) / 10)

        sentiment = round(0.55 + keyword_strength * 0.3, 4)
        coverage = round(0.4 + keyword_strength * 0.4, 4)

        logger.info(
            f"News fallback: domain={domain}, sentiment={sentiment}, coverage={coverage}"
        )

        return {
            "sentiment": sentiment,
            "coverage": coverage
        }
