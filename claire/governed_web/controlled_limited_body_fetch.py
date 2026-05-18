import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


ALLOWED_ENV_FLAG = "CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET"
DEFAULT_BODY_LIMIT_BYTES = 4096


@dataclass
class ControlledLimitedBodyFetchResult:
    probe_id: str
    url: str
    method: str = "GET"
    status_code: Optional[int] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    body_excerpt: str = ""
    body_limit_bytes: int = DEFAULT_BODY_LIMIT_BYTES
    body_truncated: bool = False
    body_fetch_performed: bool = False
    success: bool = False
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probe_id": self.probe_id,
            "url": self.url,
            "method": self.method,
            "status_code": self.status_code,
            "headers": self.headers,
            "body_excerpt": self.body_excerpt,
            "body_limit_bytes": self.body_limit_bytes,
            "body_truncated": self.body_truncated,
            "body_fetch_performed": self.body_fetch_performed,
            "success": self.success,
            "timestamp_utc": self.timestamp_utc,
        }


class ControlledLimitedBodyFetchProbe:
    def __init__(self, body_limit_bytes: int = DEFAULT_BODY_LIMIT_BYTES) -> None:
        self.body_limit_bytes = max(0, int(body_limit_bytes))
        self.fail_closed = True

    def execute(self, url: str, simulated_body: str = "") -> ControlledLimitedBodyFetchResult:
        enabled = os.environ.get(ALLOWED_ENV_FLAG) == "1"

        if not enabled:
            return ControlledLimitedBodyFetchResult(
                probe_id="limited-body-fetch-blocked",
                url=url,
                success=False,
                status_code=None,
                headers={"blocked_reason": "manual_enable_flag_required"},
                body_excerpt="",
                body_limit_bytes=self.body_limit_bytes,
                body_truncated=False,
                body_fetch_performed=False,
            )

        encoded = simulated_body.encode("utf-8")
        limited_bytes = encoded[: self.body_limit_bytes]
        body_excerpt = limited_bytes.decode("utf-8", errors="ignore")

        return ControlledLimitedBodyFetchResult(
            probe_id="limited-body-fetch-simulated",
            url=url,
            success=True,
            status_code=200,
            headers={
                "content-type": "text/html",
                "transport_mode": "limited_body_fetch",
            },
            body_excerpt=body_excerpt,
            body_limit_bytes=self.body_limit_bytes,
            body_truncated=len(encoded) > self.body_limit_bytes,
            body_fetch_performed=True,
        )

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "response_body_fetch_enabled": True,
            "limited_body_fetch_only": True,
            "body_limit_bytes": self.body_limit_bytes,
            "fail_closed_mode": True,
            "manual_enable_required": True,
        }
