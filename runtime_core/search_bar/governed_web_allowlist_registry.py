from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


DEFAULT_TRUST_LEVEL = "review_required"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


@dataclass(frozen=True)
class GovernedAllowlistEntry:
    domain: str
    category: str = "general"
    trust_level: str = DEFAULT_TRUST_LEVEL
    review_required: bool = True
    read_only_allowed: bool = False
    execution_allowed: bool = False
    runtime_truth_mutation_allowed: bool = False
    ai_agent_execution_allowed: bool = False
    automatic_updates_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def assert_allowlist_registry_non_executing(report: Mapping[str, Any]) -> bool:
    execution_state = dict(report.get("execution_state") or {})
    safety_state = dict(report.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")

    if bool(report.get("live_web_enabled")):
        raise AssertionError("live_web_enabled must remain false")
    if bool(report.get("execution_enabled")):
        raise AssertionError("execution_enabled must remain false")
    if bool(report.get("runtime_truth_mutation_enabled")):
        raise AssertionError("runtime_truth_mutation_enabled must remain false")
    if bool(report.get("ai_agent_execution_enabled")):
        raise AssertionError("ai_agent_execution_enabled must remain false")
    if bool(report.get("automatic_updates_enabled")):
        raise AssertionError("automatic_updates_enabled must remain false")

    if bool(safety_state.get("live_web_enabled")):
        raise AssertionError("safety_state.live_web_enabled must remain false")
    if bool(safety_state.get("execution_enabled")):
        raise AssertionError("safety_state.execution_enabled must remain false")
    if bool(safety_state.get("runtime_truth_mutation_enabled")):
        raise AssertionError("safety_state.runtime_truth_mutation_enabled must remain false")
    if bool(safety_state.get("ai_agent_execution_enabled")):
        raise AssertionError("safety_state.ai_agent_execution_enabled must remain false")
    if bool(safety_state.get("automatic_updates_enabled")):
        raise AssertionError("safety_state.automatic_updates_enabled must remain false")

    return True


class GovernedWebAllowlistRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, GovernedAllowlistEntry] = {}

    def register(
        self,
        domain: str,
        *,
        category: str = "general",
        trust_level: str = DEFAULT_TRUST_LEVEL,
        review_required: bool = True,
        read_only_allowed: bool = False,
    ) -> Dict[str, Any]:
        entry = GovernedAllowlistEntry(
            domain=domain.strip().lower(),
            category=category,
            trust_level=trust_level,
            review_required=review_required,
            read_only_allowed=read_only_allowed,
            execution_allowed=False,
            runtime_truth_mutation_allowed=False,
            ai_agent_execution_allowed=False,
            automatic_updates_allowed=False,
        )
        self._entries[entry.domain] = entry
        return entry.to_dict()

    def get(self, domain: str) -> Optional[Dict[str, Any]]:
        entry = self._entries.get(domain.strip().lower())
        return None if entry is None else entry.to_dict()

    def list_entries(self) -> List[Dict[str, Any]]:
        return [entry.to_dict() for entry in self._entries.values()]

    def build_report(self) -> Dict[str, Any]:
        report = {
            "build": "v18.13",
            "created_at": _utc_now(),
            "registry": "governed_web_allowlist",
            "entries": self.list_entries(),
            "total_entries": len(self._entries),
            "network_call_performed": False,
            "live_web_enabled": False,
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
            "execution_state": _false_execution_state(),
            "safety_state": {
                "read_only_future_path": True,
                "live_web_enabled": False,
                "execution_enabled": False,
                "runtime_truth_mutation_enabled": False,
                "ai_agent_execution_enabled": False,
                "automatic_updates_enabled": False,
                "operator_review_required": True,
            },
            "messages": [
                "allowlist_registry_ready",
                "no_network_call_performed",
                "live_web_remains_disabled",
                "execution_remains_disabled",
            ],
        }

        assert_allowlist_registry_non_executing(report)
        return report


def describe_allowlist_registry_contract() -> Dict[str, Any]:
    return {
        "build": "v18.13",
        "name": "Governed Web Allowlist Policy Registry",
        "default_trust_level": DEFAULT_TRUST_LEVEL,
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
