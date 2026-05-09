from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    retry_statuses: List[str] = field(default_factory=lambda: [
        "timeout",
        "fetch_error",
        "http_error",
        "completed_with_failures",
        "failed",
    ])
    non_retry_statuses: List[str] = field(default_factory=lambda: [
        "blocked",
        "review_required",
        "not_configured",
        "completed",
    ])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FailureRecord:
    operation_id: str
    operation_type: str
    target_id: str
    status: str
    category: str
    message: str
    attempt: int
    retryable: bool
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StabilityRunReport:
    stability_run_id: str
    status: str
    operation_type: str
    attempted_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0
    degraded_count: int = 0
    retry_count: int = 0
    recovered_count: int = 0
    failures: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=utc_now)
    finished_at: Optional[str] = None
    degraded_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
