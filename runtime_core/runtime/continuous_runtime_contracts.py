from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Sequence
import hashlib
import json


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def missing_required_fields(payload: Mapping[str, Any], required_fields: Sequence[str]) -> List[str]:
    missing: List[str] = []
    for field_name in required_fields:
        if field_name not in payload or not value_present(payload.get(field_name)):
            missing.append(field_name)
    return missing


def stable_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class SchedulerPolicy:
    enabled: bool = False
    fail_closed: bool = True
    max_cycles: int = 1
    max_iterations_per_cycle: int = 3
    allow_live_sources: bool = False
    allow_runtime_truth_mutation: bool = False
    require_health_green: bool = True
    require_review_gate_for_promotion: bool = True
    cycle_interval_seconds: int = 0
    source_universes: List[str] = field(default_factory=list)

    def normalized(self) -> "SchedulerPolicy":
        return SchedulerPolicy(
            enabled=bool(self.enabled),
            fail_closed=bool(self.fail_closed),
            max_cycles=max(1, int(self.max_cycles)),
            max_iterations_per_cycle=max(1, int(self.max_iterations_per_cycle)),
            allow_live_sources=bool(self.allow_live_sources),
            allow_runtime_truth_mutation=bool(self.allow_runtime_truth_mutation),
            require_health_green=bool(self.require_health_green),
            require_review_gate_for_promotion=bool(self.require_review_gate_for_promotion),
            cycle_interval_seconds=max(0, int(self.cycle_interval_seconds)),
            source_universes=list(self.source_universes or []),
        )


@dataclass(frozen=True)
class RuntimeHealth:
    status: str
    checks: Dict[str, bool] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)

    @property
    def green(self) -> bool:
        return self.status == "green" and all(bool(v) for v in self.checks.values())


@dataclass(frozen=True)
class CycleEnvelope:
    cycle_id: str
    requested_at: str
    input_summary: str
    policy_hash: str
    replay_key: str
    source_universes: List[str] = field(default_factory=list)


@dataclass
class CycleIteration:
    index: int
    status: str
    terminal_state: str = "not_terminal"
    route: str = "none"
    evidence_count: int = 0
    rejection_reasons: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class CycleResult:
    cycle_id: str
    status: str
    terminal_state: str
    route: str
    iterations: List[CycleIteration] = field(default_factory=list)
    blocked_reasons: List[str] = field(default_factory=list)
    evidence_count: int = 0
    promotion_required: bool = True
    runtime_truth_mutated: bool = False
    replay_key: str = ""
    created_at: str = field(default_factory=utc_now_iso)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "status": self.status,
            "terminal_state": self.terminal_state,
            "route": self.route,
            "iterations": [vars(item) for item in self.iterations],
            "blocked_reasons": list(self.blocked_reasons),
            "evidence_count": self.evidence_count,
            "promotion_required": self.promotion_required,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "replay_key": self.replay_key,
            "created_at": self.created_at,
        }
