from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class ValidationCheck:
    check_id: str
    name: str
    status: str
    severity: str
    details: str
    remediation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def pass_check(check_id: str, name: str, details: str) -> ValidationCheck:
    return ValidationCheck(
        check_id=check_id,
        name=name,
        status="pass",
        severity="info",
        details=details,
        remediation="",
    )


def warn_check(check_id: str, name: str, details: str, remediation: str = "") -> ValidationCheck:
    return ValidationCheck(
        check_id=check_id,
        name=name,
        status="warning",
        severity="medium",
        details=details,
        remediation=remediation,
    )


def fail_check(
    check_id: str,
    name: str,
    details: str,
    remediation: str = "",
    severity: str = "high",
) -> ValidationCheck:
    return ValidationCheck(
        check_id=check_id,
        name=name,
        status="fail",
        severity=severity,
        details=details,
        remediation=remediation,
    )


def compute_score(checks: List[ValidationCheck]) -> int:
    if not checks:
        return 0

    total_weight = 0
    earned = 0

    weights = {
        "critical": 5,
        "high": 4,
        "medium": 2,
        "low": 1,
        "info": 1,
    }

    for check in checks:
        weight = weights.get(check.severity, 1)
        total_weight += weight
        if check.status == "pass":
            earned += weight
        elif check.status == "warning":
            earned += max(0, weight - 1)

    if total_weight <= 0:
        return 0

    return round((earned / total_weight) * 100)


def final_status(checks: List[ValidationCheck]) -> str:
    critical_or_high_failures = [
        check for check in checks
        if check.status == "fail" and check.severity in {"critical", "high"}
    ]
    any_failures = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warning"]

    if critical_or_high_failures:
        return "fail"
    if any_failures:
        return "blocked"
    if warnings:
        return "warning"
    return "pass"
