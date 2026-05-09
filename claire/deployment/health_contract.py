from __future__ import annotations

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
