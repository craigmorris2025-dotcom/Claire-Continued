from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional


class ProductionProfileError(ValueError):
    """Raised when a production deployment profile is invalid."""


@dataclass(frozen=True)
class ProductionProfile:
    """Governed production deployment profile."""

    environment: str = "production"
    debug: bool = False
    allow_unbounded_orchestration: bool = False
    allow_runtime_mutation: bool = False
    enable_external_internet: bool = True
    require_source_governance: bool = True
    require_recovery_governance: bool = True
    require_dashboard_health: bool = True
    max_campaign_batch_size: int = 25
    max_retry_attempts: int = 3
    deployment_id: str = "local-production"
    allowed_hosts: tuple[str, ...] = field(default_factory=lambda: ("127.0.0.1", "localhost"))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.environment.lower() != "production":
            errors.append("environment must be 'production' for launch hardening")
        if self.debug:
            errors.append("debug must be false in production")
        if self.allow_unbounded_orchestration:
            errors.append("unbounded orchestration is forbidden in production")
        if self.allow_runtime_mutation:
            errors.append("runtime mutation is forbidden in production")
        if not self.require_source_governance:
            errors.append("source governance must remain required")
        if not self.require_recovery_governance:
            errors.append("recovery governance must remain required")
        if not self.require_dashboard_health:
            errors.append("dashboard health contract must remain required")
        if self.max_campaign_batch_size < 1 or self.max_campaign_batch_size > 100:
            errors.append("max_campaign_batch_size must be between 1 and 100")
        if self.max_retry_attempts < 0 or self.max_retry_attempts > 5:
            errors.append("max_retry_attempts must be between 0 and 5")
        if not self.deployment_id.strip():
            errors.append("deployment_id must be non-empty")
        if not self.allowed_hosts:
            errors.append("allowed_hosts must contain at least one host")
        return errors


def _bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ProductionProfileError(f"invalid boolean value: {value!r}")


def _int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ProductionProfileError(f"invalid integer value: {value!r}") from exc


def _hosts(value: Optional[str]) -> tuple[str, ...]:
    if not value:
        return ("127.0.0.1", "localhost")
    hosts = tuple(host.strip() for host in value.split(",") if host.strip())
    if not hosts:
        raise ProductionProfileError("PLATFORM_ALLOWED_HOSTS did not contain any valid hosts")
    return hosts


def load_production_profile(env: Optional[Mapping[str, str]] = None, project_root: Optional[Path] = None) -> ProductionProfile:
    """Load and validate a production profile from environment variables."""

    source = dict(os.environ if env is None else env)
    profile = ProductionProfile(
        environment=source.get("PLATFORM_ENV", "production").strip().lower(),
        debug=_bool(source.get("PLATFORM_DEBUG"), False),
        allow_unbounded_orchestration=_bool(source.get("PLATFORM_ALLOW_UNBOUNDED_ORCHESTRATION"), False),
        allow_runtime_mutation=_bool(source.get("PLATFORM_ALLOW_RUNTIME_MUTATION"), False),
        enable_external_internet=_bool(source.get("PLATFORM_EXTERNAL_INTERNET"), True),
        require_source_governance=_bool(source.get("PLATFORM_REQUIRE_SOURCE_GOVERNANCE"), True),
        require_recovery_governance=_bool(source.get("PLATFORM_REQUIRE_RECOVERY_GOVERNANCE"), True),
        require_dashboard_health=_bool(source.get("PLATFORM_REQUIRE_DASHBOARD_HEALTH"), True),
        max_campaign_batch_size=_int(source.get("PLATFORM_MAX_CAMPAIGN_BATCH_SIZE"), 25),
        max_retry_attempts=_int(source.get("PLATFORM_MAX_RETRY_ATTEMPTS"), 3),
        deployment_id=source.get("PLATFORM_DEPLOYMENT_ID", "local-production").strip(),
        allowed_hosts=_hosts(source.get("PLATFORM_ALLOWED_HOSTS")),
    )
    errors = profile.validate()
    if errors:
        raise ProductionProfileError("; ".join(errors))
    return profile
