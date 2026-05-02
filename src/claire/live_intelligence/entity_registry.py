"""Source entity registry for live intelligence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class SourceEntityRegistry:
    """Persistent registry of entities, source families, and freshness state."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.path = project_root / "data" / "live_intelligence" / "source_entity_registry.json"

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"status": "missing", "entities": [], "source_families": []}
        payload = json.loads(self.path.read_text(encoding="utf-8-sig"))
        payload["status"] = "success"
        return payload

    def status(self) -> Dict[str, Any]:
        payload = self.load()
        entities = payload.get("entities", [])
        families = payload.get("source_families", [])
        return {
            "status": payload.get("status", "success"),
            "registry_version": payload.get("registry_version"),
            "registry_path": str(self.path),
            "entity_count": len(entities),
            "source_family_count": len(families),
            "freshness_tracked": True,
            "scan_history_ready": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "entities": entities,
            "source_families": families,
        }

    def entities(
        self,
        market_universe: str = "sp500_public",
        industry_domain: str = "",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        rows = self.load().get("entities", [])
        if market_universe:
            rows = [row for row in rows if row.get("market_universe") == market_universe]
        if industry_domain:
            rows = [row for row in rows if row.get("industry_domain") == industry_domain]
        return rows[: max(0, int(limit))]

    def source_families(self) -> List[Dict[str, Any]]:
        return self.load().get("source_families", [])
