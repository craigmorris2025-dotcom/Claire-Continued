"""
Claire Syntalion v18.05 — Governed Web Execution Simulation Layer.

This module intentionally performs no external execution.
It only simulates whether a reviewed governed-web item would be eligible for a
future execution path under current policy constraints.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

REQUIRED_CONFIRMATION_TEXT = "I UNDERSTAND THIS IS A NON-EXECUTING ELIGIBILITY SIMULATION"
DISABLED_EXECUTION_REASONS = (
    "live_web_execution_disabled",
    "ai_agent_execution_disabled",
    "automatic_updates_disabled",
    "runtime_truth_mutation_disabled",
    "operator_review_gate_required",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y", "approved"}
    return bool(value)


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


@dataclass(frozen=True)
class SimulationPolicy:
    """Runtime-safe policy for v18.05 simulation only."""

    live_web_execution_enabled: bool = False
    ai_agent_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    runtime_truth_mutation_enabled: bool = False
    requires_operator_approval: bool = True
    requires_confirmation_text: bool = True
    required_confirmation_text: str = REQUIRED_CONFIRMATION_TEXT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "live_web_execution_enabled": self.live_web_execution_enabled,
            "ai_agent_execution_enabled": self.ai_agent_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "runtime_truth_mutation_enabled": self.runtime_truth_mutation_enabled,
            "requires_operator_approval": self.requires_operator_approval,
            "requires_confirmation_text": self.requires_confirmation_text,
            "required_confirmation_text": self.required_confirmation_text,
        }


@dataclass
class SimulationResult:
    """Serializable governed execution simulation result."""

    status: str
    eligible_for_execution_review: bool
    simulation_performed: bool
    execution_performed: bool
    mutation_performed: bool
    update_performed: bool
    approval_detected: bool
    confirmation_text_matched: bool
    blocked_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    policy: Dict[str, Any] = field(default_factory=dict)
    reviewed_item: Dict[str, Any] = field(default_factory=dict)
    simulated_plan: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    version: str = "v18.05"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "eligible_for_execution_review": self.eligible_for_execution_review,
            "simulation_performed": self.simulation_performed,
            "execution_performed": self.execution_performed,
            "mutation_performed": self.mutation_performed,
            "update_performed": self.update_performed,
            "approval_detected": self.approval_detected,
            "confirmation_text_matched": self.confirmation_text_matched,
            "blocked_reasons": list(self.blocked_reasons),
            "warnings": list(self.warnings),
            "policy": dict(self.policy),
            "reviewed_item": dict(self.reviewed_item),
            "simulated_plan": dict(self.simulated_plan),
            "created_at": self.created_at,
        }


def normalize_review_item(item: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Normalize review queue/control records without mutating the input."""
    raw: Mapping[str, Any] = item or {}
    request_id = _safe_text(raw.get("request_id") or raw.get("id") or raw.get("review_id") or "unassigned")
    route = _safe_text(raw.get("route") or raw.get("mode") or raw.get("search_mode") or "governed_web")
    query = _safe_text(raw.get("query") or raw.get("request") or raw.get("raw_input") or "")
    operator_approval = _as_bool(raw.get("operator_approval") or raw.get("approved") or raw.get("approval_detected"))
    confirmation_text = _safe_text(raw.get("confirmation_text") or raw.get("operator_confirmation") or "")
    return {
        "request_id": request_id,
        "route": route,
        "query": query,
        "operator_approval": operator_approval,
        "confirmation_text": confirmation_text,
        "source": _safe_text(raw.get("source") or "search_bar_review_queue"),
        "raw_status": _safe_text(raw.get("status") or "review_pending"),
    }


def _disabled_policy_reasons(policy: SimulationPolicy) -> List[str]:
    reasons: List[str] = []
    if not policy.live_web_execution_enabled:
        reasons.append("live_web_execution_disabled")
    if not policy.ai_agent_execution_enabled:
        reasons.append("ai_agent_execution_disabled")
    if not policy.automatic_updates_enabled:
        reasons.append("automatic_updates_disabled")
    if not policy.runtime_truth_mutation_enabled:
        reasons.append("runtime_truth_mutation_disabled")
    return reasons


def simulate_governed_web_execution(
    review_item: Optional[Mapping[str, Any]] = None,
    *,
    policy: Optional[SimulationPolicy] = None,
) -> Dict[str, Any]:
    """
    Simulate governed web execution eligibility.

    This is deliberately non-executing. Even when operator approval and the exact
    confirmation text are present, the result remains simulation-only and blocked
    from real execution while v18.05 policy defaults remain disabled.
    """
    active_policy = policy or SimulationPolicy()
    item = normalize_review_item(review_item)
    blocked: List[str] = []
    warnings: List[str] = []

    if not item["query"]:
        blocked.append("missing_query")
    if active_policy.requires_operator_approval and not item["operator_approval"]:
        blocked.append("operator_approval_required")
    confirmation_matched = item["confirmation_text"] == active_policy.required_confirmation_text
    if active_policy.requires_confirmation_text and not confirmation_matched:
        blocked.append("required_confirmation_text_missing_or_mismatched")

    blocked.extend(_disabled_policy_reasons(active_policy))

    approval_detected = bool(item["operator_approval"])
    eligible_for_execution_review = not any(
        reason in blocked
        for reason in ("missing_query", "operator_approval_required", "required_confirmation_text_missing_or_mismatched")
    )

    if eligible_for_execution_review:
        warnings.append("eligible_for_future_execution_review_only_not_execution")
    if approval_detected:
        warnings.append("approval_does_not_equal_execution")

    simulated_plan = {
        "plan_type": "governed_web_execution_simulation",
        "would_route_to": item["route"],
        "would_require_final_human_execute_action": True,
        "would_require_live_web_enablement": True,
        "would_require_runtime_truth_write_gate": True,
        "would_execute_now": False,
        "would_mutate_runtime_truth_now": False,
        "would_apply_updates_now": False,
    }

    result = SimulationResult(
        status="simulation_complete",
        eligible_for_execution_review=eligible_for_execution_review,
        simulation_performed=True,
        execution_performed=False,
        mutation_performed=False,
        update_performed=False,
        approval_detected=approval_detected,
        confirmation_text_matched=confirmation_matched,
        blocked_reasons=blocked,
        warnings=warnings,
        policy=active_policy.to_dict(),
        reviewed_item={k: v for k, v in item.items() if k != "confirmation_text"},
        simulated_plan=simulated_plan,
    )
    return result.to_dict()


def simulate_from_review_queue(items: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Simulate a batch of review-queue records without executing any item."""
    simulations = [simulate_governed_web_execution(item) for item in items]
    return {
        "version": "v18.05",
        "status": "batch_simulation_complete",
        "simulation_count": len(simulations),
        "execution_performed": False,
        "mutation_performed": False,
        "update_performed": False,
        "simulations": simulations,
        "created_at": _utc_now(),
    }
