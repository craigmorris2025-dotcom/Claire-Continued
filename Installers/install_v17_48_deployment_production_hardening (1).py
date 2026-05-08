#!/usr/bin/env python3
"""
Claire Syntalion v17.48 — Deployment + Production Hardening Installer

Run from project root:
    python install_v17_48_deployment_production_hardening.py

Installs:
- Governed production environment profile system
- Deployment readiness validator
- Runtime hardening guardrails
- Secret/material leakage scanner
- Network exposure policy validator
- Production health contract
- Deployment manifest
- Regression tests
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


BUILD_ID = "v17.48"
BUILD_NAME = "Deployment + Production Hardening"
INSTALLER_NAME = "install_v17_48_deployment_production_hardening.py"


FILES: Dict[str, str] = {}

FILES["src/claire/deployment/__init__.py"] = """\"\"\"
Claire deployment hardening package.

This package provides governed production-readiness validation without starting,
mutating, or expanding the autonomous internet runtime.
\"\"\"

from .production_profile import ProductionProfile, ProductionProfileError, load_production_profile
from .deployment_readiness import DeploymentReadinessReport, DeploymentReadinessValidator, ReadinessFinding
from .runtime_hardening import RuntimeHardeningPolicy, RuntimeHardeningValidator
from .secret_scanner import SecretScanner, SecretScanFinding
from .network_policy import NetworkExposurePolicy, NetworkExposureValidator
from .health_contract import ProductionHealthContract, ProductionHealthStatus

__all__ = [
    "ProductionProfile",
    "ProductionProfileError",
    "load_production_profile",
    "DeploymentReadinessReport",
    "DeploymentReadinessValidator",
    "ReadinessFinding",
    "RuntimeHardeningPolicy",
    "RuntimeHardeningValidator",
    "SecretScanner",
    "SecretScanFinding",
    "NetworkExposurePolicy",
    "NetworkExposureValidator",
    "ProductionHealthContract",
    "ProductionHealthStatus",
]
"""

FILES["src/claire/deployment/production_profile.py"] = """from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional


class ProductionProfileError(ValueError):
    \"\"\"Raised when a production deployment profile is invalid.\"\"\"


@dataclass(frozen=True)
class ProductionProfile:
    \"\"\"Governed production deployment profile.\"\"\"

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
        raise ProductionProfileError("CLAIRE_ALLOWED_HOSTS did not contain any valid hosts")
    return hosts


def load_production_profile(env: Optional[Mapping[str, str]] = None, project_root: Optional[Path] = None) -> ProductionProfile:
    \"\"\"Load and validate a production profile from environment variables.\"\"\"

    source = dict(os.environ if env is None else env)
    profile = ProductionProfile(
        environment=source.get("CLAIRE_ENV", "production").strip().lower(),
        debug=_bool(source.get("CLAIRE_DEBUG"), False),
        allow_unbounded_orchestration=_bool(source.get("CLAIRE_ALLOW_UNBOUNDED_ORCHESTRATION"), False),
        allow_runtime_mutation=_bool(source.get("CLAIRE_ALLOW_RUNTIME_MUTATION"), False),
        enable_external_internet=_bool(source.get("CLAIRE_EXTERNAL_INTERNET"), True),
        require_source_governance=_bool(source.get("CLAIRE_REQUIRE_SOURCE_GOVERNANCE"), True),
        require_recovery_governance=_bool(source.get("CLAIRE_REQUIRE_RECOVERY_GOVERNANCE"), True),
        require_dashboard_health=_bool(source.get("CLAIRE_REQUIRE_DASHBOARD_HEALTH"), True),
        max_campaign_batch_size=_int(source.get("CLAIRE_MAX_CAMPAIGN_BATCH_SIZE"), 25),
        max_retry_attempts=_int(source.get("CLAIRE_MAX_RETRY_ATTEMPTS"), 3),
        deployment_id=source.get("CLAIRE_DEPLOYMENT_ID", "local-production").strip(),
        allowed_hosts=_hosts(source.get("CLAIRE_ALLOWED_HOSTS")),
    )
    errors = profile.validate()
    if errors:
        raise ProductionProfileError("; ".join(errors))
    return profile
