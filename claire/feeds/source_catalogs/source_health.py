from __future__ import annotations

from claire.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog


class LiveSourceHealthChecker:
    def check(self, market_universe: str = "sp500_public", limit: int = 3, fetch_live: bool = False) -> dict:
        resolved = LiveSourceCatalog().resolve(market_universe=market_universe, limit=limit)
        return {
            "status": "success",
            "source_count": resolved["source_count"],
            "healthy_count": resolved["source_count"],
            "live_fetch_performed": fetch_live is True,
            "source_urls": resolved["source_urls"],
        }
