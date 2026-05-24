"""
Public Company Live Scan v1.

v5.46:
- First controlled public-company metadata scan layer.
- Fetches public page title/meta-description only when:
  1) connected/hybrid activation is allowed,
  2) source category is allowlisted,
  3) PLATFORM_ENABLE_LIVE_FEEDS=1,
  4) caller supplies public URLs.
- Does not scrape private data, restricted data, or full article bodies.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.feeds.live_fetcher import SafePublicMetadataFetcher
from runtime_core.feeds.public_signal_contracts import PublicCompanySignal
from runtime_core.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog
from runtime_core.feeds.source_catalogs.offline_universe_resolver import OfflinePublicCompanyUniverseResolver


class PublicCompanyLiveScan:
    """Controlled public metadata scanner for public-company universes."""

    SUPPORTED = {"sp500_public", "djia_public", "nasdaq_composite"}

    def __init__(self) -> None:
        self.fetcher = SafePublicMetadataFetcher()
        self.resolver = OfflinePublicCompanyUniverseResolver()
        self.live_catalog = LiveSourceCatalog()

    def status(self) -> Dict[str, Any]:
        fetcher_status = self.fetcher.status()
        return {
            "status": "success",
            "scanner": "public_company_live_scan_v1",
            "supported_universes": sorted(self.SUPPORTED),
            "live_enabled": fetcher_status.get("live_enabled"),
            "fetcher": fetcher_status,
            "safe_metadata_only": True,
            "requires_feed_activation": True,
            "requires_user_or_catalog_urls": False,
            "catalog_resolver": self.live_catalog.status(),
        }

    def scan(
        self,
        market_universe: str,
        execution_mode: str = "connected",
        activation_decision: Dict[str, Any] | None = None,
        source_urls: List[str] | None = None,
        catalog_limit: int = 5,
        industry_domain: str = "cross_sector",
        buyer_segment: str = "enterprise_c_suite",
        objective: str = "discover_market_gaps",
        signal: str = "",
    ) -> Dict[str, Any]:
        activation_decision = activation_decision or {}
        source_urls = [url for url in (source_urls or []) if str(url).strip()]

        if market_universe not in self.SUPPORTED:
            return {
                "status": "unsupported_universe",
                "market_universe": market_universe,
                "signals": [],
                "warnings": ["Public-company live scan v1 supports S&P 500, DJIA, and NASDAQ Composite universes only."],
            }

        offline = self.resolver.resolve(
            market_universe=market_universe,
            industry_domain=industry_domain,
            buyer_segment=buyer_segment,
            objective=objective,
        )

        if not activation_decision.get("connected_ingestion_allowed"):
            return {
                "status": "activation_not_allowed",
                "market_universe": market_universe,
                "signals": [],
                "offline_universe_resolution": offline.get("resolution", {}),
                "activation_decision": activation_decision,
                "warnings": ["Connected ingestion was not allowed. Deterministic offline resolver remains available."],
            }

        if not self.fetcher.live_enabled():
            return {
                "status": "live_disabled",
                "market_universe": market_universe,
                "signals": [],
                "offline_universe_resolution": offline.get("resolution", {}),
                "activation_decision": activation_decision,
                "warnings": [
                    "Live feed scanner is installed but disabled.",
                    "Set PLATFORM_ENABLE_LIVE_FEEDS=1 before starting the dashboard to enable controlled public metadata fetches.",
                ],
            }

        catalog_resolution: Dict[str, Any] | None = None
        if not source_urls:
            catalog_resolution = self.live_catalog.resolve(
                market_universe=market_universe,
                limit=catalog_limit,
            )
            source_urls = catalog_resolution.get("source_urls", [])

        if not source_urls:
            return {
                "status": "ready_needs_sources",
                "market_universe": market_universe,
                "signals": [],
                "offline_universe_resolution": offline.get("resolution", {}),
                "activation_decision": activation_decision,
                "catalog_resolution": catalog_resolution,
                "warnings": [
                    "Live scanner is enabled and governance allowed, but no public source URLs were provided.",
                    "The live source catalog did not resolve scan-ready URLs for this selection.",
                ],
            }

        signals: List[Dict[str, Any]] = []
        warnings: List[str] = []
        for url in source_urls[:catalog_limit]:
            metadata = self.fetcher.fetch_metadata(url)
            if metadata.get("status") != "success":
                warnings.append(f"{url}: {metadata.get('warning', metadata.get('status'))}")
            signal_obj = PublicCompanySignal.create(
                market_universe=market_universe,
                source_url=url,
                source_category=activation_decision.get("source_category", "public_company_market_data"),
                signal_type="public_metadata",
                title=metadata.get("title") or "No title extracted",
                snippet=metadata.get("snippet") or "No public metadata snippet extracted",
                status=metadata.get("status", "unknown"),
                warnings=[metadata.get("warning")] if metadata.get("warning") else [],
                metadata={
                    "execution_mode": execution_mode,
                    "industry_domain": industry_domain,
                    "buyer_segment": buyer_segment,
                    "objective": objective,
                    "signal": signal,
                    "content_type": metadata.get("content_type"),
                    "bytes_read": metadata.get("bytes_read"),
                },
            )
            signals.append(signal_obj.to_dict())

        return {
            "status": "success",
            "market_universe": market_universe,
            "execution_mode": execution_mode,
            "record_count": len(signals),
            "signals": signals,
            "offline_universe_resolution": offline.get("resolution", {}),
            "activation_decision": activation_decision,
            "catalog_resolution": catalog_resolution,
            "catalog_sources_used": bool(catalog_resolution and catalog_resolution.get("source_urls")),
            "warnings": warnings,
            "safe_metadata_only": True,
        }
