from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class PolicyDecision:
    decision: str
    url: Optional[str] = None
    domain: Optional[str] = None
    reason: str = ""
    requires_review: bool = False
    content_allowed: bool = True
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    source: str = "search_provider"
    rank: int = 0
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class FetchResult:
    url: str
    status: str
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    text: str = ""
    binary_size: int = 0
    error: Optional[str] = None
    policy: Dict[str, Any] = field(default_factory=dict)
    fetched_at: str = field(default_factory=utc_now)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class EvidenceRecord:
    evidence_id: str
    run_id: str
    query: str
    source_url: str
    title: str
    claim: str
    summary: str
    source_domain: str
    source_reliability: float
    confidence: float
    supporting_terms: List[str] = field(default_factory=list)
    conflicting_terms: List[str] = field(default_factory=list)
    extracted_at: str = field(default_factory=utc_now)
    lineage: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class ResearchRun:
    run_id: str
    query: str
    status: str
    search_provider: str
    searched: bool = False
    fetched_count: int = 0
    evidence_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)
