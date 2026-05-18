from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

try:
    from claire.runtime.continuous_runtime_contracts import SchedulerPolicy
    from claire.runtime.continuous_runtime_scheduler import ContinuousGovernedRuntimeScheduler
except Exception:
    SchedulerPolicy = None
    ContinuousGovernedRuntimeScheduler = None


@dataclass
class ContinuousRuntimeCycleResult:
    status: str = "blocked"
    terminal_state: str = "blocked"
    route: str = "none"
    cycle_id: str = ""
    evidence_count: int = 0
    runtime_truth_mutated: bool = False
    promotion_required: bool = True
    blocked_reasons: list[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        if self.payload:
            return dict(self.payload)
        return {
            "status": self.status,
            "terminal_state": self.terminal_state,
            "route": self.route,
            "cycle_id": self.cycle_id,
            "evidence_count": self.evidence_count,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "promotion_required": self.promotion_required,
            "blocked_reasons": list(self.blocked_reasons),
        }


class ContinuousRuntimeCycle:
    """Compatibility wrapper for older v19.84.2 tests."""

    def __init__(self, scheduler: Optional[Any] = None) -> None:
        if scheduler is not None:
            self.scheduler = scheduler
        elif SchedulerPolicy is not None and ContinuousGovernedRuntimeScheduler is not None:
            self.scheduler = ContinuousGovernedRuntimeScheduler(
                policy=SchedulerPolicy(
                    enabled=True,
                    fail_closed=True,
                    max_cycles=1,
                    max_iterations_per_cycle=1,
                    allow_live_sources=False,
                    allow_runtime_truth_mutation=False,
                    require_health_green=True,
                    require_review_gate_for_promotion=True,
                ),
                runtime_adapter=lambda request, envelope, index: {
                    "status": "completed",
                    "terminal_state": "insufficient_data",
                    "route": str(request.get("route") or "discovery"),
                    "evidence_count": int(request.get("evidence_count") or 0),
                    "rejection_reasons": ["compatibility_cycle_no_admissible_runtime_adapter"],
                },
            )
        else:
            self.scheduler = None

    def run(self, request: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> ContinuousRuntimeCycleResult:
        payload: Dict[str, Any] = {}
        if request:
            payload.update(dict(request))
        payload.update(kwargs)
        if "input_summary" not in payload:
            payload["input_summary"] = str(payload.get("query") or payload.get("raw_input") or "continuous runtime compatibility cycle")

        if self.scheduler is None:
            return ContinuousRuntimeCycleResult(blocked_reasons=["continuous_runtime_scheduler_unavailable"])

        result = self.scheduler.run_cycle(payload)
        result_payload = result.to_payload() if hasattr(result, "to_payload") else dict(result)
        return ContinuousRuntimeCycleResult(
            status=str(result_payload.get("status") or "blocked"),
            terminal_state=str(result_payload.get("terminal_state") or "blocked"),
            route=str(result_payload.get("route") or "none"),
            cycle_id=str(result_payload.get("cycle_id") or ""),
            evidence_count=int(result_payload.get("evidence_count") or 0),
            runtime_truth_mutated=bool(result_payload.get("runtime_truth_mutated") or False),
            promotion_required=bool(result_payload.get("promotion_required", True)),
            blocked_reasons=list(result_payload.get("blocked_reasons") or []),
            payload=result_payload,
        )


def ensure_continuous_runtime_cycle() -> ContinuousRuntimeCycle:
    return ContinuousRuntimeCycle()


def run_continuous_runtime_cycle(request: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
    return ensure_continuous_runtime_cycle().run(request, **kwargs).to_payload()


ensure_cycle = ensure_continuous_runtime_cycle
run_cycle = run_continuous_runtime_cycle
