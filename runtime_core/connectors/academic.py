"""
Academic Connector — research signal provider
Fully self-contained (no backend dependencies)
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("claire.connectors.academic")


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
class AcademicConnector(BaseConnector):

    def get_name(self) -> str:
        return "academic"

    def fetch(self, query: Any, mode: str = "deterministic") -> Dict[str, Any]:

        # Normalize input
        if isinstance(query, str):
            query = {
                "domain": "technology",
                "keywords": query.split()
            }

        return self._safe_fetch(query, mode)

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:

        domain = query.get("domain", "technology")
        keywords = query.get("keywords", [])

        # Simple heuristic signals (stable + deterministic)
        keyword_strength = min(1.0, len(keywords) / 10)

        citation_density = round(0.4 + keyword_strength * 0.4, 4)
        research_maturity = round(0.45 + keyword_strength * 0.3, 4)

        logger.info(
            f"Academic fallback: domain={domain}, "
            f"citation_density={citation_density}, maturity={research_maturity}"
        )

        return {
            "citation_density": citation_density,
            "research_maturity": research_maturity
        }
