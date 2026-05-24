"""
Connected opportunity enrichment contracts.

v5.49:
- Defines the safe public enrichment layer between normalized feed signals and
  opportunity candidates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class OpportunityEnrichment:
    status: str
    enrichment_mode: str
    signal_count: int
    matched_signal_count: int
    top_signal_types: List[str] = field(default_factory=list)
    source_categories: List[str] = field(default_factory=list)
    opportunity_relevance: str = "low"
    enrichment_score: float = 0.0
    connected_thesis: str = ""
    timing_window: str = "unconfirmed"
    safe_to_enrich: bool = False
    supporting_signals: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


__all__ = ["OpportunityEnrichment"]
