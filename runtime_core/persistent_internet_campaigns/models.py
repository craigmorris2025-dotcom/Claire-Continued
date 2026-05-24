from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class InternetCampaign:
    campaign_id: str
    name: str
    query: str
    urls: List[str] = field(default_factory=list)
    cadence: str = "manual"
    status: str = "active"
    max_results: int = 5
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    last_refresh_at: Optional[str] = None
    refresh_count: int = 0
    evidence_ids: List[str] = field(default_factory=list)
    average_confidence: float = 0.0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignRefreshReport:
    report_id: str
    campaign_id: str
    campaign_name: str
    query: str
    status: str
    previous_evidence_count: int
    new_evidence_count: int
    total_evidence_count: int
    previous_average_confidence: float
    new_average_confidence: float
    confidence_delta: float
    new_sources: List[str] = field(default_factory=list)
    repeated_sources: List[str] = field(default_factory=list)
    removed_sources: List[str] = field(default_factory=list)
    drift_status: str = "stable"
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    refreshed_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
