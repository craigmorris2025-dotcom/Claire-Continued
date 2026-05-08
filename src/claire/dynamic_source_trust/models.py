from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class SourceTrustProfile:
    domain: str
    base_score: float = 0.55
    adaptive_score: float = 0.55
    status: str = "active"
    evidence_count: int = 0
    positive_events: int = 0
    negative_events: int = 0
    contradiction_events: int = 0
    correction_events: int = 0
    last_seen_at: Optional[str] = None
    last_updated_at: str = field(default_factory=utc_now)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceTrustEvent:
    event_id: str
    domain: str
    event_type: str
    evidence_id: Optional[str] = None
    confidence: float = 0.0
    impact: float = 0.0
    reason: str = ""
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceWeightResult:
    evidence_id: str
    domain: str
    original_confidence: float
    source_reliability: float
    adaptive_source_score: float
    weighted_confidence: float
    source_status: str
    weighting_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
