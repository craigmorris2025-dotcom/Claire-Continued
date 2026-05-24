"""Live source orchestration for governed desktop intelligence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from runtime_core.feeds.public_company_live_scan import PublicCompanyLiveScan
from runtime_core.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog
from runtime_core.feeds.source_catalogs.source_health import LiveSourceHealthChecker


class LiveSourceOrchestrator:
    """Prepare catalog sources, health checks, and metadata scan in one workflow."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.catalog = LiveSourceCatalog(project_root)
        self.health = LiveSourceHealthChecker(project_root)
        self.scanner = PublicCompanyLiveScan()

    def status(self) -> Dict[str, Any]:
        catalog_status = self.catalog.status()
        return {
            "status": "success" if catalog_status.get("status") == "success" else "partial",
            "orchestrator": "live_source_orchestrator_v1",
            "catalog_version": catalog_status.get("catalog_version"),
            "active_source_count": catalog_status.get("active_source_count", 0),
            "workflow": [
                "resolve_catalog_sources",
                "check_catalog_health",
                "run_governed_metadata_scan",
                "normalize_signals",
                "store_signal_registry",
            ],
            "desktop_live_ready": catalog_status.get("active_source_count", 0) > 0,
            "safe_metadata_only": True,
        }

    def run(
        self,
        payload: Dict[str, Any],
        activation_decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        market_universe = payload.get("market_universe", "sp500_public")
        limit = int(payload.get("catalog_limit", payload.get("limit", 5)) or 5)
        resolved = self.catalog.resolve(market_universe=market_universe, limit=limit)
        health = self.health.check(
            market_universe=market_universe,
            limit=limit,
            fetch_live=bool(payload.get("health_fetch_live", False)),
        )
        scan = self.scanner.scan(
            market_universe=market_universe,
            execution_mode=payload.get("execution_mode", "hybrid"),
            activation_decision=activation_decision,
            source_urls=resolved.get("source_urls", []),
            catalog_limit=limit,
            industry_domain=payload.get("industry_domain", "cross_sector"),
            buyer_segment=payload.get("buyer_segment", "enterprise_c_suite"),
            objective=payload.get("objective", "discover_market_gaps"),
            signal=payload.get("signal", ""),
        )
        ready = (
            resolved.get("status") == "success"
            and health.get("healthy_count", 0) > 0
            and scan.get("status") == "success"
        )
        return {
            "status": "success" if ready else scan.get("status", "partial"),
            "orchestrator": "live_source_orchestrator_v1",
            "market_universe": market_universe,
            "resolved": resolved,
            "health": health,
            "scan": scan,
            "live_intelligence_ready": ready,
            "safe_metadata_only": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