"""

FILES["src/claire/deployment/runtime_hardening.py"] = """from __future__ import annotations

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
    \"\"\"Validates launch-critical runtime invariants.\"\"\"

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
"""

FILES["src/claire/deployment/secret_scanner.py"] = """from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SecretScanFinding:
    path: str
    line_number: int
    pattern_name: str
    detail: str


class SecretScanner:
    \"\"\"Scans project text files for accidental secret material before deployment.\"\"\"

    DEFAULT_EXCLUDED_DIRS = {
        ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
        "node_modules", "dist", "build", ".mypy_cache", "backups",
    }
    DEFAULT_EXTENSIONS = {".py", ".json", ".toml", ".yaml", ".yml", ".env", ".txt", ".md", ".ini", ".cfg"}
    PATTERNS = {
        "aws_access_key": re.compile(r"\\bAKIA[0-9A-Z]{16}\\b"),
        "private_key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
        "generic_secret_assignment": re.compile(
            r"(?i)\\b(secret|api[_-]?key|token|password)\\b\\s*[:=]\\s*['\\"][^'\\"]{12,}['\\"]"
        ),
        "bearer_token": re.compile(r"(?i)\\bbearer\\s+[a-z0-9._\\-]{20,}"),
    }

    def __init__(self, excluded_dirs: Iterable[str] | None = None, extensions: Iterable[str] | None = None) -> None:
        self.excluded_dirs = set(excluded_dirs or self.DEFAULT_EXCLUDED_DIRS)
        self.extensions = set(extensions or self.DEFAULT_EXTENSIONS)

    def scan_text(self, text: str, path: str = "<memory>") -> list[SecretScanFinding]:
        findings: list[SecretScanFinding] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") and "example" in stripped.lower():
                continue
            for name, pattern in self.PATTERNS.items():
                if pattern.search(line):
                    findings.append(SecretScanFinding(path, line_number, name, "possible secret material detected"))
        return findings

    def scan_project(self, project_root: Path) -> list[SecretScanFinding]:
        root = Path(project_root)
        findings: list[SecretScanFinding] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in self.excluded_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in self.extensions and path.name != ".env":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            findings.extend(self.scan_text(text, str(path.relative_to(root))))
        return findings
"""

FILES["src/claire/deployment/network_policy.py"] = """from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class NetworkExposurePolicy:
    allowed_hosts: tuple[str, ...] = ("127.0.0.1", "localhost")
    forbid_wildcard_cors: bool = True
    forbid_debug_ports: bool = True
    require_https_at_edge: bool = True


class NetworkExposureValidator:
    DEBUG_PORTS = {3000, 5000, 5173, 8000, 8080, 8888}

    def __init__(self, policy: NetworkExposurePolicy | None = None) -> None:
        self.policy = policy or NetworkExposurePolicy()

    def validate_allowed_hosts(self, hosts: Iterable[str]) -> list[str]:
        host_set = {str(host).strip() for host in hosts if str(host).strip()}
        findings: list[str] = []
        if "*" in host_set and self.policy.forbid_wildcard_cors:
            findings.append("wildcard host exposure is forbidden in production")
        if not host_set:
            findings.append("allowed hosts cannot be empty")
        if "0.0.0.0" in host_set:
            findings.append("0.0.0.0 is a bind address, not a safe allowed host")
        return findings

    def validate_cors_origins(self, origins: Iterable[str]) -> list[str]:
        origin_set = {str(origin).strip() for origin in origins if str(origin).strip()}
        findings: list[str] = []
        if self.policy.forbid_wildcard_cors and "*" in origin_set:
            findings.append("wildcard CORS origin is forbidden in production")
        for origin in origin_set:
            if origin.startswith("http://") and self.policy.require_https_at_edge:
                if "localhost" not in origin and "127.0.0.1" not in origin:
                    findings.append(f"non-local production origin must use HTTPS: {origin}")
        return findings

    def validate_port(self, port: int) -> list[str]:
        if self.policy.forbid_debug_ports and port in self.DEBUG_PORTS:
            return [f"debug/development port is not production-hardened: {port}"]
        if port <= 0 or port > 65535:
            return [f"invalid TCP port: {port}"]
        return []
