"""Status vocabulary for Claire core lifecycle execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


PENDING = "pending"
RUNNING = "running"
COMPLETE = "complete"
FAILED = "failed"
INSUFFICIENT_DATA = "insufficient_data"
BLOCKED = "blocked"
SKIPPED_BY_ROUTE = "skipped_by_route"

ALLOWED_STATUSES = {
    PENDING,
    RUNNING,
    COMPLETE,
    FAILED,
    INSUFFICIENT_DATA,
    BLOCKED,
    SKIPPED_BY_ROUTE,
}


@dataclass
class StageStatus:
    stage_id: str
    status: str = PENDING
    message: str = ""
    errors: List[str] | None = None
    warnings: List[str] | None = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "stage_id": self.stage_id,
            "status": self.status,
            "message": self.message,
            "errors": list(self.errors or []),
            "warnings": list(self.warnings or []),
        }


def validate_status(status: str) -> str:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported lifecycle stage status: {status}")
    return status
