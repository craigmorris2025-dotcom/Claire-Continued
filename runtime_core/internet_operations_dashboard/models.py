from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class DashboardPanelStatus:
    panel: str
    status: str
    count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DashboardSnapshot:
    status: str
    generated_at: str = field(default_factory=utc_now)
    panels: List[Dict[str, Any]] = field(default_factory=list)
    campaigns: List[Dict[str, Any]] = field(default_factory=list)
    schedules: List[Dict[str, Any]] = field(default_factory=list)
    scheduler_reports: List[Dict[str, Any]] = field(default_factory=list)
    stability: Dict[str, Any] = field(default_factory=dict)
    source_trust_profiles: List[Dict[str, Any]] = field(default_factory=list)
    source_trust_events: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