"""

FILES["src/claire/deployment/health_contract.py"] = """from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping


@dataclass(frozen=True)
class ProductionHealthStatus:
    status: str
    build_id: str
    timestamp: str
    checks: dict[str, str] = field(default_factory=dict)
    degraded: bool = False

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "build_id": self.build_id,
            "timestamp": self.timestamp,
            "checks": dict(self.checks),
            "degraded": self.degraded,
        }


class ProductionHealthContract:
    REQUIRED_CHECKS = (
        "runtime",
        "internet_governance",
        "campaign_scheduler",
        "source_trust",
        "recovery",
        "dashboard",
    )

    def create_status(self, checks: Mapping[str, str], build_id: str = "v17.48") -> ProductionHealthStatus:
        normalized = {str(k): str(v) for k, v in checks.items()}
        missing = [name for name in self.REQUIRED_CHECKS if name not in normalized]
        if missing:
            status = "blocked"
            for name in missing:
                normalized[name] = "missing"
        elif any(value in {"failed", "blocked"} for value in normalized.values()):
            status = "blocked"
        elif any(value in {"degraded", "recovering"} for value in normalized.values()):
            status = "degraded"
        else:
            status = "ready"
        return ProductionHealthStatus(
            status=status,
            build_id=build_id,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            checks=normalized,
            degraded=(status == "degraded"),
        )

    def validate_status(self, payload: Mapping[str, object]) -> list[str]:
        findings: list[str] = []
        if payload.get("build_id") != "v17.48":
            findings.append("health payload build_id must be v17.48")
        if payload.get("status") not in {"ready", "degraded", "blocked"}:
            findings.append("health status must be ready, degraded, or blocked")
        checks = payload.get("checks")
        if not isinstance(checks, dict):
            findings.append("health checks must be a dictionary")
            return findings
        for check in self.REQUIRED_CHECKS:
            if check not in checks:
                findings.append(f"missing required health check: {check}")
        return findings
"""

FILES["src/claire/deployment/deployment_readiness.py"] = """from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from .health_contract import ProductionHealthContract
from .network_policy import NetworkExposureValidator
from .production_profile import ProductionProfile, load_production_profile
from .runtime_hardening import RuntimeHardeningValidator
from .secret_scanner import SecretScanner


@dataclass(frozen=True)
class ReadinessFinding:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class DeploymentReadinessReport:
    build_id: str
    ready: bool
    findings: list[ReadinessFinding] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "build_id": self.build_id,
            "ready": self.ready,
            "findings": [
                {"severity": item.severity, "code": item.code, "message": item.message}
                for item in self.findings
            ],
        }


class DeploymentReadinessValidator:
    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.runtime_validator = RuntimeHardeningValidator()
        self.secret_scanner = SecretScanner()
        self.network_validator = NetworkExposureValidator()
        self.health_contract = ProductionHealthContract()

    def _finding(self, severity: str, code: str, message: str) -> ReadinessFinding:
        return ReadinessFinding(severity=severity, code=code, message=message)

    def validate(
        self,
        capabilities: Iterable[str],
        env: Mapping[str, str] | None = None,
        cors_origins: Iterable[str] | None = None,
        port: int | None = None,
        scan_secrets: bool = True,
    ) -> DeploymentReadinessReport:
        findings: list[ReadinessFinding] = []
        try:
            profile = load_production_profile(env=env, project_root=self.project_root)
        except Exception as exc:
            findings.append(self._finding("blocker", "production_profile_invalid", str(exc)))
            profile = ProductionProfile()

        for message in profile.validate():
            findings.append(self._finding("blocker", "production_profile", message))
        for message in self.runtime_validator.validate_profile(profile):
            findings.append(self._finding("blocker", "runtime_hardening", message))
        for message in self.runtime_validator.validate_capabilities(capabilities):
            findings.append(self._finding("blocker", "missing_capability", message))
        for message in self.network_validator.validate_allowed_hosts(profile.allowed_hosts):
            findings.append(self._finding("blocker", "network_allowed_hosts", message))
        if cors_origins is not None:
            for message in self.network_validator.validate_cors_origins(cors_origins):
                findings.append(self._finding("blocker", "network_cors", message))
        if port is not None:
            for message in self.network_validator.validate_port(port):
                findings.append(self._finding("warning", "network_port", message))
        if scan_secrets:
            for secret in self.secret_scanner.scan_project(self.project_root):
                findings.append(
                    self._finding("blocker", "secret_material", f"{secret.path}:{secret.line_number} {secret.pattern_name}")
                )
        ready = not any(item.severity == "blocker" for item in findings)
        return DeploymentReadinessReport(build_id="v17.48", ready=ready, findings=findings)

    def write_report(self, report: DeploymentReadinessReport, output_path: Path | str) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report.as_dict(), indent=2), encoding="utf-8")
        return path
