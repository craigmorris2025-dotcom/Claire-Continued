from __future__ import annotations

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
