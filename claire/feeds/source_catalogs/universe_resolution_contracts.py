"""
Offline Universe Resolution Contracts.

v5.45:
- Stable shapes for offline market-universe resolution.
- No live membership resolution, scraping, APIs, or network calls.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class OfflineCoverageBucket:
    bucket_id: str
    name: str
    purpose: str
    opportunity_lens: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OfflineUniverseResolution:
    universe_id: str
    name: str
    coverage_target: str
    source_category: str
    market_category: str
    resolution_status: str = "offline_ready"
    connected_scan_status: str = "not_enabled"
    deterministic_fallback: bool = True
    coverage_buckets: List[Dict[str, Any]] = field(default_factory=list)
    recommended_use: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
