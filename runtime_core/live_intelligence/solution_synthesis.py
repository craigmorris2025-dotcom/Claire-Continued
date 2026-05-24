"""
Claire Live Intelligence Solution Synthesis Compatibility Adapter.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from runtime_core.engines.breakthrough_synthesis_engine import BreakthroughSynthesisEngine


class SolutionSynthesisEngine:
    def __init__(self) -> None:
        self.engine = BreakthroughSynthesisEngine()

    def synthesize(
        self,
        text: str = "",
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        scores: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.engine.analyze(
            text=text or kwargs.get("raw_input", ""),
            domain=domain or kwargs.get("domain", "general"),
            keywords=keywords or kwargs.get("keywords", []),
            scores=scores or kwargs.get("scores", {}),
            market_gap=kwargs.get("market_gap", {}),
            trend_trajectory=kwargs.get("trend_trajectory", {}),
            market_formation=kwargs.get("market_formation", {}),
            opportunity_discovery=kwargs.get("opportunity_discovery", {}),
            moat=kwargs.get("moat", {}),
            risk_regulation=kwargs.get("risk_regulation", {}),
            business_model=kwargs.get("business_model", {}),
            connector_sources=connector_sources or kwargs.get("connector_sources", {}),
        )

    def analyze(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.synthesize(*args, **kwargs)

    def run(self, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        payload = payload or {}
        return self.synthesize(
            text=payload.get("text") or payload.get("raw_input") or kwargs.get("text", ""),
            domain=payload.get("domain") or kwargs.get("domain", "general"),
            keywords=payload.get("keywords") or kwargs.get("keywords", []),
            scores=payload.get("scores") or kwargs.get("scores", {}),
            connector_sources=payload.get("connector_sources") or payload.get("sources") or kwargs.get("connector_sources", {}),
            **payload,
        )