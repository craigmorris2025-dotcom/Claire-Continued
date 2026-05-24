import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


ALLOWED_ENV_FLAG = "PLATFORM_ALLOW_CONTROLLED_METADATA_GET"


@dataclass
class ControlledMetadataProbeResult:
    probe_id: str
    url: str
    method: str = "GET"
    status_code: Optional[int] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    metadata_only: bool = True
    body_fetch_performed: bool = False
    success: bool = False
    timestamp_utc: str = field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )


class ControlledMetadataOnlyProbe:
    def __init__(self) -> None:
        self.fail_closed = True

    def execute(self, url: str) -> ControlledMetadataProbeResult:
        enabled = os.environ.get(ALLOWED_ENV_FLAG) == "1"

        if not enabled:
            return ControlledMetadataProbeResult(
                probe_id="metadata-probe-blocked",
                url=url,
                success=False,
                status_code=None,
                headers={
                    "blocked_reason": "manual_enable_flag_required"
                },
            )

        return ControlledMetadataProbeResult(
            probe_id="metadata-probe-simulated",
            url=url,
            success=True,
            status_code=200,
            headers={
                "content-type": "text/html",
                "transport_mode": "metadata_only"
            },
        )

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "response_body_fetch_enabled": False,
            "metadata_only_mode": True,
            "fail_closed_mode": True,
        }
