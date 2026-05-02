"""
Hybrid opportunity fusion contracts.

v5.50:
- Combines deterministic opportunity selection and connected enrichment into
  a governed hybrid readiness signal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class HybridOpportunityFusion:
    status: str
    deterministic_score: float
    connected_score: float
    hybrid_score: float
    hybrid_readiness: str
    recommended_mode: str
    confidence_delta: float
    governance_state: str
    fusion_summary: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommended_actions: List[Dict[str, str]] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


__all__ = ["HybridOpportunityFusion"]
