"""
Claire Syntalion v17.49 — Launch Regression Lock

This module freezes launch-critical runtime invariants before internet-ready release.
It does not execute campaigns, mutate external state, or bypass previous governance.
It validates contracts, manifests, rollback guarantees, isolation boundaries, and
operational continuity using deterministic stdlib-only checks.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


LOCK_VERSION = "v17.49"
LOCK_NAME = "Launch Regression Lock"
LOCK_STATUS = "locked"

REQUIRED_PRIOR_BUILDS: Tuple[str, ...] = (
    "v17.41",
    "v17.42",
    "v17.43",
    "v17.44",
    "v17.45",
    "v17.46",
    "v17.47",
    "v17.48",
)

REQUIRED_INVARIANTS: Tuple[str, ...] = (
    "governed_internet_activation",
    "runtime_internet_integration",
    "persistent_campaign_runtime",
    "governed_campaign_scheduler",
    "runtime_stability_recovery",
    "source_trust_reputation",
    "internet_operations_dashboard",
    "deployment_production_hardening",
    "bounded_orchestration_preserved",
    "runtime_isolation_preserved",
    "rollback_safety_preserved",
    "launch_continuity_preserved",
)

LOCKED_CONTRACTS: Tuple[str, ...] = (
    "runtime_contract",
    "deployment_contract",
    "manifest_contract",
    "governance_boundary_contract",
    "rollback_contract",
    "api_compatibility_contract",
    "orchestration_invariant_contract",
    "recovery_invariant_contract",
    "operational_state_contract",
    "launch_regression_suite_contract",
)

FORBIDDEN_RUNTIME_FLAGS: Tuple[str, ...] = (
    "disable_governance",
    "unbounded_orchestration",
    "unsafe_external_write",
    "skip_rollback_capture",
    "skip_source_trust",
    "disable_runtime_isolation",
    "force_live_without_lock",
)


class LaunchRegressionLockError(RuntimeError):
    """Raised when the launch lock detects a release-blocking violation."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RegressionCheckResult:
    name: str
    passed: bool
    severity: str
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LaunchLockCertificate:
    version: str
    status: str
    generated_at: str
    passed: bool
    release_blocked: bool
    required_prior_builds: Tuple[str, ...]
    locked_contracts: Tuple[str, ...]
    invariant_hash: str
    checks: Tuple[RegressionCheckResult, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "generated_at": self.generated_at,
            "passed": self.passed,
            "release_blocked": self.release_blocked,
            "required_prior_builds": list(self.required_prior_builds),
            "locked_contracts": list(self.locked_contracts),
            "invariant_hash": self.invariant_hash,
            "checks": [check.to_dict() for check in self.checks],
        }


