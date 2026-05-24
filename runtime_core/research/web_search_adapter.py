"""Adapter interface for future governed web search and browsing."""

from __future__ import annotations

from typing import Any, Dict, List


class WebSearchAdapter:
    """Placeholder adapter. It does not fake live web results."""

    configured = False

    def search_web(self, query: str) -> Dict[str, Any]:
        return {
            "status": "unavailable",
            "reason": "Live web search not configured yet.",
            "query": query,
            "results": [],
        }

    def fetch_page(self, url: str) -> Dict[str, Any]:
        return {
            "status": "unavailable",
            "reason": "Live page browsing/fetching not configured yet.",
            "url": url,
        }

    def extract_text(self, source: Dict[str, Any]) -> str:
        return str(source.get("text") or source.get("summary") or "")

    def extract_signals(self, source: Dict[str, Any]) -> List[str]:
        text = self.extract_text(source)
        return [part.strip() for part in text.replace(".", ",").split(",") if len(part.strip()) > 12][:8]

    def score_source(self, source: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "source_credibility": 0.0,
            "freshness": 0.0,
            "governance_status": "unavailable",
            "reason": "Live web source scoring requires a configured provider.",
        }
