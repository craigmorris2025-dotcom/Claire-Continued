"""
Feed Result Contracts — stable result shapes for Claire live-feed scaffolding.

v5.41:
- Defines feed scan result contracts without performing live ingestion.
- Keeps deterministic fallback status separate from connected/hybrid feed activation.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class FeedCoverage:
    market_universe: str
    display_name: str
    coverage_label: str
    coverage_target: str
    category: str
    deterministic_fallback: bool = True
    connected_feed_available: bool = False
    connected_feed_enabled: bool = False
    last_scan_at: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeedScanResult:
    feed_id: str
    market_universe: str
    status: str
    mode: str
    generated_at: str
    records_found: int = 0
    signals: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def offline_stub(cls, feed_id: str, market_universe: str, mode: str = "deterministic") -> "FeedScanResult":
        return cls(
            feed_id=feed_id,
            market_universe=market_universe,
            status="offline_scaffold",
            mode=mode,
            generated_at=datetime.now(timezone.utc).isoformat(),
            records_found=0,
            signals=[],
            warnings=[
                "Connected live-feed ingestion is not enabled in this scaffold package.",
                "Deterministic fallback taxonomy is available for opportunity generation.",
            ],
            metadata={
                "scaffold_only": True,
                "safe_to_run_offline": True,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
