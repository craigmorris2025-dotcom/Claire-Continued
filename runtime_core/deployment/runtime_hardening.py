from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .production_profile import ProductionProfile


@dataclass(frozen=True)
class RuntimeHardeningPolicy:
    require_bounded_orchestration: bool = True
    require_rollback_safety: bool = True
    require_runtime_isolation: bool = True
    require_degraded_mode: bool = True
    require_retry_limits: bool = True
    require_source_trust: bool = True
    require_live_dashboard_routes: bool = True


class RuntimeHardeningValidator:
    """Validates launch-critical runtime invariants."""

    REQUIRED_CAPABILITIES = {
        "governed_external_search",
        "persistent_campaigns",
        "campaign_scheduler",
        "runtime_recovery",
        "adaptive_source_trust",
        "source_quarantine",
        "operations_dashboard",
        "bounded_orchestration",
        "rollback_safety",
        "runtime_isolation",
    }

    def __init__(self, policy: RuntimeHardeningPolicy | None = None) -> None:
        self.policy = policy or RuntimeHardeningPolicy()

    def validate_capabilities(self, capabilities: Iterable[str]) -> list[str]:
        present = {str(item).strip() for item in capabilities if str(item).strip()}
        missing = sorted(self.REQUIRED_CAPABILITIES - present)
        return [f"missing launch-critical capability: {name}" for name in missing]

    def validate_profile(self, profile: ProductionProfile) -> list[str]:
        findings: list[str] = []
        if self.policy.require_bounded_orchestration and profile.allow_unbounded_orchestration:
            findings.append("profile violates bounded orchestration")
        if self.policy.require_runtime_isolation and profile.allow_runtime_mutation:
            findings.append("profile violates runtime isolation")
        if self.policy.require_retry_limits and profile.max_retry_attempts > 5:
            findings.append("retry limit exceeds production maximum")
        if self.policy.require_source_trust and not profile.require_source_governance:
            findings.append("source trust governance disabled")
        return findings

    def validate_manifest_shape(self, manifest: dict) -> list[str]:
        findings: list[str] = []
        if not isinstance(manifest, dict):
            return ["manifest must be a dictionary"]
        if manifest.get("build_id") != "v17.48":
            findings.append("manifest build_id must be v17.48")
        protected = manifest.get("protected_architecture", {})
        for key in [
            "governance_architecture",
            "bounded_orchestration",
            "rollback_safety",
            "runtime_isolation",
            "launch_continuity",
        ]:
            if protected.get(key) is not True:
                findings.append(f"protected architecture flag must be true: {key}")
        if not manifest.get("tests"):
            findings.append("manifest must include tests")
        return findings
