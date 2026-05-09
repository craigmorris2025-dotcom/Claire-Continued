"""
Feed signal registry.

v5.47:
- Keeps recent normalized signals available to the local dashboard.
- This is intentionally local/in-memory for the dashboard build phase.
"""

from __future__ import annotations

from typing import Any, Dict, List


class SignalRegistry:
    """Small in-memory registry for normalized feed signals."""

    def __init__(self, max_items: int = 200) -> None:
        self.max_items = max_items
        self._signals: List[Dict[str, Any]] = []

    def put_many(self, signals: List[Dict[str, Any]] | None) -> Dict[str, Any]:
        incoming = [signal for signal in (signals or []) if isinstance(signal, dict)]
        if incoming:
            self._signals = (incoming + self._signals)[: self.max_items]
        return self.status()

    def list(self, limit: int = 50) -> Dict[str, Any]:
        limit = max(1, min(int(limit or 50), self.max_items))
        signals = self._signals[:limit]
        return {
            "status": "success",
            "signal_count": len(self._signals),
            "returned_count": len(signals),
            "signals": signals,
            "summary": self.summary(signals),
        }

    def status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "registry": "feed_signal_registry_v1",
            "signal_count": len(self._signals),
            "max_items": self.max_items,
            "summary": self.summary(self._signals),
        }

    def clear(self) -> Dict[str, Any]:
        self._signals = []
        return self.status()

    def summary(self, signals: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        items = signals or []
        if not items:
            return {
                "safe_to_enrich_count": 0,
                "high_relevance_count": 0,
                "source_categories": [],
                "signal_types": [],
            }
        return {
            "safe_to_enrich_count": sum(1 for item in items if item.get("safe_to_enrich")),
            "high_relevance_count": sum(1 for item in items if item.get("opportunity_relevance") == "high"),
            "source_categories": sorted({str(item.get("source_category")) for item in items if item.get("source_category")}),
            "signal_types": sorted({str(item.get("signal_type")) for item in items if item.get("signal_type")}),
        }


SIGNAL_REGISTRY = SignalRegistry()


__all__ = ["SIGNAL_REGISTRY", "SignalRegistry"]