class LaunchRegressionLock:
    """Deterministic launch-readiness validator for Claire v17.49."""

    def __init__(self, project_root: Optional[Path | str] = None) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.manifest_dir = self.project_root / "manifests"
        self.runtime_dir = self.project_root / "runtime"
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"

    def run_all(self, runtime_config: Optional[Mapping[str, Any]] = None) -> LaunchLockCertificate:
        config = dict(runtime_config or {})
        checks: List[RegressionCheckResult] = []
        checks.append(self.check_prior_build_chain())
        checks.append(self.check_locked_contract_catalog())
        checks.append(self.check_runtime_flags(config))
        checks.append(self.check_required_directories())
        checks.append(self.check_manifest_integrity())
        checks.append(self.check_rollback_continuity())
        checks.append(self.check_orchestration_bounds(config))
        checks.append(self.check_isolation_boundary(config))
        checks.append(self.check_operational_state_contract())
        checks.append(self.check_release_certificate_contract())

        passed = all(check.passed for check in checks)
        invariant_hash = self.compute_invariant_hash(checks)
        return LaunchLockCertificate(
            version=LOCK_VERSION,
            status=LOCK_STATUS if passed else "blocked",
            generated_at=utc_now(),
            passed=passed,
            release_blocked=not passed,
            required_prior_builds=REQUIRED_PRIOR_BUILDS,
            locked_contracts=LOCKED_CONTRACTS,
            invariant_hash=invariant_hash,
            checks=tuple(checks),
        )

    def check_prior_build_chain(self) -> RegressionCheckResult:
        build_manifest = self.manifest_dir / "v17_49_launch_regression_lock_manifest.json"
        evidence: Dict[str, Any] = {"required": list(REQUIRED_PRIOR_BUILDS)}
        if build_manifest.exists():
            try:
                data = json.loads(build_manifest.read_text(encoding="utf-8"))
                installed = data.get("prior_builds_locked", [])
                evidence["manifest_prior_builds"] = installed
                missing = [build for build in REQUIRED_PRIOR_BUILDS if build not in installed]
                return RegressionCheckResult(
                    "prior_build_chain",
                    not missing,
                    "critical",
                    "All prior launch-critical builds are represented." if not missing else "Missing prior build locks.",
                    {**evidence, "missing": missing},
                )
            except json.JSONDecodeError as exc:
                return RegressionCheckResult("prior_build_chain", False, "critical", "Manifest JSON is invalid.", {**evidence, "error": str(exc)})
        return RegressionCheckResult("prior_build_chain", False, "critical", "v17.49 manifest is missing.", evidence)

    def check_locked_contract_catalog(self) -> RegressionCheckResult:
        path = self.manifest_dir / "launch_locked_contracts.json"
        evidence = {"required_contracts": list(LOCKED_CONTRACTS), "path": str(path)}
        if not path.exists():
            return RegressionCheckResult("locked_contract_catalog", False, "critical", "Locked contract catalog is missing.", evidence)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return RegressionCheckResult("locked_contract_catalog", False, "critical", "Locked contract catalog JSON is invalid.", {**evidence, "error": str(exc)})
        locked = data.get("locked_contracts", [])
        missing = [item for item in LOCKED_CONTRACTS if item not in locked]
        return RegressionCheckResult(
            "locked_contract_catalog",
            not missing and data.get("lock_version") == LOCK_VERSION,
            "critical",
            "Launch contracts are locked." if not missing and data.get("lock_version") == LOCK_VERSION else "Launch contract catalog is incomplete.",
            {**evidence, "locked": locked, "missing": missing, "lock_version": data.get("lock_version")},
        )

    def check_runtime_flags(self, config: Mapping[str, Any]) -> RegressionCheckResult:
        active_forbidden = [flag for flag in FORBIDDEN_RUNTIME_FLAGS if bool(config.get(flag))]
        return RegressionCheckResult(
            "forbidden_runtime_flags",
            not active_forbidden,
            "critical",
            "No forbidden runtime flags are active." if not active_forbidden else "Forbidden launch-time runtime flags are active.",
            {"forbidden_flags": list(FORBIDDEN_RUNTIME_FLAGS), "active_forbidden": active_forbidden},
        )

    def check_required_directories(self) -> RegressionCheckResult:
        required = [self.manifest_dir, self.data_dir, self.output_dir]
        missing = [str(path) for path in required if not path.exists()]
        return RegressionCheckResult(
            "required_directories",
            not missing,
            "high",
            "Required launch directories exist." if not missing else "Required launch directories are missing.",
            {"missing": missing, "required": [str(path) for path in required]},
        )

    def check_manifest_integrity(self) -> RegressionCheckResult:
        manifest_path = self.manifest_dir / "v17_49_launch_regression_lock_manifest.json"
        evidence = {"path": str(manifest_path)}
        if not manifest_path.exists():
            return RegressionCheckResult("manifest_integrity", False, "critical", "Launch lock manifest is missing.", evidence)
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return RegressionCheckResult("manifest_integrity", False, "critical", "Launch lock manifest JSON is invalid.", {**evidence, "error": str(exc)})
        required_keys = {"build", "name", "status", "installed_files", "prior_builds_locked", "governance_preserved"}
        missing_keys = sorted(required_keys.difference(data.keys()))
        governance = data.get("governance_preserved", {})
        governance_ok = all(bool(governance.get(key)) for key in ("bounded_orchestration", "rollback_safety", "runtime_isolation", "launch_continuity"))
        passed = not missing_keys and data.get("build") == LOCK_VERSION and governance_ok
        return RegressionCheckResult(
            "manifest_integrity",
            passed,
            "critical",
            "Launch manifest integrity validated." if passed else "Launch manifest integrity failed.",
            {**evidence, "missing_keys": missing_keys, "build": data.get("build"), "governance_ok": governance_ok},
        )

    def check_rollback_continuity(self) -> RegressionCheckResult:
        rollback_path = self.manifest_dir / "launch_rollback_guarantees.json"
        evidence = {"path": str(rollback_path)}
        if not rollback_path.exists():
            return RegressionCheckResult("rollback_continuity", False, "critical", "Rollback guarantee manifest is missing.", evidence)
        data = json.loads(rollback_path.read_text(encoding="utf-8"))
        guarantees = data.get("rollback_guarantees", {})
        required = ["pre_launch_state_capture", "manifest_replay", "safe_failure_state", "no_external_mutation_on_lock_failure"]
        missing = [key for key in required if not guarantees.get(key)]
        return RegressionCheckResult(
            "rollback_continuity",
            not missing,
            "critical",
            "Rollback guarantees are locked." if not missing else "Rollback guarantee lock is incomplete.",
            {**evidence, "missing": missing, "guarantees": guarantees},
        )

    def check_orchestration_bounds(self, config: Mapping[str, Any]) -> RegressionCheckResult:
        max_depth = int(config.get("max_orchestration_depth", 8))
        max_runtime_seconds = int(config.get("max_runtime_seconds", 900))
        max_campaigns = int(config.get("max_concurrent_campaigns", 4))
        passed = max_depth <= 12 and max_runtime_seconds <= 1800 and max_campaigns <= 8
        return RegressionCheckResult(
            "orchestration_bounds",
            passed,
            "critical",
            "Bounded orchestration remains within launch envelope." if passed else "Orchestration bounds exceed launch envelope.",
            {"max_orchestration_depth": max_depth, "max_runtime_seconds": max_runtime_seconds, "max_concurrent_campaigns": max_campaigns},
        )

    def check_isolation_boundary(self, config: Mapping[str, Any]) -> RegressionCheckResult:
        isolation_mode = str(config.get("runtime_isolation", "enforced"))
        external_mutation = bool(config.get("allow_external_mutation_during_lock", False))
        passed = isolation_mode in {"enforced", "strict"} and not external_mutation
        return RegressionCheckResult(
            "runtime_isolation_boundary",
            passed,
            "critical",
            "Runtime isolation boundary is enforced." if passed else "Runtime isolation boundary is unsafe.",
            {"runtime_isolation": isolation_mode, "allow_external_mutation_during_lock": external_mutation},
        )

    def check_operational_state_contract(self) -> RegressionCheckResult:
        state_contract = self.manifest_dir / "launch_operational_state_contract.json"
        evidence = {"path": str(state_contract)}
        if not state_contract.exists():
            return RegressionCheckResult("operational_state_contract", False, "high", "Operational state contract is missing.", evidence)
        data = json.loads(state_contract.read_text(encoding="utf-8"))
        required = ["health_surface", "dashboard_surface", "degraded_mode_surface", "source_trust_surface", "campaign_state_surface"]
        missing = [key for key in required if key not in data.get("surfaces", [])]
        return RegressionCheckResult(
            "operational_state_contract",
            not missing,
            "high",
            "Operational state surfaces are launch-locked." if not missing else "Operational state surfaces are incomplete.",
            {**evidence, "missing": missing, "surfaces": data.get("surfaces", [])},
        )

    def check_release_certificate_contract(self) -> RegressionCheckResult:
        cert_path = self.manifest_dir / "launch_release_certificate_schema.json"
        evidence = {"path": str(cert_path)}
        if not cert_path.exists():
            return RegressionCheckResult("release_certificate_contract", False, "high", "Release certificate schema is missing.", evidence)
        data = json.loads(cert_path.read_text(encoding="utf-8"))
        required_fields = ["version", "status", "generated_at", "passed", "release_blocked", "invariant_hash", "checks"]
        fields = data.get("required_fields", [])
        missing = [field for field in required_fields if field not in fields]
        return RegressionCheckResult(
            "release_certificate_contract",
            not missing,
            "high",
            "Release certificate schema is locked." if not missing else "Release certificate schema is incomplete.",
            {**evidence, "missing": missing, "required_fields": fields},
        )

    def compute_invariant_hash(self, checks: Sequence[RegressionCheckResult]) -> str:
        payload = {
            "version": LOCK_VERSION,
            "required_prior_builds": list(REQUIRED_PRIOR_BUILDS),
            "required_invariants": list(REQUIRED_INVARIANTS),
            "locked_contracts": list(LOCKED_CONTRACTS),
            "checks": [check.to_dict() for check in checks],
        }
        return stable_hash(payload)

    def write_certificate(self, certificate: LaunchLockCertificate, path: Optional[Path | str] = None) -> Path:
        target = Path(path) if path else self.output_dir / "v17_49_launch_lock_certificate.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(certificate.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return target


def run_launch_regression_lock(project_root: Optional[Path | str] = None, runtime_config: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    lock = LaunchRegressionLock(project_root)
    certificate = lock.run_all(runtime_config)
    lock.write_certificate(certificate)
    if not certificate.passed:
        failed = [check.name for check in certificate.checks if not check.passed]
        raise LaunchRegressionLockError(f"Launch regression lock failed: {', '.join(failed)}")
    return certificate.to_dict()
