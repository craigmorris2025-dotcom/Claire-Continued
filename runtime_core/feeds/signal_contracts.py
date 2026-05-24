"""
Feed signal contracts.

v5.47:
- Converts raw feed metadata into Claire-ready opportunity signal records.
- Keeps provenance, governance, and scoring fields explicit for dashboard and export use.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


@dataclass
class NormalizedFeedSignal:
    signal_id: str
    raw_signal_id: str
    market_universe: str
    industry_domain: str
    source_category: str
    governance_status: str
    signal_type: str
    signal_strength: str
    signal_strength_score: float
    opportunity_relevance: str
    opportunity_relevance_score: float
    safe_to_enrich: bool
    title: str
    summary: str
    source_url: str = ""
    normalized_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    warnings: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        raw_signal_id: str,
        market_universe: str,
        industry_domain: str,
        source_category: str,
        governance_status: str,
        signal_type: str,
        signal_strength: str,
        signal_strength_score: float,
        opportunity_relevance: str,
        opportunity_relevance_score: float,
        safe_to_enrich: bool,
        title: str,
        summary: str,
        source_url: str = "",
        warnings: List[str] | None = None,
        evidence: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> "NormalizedFeedSignal":
        return cls(
            signal_id="norm_" + uuid.uuid4().hex[:12],
            raw_signal_id=raw_signal_id or "",
            market_universe=market_universe or "custom_universe",
            industry_domain=industry_domain or "cross_sector",
            source_category=source_category or "unknown_source",
            governance_status=governance_status or "unknown",
            signal_type=signal_type or "market_signal",
            signal_strength=signal_strength or "low",
            signal_strength_score=round(float(signal_strength_score or 0.0), 3),
            opportunity_relevance=opportunity_relevance or "low",
            opportunity_relevance_score=round(float(opportunity_relevance_score or 0.0), 3),
            safe_to_enrich=bool(safe_to_enrich),
            title=title or "Untitled signal",
            summary=summary or "",
            source_url=source_url or "",
            warnings=warnings or [],
            evidence=evidence or {},
            metadata=metadata or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


__all__ = ["NormalizedFeedSignal"]
