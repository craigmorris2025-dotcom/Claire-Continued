"""
Public Company Signal Contracts.

v5.46:
- Stable, safe signal shape for public-company metadata scans.
- Designed for connected/hybrid enrichment without exposing internal discovery construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


@dataclass
class PublicCompanySignal:
    signal_id: str
    market_universe: str
    source_url: str
    source_category: str
    signal_type: str
    title: str
    snippet: str
    status: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        market_universe: str,
        source_url: str,
        source_category: str,
        signal_type: str,
        title: str,
        snippet: str,
        status: str = "success",
        warnings: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> "PublicCompanySignal":
        return cls(
            signal_id="sig_" + uuid.uuid4().hex[:12],
            market_universe=market_universe,
            source_url=source_url,
            source_category=source_category,
            signal_type=signal_type,
            title=title,
            snippet=snippet,
            status=status,
            warnings=warnings or [],
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
