"""Governed provider health registry for Claire live search.

v18.52 purpose:
- Track whether a live-search provider is eligible for controlled execution.
- Surface operator-visible health state before dashboard/provider execution.
- Preserve fail-closed behavior, manual enable controls, immutable runtime truth,
  and review-gated execution.

This module performs no network calls, no automatic updates, no autonomous
execution, and no runtime-truth mutation. It is a governance/readiness layer.
"""
from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

PROVIDER_HEALTH_CONTRACT = "governed_provider_health_registry.v18_52"

DEFAULT_REQUIRED_FLAGS: Tuple[str, ...] = (
    "CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE",
    "CLAIRE_ALLOW_CONTROLLED_METADATA_GET",
    "CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET",
    "CLAIRE_ALLOW_REAL_SEARCH_PROVIDER",
)

DEFAULT_PROVIDER_ID = "controlled-search-provider"
MAX_PROVIDER_ID_CHARS = 96
MIN_TIMEOUT_MS = 100
MAX_TIMEOUT_MS = 30_000


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    display_name: str
    provider_type: str = "search"
    manual_flags: Tuple[str, ...] = DEFAULT_REQUIRED_FLAGS
    enabled: bool = True
    timeout_ms: int = 5_000
    max_retries: int = 1
    max_results: int = 10
    fail_closed: bool = True
    review_required: bool = True
    runtime_truth_mutation_allowed: bool = False
    automatic_update_allowed: bool = False
    autonomous_execution_allowed: bool = False
    unrestricted_body_fetch_allowed: bool = False
    unbounded_concurrency_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["manual_flags"] = list(self.manual_flags)
        return data


@dataclass
class ProviderHealthState:
    provider_id: str
    status: str
    ready_for_controlled_execution: bool
    manual_flags: Dict[str, bool]
    missing_manual_flags: List[str]
    reason: str
    checked_at_epoch: float
    display_name: str = ""
    provider_type: str = "search"
    timeout_ms: int = 5_000
    max_retries: int = 1
    max_results: int = 10
    last_error: Optional[str] = None
    error_count: int = 0
    cooldown_active: bool = False
    cooldown_until_epoch: Optional[float] = None
    governance: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["operator_visible"] = True
        data["review_required"] = True
        data["runtime_truth_mutated"] = False
        data["automatic_update_triggered"] = False
        data["autonomous_execution_triggered"] = False
        return data


@dataclass
class ProviderRegistryReport:
    status: str
    provider_count: int
    ready_count: int
    blocked_count: int
    providers: List[Dict[str, Any]]
    selected_provider_id: Optional[str]
    governance: Dict[str, Any]
    contract: str = PROVIDER_HEALTH_CONTRACT

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _clean_text(value: Any, limit: int = MAX_PROVIDER_ID_CHARS) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.strip().split())
    return text[:limit]


def _provider_id(value: Any) -> str:
    text = _clean_text(value).lower()
    safe = []
    for char in text:
        if char.isalnum() or char in {"-", "_", "."}:
            safe.append(char)
        elif char.isspace():
            safe.append("-")
    result = "".join(safe).strip("-._")
    return result or DEFAULT_PROVIDER_ID


