"""Source freshness and scan planning."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from claire.live_intelligence.entity_registry import SourceEntityRegistry
from claire.live_intelligence.history_store import LiveIntelligenceHistoryStore


class SourceScanPlanner:
    """Build the next live intelligence scan plan from registry and history."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.registry = SourceEntityRegistry(project_root)
        self.history = LiveIntelligenceHistoryStore(project_root)

    def plan(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        entities = self.registry.entities(
            market_universe=payload.get("market_universe", "sp500_public"),
            industry_domain=payload.get("industry_domain", ""),
            limit=int(payload.get("entity_limit", 4) or 4),
        )
        families = self.registry.source_families()
        latest = self.history.latest()
        scan_items: List[Dict[str, Any]] = []
        for entity in entities:
            for family in families:
                scan_items.append({
                    "entity_id": entity.get("entity_id"),
                    "entity_name": entity.get("name"),
                    "ticker": entity.get("ticker"),
                    "source_family": family.get("family_id"),
                    "connector": family.get("connector"),
                    "freshness_days": family.get("freshness_days"),
                    "status": "due",
                    "reason": "starter planner schedules all selected entity/source family pairs for on-demand scans",
                })
        return {
            "status": "success",
            "planner": "source_scan_planner_v1",
            "entity_count": len(entities),
            "source_family_count": len(families),
            "scan_item_count": len(scan_items),
            "scan_items": scan_items,
            "latest_monitor_run": latest.get("monitor_run_id"),
            "latest_recorded_at": latest.get("recorded_at"),
            "planned_at": datetime.now(timezone.utc).isoformat(),
        }
