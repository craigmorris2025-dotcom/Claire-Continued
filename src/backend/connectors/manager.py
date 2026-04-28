"""
ConnectorManager — orchestrates market, patent, financial connectors.
Respects operating mode (deterministic/connected/hybrid).
Provides unified data fetch for the pipeline.
"""
import logging
from typing import Any, Dict, List, Optional
from backend.connectors.base import BaseConnector
from backend.connectors.market import MarketConnector
from backend.connectors.patent import PatentConnector
from backend.connectors.financial import FinancialConnector

logger = logging.getLogger("claire.connectors.manager")


class ConnectorManager:
    """Central manager for all data connectors."""

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
        self._register_defaults()

    def _register_defaults(self):
        for conn in [MarketConnector(), PatentConnector(), FinancialConnector()]:
            self._connectors[conn.get_name()] = conn

    @property
    def available(self) -> List[str]:
        return list(self._connectors.keys())

    def get_connector(self, name: str) -> Optional[BaseConnector]:
        return self._connectors.get(name)

    def status(self) -> Dict[str, str]:
        return {name: "registered" for name in self._connectors}

    def fetch_all(self, query: Dict[str, Any], mode: str = "deterministic") -> Dict[str, Any]:
        """
        Fetch data from all connectors for a given query context.
        In deterministic mode, connectors return enriched fallback data.
        In connected/hybrid mode, connectors attempt live API calls first.
        """
        results = {}
        for name, connector in self._connectors.items():
            try:
                if mode == "deterministic":
                    data = connector.fallback(query)
                    data["source"] = "fallback"
                else:
                    data = connector.fetch(query, mode=mode)
                results[name] = data
            except Exception as e:
                logger.error(f"Connector {name} error: {e}")
                results[name] = {"connector": name, "error": str(e), "source": "error"}

        logger.info(f"ConnectorManager.fetch_all: mode={mode}, connectors={list(results.keys())}")
        return results

    def fetch_one(self, connector_name: str, query: Dict[str, Any],
                  mode: str = "deterministic") -> Dict[str, Any]:
        """Fetch from a single named connector."""
        connector = self._connectors.get(connector_name)
        if not connector:
            return {"error": f"Unknown connector: {connector_name}"}
        if mode == "deterministic":
            result = connector.fallback(query)
            result["source"] = "fallback"
            return result
        return connector.fetch(query, mode=mode)
