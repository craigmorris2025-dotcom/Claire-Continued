"""
Live source health and freshness checks.

Health checks are metadata-only and respect the same CLAIRE_ENABLE_LIVE_FEEDS gate
used by the public-company live scanner.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from claire.feeds.live_fetcher import SafePublicMetadataFetcher
from claire.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog


class LiveSourceHealthChecker:
    """Validate catalog sources and optionally perform safe public metadata checks."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[4]
        self.catalog = LiveSourceCatalog(self.project_root)
        self.fetcher = SafePublicMetadataFetcher()
        self.snapshot_path = self.project_root / "data" / "live_sources" / "source_health_snapshot.json"

    def snapshot(self) -> Dict[str, Any]:
        if not self.snapshot_path.exists():
            return {
                "status": "not_checked",
                "snapshot_path": str(self.snapshot_path),
                "message": "No live source health snapshot has been written yet.",
            }
        return json.loads(self.snapshot_path.read_text(encoding="utf-8-sig"))

    def check(
        self,
        market_universe: str = "sp500_public",
        limit: int = 5,
        fetch_live: bool = False,
    ) -> Dict[str, Any]:
        resolved = self.catalog.resolve(market_universe=market_universe, limit=limit)
        rows: List[Dict[str, Any]] = []
        live_fetch_performed = bool(fetch_live and self.fetcher.live_enabled())

        for source in resolved.get("sources", []):
            row = {
                "source_entry_id": source.get("source_entry_id"),
                "name": source.get("name"),
                "url": source.get("url"),
                "domain": source.get("domain"),
                "source_id": source.get("source_id"),
                "source_type": source.get("source_type"),
                "freshness_days": source.get("freshness_days"),
                "catalog_validation": source.get("validation", {}),
                "health_status": "catalog_valid",
                "checked_live": False,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
            if fetch_live:
                if not self.fetcher.live_enabled():
                    row["health_status"] = "live_disabled"
                    row["warning"] = "Live fetch requested but CLAIRE_ENABLE_LIVE_FEEDS is not enabled."
                else:
                    metadata = self.fetcher.fetch_metadata(source.get("url", ""))
                    row["checked_live"] = True
                    row["health_status"] = metadata.get("status", "unknown")
                    row["title"] = metadata.get("title", "")
                    row["snippet_present"] = bool(metadata.get("snippet"))
                    row["content_type"] = metadata.get("content_type")
                    row["bytes_read"] = metadata.get("bytes_read")
                    if metadata.get("warning"):
                        row["warning"] = metadata.get("warning")
            rows.append(row)

        healthy = [row for row in rows if row.get("health_status") in {"catalog_valid", "success"}]
        warnings = [row for row in rows if row.get("warning")]
        payload = {
            "status": "success",
            "checker": "live_source_health_checker_v1",
            "market_universe": market_universe,
            "source_count": len(rows),
            "healthy_count": len(healthy),
            "warning_count": len(warnings),
            "live_fetch_requested": bool(fetch_live),
            "live_fetch_performed": live_fetch_performed,
            "fetcher_status": self.fetcher.status(),
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "sources": rows,
            "resolver": {
                "status": resolved.get("status"),
                "catalog_version": resolved.get("catalog_version"),
                "warnings": resolved.get("warnings", []),
            },
        }
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
