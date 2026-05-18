from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class HeadProbeReviewResult:
    probe_id: str
    url: str
    transport: str
    status_code: Optional[int]
    success: bool
    reviewed: bool = False
    approved: bool = False
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probe_id": self.probe_id,
            "url": self.url,
            "transport": self.transport,
            "status_code": self.status_code,
            "success": self.success,
            "reviewed": self.reviewed,
            "approved": self.approved,
            "timestamp_utc": self.timestamp_utc,
            "metadata": self.metadata,
        }


class RealHeadProbeReviewCapture:
    def __init__(self) -> None:
        self._results = []

    def capture(self, result: HeadProbeReviewResult) -> Dict[str, Any]:
        payload = result.to_dict()
        payload["governance_state"] = {
            "runtime_truth_mutation": False,
            "response_body_fetch_enabled": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "fail_closed_mode": True,
            "review_required": True,
        }
        self._results.append(payload)
        return payload

    @property
    def results(self):
        return list(self._results)
