"""
Public Company Source Catalog.

v5.44:
- Defines safe source categories for S&P 500, DJIA, and NASDAQ Composite universe work.
- This is a catalog only. It does not scrape, call APIs, or fetch live data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from runtime_core.feeds.source_catalogs.source_contracts import (
    SourceCatalogResult,
    SourceDefinition,
    IndexUniverseDefinition,
)


class PublicCompanySourceCatalog:
    """Catalog of future public-company source families and public index universes."""

    def sources(self) -> List[SourceDefinition]:
        return [
            SourceDefinition(
                source_id="official_company_investor_relations",
                name="Official company investor relations pages",
                source_category="public_company_market_data",
                access_type="public_web",
                status="cataloged_not_ingesting",
                intended_use="Company descriptions, business segments, strategy updates, and public corporate disclosures.",
                examples=["issuer websites", "investor relations pages", "public press releases"],
                governance_notes=[
                    "Use public pages only.",
                    "No login, paywalled, private, or restricted data.",
                    "Connected ingestion must pass feed activation governance before use.",
                ],
            ),
            SourceDefinition(
                source_id="public_sec_filings",
                name="Public SEC filing references",
                source_category="public_company_market_data",
                access_type="public_regulatory",
                status="cataloged_not_ingesting",
                intended_use="Future filing-aware market pressure, risk, segment, and strategy signals.",
                examples=["10-K", "10-Q", "8-K", "registration statements"],
                governance_notes=[
                    "Public regulatory filings are allowed source candidates.",
                    "No insider, confidential, or non-public company information.",
                ],
            ),
            SourceDefinition(
                source_id="public_market_news",
                name="Public market and company news",
                source_category="public_company_market_data",
                access_type="public_news",
                status="cataloged_not_ingesting",
                intended_use="Future company movement, product launch, market pressure, and acquisition-signal awareness.",
                examples=["public news releases", "business news headlines", "public market commentary"],
                governance_notes=[
                    "Respect publisher terms and access boundaries.",
                    "Do not redistribute proprietary article bodies.",
                    "Use summaries/signals, not copyrighted full-text replication.",
                ],
            ),
            SourceDefinition(
                source_id="public_index_membership_reference",
                name="Public index membership reference",
                source_category="public_company_market_data",
                access_type="public_reference",
                status="cataloged_not_ingesting",
                intended_use="Universe membership mapping for S&P 500, DJIA, and NASDAQ Composite-style coverage.",
                examples=["index constituent references", "exchange-listed issuer references"],
                governance_notes=[
                    "Catalog stores target universe definitions only.",
                    "Actual live membership resolution will be implemented later.",
                ],
            ),
        ]

    def universes(self) -> List[IndexUniverseDefinition]:
        common_sources = [
            "official_company_investor_relations",
            "public_sec_filings",
            "public_market_news",
            "public_index_membership_reference",
        ]
        return [
            IndexUniverseDefinition(
                universe_id="sp500_public",
                name="S&P 500 public-company universe",
                coverage_target="503 companies / securities coverage target",
                market_category="large_cap_public_companies",
                source_category="public_company_market_data",
                source_ids=common_sources,
            ),
            IndexUniverseDefinition(
                universe_id="djia_public",
                name="Dow Jones Industrial Average blue-chip universe",
                coverage_target="30 companies",
                market_category="blue_chip_public_companies",
                source_category="public_company_market_data",
                source_ids=common_sources,
            ),
            IndexUniverseDefinition(
                universe_id="nasdaq_composite",
                name="NASDAQ Composite public-growth universe",
                coverage_target="3,300 companies coverage target",
                market_category="public_growth_and_technology_companies",
                source_category="public_company_market_data",
                source_ids=common_sources,
            ),
        ]

    def catalog(self) -> Dict[str, Any]:
        sources = [source.to_dict() for source in self.sources()]
        universes = [universe.to_dict() for universe in self.universes()]
        return SourceCatalogResult(
            status="success",
            catalog_name="public_company_source_catalog",
            generated_at=datetime.now(timezone.utc).isoformat(),
            source_count=len(sources),
            universe_count=len(universes),
            sources=sources,
            universes=universes,
            notes=[
                "This catalog does not perform live ingestion.",
                "Connected/hybrid live scans must pass feed activation governance first.",
                "The current purpose is source organization, source category mapping, and dashboard readiness.",
            ],
        ).to_dict()

    def universe(self, universe_id: str) -> Dict[str, Any]:
        for universe in self.universes():
            if universe.universe_id == universe_id:
                return {
                    "status": "success",
                    "universe": universe.to_dict(),
                    "sources": [
                        source.to_dict()
                        for source in self.sources()
                        if source.source_id in universe.source_ids
                    ],
                }
        return {
            "status": "not_found",
            "universe_id": universe_id,
            "sources": [],
        }
