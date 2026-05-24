"""Deterministic production readiness helpers."""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def env_report(env: dict[str, Any] | None = None) -> dict[str, Any]:
    env = env or {}
    required = list(env.get("required_env_vars", [])) if isinstance(env.get("required_env_vars"), list) else []
    missing = [name for name in required if not os.environ.get(str(name))]
    disk = shutil.disk_usage(Path.cwd())
    checks = {
        "python_version": sys.version_info >= (3, 11),
        "working_directory_writable": os.access(Path.cwd(), os.W_OK),
        "disk_space_available": disk.free > 500 * 1024 * 1024,
        "required_env_vars_present": not missing,
    }
    return {
        "schema_version": "claire.production.environment_report.v1",
        "generated_at": now(),
        "status": "valid" if all(checks.values()) else "needs_attention",
        "checks": checks,
        "missing_env_vars": missing,
        "python_version": sys.version.split()[0],
        "free_disk_bytes": disk.free,
    }


def readiness_report(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    environment = env_report(config.get("environment", {}) if isinstance(config.get("environment"), dict) else config)
    blockers = []
    warnings = []
    if environment["status"] != "valid":
        warnings.append("environment_needs_attention")
    if config.get("allow_automatic_updates") is True:
        blockers.append("automatic_updates_must_remain_operator_governed")
    if config.get("allow_runtime_truth_mutation") is True:
        blockers.append("runtime_truth_mutation_requires_explicit_governance")
    checks_passed = sum(1 for passed in environment["checks"].values() if passed)
    checks_failed = sum(1 for passed in environment["checks"].values() if not passed)
    return {
        "schema_version": "claire.production.readiness_report.v1",
        "generated_at": now(),
        "overall_status": "NOGO" if blockers else "CONDITIONAL" if warnings or checks_failed else "GO",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "blockers": blockers,
        "warnings": warnings,
        "environment": environment,
        "manual_review_required": True,
    }


def security_report(system: dict[str, Any] | None = None) -> dict[str, Any]:
    system = system or {}
    checks = {
        "secrets_not_requested": True,
        "body_reads_disabled": system.get("body_reads_allowed") is not True,
        "automatic_updates_disabled": system.get("automatic_updates_enabled") is not True,
        "runtime_mutation_disabled": system.get("runtime_truth_mutation") is not True,
        "auth_reviewed": bool(system.get("auth_configured") or system.get("local_only")),
    }
    failed = [key for key, passed in checks.items() if not passed]
    return {
        "schema_version": "claire.production.security_report.v1",
        "generated_at": now(),
        "level": "PRODUCTION_READY" if not failed else "NEEDS_REMEDIATION",
        "score": round(sum(1 for passed in checks.values() if passed) / len(checks), 4),
        "checks": checks,
        "findings": failed,
    }


def backup_policy(name: str = "claire-default", schedule: str = "manual", retention: int = 14, targets: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "claire.production.backup_policy.v1",
        "name": name,
        "schedule_cron": schedule,
        "retention_days": int(retention),
        "targets": targets or ["data", "reports", "runtime"],
        "encryption_required": True,
        "created_at": now(),
        "execution_mode": "policy_only_no_backup_started",
    }


def recovery_drill(name: str = "manual-recovery-drill", scenario: str = "restore latest governed artifacts") -> dict[str, Any]:
    start = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema_version": "claire.production.recovery_drill.v1",
        "name": name,
        "scenario": scenario,
        "start_time": start.isoformat(),
        "next_review_after": (start + timedelta(days=30)).isoformat(),
        "steps": ["verify backups exist", "restore to isolated workspace", "run compile checks", "run focused regression tests"],
        "success_criteria": ["artifacts restored", "tests pass", "no governance locks weakened"],
        "execution_mode": "plan_only",
    }
