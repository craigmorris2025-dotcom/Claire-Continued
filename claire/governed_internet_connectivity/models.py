from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class SourcePolicy:
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    require_review_for_unknown_sources: bool = True
    max_fetches_per_run: int = 10
    governance_mode: str = "review_first"


@dataclass
class FetchRequest:
    request_id: str
    query: str
    source_url: Optional[str] = None
    domain: Optional[str] = None
    purpose: str = "research"
    status: str = "pending_policy_check"
    created_at: str = field(default_factory=utc_now)


@dataclass
class FetchResult:
    request_id: str
    status: str
    content: str = ""
    source_url: Optional[str] = None
    domain: Optional[str] = None
    policy_decision: str = "unknown"
    error: Optional[str] = None
    fetched_at: str = field(default_factory=utc_now)


@dataclass
class EvidencePacket:
    evidence_id: str
    claim: str
    source_url: Optional[str]
    domain: Optional[str]
    reliability_score: float
    confidence: float
    extraction_method: str = "bounded_text_extraction"
    supporting_terms: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    lineage: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueueItem:
    item_id: str
    query: str
    priority: int = 5
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 3
    created_at: str = field(default_factory=utc_now)


@dataclass
class WatchlistItem:
    watch_id: str
    topic: str
    thesis: str
    cadence: str = "daily"
    status: str = "active"
    last_checked_at: Optional[str] = None
    confidence: float = 0.0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