def _flag_enabled(env: Mapping[str, str], name: str) -> bool:
    return str(env.get(name, "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _governance(config: Optional[ProviderConfig] = None) -> Dict[str, Any]:
    return {
        "contract": PROVIDER_HEALTH_CONTRACT,
        "fail_closed": True if config is None else bool(config.fail_closed),
        "manual_enable_required": True,
        "review_required": True,
        "operator_visible": True,
        "runtime_truth_immutable": True,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_execution_allowed": False,
        "unrestricted_body_fetch_allowed": False,
        "unbounded_concurrency_allowed": False,
        "network_call_performed": False,
        "health_registry_only": True,
    }


def build_default_provider_registry() -> Dict[str, ProviderConfig]:
    """Return the default governed provider registry without network access."""
    config = ProviderConfig(
        provider_id=DEFAULT_PROVIDER_ID,
        display_name="Controlled Search Provider",
        provider_type="live_search",
    )
    return {config.provider_id: config}


def normalize_provider_registry(registry: Optional[Mapping[str, Any]] = None) -> Dict[str, ProviderConfig]:
    if registry is None:
        return build_default_provider_registry()

    normalized: Dict[str, ProviderConfig] = {}
    for key, value in registry.items():
        if isinstance(value, ProviderConfig):
            config = value
        elif isinstance(value, Mapping):
            pid = _provider_id(value.get("provider_id") or key)
            flags_raw = value.get("manual_flags") or DEFAULT_REQUIRED_FLAGS
            flags = tuple(str(item) for item in flags_raw if str(item).strip())
            config = ProviderConfig(
                provider_id=pid,
                display_name=_clean_text(value.get("display_name") or value.get("name") or pid, 160),
                provider_type=_clean_text(value.get("provider_type") or "search", 80),
                manual_flags=flags or DEFAULT_REQUIRED_FLAGS,
                enabled=bool(value.get("enabled", True)),
                timeout_ms=int(value.get("timeout_ms", 5_000)),
                max_retries=int(value.get("max_retries", 1)),
                max_results=int(value.get("max_results", 10)),
            )
        else:
            pid = _provider_id(key)
            config = ProviderConfig(provider_id=pid, display_name=pid)
        normalized[config.provider_id] = config
    return normalized or build_default_provider_registry()


def register_provider(
    registry: Optional[Mapping[str, Any]],
    provider_id: str,
    display_name: Optional[str] = None,
    *,
    manual_flags: Iterable[str] = DEFAULT_REQUIRED_FLAGS,
    provider_type: str = "live_search",
    enabled: bool = True,
    timeout_ms: int = 5_000,
    max_retries: int = 1,
    max_results: int = 10,
) -> Dict[str, ProviderConfig]:
    """Return a new registry with the requested provider registered."""
    new_registry = normalize_provider_registry(registry)
    pid = _provider_id(provider_id)
    new_registry[pid] = ProviderConfig(
        provider_id=pid,
        display_name=_clean_text(display_name or provider_id, 160),
        provider_type=_clean_text(provider_type, 80),
        manual_flags=tuple(str(flag) for flag in manual_flags if str(flag).strip()) or DEFAULT_REQUIRED_FLAGS,
        enabled=enabled,
        timeout_ms=int(timeout_ms),
        max_retries=max(0, int(max_retries)),
        max_results=max(1, int(max_results)),
    )
    return new_registry


def evaluate_provider_health(
    provider_id: str = DEFAULT_PROVIDER_ID,
    registry: Optional[Mapping[str, Any]] = None,
    env: Optional[Mapping[str, str]] = None,
    observation: Optional[Mapping[str, Any]] = None,
    now_epoch: Optional[float] = None,
) -> ProviderHealthState:
    """Evaluate controlled-execution readiness for one provider.

    This is intentionally read-only. Observations may report previous errors or
    cooldowns, but the function itself never performs I/O or network probes.
    """
    now = float(now_epoch if now_epoch is not None else time.time())
    providers = normalize_provider_registry(registry)
    pid = _provider_id(provider_id)
    source_env: Mapping[str, str] = env if env is not None else os.environ
    obs = dict(observation or {})

    if pid not in providers:
        return ProviderHealthState(
            provider_id=pid,
            status="blocked_unknown_provider",
            ready_for_controlled_execution=False,
            manual_flags={},
            missing_manual_flags=[],
            reason="unknown_provider",
            checked_at_epoch=now,
            governance=_governance(),
        )

    config = providers[pid]
    manual_flags = {name: _flag_enabled(source_env, name) for name in config.manual_flags}
    missing = [name for name, enabled in manual_flags.items() if not enabled]
    cooldown_until = obs.get("cooldown_until_epoch")
    try:
        cooldown_until_float = None if cooldown_until is None else float(cooldown_until)
    except (TypeError, ValueError):
        cooldown_until_float = None
    cooldown_active = bool(cooldown_until_float is not None and cooldown_until_float > now)
    last_error = None if obs.get("last_error") is None else _clean_text(obs.get("last_error"), 240)
    try:
        error_count = max(0, int(obs.get("error_count", 0)))
    except (TypeError, ValueError):
        error_count = 0

    status = "ready_for_controlled_execution"
    reason = "provider_ready"
    ready = True

    if not config.enabled:
        status = "blocked_provider_disabled"
        reason = "provider_disabled"
        ready = False
    elif config.timeout_ms < MIN_TIMEOUT_MS or config.timeout_ms > MAX_TIMEOUT_MS:
        status = "blocked_invalid_timeout_policy"
        reason = "invalid_timeout_policy"
        ready = False
    elif missing:
        status = "blocked_manual_enable_required"
        reason = "manual_enable_required"
        ready = False
    elif cooldown_active:
        status = "blocked_cooldown_active"
        reason = "cooldown_active"
        ready = False
    elif error_count >= 3:
        status = "degraded_prior_errors_review_required"
        reason = "prior_errors_require_review"
        ready = False

    return ProviderHealthState(
        provider_id=config.provider_id,
        display_name=config.display_name,
        provider_type=config.provider_type,
        status=status,
        ready_for_controlled_execution=ready,
        manual_flags=manual_flags,
        missing_manual_flags=missing,
        reason=reason,
        checked_at_epoch=now,
        timeout_ms=config.timeout_ms,
        max_retries=config.max_retries,
        max_results=config.max_results,
        last_error=last_error,
        error_count=error_count,
        cooldown_active=cooldown_active,
        cooldown_until_epoch=cooldown_until_float,
        governance=_governance(config),
    )


def build_provider_health_report(
    registry: Optional[Mapping[str, Any]] = None,
    env: Optional[Mapping[str, str]] = None,
    observations: Optional[Mapping[str, Mapping[str, Any]]] = None,
    preferred_provider_id: Optional[str] = None,
) -> ProviderRegistryReport:
    providers = normalize_provider_registry(registry)
    obs_map = observations or {}
    states = [
        evaluate_provider_health(pid, providers, env, obs_map.get(pid))
        for pid in sorted(providers.keys())
    ]
    ready_states = [state for state in states if state.ready_for_controlled_execution]
    selected = None
    if preferred_provider_id:
        preferred = _provider_id(preferred_provider_id)
        selected = next((state.provider_id for state in ready_states if state.provider_id == preferred), None)
    if selected is None and ready_states:
        selected = ready_states[0].provider_id

    status = "provider_ready" if selected else "blocked_no_ready_provider"
    return ProviderRegistryReport(
        status=status,
        provider_count=len(states),
        ready_count=len(ready_states),
        blocked_count=len(states) - len(ready_states),
        providers=[state.to_dict() for state in states],
        selected_provider_id=selected,
        governance=_governance(),
    )


def select_ready_provider(
    registry: Optional[Mapping[str, Any]] = None,
    env: Optional[Mapping[str, str]] = None,
    observations: Optional[Mapping[str, Mapping[str, Any]]] = None,
    preferred_provider_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the selected provider decision as a plain dict for dashboard APIs."""
    report = build_provider_health_report(registry, env, observations, preferred_provider_id)
    data = report.to_dict()
    if report.selected_provider_id:
        selected = next((item for item in data["providers"] if item["provider_id"] == report.selected_provider_id), None)
        data["selected_provider"] = selected
        data["decision"] = "allow_controlled_provider_execution"
    else:
        data["selected_provider"] = None
        data["decision"] = "block_provider_execution"
    data["runtime_truth_mutated"] = False
    data["automatic_update_triggered"] = False
    data["autonomous_execution_triggered"] = False
    return data


# Compatibility aliases for future adapters/tests.
build_governed_provider_health_registry = build_default_provider_registry
build_governed_provider_health_report = build_provider_health_report
evaluate_search_provider_health = evaluate_provider_health
select_governed_ready_provider = select_ready_provider
