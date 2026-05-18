# Claire Syntalion Runtime Proof Exit Policy
from __future__ import annotations

from typing import Any


SUCCESS_PROCESS_STATES = {
    "success",
    "ok",
    "healthy",
    "degraded",
    "not_configured",
    "configured_fail_closed",
    "configured_live_gated",
    "partial",
    "warning",
    "warnings",
    "completed",
    "complete",
}

FAIL_PROCESS_STATES = {
    "failed",
    "failure",
    "error",
    "blocked",
    "missing",
    "invalid",
    "exception",
    "crashed",
}


def normalize_status(value: Any) -> str:
    return str(value or "").strip().lower()


def exit_code_for_status(status: Any, *, output_written: bool = True) -> int:
    normalized = normalize_status(status)
    if not output_written:
        return 1
    if normalized in FAIL_PROCESS_STATES:
        return 1
    if normalized in SUCCESS_PROCESS_STATES:
        return 0
    return 1


def truth_is_operationally_complete(value: Any) -> bool:
    return exit_code_for_status(value, output_written=True) == 0
