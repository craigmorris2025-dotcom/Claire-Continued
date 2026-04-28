"""
News Connector — fetches news/press data for engine context.
Uses WebFetcher for outbound requests when in connected/hybrid mode.
"""
import logging
from typing import Any, Dict
from backend.connectors.base import BaseConnector

logger = logging.getLogger("claire.connectors.news")


class NewsConnector(BaseConnector):
    """News and press release data connector."""

    name = "news"
    source_type = "news"

    # Free/open news endpoints the fetcher can hit
    ENDPOINTS = {
        "newsapi": "https://newsapi.org/v2/everything",
        "gnews": "https://gnews.io/api/v4/search",
    }

    def fetch(self, query: Dict[str, Any], mode: str = "deterministic") -> Dict[str, Any]:
        if mode == "deterministic":
            return self._deterministic(query)
        return self._connected(query)

    def _deterministic(self, query: Dict[str, Any]) -> Dict[str, Any]:
        domain = query.get("domain", "technology")
        keywords = query.get("keywords", [])
        return {
            "source": "deterministic",
            "connector": self.name,
            "articles": [],
            "sentiment_score": 0.65,
            "coverage_score": 0.50,
            "domain": domain,
            "keywords": keywords,
            "note": "No live news data — deterministic fallback",
        }

    def _connected(self, query: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from backend.connectors.web_fetcher import get_fetcher
            fetcher = get_fetcher()
            keywords = " ".join(query.get("keywords", [query.get("domain", "technology")]))
            api_key = self._get_api_key("CLAIRE_NEWS_API_KEY")

            if api_key:
                data = fetcher.get(self.ENDPOINTS["newsapi"], params={
                    "q": keywords, "sortBy": "relevancy",
                    "pageSize": "10", "apiKey": api_key,
                })
                if data and "articles" in data:
                    articles = data["articles"][:10]
                    return {
                        "source": "newsapi",
                        "connector": self.name,
                        "articles": [{"title": a.get("title",""), "source": a.get("source",{}).get("name","")}
                                     for a in articles],
                        "sentiment_score": 0.65,
                        "coverage_score": min(1.0, len(articles) / 10),
                        "article_count": len(articles),
                    }

            # Fallback to deterministic if no API key or fetch fails
            return self._deterministic(query)

        except Exception as e:
            logger.warning(f"News connector error: {e}")
            return self._deterministic(query)
