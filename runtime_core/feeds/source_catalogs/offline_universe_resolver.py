"""
Offline Public-Company Universe Resolver.

v5.45:
- Resolves S&P 500, DJIA, and NASDAQ Composite launch selections into offline coverage metadata.
- Does not fetch live membership or perform external ingestion.
- Gives Claire a stable deterministic resolver before public-company live scan v1.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.feeds.source_catalogs.index_universe_registry import IndexUniverseRegistry
from runtime_core.feeds.source_catalogs.universe_resolution_contracts import (
    OfflineCoverageBucket,
    OfflineUniverseResolution,
)


class OfflinePublicCompanyUniverseResolver:
    """Resolve public-company market universes into deterministic offline scan plans."""

    def __init__(self) -> None:
        self.registry = IndexUniverseRegistry()

    def status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "resolver": "offline_public_company_universe_resolver",
            "live_ingestion_enabled": False,
            "deterministic_fallback_enabled": True,
            "supported_universes": ["sp500_public", "djia_public", "nasdaq_composite"],
            "purpose": "Prepare stable universe metadata, scan lenses, and opportunity coverage buckets before live ingestion.",
        }

    def resolve(
        self,
        market_universe: str = "sp500_public",
        industry_domain: str = "cross_sector",
        buyer_segment: str = "enterprise_c_suite",
        objective: str = "discover_market_gaps",
    ) -> Dict[str, Any]:
        base = self.registry.resolve(market_universe)
        if base.get("status") != "success":
            return {
                "status": "not_found",
                "market_universe": market_universe,
                "resolution_status": "unsupported_universe",
                "deterministic_fallback": True,
                "connected_scan_status": "not_enabled",
            }

        resolution = OfflineUniverseResolution(
            universe_id=market_universe,
            name=base.get("name"),
            coverage_target=base.get("coverage_target"),
            source_category=base.get("source_category"),
            market_category=base.get("market_category"),
            coverage_buckets=[bucket.to_dict() for bucket in self._buckets(market_universe, industry_domain, buyer_segment, objective)],
            recommended_use=self._recommended_use(market_universe, objective),
            warnings=[
                "Offline resolver does not include live membership resolution.",
                "Use connected/hybrid mode with feed activation governance before future live public-company scanning.",
                "This layer prepares scan intent and opportunity coverage structure only.",
            ],
        )

        return {
            "status": "success",
            "resolution": resolution.to_dict(),
            "source_catalog": base,
        }

    def _buckets(
        self,
        market_universe: str,
        industry_domain: str,
        buyer_segment: str,
        objective: str,
    ) -> List[OfflineCoverageBucket]:
        universe_label = market_universe.replace("_", " ")
        industry_label = industry_domain.replace("_", " ")
        buyer_label = buyer_segment.replace("_", " ")
        objective_label = objective.replace("_", " ")

        common = [
            OfflineCoverageBucket(
                bucket_id="market_pressure",
                name="Market Pressure",
                purpose=f"Identify pressure affecting {industry_label} companies in the {universe_label} universe.",
                opportunity_lens="margin pressure, strategic urgency, public-company transformation need",
            ),
            OfflineCoverageBucket(
                bucket_id="capability_gap",
                name="Capability Gap",
                purpose=f"Find missing capabilities for {buyer_label}.",
                opportunity_lens=objective_label,
            ),
            OfflineCoverageBucket(
                bucket_id="workflow_friction",
                name="Workflow Friction",
                purpose="Locate repeated operational friction that can become a productized solution.",
                opportunity_lens="manual process, compliance burden, visibility gap, decision bottleneck",
            ),
            OfflineCoverageBucket(
                bucket_id="acquirer_logic",
                name="Strategic Acquirer Logic",
                purpose="Prepare acquisition-readiness reasoning before connected enrichment.",
                opportunity_lens="capability gap, portfolio fit, defensibility, speed-to-market",
            ),
        ]

        if market_universe == "nasdaq_composite":
            common.append(OfflineCoverageBucket(
                bucket_id="growth_technology_signal",
                name="Growth / Technology Signal",
                purpose="Prepare technology and growth-company opportunity lenses.",
                opportunity_lens="AI infrastructure, data operations, platform efficiency, software leverage",
            ))
        elif market_universe == "djia_public":
            common.append(OfflineCoverageBucket(
                bucket_id="blue_chip_modernization",
                name="Blue-Chip Modernization",
                purpose="Prepare mature-enterprise modernization opportunity lenses.",
                opportunity_lens="legacy systems, enterprise resilience, operating efficiency, executive visibility",
            ))
        elif market_universe == "sp500_public":
            common.append(OfflineCoverageBucket(
                bucket_id="large_cap_operating_gap",
                name="Large-Cap Operating Gap",
                purpose="Prepare large-cap enterprise opportunity lenses.",
                opportunity_lens="enterprise operations, risk visibility, governance, automation, market pressure",
            ))

        return common

    def _recommended_use(self, market_universe: str, objective: str) -> List[str]:
        return [
            f"Use {market_universe.replace('_', ' ')} to scope public-company opportunity discovery.",
            f"Use objective '{objective.replace('_', ' ')}' to select opportunity lenses.",
            "Generate protected opportunity candidates before connected enrichment.",
            "Use future live scan v1 only after feed activation governance allows connected/hybrid scanning.",
        ]
