from __future__ import annotations

from typing import Any, Callable, List, Mapping, Optional

from .continuous_runtime_contracts import (
    CycleEnvelope,
    CycleIteration,
    CycleResult,
    RuntimeHealth,
    SchedulerPolicy,
    missing_required_fields,
    stable_hash,
    utc_now_iso,
)


RuntimeAdapter = Callable[[Mapping[str, Any], CycleEnvelope, int], Mapping[str, Any]]
HealthProvider = Callable[[], RuntimeHealth]


TERMINAL_STATES = {
    "trend_thesis_ready",
    "portfolio_action_ready",
    "portfolio_optimization_ready",
    "discovery_ready",
    "breakthrough_classified",
    "advancement_path_selected",
    "design_output_ready",
    "acquisition_package_ready",
    "final_package_ready",
    "insufficient_data",
    "blocked",
    "failed",
    "max_iterations_reached",
}


class ContinuousGovernedRuntimeScheduler:
    def __init__(
        self,
        policy: Optional[SchedulerPolicy] = None,
        runtime_adapter: Optional[RuntimeAdapter] = None,
        health_provider: Optional[HealthProvider] = None,
    ) -> None:
        self.policy = (policy or SchedulerPolicy()).normalized()
        self.runtime_adapter = runtime_adapter
        self.health_provider = health_provider or (lambda: RuntimeHealth(status="green", checks={"default": True}))

    def _health_gate(self) -> RuntimeHealth:
        try:
            health = self.health_provider()
        except Exception as exc:
            return RuntimeHealth(status="red", checks={"health_provider": False}, reasons=[f"health_provider_error:{type(exc).__name__}"])
        if not isinstance(health, RuntimeHealth):
            return RuntimeHealth(status="red", checks={"health_provider_contract": False}, reasons=["health_provider_returned_invalid_contract"])
        return health

    def _make_envelope(self, request: Mapping[str, Any]) -> CycleEnvelope:
        policy_payload = {
            "enabled": self.policy.enabled,
            "fail_closed": self.policy.fail_closed,
            "max_cycles": self.policy.max_cycles,
            "max_iterations_per_cycle": self.policy.max_iterations_per_cycle,
            "allow_live_sources": self.policy.allow_live_sources,
            "allow_runtime_truth_mutation": self.policy.allow_runtime_truth_mutation,
            "require_health_green": self.policy.require_health_green,
            "require_review_gate_for_promotion": self.policy.require_review_gate_for_promotion,
            "cycle_interval_seconds": self.policy.cycle_interval_seconds,
            "source_universes": self.policy.source_universes,
        }
        policy_hash = stable_hash(policy_payload)
        replay_basis = {
            "request": dict(request),
            "policy_hash": policy_hash,
            "source_universes": self.policy.source_universes,
        }
        replay_key = stable_hash(replay_basis)
        return CycleEnvelope(
            cycle_id=f"cycle_{replay_key[:16]}",
            requested_at=utc_now_iso(),
            input_summary=str(request.get("input_summary") or request.get("query") or request.get("raw_input") or "")[:500],
            policy_hash=policy_hash,
            replay_key=replay_key,
            source_universes=list(self.policy.source_universes),
        )

    def run_cycle(self, request: Mapping[str, Any]) -> CycleResult:
        envelope = self._make_envelope(request)
        missing = missing_required_fields(request, ["input_summary"])
        if missing:
            return CycleResult(
                cycle_id=envelope.cycle_id,
                status="blocked",
                terminal_state="blocked",
                route="none",
                blocked_reasons=[f"missing_required_field:{name}" for name in missing],
                replay_key=envelope.replay_key,
            )

        if not self.policy.enabled:
            return CycleResult(
                cycle_id=envelope.cycle_id,
                status="blocked",
                terminal_state="blocked",
                route="none",
                blocked_reasons=["scheduler_disabled"],
                replay_key=envelope.replay_key,
            )

        health = self._health_gate()
        if self.policy.require_health_green and not health.green:
            return CycleResult(
                cycle_id=envelope.cycle_id,
                status="blocked",
                terminal_state="blocked",
                route="none",
                blocked_reasons=["runtime_health_gate_failed", *health.reasons],
                replay_key=envelope.replay_key,
            )

        if self.runtime_adapter is None:
            return CycleResult(
                cycle_id=envelope.cycle_id,
                status="blocked",
                terminal_state="blocked",
                route="none",
                blocked_reasons=["runtime_adapter_not_configured"],
                replay_key=envelope.replay_key,
            )

        iterations: List[CycleIteration] = []
        latest_route = "none"
        latest_terminal = "not_terminal"
        evidence_count = 0

        for index in range(1, self.policy.max_iterations_per_cycle + 1):
            try:
                output = dict(self.runtime_adapter(request, envelope, index))
            except Exception as exc:
                iterations.append(
                    CycleIteration(
                        index=index,
                        status="failed",
                        terminal_state="failed",
                        route=latest_route,
                        evidence_count=evidence_count,
                        rejection_reasons=[f"runtime_adapter_error:{type(exc).__name__}"],
                    )
                )
                return CycleResult(
                    cycle_id=envelope.cycle_id,
                    status="failed",
                    terminal_state="failed",
                    route=latest_route,
                    iterations=iterations,
                    blocked_reasons=["runtime_adapter_error"],
                    evidence_count=evidence_count,
                    replay_key=envelope.replay_key,
                )

            latest_terminal = str(output.get("terminal_state") or "not_terminal")
            latest_route = str(output.get("route") or latest_route or "none")
            evidence_count = int(output.get("evidence_count") or evidence_count or 0)
            rejection_reasons = list(output.get("rejection_reasons") or [])
            notes = list(output.get("notes") or [])

            if latest_terminal not in TERMINAL_STATES and latest_terminal != "not_terminal":
                rejection_reasons.append(f"invalid_terminal_state:{latest_terminal}")
                latest_terminal = "blocked"

            iterations.append(
                CycleIteration(
                    index=index,
                    status=str(output.get("status") or "completed"),
                    terminal_state=latest_terminal,
                    route=latest_route,
                    evidence_count=evidence_count,
                    rejection_reasons=rejection_reasons,
                    notes=notes,
                )
            )

            if latest_terminal in TERMINAL_STATES and latest_terminal != "max_iterations_reached":
                return CycleResult(
                    cycle_id=envelope.cycle_id,
                    status="completed" if latest_terminal not in {"blocked", "failed"} else latest_terminal,
                    terminal_state=latest_terminal,
                    route=latest_route,
                    iterations=iterations,
                    evidence_count=evidence_count,
                    promotion_required=self.policy.require_review_gate_for_promotion,
                    runtime_truth_mutated=False,
                    replay_key=envelope.replay_key,
                )

        return CycleResult(
            cycle_id=envelope.cycle_id,
            status="completed",
            terminal_state="max_iterations_reached",
            route=latest_route,
            iterations=iterations,
            evidence_count=evidence_count,
            promotion_required=self.policy.require_review_gate_for_promotion,
            runtime_truth_mutated=False,
            replay_key=envelope.replay_key,
        )
