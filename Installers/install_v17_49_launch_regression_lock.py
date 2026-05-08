#!/usr/bin/env python3
"""
Claire Syntalion v17.49 — Launch Regression Lock Installer

Single-file root installer. Creates launch regression lock modules, manifests, and tests.
Preserves governance architecture, bounded orchestration, runtime isolation, rollback safety,
and launch continuity. No external dependencies beyond Python stdlib and pytest for tests.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

BUILD = "v17.49"
BUILD_NAME = "Launch Regression Lock"
ROOT = Path.cwd()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


FILES: Dict[str, str] = {}

FILES["src/claire/governance/launch_regression_lock.py"] = r'''"""
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
'''

FILES["src/claire/governance/launch_release_gate.py"] = r'''"""Claire v17.49 launch release gate."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .launch_regression_lock import LaunchRegressionLock, LaunchRegressionLockError


@dataclass(frozen=True)
class LaunchGateDecision:
    allowed: bool
    status: str
    reason: str
    certificate_path: str
    invariant_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LaunchReleaseGate:
    """Blocks launch unless the v17.49 regression certificate passes."""

    def __init__(self, project_root: Optional[str | Path] = None) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.lock = LaunchRegressionLock(self.project_root)

    def evaluate(self, runtime_config: Optional[Mapping[str, Any]] = None) -> LaunchGateDecision:
        certificate = self.lock.run_all(runtime_config)
        cert_path = self.lock.write_certificate(certificate)
        if certificate.passed:
            return LaunchGateDecision(True, "launch_allowed", "Launch regression lock passed.", str(cert_path), certificate.invariant_hash)
        failed = [check.name for check in certificate.checks if not check.passed]
        return LaunchGateDecision(False, "launch_blocked", "Failed checks: " + ", ".join(failed), str(cert_path), certificate.invariant_hash)

    def require_launch_allowed(self, runtime_config: Optional[Mapping[str, Any]] = None) -> LaunchGateDecision:
        decision = self.evaluate(runtime_config)
        if not decision.allowed:
            raise LaunchRegressionLockError(decision.reason)
        return decision
'''

FILES["src/claire/governance/launch_contract_freeze.py"] = r'''"""Claire v17.49 contract freeze utilities."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


@dataclass(frozen=True)
class FrozenContractSnapshot:
    name: str
    version: str
    digest: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def freeze_contract(name: str, version: str, payload: Mapping[str, Any]) -> FrozenContractSnapshot:
    normalized = json.loads(json.dumps(dict(payload), sort_keys=True, default=str))
    digest = hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return FrozenContractSnapshot(name=name, version=version, digest=digest, payload=normalized)


