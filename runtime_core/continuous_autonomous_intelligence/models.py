from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class WorkerState:
    worker_id: str
    worker_type: str
    status: str = "idle"
    assigned_topic: Optional[str] = None
    last_heartbeat_at: Optional[str] = None
    processed_count: int = 0
    error_count: int = 0
    governance_boundary: str = "bounded_no_unreviewed_external_action"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SignalEvent:
    event_id: str
    event_type: str
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    status: str = "new"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignState:
    campaign_id: str
    name: str
    topics: List[str]
    status: str = "active"
    confidence: float = 0.0
    last_checkpoint_at: Optional[str] = None
    event_count: int = 0
    escalation_count: int = 0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EscalationDecision:
    escalation_id: str
    topic: str
    route: str
    reason: str
    confidence: float
    status: str = "requires_review"
    governance_boundary: str = "recommendation_only"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
