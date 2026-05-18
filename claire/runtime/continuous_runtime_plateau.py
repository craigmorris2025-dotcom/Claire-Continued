from __future__ import annotations

from typing import Any, Mapping

from .continuous_runtime_contracts import SchedulerPolicy
from .continuous_runtime_scheduler import ContinuousGovernedRuntimeScheduler


def scheduler_plateau_audit():
    policy = SchedulerPolicy(
        enabled=True,
        fail_closed=True,
        max_cycles=1,
        max_iterations_per_cycle=2,
        allow_live_sources=False,
        allow_runtime_truth_mutation=False,
        require_health_green=True,
        require_review_gate_for_promotion=True,
        source_universes=["internal_runtime_truth", "review_queue"],
    )

    def adapter(request: Mapping[str, Any], envelope: Any, index: int):
        if index == 1:
            return {
                "status": "completed",
                "terminal_state": "not_terminal",
                "route": "discovery",
                "evidence_count": 0,
                "rejection_reasons": ["insufficient_admissible_evidence"],
            }
        return {
            "status": "completed",
            "terminal_state": "insufficient_data",
            "route": "discovery",
            "evidence_count": 0,
            "rejection_reasons": ["bounded_cycle_completed_without_promotion"],
        }

    scheduler = ContinuousGovernedRuntimeScheduler(policy=policy, runtime_adapter=adapter)
    result = scheduler.run_cycle({"input_summary": "plateau audit governed continuous discovery cycle"})
    return {
        "version": "19.87.4",
        "lane": "continuous_governed_runtime_scheduler",
        "scheduler_policy_enabled": policy.enabled,
        "fail_closed": policy.fail_closed,
        "runtime_truth_mutated": result.runtime_truth_mutated,
        "terminal_state": result.terminal_state,
        "route": result.route,
        "iterations": len(result.iterations),
        "promotion_required": result.promotion_required,
        "blocked_reasons": result.blocked_reasons,
        "replay_key_present": bool(result.replay_key),
        "passed": (
            result.terminal_state in {"insufficient_data", "max_iterations_reached", "blocked"}
            and result.runtime_truth_mutated is False
            and result.promotion_required is True
            and bool(result.replay_key)
        ),
    }
