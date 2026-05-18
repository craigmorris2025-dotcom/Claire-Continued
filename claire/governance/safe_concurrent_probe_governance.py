"""Safe concurrent probe governance for Claire governed live web execution.

This module is intentionally policy-only. It does not perform network I/O.
It decides whether a requested concurrent probe batch is allowed, normalizes
safe limits, and returns operator-visible governance state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ConcurrentProbePolicy:
    enabled: bool = False
    max_concurrent_probes: int = 1
    max_batch_size: int = 3
    require_manual_enable: bool = True
    allow_runtime_truth_mutation: bool = False
    allow_autonomous_execution: bool = False
    fail_closed: bool = True


@dataclass(frozen=True)
class ConcurrentProbeDecision:
    allowed: bool
    status: str
    requested_count: int
    effective_concurrency: int
    max_batch_size: int
    reasons: list[str] = field(default_factory=list)
    governance_state: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "status": self.status,
            "requested_count": self.requested_count,
            "effective_concurrency": self.effective_concurrency,
            "max_batch_size": self.max_batch_size,
            "reasons": list(self.reasons),
            "governance_state": dict(self.governance_state),
        }


def _env_enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def policy_from_environment(env: Mapping[str, str] | None = None) -> ConcurrentProbePolicy:
    """Create a concurrency policy from environment-like values.

    Required manual flag:
        CLAIRE_ALLOW_SAFE_CONCURRENT_PROBES=1

    Optional limits:
        CLAIRE_MAX_CONCURRENT_PROBES defaults to 2 when enabled
        CLAIRE_MAX_CONCURRENT_PROBE_BATCH defaults to 5 when enabled
    """
    import os

    source: Mapping[str, str] = env if env is not None else os.environ
    enabled = _env_enabled(source.get("CLAIRE_ALLOW_SAFE_CONCURRENT_PROBES"))

    def read_int(name: str, default: int, minimum: int, maximum: int) -> int:
        try:
            parsed = int(str(source.get(name, default)).strip())
        except Exception:
            parsed = default
        return max(minimum, min(maximum, parsed))

    if not enabled:
        return ConcurrentProbePolicy(enabled=False, max_concurrent_probes=1, max_batch_size=3)

    return ConcurrentProbePolicy(
        enabled=True,
        max_concurrent_probes=read_int("CLAIRE_MAX_CONCURRENT_PROBES", 2, 1, 4),
        max_batch_size=read_int("CLAIRE_MAX_CONCURRENT_PROBE_BATCH", 5, 1, 10),
        require_manual_enable=True,
        allow_runtime_truth_mutation=False,
        allow_autonomous_execution=False,
        fail_closed=True,
    )


def evaluate_safe_concurrency(
    requested_count: int,
    policy: ConcurrentProbePolicy | None = None,
) -> ConcurrentProbeDecision:
    """Evaluate whether a concurrent probe batch may proceed.

    The result is intentionally conservative. If anything is malformed or
    exceeds policy, execution is denied and the caller should fall back to
    sequential/manual review behavior.
    """
    active_policy = policy or policy_from_environment()
    reasons: list[str] = []

    try:
        count = int(requested_count)
    except Exception:
        count = 0
        reasons.append("requested_count_invalid")

    if count <= 0:
        reasons.append("requested_count_must_be_positive")

    if not active_policy.enabled:
        reasons.append("safe_concurrent_probes_not_manually_enabled")

    if active_policy.allow_runtime_truth_mutation:
        reasons.append("runtime_truth_mutation_not_allowed_for_concurrent_probes")

    if active_policy.allow_autonomous_execution:
        reasons.append("autonomous_execution_not_allowed_for_concurrent_probes")

    if count > active_policy.max_batch_size:
        reasons.append("requested_batch_exceeds_policy_limit")

    effective = min(max(count, 0), active_policy.max_concurrent_probes, active_policy.max_batch_size)
    allowed = not reasons and count > 0

    return ConcurrentProbeDecision(
        allowed=allowed,
        status="allowed" if allowed else "blocked",
        requested_count=max(count, 0),
        effective_concurrency=effective if allowed else 0,
        max_batch_size=active_policy.max_batch_size,
        reasons=reasons,
        governance_state={
            "fail_closed": active_policy.fail_closed,
            "manual_enable_required": active_policy.require_manual_enable,
            "manual_enable_flag": "CLAIRE_ALLOW_SAFE_CONCURRENT_PROBES",
            "runtime_truth_mutation_allowed": active_policy.allow_runtime_truth_mutation,
            "autonomous_execution_allowed": active_policy.allow_autonomous_execution,
            "max_concurrent_probes": active_policy.max_concurrent_probes,
            "max_batch_size": active_policy.max_batch_size,
        },
    )


def build_concurrent_probe_review_payload(
    requested_targets: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
    policy: ConcurrentProbePolicy | None = None,
) -> dict[str, Any]:
    """Return a dashboard/API-safe review payload for a proposed probe batch."""
    targets = list(requested_targets or [])
    decision = evaluate_safe_concurrency(len(targets), policy=policy)
    return {
        "contract": "safe_concurrent_probe_governance.v18_48",
        "execution_allowed": decision.allowed,
        "execution_status": decision.status,
        "requested_target_count": len(targets),
        "effective_concurrency": decision.effective_concurrency,
        "targets_review": [
            {
                "index": index,
                "url": str(target.get("url", "")),
                "method": str(target.get("method", "GET")).upper(),
                "review_required": True,
            }
            for index, target in enumerate(targets)
        ],
        "decision": decision.to_dict(),
        "safety_invariants": {
            "fail_closed": True,
            "manual_enable_controls_preserved": True,
            "runtime_truth_immutable": True,
            "automatic_updates_disabled": True,
            "autonomous_execution_disabled": True,
            "unbounded_concurrency_disabled": True,
        },
    }
