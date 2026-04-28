"""
Academic Connector — fetches academic/research data for engine context.
Uses WebFetcher for outbound requests when in connected/hybrid mode.
"""
import logging
from typing import Any, Dict
from backend.connectors.base import BaseConnector

logger = logging.getLogger("claire.connectors.academic")


class AcademicConnector(BaseConnector):
    """Academic and research paper data connector."""

    name = "academic"
    source_type = "academic"

    ENDPOINTS = {
        "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search",
        "crossref": "https://api.crossref.org/works",
    }

    def fetch(self, query: Dict[str, Any], mode: str = "deterministic") -> Dict[str, Any]:
        if mode == "deterministic":
            return self._deterministic(query)
        return self._connected(query)

    def _deterministic(self, query: Dict[str, Any]) -> Dict[str, Any]:
        domain = query.get("domain", "technology")
        return {
            "source": "deterministic",
            "connector": self.name,
            "papers": [],
            "citation_density": 0.50,
            "research_maturity": 0.55,
            "domain": domain,
            "note": "No live academic data — deterministic fallback",
        }

    def _connected(self, query: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from backend.connectors.web_fetcher import get_fetcher
            fetcher = get_fetcher()
            keywords = " ".join(query.get("keywords", [query.get("domain", "technology")]))

            # Try Semantic Scholar (free, no key needed)
            data = fetcher.get(self.ENDPOINTS["semantic_scholar"], params={
                "query": keywords, "limit": "10",
                "fields": "title,year,citationCount,abstract",
            })

            if data and "data" in data:
                papers = data["data"][:10]
                avg_citations = sum(p.get("citationCount", 0) for p in papers) / max(len(papers), 1)
                return {
                    "source": "semantic_scholar",
                    "connector": self.name,
                    "papers": [{"title": p.get("title",""), "year": p.get("year"),
                                "citations": p.get("citationCount",0)} for p in papers],
                    "citation_density": min(1.0, avg_citations / 100),
                    "research_maturity": min(1.0, len(papers) / 10),
                    "paper_count": len(papers),
                }

            return self._deterministic(query)

        except Exception as e:
            logger.warning(f"Academic connector error: {e}")
            return self._deterministic(query)
