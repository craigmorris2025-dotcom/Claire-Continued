"""
Index Universe Registry.

v5.44:
- Resolver for public-company universe IDs.
- No network calls or live membership resolution.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.feeds.source_catalogs.public_company_sources import PublicCompanySourceCatalog


class IndexUniverseRegistry:
    """Resolve public index universes to coverage and source-category metadata."""

    def __init__(self) -> None:
        self.catalog = PublicCompanySourceCatalog()

    def resolve(self, universe_id: str) -> Dict[str, Any]:
        result = self.catalog.universe(universe_id)
        if result.get("status") != "success":
            return {
                "status": "not_found",
                "universe_id": universe_id,
                "deterministic_fallback": True,
                "connected_scan_status": "not_enabled",
            }

        universe = result["universe"]
        return {
            "status": "success",
            "universe_id": universe_id,
            "name": universe.get("name"),
            "coverage_target": universe.get("coverage_target"),
            "market_category": universe.get("market_category"),
            "source_category": universe.get("source_category"),
            "source_ids": universe.get("source_ids", []),
            "source_count": len(result.get("sources", [])),
            "deterministic_fallback": universe.get("deterministic_fallback", True),
            "connected_scan_status": universe.get("connected_scan_status", "not_enabled"),
            "ready_for_future_live_connector": True,
        }

    def all(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "universes": [
                self.resolve(universe.universe_id)
                for universe in self.catalog.universes()
            ],
        }
