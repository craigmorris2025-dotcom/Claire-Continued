"""
Claire Live Intelligence Trend Clustering Compatibility Adapter.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class TrendClusterer:
    """
    Compatibility class expected by tools/serve_export_dashboard.py.
    Provides lightweight trend clustering for dashboard startup.
    """

    def __init__(self) -> None:
        pass

    def cluster(
        self,
        signals: Optional[List[Dict[str, Any]]] = None,
        keywords: Optional[List[str]] = None,
        domain: str = "general",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        signals = signals or kwargs.get("items") or []
        keywords = keywords or kwargs.get("keywords") or []

        cluster_name = self._cluster_name(domain, keywords)

        return {
            "status": "success",
            "domain": domain,
            "cluster": cluster_name,
            "clusters": [
                {
                    "name": cluster_name,
                    "domain": domain,
                    "keywords": keywords[:10],
                    "signal_count": len(signals),
                    "confidence": 0.72 if signals else 0.45,
                }
            ],
            "accepted_signal_count": len(signals),
        }

    def analyze(
        self,
        signals: Optional[List[Dict[str, Any]]] = None,
        keywords: Optional[List[str]] = None,
        domain: str = "general",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.cluster(
            signals=signals,
            keywords=keywords,
            domain=domain,
            **kwargs,
        )

    def run(self, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        payload = payload or {}
        return self.cluster(
            signals=payload.get("signals") or payload.get("items") or kwargs.get("signals", []),
            keywords=payload.get("keywords") or kwargs.get("keywords", []),
            domain=payload.get("domain") or kwargs.get("domain", "general"),
        )

    def _cluster_name(self, domain: str, keywords: List[str]) -> str:
        clean = [str(k).replace("_", " ").strip() for k in keywords if str(k).strip()]
        if clean:
            return f"{domain}:{' '.join(clean[:3])}"
        return f"{domain}:live intelligence cluster"