"""

FILES["manifests/v17_48_deployment_production_hardening.json"] = """{
  "build_id": "v17.48",
  "name": "Deployment + Production Hardening",
  "phase": "launch-critical-hardening",
  "installed_by": "install_v17_48_deployment_production_hardening.py",
  "protected_architecture": {
    "governance_architecture": true,
    "bounded_orchestration": true,
    "rollback_safety": true,
    "runtime_isolation": true,
    "launch_continuity": true,
    "internet_runtime_integration": true,
    "persistent_campaigns": true,
    "adaptive_source_trust": true,
    "operations_dashboard": true
  },
  "capabilities_added": [
    "production_profile_validation",
    "deployment_readiness_gate",
    "runtime_hardening_policy",
    "secret_material_scan",
    "network_exposure_policy",
    "production_health_contract"
  ],
  "runtime_mutation": false,
  "external_network_calls": false,
  "rollback_safe": true,
  "tests": [
    "tests/test_v17_48_deployment_production_hardening.py"
  ],
  "files": [
    "src/claire/deployment/__init__.py",
    "src/claire/deployment/production_profile.py",
    "src/claire/deployment/runtime_hardening.py",
    "src/claire/deployment/secret_scanner.py",
    "src/claire/deployment/network_policy.py",
    "src/claire/deployment/health_contract.py",
    "src/claire/deployment/deployment_readiness.py",
    "manifests/v17_48_deployment_production_hardening.json",
    "tests/test_v17_48_deployment_production_hardening.py"
  ]
}
"""

FILES["tests/test_v17_48_deployment_production_hardening.py"] = """from __future__ import annotations

import json
from pathlib import Path

import pytest

from claire.deployment import (
    DeploymentReadinessValidator,
    NetworkExposureValidator,
    ProductionHealthContract,
    ProductionProfileError,
    RuntimeHardeningValidator,
    SecretScanner,
    load_production_profile,
)


def test_production_profile_accepts_safe_defaults():
    profile = load_production_profile(env={})
    assert profile.environment == "production"
    assert profile.debug is False
    assert profile.allow_unbounded_orchestration is False
    assert profile.allow_runtime_mutation is False
    assert profile.max_retry_attempts == 3


def test_production_profile_rejects_debug_mode():
    with pytest.raises(ProductionProfileError):
        load_production_profile(env={"CLAIRE_DEBUG": "true"})


