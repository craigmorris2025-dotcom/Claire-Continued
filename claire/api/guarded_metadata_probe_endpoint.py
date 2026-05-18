"""S34 guarded metadata probe endpoint candidate.

This module defines a HEAD-only, operator-triggered, metadata-only execution path.
It is safe to import. It does not execute anything on import.

Important:
- This router is not automatically registered by this module.
- No response body is read.
- Browser execution is not used.
- Runtime truth is not mutated.
- Autonomous execution is not enabled.
- Automatic updates are not enabled.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from claire.api.guarded_metadata_probe_request_policy import (
    validate_guarded_metadata_probe_request,
)


router = APIRouter(prefix="/api/governed-web", tags=["governed-web"])


class GuardedMetadataProbeRequest(BaseModel):
    target_url: str = Field(..., description="HTTPS URL whose host must be allowlisted")
    operator_trigger_id: str = Field(..., description="Required operator trigger identifier")
    reason: str | None = Field(default=None, description="Operator-visible reason")


def _flag_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _capture_metadata_only(target_url: str) -> Dict[str, Any]:
    parsed = urlparse(target_url)
    if parsed.scheme != "https":
        raise ValueError("Only HTTPS targets are allowed.")

    request = Request(target_url, method="HEAD")
    started = time.perf_counter()

    with urlopen(request, timeout=10) as response:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        headers = dict(response.headers.items())

        return {
            "status_code": getattr(response, "status", None),
            "response_headers": headers,
            "content_type": headers.get("Content-Type"),
            "server": headers.get("Server"),
            "date": headers.get("Date"),
            "elapsed_ms": elapsed_ms,
            "final_url": response.geturl(),
            "redirect_count": 0,
        }


@router.post("/metadata-probe")
def run_guarded_metadata_probe(payload: GuardedMetadataProbeRequest) -> Dict[str, Any]:
    """Operator-triggered metadata-only probe.

    This endpoint remains blocked unless explicit environment gates are enabled.
    It performs a HEAD request only and never reads the response body.
    """

    policy = validate_guarded_metadata_probe_request(
        target_url=payload.target_url,
        operator_trigger_id=payload.operator_trigger_id,
        method="HEAD",
    )

    if policy.get("accepted_for_future_execution") is not True:
        raise HTTPException(status_code=403, detail=policy)

    if not _flag_enabled("CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE"):
        raise HTTPException(
            status_code=403,
            detail={
                "status": "blocked_missing_one_shot_authorization",
                "network_request_performed": False,
                "response_body_read": False,
                "browser_execution": False,
                "runtime_truth_mutation": False,
                "automatic_update": False,
            },
        )

    try:
        metadata = _capture_metadata_only(payload.target_url)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "metadata_probe_failed",
                "error": str(exc),
                "response_body_read": False,
                "browser_execution": False,
                "runtime_truth_mutation": False,
            },
        ) from exc

    return {
        "version": "v19.89.8-S34R1",
        "status": "metadata_probe_completed_metadata_only",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "operator_trigger_id": payload.operator_trigger_id,
        "target_url": payload.target_url,
        "reason": payload.reason,
        "capture_type": "metadata_only_head",
        "metadata": metadata,
        "response_body_read": False,
        "browser_execution": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "automatic_update": False,
        "promotion_state": "quarantined_review_required",
    }


def get_guarded_metadata_probe_endpoint_candidate() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S34R1",
        "status": "endpoint_candidate_defined",
        "router_defined": True,
        "router_registered_by_this_module": False,
        "endpoint": "/api/governed-web/metadata-probe",
        "method": "POST",
        "actual_network_execution_requires": [
            "provider readiness passed",
            "target host allowlisted",
            "operator trigger id",
            "CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE=true",
        ],
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
