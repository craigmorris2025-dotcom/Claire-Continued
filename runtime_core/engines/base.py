"""
Abstract base engine — all 24 domain engines inherit from this.
Each engine receives the pipeline context, computes a score, and returns enriched data.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseEngine(ABC):
    """Interface for all domain engines."""

    @abstractmethod
    def get_key(self) -> str:
        """Unique engine identifier."""
        ...

    @abstractmethod
    def get_phase(self) -> str:
        """Which processing phase this engine belongs to."""
        ...

    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input context and return enriched data with a score.
        Must set context[self.get_key() + "_score"] before returning.
        """
        ...

    def _clamp(self, value: float) -> float:
        """Clamp a score to [0, 1]."""
        return max(0.0, min(1.0, value))

    def _text_signal(self, text: str, keywords: set) -> float:
        """Calculate signal strength from keyword overlap."""
        words = set(text.lower().split())
        hits = words & keywords
        if not hits:
            return 0.0
        return min(1.0, len(hits) / max(len(keywords), 1) * 4.0)

    def _get_connector(self, context: Dict[str, Any],
                       connector_name: str) -> Dict[str, Any]:
        """Safely retrieve connector data by name."""
        return (context.get("connector_data", {})
                .get(connector_name, {})
                .get("data", {}))

    def _get_market_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_connector(context, "market")

    def _get_patent_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_connector(context, "patent")

    def _get_financial_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_connector(context, "financial")

    def _score_with_detail(self, context: Dict[str, Any],
                           score: float, detail: Dict[str, Any]) -> Dict[str, Any]:
        """Set score and store engine detail breakdown in context."""
        key = self.get_key()
        clamped = self._clamp(score)
        context[f"{key}_score"] = round(clamped, 4)
        context.setdefault("engine_details", {})[key] = {
            "score": round(clamped, 4),
            "phase": self.get_phase(),
            **detail,
        }
        return context
