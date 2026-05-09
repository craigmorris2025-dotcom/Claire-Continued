from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class CampaignSchedule:
    campaign_id: str
    enabled: bool = True
    cadence_minutes: int = 1440
    max_results: Optional[int] = None
    last_run_at: Optional[str] = None
    next_due_at: Optional[str] = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchedulerRunReport:
    scheduler_run_id: str
    status: str
    due_count: int
    refreshed_count: int
    skipped_count: int
    failed_count: int
    refreshed_campaign_ids: List[str] = field(default_factory=list)
    skipped_campaign_ids: List[str] = field(default_factory=list)
    failed_campaigns: List[Dict[str, str]] = field(default_factory=list)
    started_at: str = field(default_factory=utc_now)
    finished_at: Optional[str] = None
    lock_acquired: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
