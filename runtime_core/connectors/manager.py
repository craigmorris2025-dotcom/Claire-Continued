"""
ConnectorManager — unified connector orchestration (v5 clean)

- No backend dependencies
- Accepts raw string input (pipeline-compatible)
- Returns clean flat signals (no mutation)
"""

import logging
from typing import Dict, Any

from runtime_core.connectors.market import MarketConnector
from runtime_core.connectors.patent import PatentConnector
from runtime_core.connectors.financial import FinancialConnector

logger = logging.getLogger("claire.connectors.manager")


class ConnectorManager:

    def __init__(self):
        self.market = MarketConnector()
        self.patent = PatentConnector()
        self.financial = FinancialConnector()

    # =========================
    # MAIN FETCH
    # =========================
    def fetch_all(self, query: Any) -> Dict[str, Any]:
        """
        Pipeline passes raw text → connectors normalize internally
        Returns clean signals used directly by scoring engine
        """

        try:
            results = {
                "market": self.market.fetch(query),
                "patent": self.patent.fetch(query),
                "financial": self.financial.fetch(query),
            }

            logger.info("ConnectorManager.fetch_all successful")
            return results

        except Exception as e:
            logger.error(f"ConnectorManager failure: {e}")

            # Safe fallback (prevents pipeline crash)
            return {
                "market": {"growth": 0.5, "volatility": 0.5},
                "patent": {"activity": 0.4, "novelty": 0.4},
                "financial": {"health": 0.5, "risk": 0.5},
            }
