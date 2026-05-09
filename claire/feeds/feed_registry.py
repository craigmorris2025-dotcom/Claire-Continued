"""
Feed Registry — central connector registry for Claire live-feed scaffolding.

v5.41:
- Provides dashboard-visible feed status.
- Routes scan requests to scaffold feed classes.
- Does not activate connected ingestion by default.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.feeds.market_universe_feeds import market_universe_feed_coverage
from claire.feeds.public_company_universe import PublicCompanyUniverseFeed
from claire.feeds.private_establishment_universe import PrivateEstablishmentUniverseFeed
from claire.feeds.government_defense_universe import GovernmentDefenseUniverseFeed
from claire.feeds.feed_result_contracts import FeedScanResult


class FeedRegistry:
    """Registry for current and future market-universe feed connectors."""

    def __init__(self) -> None:
        self.feeds = [
            PublicCompanyUniverseFeed(),
            PrivateEstablishmentUniverseFeed(),
            GovernmentDefenseUniverseFeed(),
        ]

    def status(self) -> Dict[str, Any]:
        coverage = [item.to_dict() for item in market_universe_feed_coverage()]
        return {
            "status": "success",
            "feed_layer": "scaffold",
            "connected_ingestion_enabled": False,
            "deterministic_fallback_enabled": True,
            "mode_boundary": {
                "deterministic": "Uses offline taxonomy and protected opportunity generation only.",
                "connected": "Future mode for controlled external feed scanning.",
                "hybrid": "Future mode for governed fusion of deterministic candidates and connected market signals.",
            },
            "coverage_count": len(coverage),
            "coverage": coverage,
        }

    def scan(self, market_universe: str, mode: str = "deterministic", filters: Dict[str, Any] | None = None) -> Dict[str, Any]:
        for feed in self.feeds:
            if feed.supports(market_universe):
                return feed.scan(market_universe, mode=mode, filters=filters)
        return FeedScanResult.offline_stub(
            feed_id="generic_market_universe",
            market_universe=market_universe,
            mode=mode,
        ).to_dict()

    def list_feed_ids(self) -> List[str]:
        return [
            "public_company_universe",
            "private_establishment_universe",
            "government_defense_universe",
        ]