def write_contract_freeze(path: str | Path, snapshots: Iterable[FrozenContractSnapshot]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"frozen_contracts": [snapshot.to_dict() for snapshot in snapshots]}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def read_contract_freeze(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
'''

FILES["manifests/v17_49_launch_regression_lock_manifest.json"] = json.dumps({
    "build": "v17.49",
    "name": "Launch Regression Lock",
    "status": "installed",
    "installed_at": "INSTALL_TIME_REPLACED",
    "prior_builds_locked": ["v17.41", "v17.42", "v17.43", "v17.44", "v17.45", "v17.46", "v17.47", "v17.48"],
    "governance_preserved": {
        "bounded_orchestration": True,
        "rollback_safety": True,
        "runtime_isolation": True,
        "launch_continuity": True,
        "source_trust_memory": True,
        "adaptive_evidence_weighting": True,
        "degraded_mode_execution": True
    },
    "installed_files": [
        "src/claire/governance/launch_regression_lock.py",
        "src/claire/governance/launch_release_gate.py",
        "src/claire/governance/launch_contract_freeze.py",
        "manifests/launch_locked_contracts.json",
        "manifests/launch_rollback_guarantees.json",
        "manifests/launch_operational_state_contract.json",
        "manifests/launch_release_certificate_schema.json",
        "tests/test_v17_49_launch_regression_lock.py"
    ]
}, indent=2)

FILES["manifests/launch_locked_contracts.json"] = json.dumps({
    "lock_version": "v17.49",
    "locked_contracts": [
        "runtime_contract",
        "deployment_contract",
        "manifest_contract",
        "governance_boundary_contract",
        "rollback_contract",
        "api_compatibility_contract",
        "orchestration_invariant_contract",
        "recovery_invariant_contract",
        "operational_state_contract",
        "launch_regression_suite_contract"
    ],
    "contract_policy": {
        "breaking_changes_after_lock": "blocked_without_new_version",
        "runtime_mutation_without_manifest": "blocked",
        "ungoverned_internet_path": "blocked",
        "unbounded_campaign_execution": "blocked"
    }
}, indent=2)

FILES["manifests/launch_rollback_guarantees.json"] = json.dumps({
    "lock_version": "v17.49",
    "rollback_guarantees": {
        "pre_launch_state_capture": True,
        "manifest_replay": True,
        "safe_failure_state": True,
        "no_external_mutation_on_lock_failure": True,
        "certificate_written_before_release": True,
        "launch_blocked_on_failed_lock": True
    }
}, indent=2)

FILES["manifests/launch_operational_state_contract.json"] = json.dumps({
    "lock_version": "v17.49",
    "surfaces": [
        "health_surface",
        "dashboard_surface",
        "degraded_mode_surface",
        "source_trust_surface",
        "campaign_state_surface"
    ],
    "state_requirements": {
        "main_result_never_blank": True,
        "degraded_mode_visible": True,
        "source_trust_visible": True,
        "campaign_scheduler_visible": True,
        "rollback_state_visible": True
    }
}, indent=2)

FILES["manifests/launch_release_certificate_schema.json"] = json.dumps({
    "lock_version": "v17.49",
    "required_fields": [
        "version",
        "status",
        "generated_at",
        "passed",
        "release_blocked",
        "required_prior_builds",
        "locked_contracts",
        "invariant_hash",
        "checks"
    ]
}, indent=2)

FILES["tests/test_v17_49_launch_regression_lock.py"] = r'''from __future__ import annotations

import json
from pathlib import Path

from claire.governance.launch_regression_lock import LaunchRegressionLock, LaunchRegressionLockError, run_launch_regression_lock
from claire.governance.launch_release_gate import LaunchReleaseGate
from claire.governance.launch_contract_freeze import freeze_contract


def test_v17_49_lock_passes_with_default_launch_config():
    cert = run_launch_regression_lock(Path.cwd(), {
        "runtime_isolation": "enforced",
        "max_orchestration_depth": 8,
        "max_runtime_seconds": 900,
        "max_concurrent_campaigns": 4,
    })
    assert cert["version"] == "v17.49"
    assert cert["passed"] is True
    assert cert["release_blocked"] is False
    assert cert["invariant_hash"]
    assert len(cert["checks"]) >= 10


def test_launch_gate_allows_when_regression_lock_passes():
    gate = LaunchReleaseGate(Path.cwd())
    decision = gate.evaluate({"runtime_isolation": "strict"})
    assert decision.allowed is True
    assert decision.status == "launch_allowed"
    assert Path(decision.certificate_path).exists()


def test_launch_gate_blocks_forbidden_runtime_flag():
    gate = LaunchReleaseGate(Path.cwd())
    decision = gate.evaluate({"disable_governance": True})
    assert decision.allowed is False
    assert decision.status == "launch_blocked"
    assert "forbidden_runtime_flags" in decision.reason


def test_orchestration_bounds_are_enforced():
    lock = LaunchRegressionLock(Path.cwd())
    cert = lock.run_all({"max_orchestration_depth": 99, "max_runtime_seconds": 9999, "max_concurrent_campaigns": 99})
    failed = [check.name for check in cert.checks if not check.passed]
    assert "orchestration_bounds" in failed
    assert cert.release_blocked is True


def test_contract_freeze_digest_is_stable():
    first = freeze_contract("runtime_contract", "v17.49", {"b": 2, "a": 1})
    second = freeze_contract("runtime_contract", "v17.49", {"a": 1, "b": 2})
    assert first.digest == second.digest
    assert first.name == "runtime_contract"


def test_certificate_file_is_written():
    lock = LaunchRegressionLock(Path.cwd())
    cert = lock.run_all({})
    path = lock.write_certificate(cert)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == "v17.49"
    assert "checks" in data
'''

FILES["data/launch/v17_49_launch_lock_state.json"] = json.dumps({
    "build": "v17.49",
    "state": "launch_regression_locked",
    "release_mode": "guarded",
    "launch_allowed_only_after_certificate_pass": True,
    "bounded_orchestration": True,
    "rollback_safety": True,
    "runtime_isolation": True,
    "created_at": "INSTALL_TIME_REPLACED"
}, indent=2)


def install() -> None:
    installed: List[Tuple[str, str]] = []
    stamp = now_iso()
    for rel, content in FILES.items():
        rendered = content.replace("INSTALL_TIME_REPLACED", stamp)
        path = ROOT / rel
        write_file(path, rendered)
        installed.append((rel, sha256_text(rendered)))

    # Preserve existing package init files while ensuring import path exists.
    for init in [ROOT / "src" / "claire" / "__init__.py", ROOT / "src" / "claire" / "governance" / "__init__.py"]:
        if not init.exists():
            write_file(init, "")

    installer_manifest = {
        "build": BUILD,
        "name": BUILD_NAME,
        "installed_at": stamp,
        "project_root": str(ROOT),
        "files": [{"path": rel, "sha256": digest} for rel, digest in installed],
        "tests": ["tests/test_v17_49_launch_regression_lock.py"],
        "commands": [
            "python install_v17_49_launch_regression_lock.py",
            "python -m pytest tests/test_v17_49_launch_regression_lock.py",
        ],
    }
    write_file(ROOT / "manifests" / "v17_49_installer_manifest.json", json.dumps(installer_manifest, indent=2, sort_keys=True))
    print("Claire Syntalion v17.49 — Launch Regression Lock installed successfully.")
    print("Installed files:")
    for rel, _ in installed:
        print(f"  - {rel}")
    print("\nRun tests:")
    print("  python -m pytest tests\\test_v17_49_launch_regression_lock.py")


if __name__ == "__main__":
    install()