def test_runtime_hardening_requires_launch_critical_capabilities():
    validator = RuntimeHardeningValidator()
    findings = validator.validate_capabilities(
        {
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
    )
    assert findings == []


def test_runtime_hardening_reports_missing_capability():
    validator = RuntimeHardeningValidator()
    findings = validator.validate_capabilities({"governed_external_search"})
    assert any("persistent_campaigns" in item for item in findings)


def test_secret_scanner_detects_secret_assignment():
    scanner = SecretScanner()
    findings = scanner.scan_text("api_key = 'abcdefghijklmnopqrstuvwxyz'", path="sample.py")
    assert findings
    assert findings[0].pattern_name == "generic_secret_assignment"


def test_network_policy_rejects_wildcard_cors():
    validator = NetworkExposureValidator()
    findings = validator.validate_cors_origins(["*"])
    assert findings


def test_health_contract_ready_status():
    contract = ProductionHealthContract()
    status = contract.create_status(
        {
            "runtime": "ok",
            "internet_governance": "ok",
            "campaign_scheduler": "ok",
            "source_trust": "ok",
            "recovery": "ok",
            "dashboard": "ok",
        }
    )
    payload = status.as_dict()
    assert payload["status"] == "ready"
    assert contract.validate_status(payload) == []


def test_health_contract_blocks_missing_checks():
    contract = ProductionHealthContract()
    status = contract.create_status({"runtime": "ok"})
    payload = status.as_dict()
    assert payload["status"] == "blocked"
    assert payload["checks"]["dashboard"] == "missing"


def test_deployment_readiness_passes_with_required_capabilities(tmp_path: Path):
    validator = DeploymentReadinessValidator(project_root=tmp_path)
    report = validator.validate(
        capabilities={
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
        },
        env={"CLAIRE_ALLOWED_HOSTS": "localhost,127.0.0.1"},
        cors_origins=["https://example.com"],
        port=443,
        scan_secrets=True,
    )
    assert report.ready is True
    assert report.findings == []


def test_deployment_readiness_blocks_missing_capabilities(tmp_path: Path):
    validator = DeploymentReadinessValidator(project_root=tmp_path)
    report = validator.validate(
        capabilities={"governed_external_search"},
        env={},
        cors_origins=["https://example.com"],
        port=443,
        scan_secrets=False,
    )
    assert report.ready is False
    assert any(item.code == "missing_capability" for item in report.findings)


def test_manifest_shape_is_valid():
    manifest_path = Path("manifests/v17_48_deployment_production_hardening.json")
    if not manifest_path.exists():
        pytest.skip("manifest is installed by root installer")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    findings = RuntimeHardeningValidator().validate_manifest_shape(manifest)
    assert findings == []
"""


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def project_root() -> Path:
    return Path.cwd().resolve()


def backup_existing(root: Path, rel_path: str, backup_root: Path) -> str | None:
    target = root / rel_path
    if not target.exists():
        return None
    backup_path = backup_root / rel_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        shutil.copy2(target, backup_path)
    else:
        shutil.copytree(target, backup_path, dirs_exist_ok=True)
    return str(backup_path.relative_to(root))


def write_file(root: Path, rel_path: str, text: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\\n")


def install() -> int:
    root = project_root()
    if not (root / "src").exists():
        print("ERROR: Run this installer from the Claire project root. Missing ./src", file=sys.stderr)
        return 2

    stamp = now_stamp()
    backup_root = root / "backups" / f"{BUILD_ID.replace('.', '_')}_{stamp}"
    rollback_entries: List[dict] = []

    print(f"Installing Claire {BUILD_ID} — {BUILD_NAME}")
    print(f"Project root: {root}")

    for rel_path, text in FILES.items():
        backup = backup_existing(root, rel_path, backup_root)
        write_file(root, rel_path, text)
        rollback_entries.append({"path": rel_path, "backup": backup, "action": "replace" if backup else "create"})
        print(f"  wrote {rel_path}")

    rollback_manifest = {
        "build_id": BUILD_ID,
        "build_name": BUILD_NAME,
        "installed_at": stamp,
        "installer": INSTALLER_NAME,
        "project_root": str(root),
        "entries": rollback_entries,
        "rollback_note": "Restore each backup path over its matching project path. Created files with backup=null can be removed if rolling back.",
    }
    rollback_path = root / "manifests" / "rollback" / f"rollback_{BUILD_ID.replace('.', '_')}_{stamp}.json"
    rollback_path.parent.mkdir(parents=True, exist_ok=True)
    rollback_path.write_text(json.dumps(rollback_manifest, indent=2), encoding="utf-8")
    print(f"  wrote {rollback_path.relative_to(root)}")
    print()
    print("Install complete.")
    print("Recommended verification:")
    print("  python -m pytest tests/test_v17_48_deployment_production_hardening.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(install())
