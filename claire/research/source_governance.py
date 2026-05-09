"""Governance scoring for research sources."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


class SourceGovernance:
    TRUSTED_TYPES = {
        "technology": 0.82,
        "run": 0.78,
        "package": 0.80,
        "design": 0.76,
        "portfolio": 0.76,
        "breakthrough": 0.76,
        "system": 0.70,
        "web": 0.0,
    }

    def score(self, source: Dict[str, Any]) -> Dict[str, Any]:
        source_type = source.get("source_type", "unknown")
        credibility = self.TRUSTED_TYPES.get(source_type, 0.45)
        freshness = self._freshness(source.get("timestamp") or source.get("created_at"))
        return {
            "source_type": source_type,
            "source_credibility": round(credibility, 4),
            "freshness": freshness,
            "governance_status": "available" if credibility > 0 else "unavailable",
            "source_policy": "internal_or_configured_source" if source_type != "web" else "live_web_not_configured",
        }

    def _freshness(self, value: Any) -> float:
        if not value:
            return 0.5
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            age_days = max(0, (datetime.now(timezone.utc) - dt).days)
            return round(max(0.2, 1.0 - age_days / 365), 4)
        except Exception:
            return 0.5
