from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class InternetRuntimeRequest:
    query: str
    run_id: Optional[str] = None
    urls: Optional[List[str]] = None
    max_results: Optional[int] = None
    attach_to_core_output: bool = True
    lifecycle_stage: str = "research"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InternetEvidenceLink:
    evidence_id: str
    run_id: str
    query: str
    source_url: str
    source_domain: str
    confidence: float
    source_reliability: float
    lifecycle_stage: str = "research"
    linked_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeInternetSummary:
    run_id: str
    query: str
    internet_status: str
    searched: bool
    fetched_count: int
    evidence_count: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
