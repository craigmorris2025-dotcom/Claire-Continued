from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class LiveFetchRequest:
    request_id: str
    url: str
    purpose: str = "governed_research"
    method: str = "GET"
    timeout_seconds: int = 10
    max_bytes: int = 500000
    status: str = "pending_policy"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiveFetchResult:
    request_id: str
    url: str
    status: str
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    text: str = ""
    error: Optional[str] = None
    policy_decision: str = "unknown"
    fetched_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiveSearchRequest:
    search_id: str
    query: str
    max_results: int = 5
    status: str = "pending"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiveSearchResult:
    search_id: str
    query: str
    status: str
    results: List[Dict[str, Any]] = field(default_factory=list)
    adapter_status: str = "not_configured"
    error: Optional[str] = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedContent:
    source_url: str
    title: str
    summary: str
    text: str
    content_type: Optional[str]
    extracted_terms: List[str] = field(default_factory=list)
    normalization_status: str = "normalized"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PersistentEvidenceRecord:
    evidence_id: str
    source_url: str
    claim: str
    reliability_score: float
    confidence: float
    lineage: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
