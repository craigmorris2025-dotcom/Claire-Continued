"""
Abstract connector interface — API-ready adapter pattern.
Each connector has: fetch() for live data, fallback() for offline/deterministic,
and is_available() for mode gating.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger("claire.connectors.base")


class BaseConnector(ABC):
    """All connectors implement this interface."""

    @abstractmethod
    def get_name(self) -> str:
        """Unique connector identifier."""
        ...

    @abstractmethod
    def fetch(self, query: Dict[str, Any], mode: str = "connected") -> Dict[str, Any]:
        """Fetch data — tries live API first, falls back to local data."""
        ...

    @abstractmethod
    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Return enriched local/cached data when API is unavailable."""
        ...

    def is_available(self, mode: str = "connected") -> bool:
        """Whether this connector is active in the given mode."""
        return mode in ("connected", "hybrid")

    def _safe_fetch(self, query: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Try live API, gracefully degrade to fallback."""
        if not self.is_available(mode):
            return {"source": "blocked", "reason": f"{self.get_name()} blocked in {mode} mode"}
        try:
            result = self._live_fetch(query)
            if result and not result.get("error"):
                result["source"] = "live"
                return result
        except Exception as e:
            logger.warning(f"{self.get_name()} live fetch failed: {e}")
        # Fallback
        result = self.fallback(query)
        result["source"] = "fallback"
        return result

    def _live_fetch(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Override this to implement actual API calls. Returns None to trigger fallback."""
        return None
