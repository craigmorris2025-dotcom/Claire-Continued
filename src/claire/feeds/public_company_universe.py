"""
Public Company Universe Feed Scaffold.

v5.46:
- Uses public company source catalog, index registry, offline resolver, and public-company live scan v1.
- Live metadata scanning is disabled by default and requires governance activation plus CLAIRE_ENABLE_LIVE_FEEDS=1.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.feeds.feed_result_contracts import FeedScanResult
from claire.feeds.source_catalogs.index_universe_registry import IndexUniverseRegistry
from claire.feeds.source_catalogs.offline_universe_resolver import OfflinePublicCompanyUniverseResolver
from claire.feeds.public_company_live_scan import PublicCompanyLiveScan


class PublicCompanyUniverseFeed:
    """Scaffold for S&P 500, DJIA, and NASDAQ Composite future connected feeds."""

    SUPPORTED = {"sp500_public", "djia_public", "nasdaq_composite"}

    def __init__(self) -> None:
        self.registry = IndexUniverseRegistry()
        self.resolver = OfflinePublicCompanyUniverseResolver()
        self.live_scan = PublicCompanyLiveScan()

    def supports(self, market_universe: str) -> bool:
        return market_universe in self.SUPPORTED

    def scan(self, market_universe: str, mode: str = "deterministic", filters: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.supports(market_universe):
            return {
                "status": "unsupported",
                "market_universe": market_universe,
                "feed_id": "public_company_universe",
            }

        filters = filters or {}
        resolved = self.registry.resolve(market_universe)
        offline_resolution = self.resolver.resolve(
            market_universe=market_universe,
            industry_domain=filters.get("industry_domain", "cross_sector"),
            buyer_segment=filters.get("buyer_segment", "enterprise_c_suite"),
            objective=filters.get("objective", "discover_market_gaps"),
        )

        if filters.get("_connected_ingestion_allowed") and mode in {"connected", "hybrid"}:
            live_result = self.live_scan.scan(
                market_universe=market_universe,
                execution_mode=mode,
                activation_decision=filters.get("_activation_decision", {}),
                source_urls=filters.get("source_urls", []),
                industry_domain=filters.get("industry_domain", "cross_sector"),
                buyer_segment=filters.get("buyer_segment", "enterprise_c_suite"),
                objective=filters.get("objective", "discover_market_gaps"),
                signal=filters.get("signal", ""),
            )
            live_result["source_catalog"] = resolved
            return live_result

        result = FeedScanResult.offline_stub(
            feed_id="public_company_universe",
            market_universe=market_universe,
            mode=mode,
        ).to_dict()
        result["source_catalog"] = resolved
        result["offline_universe_resolution"] = offline_resolution.get("resolution", {})
        result["records_found"] = 0
        result["signals"] = []
        result["warnings"] = [
            "Offline universe resolver is ready, but connected metadata scanning was not activated.",
            "Use connected or hybrid mode with feed activation governance before future live scanning.",
        ]
        return result
