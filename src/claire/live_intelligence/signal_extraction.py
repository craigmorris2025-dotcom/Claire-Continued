"""
Claire Live Intelligence Signal Extraction Compatibility Adapter.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from claire.engines.signal_extraction_engine import SignalExtractionEngine


class SignalExtractionWorker:
    def __init__(self) -> None:
        self.engine = SignalExtractionEngine()

    def extract(
        self,
        text: str = "",
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.engine.analyze(
            text=text or kwargs.get("raw_input", ""),
            domain=domain or kwargs.get("domain", "general"),
            keywords=keywords or kwargs.get("keywords", []),
            connector_sources=connector_sources or kwargs.get("connector_sources", {}),
        )

    def analyze(
        self,
        text: str = "",
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.extract(
            text=text,
            domain=domain,
            keywords=keywords,
            connector_sources=connector_sources,
            **kwargs,
        )

    def run(self, payload: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        payload = payload or {}
        return self.extract(
            text=payload.get("text") or payload.get("raw_input") or kwargs.get("text", ""),
            domain=payload.get("domain") or kwargs.get("domain", "general"),
            keywords=payload.get("keywords") or kwargs.get("keywords", []),
            connector_sources=payload.get("connector_sources") or payload.get("sources") or kwargs.get("connector_sources", {}),
        )