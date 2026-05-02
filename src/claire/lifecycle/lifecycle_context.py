"""Unified context object for Claire core lifecycle execution."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .lifecycle_registry import CoreLifecycleRegistry
from .stage_status import (
    BLOCKED,
    COMPLETE,
    FAILED,
    INSUFFICIENT_DATA,
    PENDING,
    RUNNING,
    SKIPPED_BY_ROUTE,
    validate_status,
)


@dataclass
class LifecycleContext:
    run_id: str = "unknown"
    route: str = "portfolio_only"
    stage_outputs: Dict[str, Any] = field(default_factory=dict)
    stage_statuses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: Dict[str, Any] = field(default_factory=dict)
    final_outputs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "route": self.route,
            "stage_outputs": deepcopy(self.stage_outputs),
            "stage_statuses": deepcopy(self.stage_statuses),
            "errors": deepcopy(self.errors),
            "warnings": deepcopy(self.warnings),
            "metadata": deepcopy(self.metadata),
            "evidence": deepcopy(self.evidence),
            "confidence": deepcopy(self.confidence),
            "final_outputs": deepcopy(self.final_outputs),
        }


def initialize_context(
    run_id: str = "unknown",
    route: str = "portfolio_only",
    metadata: Dict[str, Any] | None = None,
) -> LifecycleContext:
    context = LifecycleContext(run_id=run_id, route=route, metadata=metadata or {})
    for stage in CoreLifecycleRegistry().stages():
        context.stage_statuses[stage["id"]] = {
            "stage_id": stage["id"],
            "stage_number": stage["number"],
            "stage_name": stage["name"],
            "status": PENDING,
            "message": "",
            "errors": [],
            "warnings": [],
        }
    return context


def _set_stage(
    context: LifecycleContext,
    stage_id: str,
    status: str,
    message: str = "",
    output: Any | None = None,
    error: str | None = None,
    warning: str | None = None,
) -> LifecycleContext:
    validate_status(status)
    if stage_id not in context.stage_statuses:
        raise KeyError(f"Unknown lifecycle stage id: {stage_id}")
    state = context.stage_statuses[stage_id]
    state["status"] = status
    state["message"] = message
    if output is not None:
        context.stage_outputs[stage_id] = output
    if error:
        state["errors"].append(error)
        context.errors.append({"stage_id": stage_id, "error": error})
    if warning:
        state["warnings"].append(warning)
        context.warnings.append({"stage_id": stage_id, "warning": warning})
    return context


def mark_stage_running(context: LifecycleContext, stage_id: str, message: str = "") -> LifecycleContext:
    return _set_stage(context, stage_id, RUNNING, message)


def mark_stage_complete(context: LifecycleContext, stage_id: str, output: Any | None = None, message: str = "") -> LifecycleContext:
    return _set_stage(context, stage_id, COMPLETE, message, output=output)


def mark_stage_failed(context: LifecycleContext, stage_id: str, error: str, message: str = "") -> LifecycleContext:
    return _set_stage(context, stage_id, FAILED, message, error=error)


def mark_stage_insufficient_data(context: LifecycleContext, stage_id: str, message: str = "") -> LifecycleContext:
    return _set_stage(context, stage_id, INSUFFICIENT_DATA, message)


def mark_stage_blocked(context: LifecycleContext, stage_id: str, error: str, message: str = "") -> LifecycleContext:
    return _set_stage(context, stage_id, BLOCKED, message, error=error)


def mark_stage_skipped_by_route(context: LifecycleContext, stage_id: str, message: str = "") -> LifecycleContext:
    return _set_stage(context, stage_id, SKIPPED_BY_ROUTE, message)


def summarize_run_state(context: LifecycleContext) -> Dict[str, Any]:
    counts = {status: 0 for status in [PENDING, RUNNING, COMPLETE, FAILED, INSUFFICIENT_DATA, BLOCKED, SKIPPED_BY_ROUTE]}
    for state in context.stage_statuses.values():
        counts[state["status"]] = counts.get(state["status"], 0) + 1
    terminal_problem_count = counts[FAILED] + counts[BLOCKED]
    return {
        "status": "blocked" if terminal_problem_count else "success",
        "route": context.route,
        "stage_count": len(context.stage_statuses),
        "complete_stage_count": counts[COMPLETE],
        "incomplete_stage_count": counts[PENDING] + counts[RUNNING] + counts[INSUFFICIENT_DATA],
        "blocked_stage_count": counts[BLOCKED],
        "failed_stage_count": counts[FAILED],
        "skipped_by_route_stage_count": counts[SKIPPED_BY_ROUTE],
        "status_counts": counts,
        "error_count": len(context.errors),
        "warning_count": len(context.warnings),
    }
