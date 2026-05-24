"""Claire v17.49 launch release gate."""
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
