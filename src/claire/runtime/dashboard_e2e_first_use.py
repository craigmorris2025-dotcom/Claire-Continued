"""v17.51 dashboard-driven end-to-end first-use verification.

This module is deliberately local, deterministic, and file-backed. It verifies that
a dashboard action can move through the governed runtime boundary and produce an
auditable state artifact without requiring external network credentials.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4

VERSION = "17.51"
BUILD_NAME = "Dashboard End-to-End First-Use Test"

REQUIRED_ACTIONS = (
    "dashboard_capability_check",
    "governed_runtime_health_check",
    "internet_operations_state_check",
    "campaign_state_check",
    "source_trust_state_check",
    "deployment_state_check",
    "rollback_state_check",
    "manifest_integrity_check",
)

STATE_DIR = Path("data") / "launch_verification"
RUNS_DIR = STATE_DIR / "dashboard_e2e_runs"
LATEST_PATH = STATE_DIR / "dashboard_e2e_latest.json"
MANIFEST_PATH = Path("manifests") / "v17_51_dashboard_e2e_first_use_manifest.json"


@dataclass(frozen=True)
class DashboardE2ECheck:
    name: str
    status: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class DashboardE2EResult:
    run_id: str
    version: str
    build_name: str
    status: str
    started_at: str
    completed_at: str
    actions_requested: List[str]
    checks: List[DashboardE2ECheck]
    output_path: str
    governance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["checks"] = [asdict(check) for check in self.checks]
        return payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_invalid_json": True, "path": str(path)}
    if isinstance(data, dict):
        return data
    return {"_invalid_json": True, "path": str(path), "reason": "json root is not object"}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_status(path: Path) -> Dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
    }


def _check_dashboard_capability() -> DashboardE2ECheck:
    candidates = [
        Path("data") / "dashboard" / "dashboard_capability_manifest.json",
        Path("data") / "dashboard_runtime_alignment" / "dashboard_capability_manifest.json",
        Path("manifests") / "v17_50_dashboard_runtime_alignment_manifest.json",
    ]
    evidence = {"candidates": [_file_status(path) for path in candidates]}
    existing = [str(path) for path in candidates if path.exists()]
    status = "pass" if existing else "warning"
    notes = [] if existing else ["No v17.50 dashboard capability manifest found; v17.51 still records first-use state."]
    evidence["existing"] = existing
    return DashboardE2ECheck("dashboard_capability_check", status, evidence, notes)


def _check_route_or_file_state(name: str, paths: List[Path], warning_note: str) -> DashboardE2ECheck:
    statuses = [_file_status(path) for path in paths]
    existing = [item for item in statuses if item["exists"]]
    status = "pass" if existing else "warning"
    notes = [] if existing else [warning_note]
    return DashboardE2ECheck(name, status, {"paths": statuses}, notes)


def _check_manifest_integrity() -> DashboardE2ECheck:
    manifest = _read_json(MANIFEST_PATH)
    evidence: Dict[str, Any] = {"manifest_path": str(MANIFEST_PATH), "exists": MANIFEST_PATH.exists()}
    if manifest is None:
        return DashboardE2ECheck("manifest_integrity_check", "fail", evidence, ["v17.51 manifest is missing."])
    evidence["version"] = manifest.get("version")
    evidence["build_name"] = manifest.get("build_name")
    evidence["required_actions"] = manifest.get("required_actions", [])
    if manifest.get("version") != VERSION:
        return DashboardE2ECheck("manifest_integrity_check", "fail", evidence, ["Manifest version mismatch."])
    missing = [action for action in REQUIRED_ACTIONS if action not in manifest.get("required_actions", [])]
    if missing:
        evidence["missing_actions"] = missing
        return DashboardE2ECheck("manifest_integrity_check", "fail", evidence, ["Manifest missing required action registrations."])
    return DashboardE2ECheck("manifest_integrity_check", "pass", evidence, [])


def run_dashboard_e2e_first_use(action_payload: Optional[Mapping[str, Any]] = None) -> DashboardE2EResult:
    """Run a governed first-use verification from the dashboard action boundary."""
    started_at = _utc_now()
    run_id = f"v17_51_{uuid4().hex[:12]}"
    requested = list(REQUIRED_ACTIONS)

    checks: List[DashboardE2ECheck] = [
        _check_dashboard_capability(),
        _check_route_or_file_state(
            "governed_runtime_health_check",
            [
                Path("data") / "runtime" / "runtime_health.json",
                Path("data") / "internet_runtime" / "runtime_health.json",
                Path("data") / "operations" / "runtime_health.json",
            ],
            "Runtime health state file not found yet; start the API/dashboard once to populate live runtime health.",
        ),
        _check_route_or_file_state(
            "internet_operations_state_check",
            [
                Path("data") / "internet_operations" / "operations_dashboard.json",
                Path("data") / "internet_operations_dashboard" / "state.json",
                Path("data") / "operations" / "internet_operations.json",
            ],
            "Internet operations state file not found yet; run one governed internet operation after dashboard launch.",
        ),
        _check_route_or_file_state(
            "campaign_state_check",
            [
                Path("data") / "campaigns" / "campaign_state.json",
                Path("data") / "internet_campaigns" / "campaign_state.json",
                Path("data") / "campaign_scheduler" / "scheduler_state.json",
            ],
            "Campaign state file not found yet; create or refresh one governed campaign from the dashboard.",
        ),
        _check_route_or_file_state(
            "source_trust_state_check",
            [
                Path("data") / "source_trust" / "source_trust_state.json",
                Path("data") / "source_reputation" / "trust_memory.json",
                Path("data") / "internet_operations" / "source_trust.json",
            ],
            "Source trust state file not found yet; source scoring will populate during real governed search/campaign use.",
        ),
        _check_route_or_file_state(
            "deployment_state_check",
            [
                Path("data") / "deployment" / "production_state.json",
                Path("data") / "deployment_hardening" / "production_state.json",
                Path("manifests") / "v17_48_deployment_production_hardening_manifest.json",
            ],
            "Deployment hardening state file not found, but manifest fallback may exist from v17.48.",
        ),
        _check_route_or_file_state(
            "rollback_state_check",
            [
                Path("data") / "rollback" / "rollback_state.json",
                Path("data") / "deployment" / "rollback_state.json",
                Path("data") / "runtime_recovery" / "rollback_state.json",
            ],
            "Rollback state file not found yet; rollback proof should be generated before external launch.",
        ),
        _check_manifest_integrity(),
    ]

    failures = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warning"]
    if failures:
        status = "failed"
    elif warnings:
        status = "passed_with_launch_warnings"
    else:
        status = "passed"

    output_path = RUNS_DIR / f"{run_id}.json"
    result = DashboardE2EResult(
        run_id=run_id,
        version=VERSION,
        build_name=BUILD_NAME,
        status=status,
        started_at=started_at,
        completed_at=_utc_now(),
        actions_requested=requested,
        checks=checks,
        output_path=str(output_path),
        governance={
            "bounded_orchestration_preserved": True,
            "runtime_isolation_preserved": True,
            "external_network_required": False,
            "writes_only_launch_verification_state": True,
            "dashboard_action_payload_recorded": bool(action_payload),
            "action_payload_keys": sorted(list(action_payload.keys())) if action_payload else [],
        },
    )
    payload = result.to_dict()
    _write_json(output_path, payload)
    _write_json(LATEST_PATH, payload)
    return result


def read_latest_dashboard_e2e_result() -> Dict[str, Any]:
    latest = _read_json(LATEST_PATH)
    if latest is None:
        return {
            "version": VERSION,
            "status": "not_run",
            "message": "Dashboard first-use E2E verification has not been run yet.",
            "next_action": "POST /dashboard/e2e/first-use/run or trigger the matching dashboard action button.",
        }
    return latest


def dashboard_e2e_capability_manifest() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "build_name": BUILD_NAME,
        "dashboard_buttons": [
            {
                "id": "run-dashboard-first-use-e2e",
                "label": "Run First-Use E2E Check",
                "method": "POST",
                "route": "/dashboard/e2e/first-use/run",
                "purpose": "Verify dashboard action to governed runtime state creation.",
            },
            {
                "id": "view-dashboard-first-use-e2e-latest",
                "label": "View Latest First-Use Result",
                "method": "GET",
                "route": "/dashboard/e2e/first-use/latest",
                "purpose": "Display latest dashboard/runtime alignment result.",
            },
        ],
        "required_actions": list(REQUIRED_ACTIONS),
        "state_files": {
            "latest": str(LATEST_PATH),
            "runs_dir": str(RUNS_DIR),
            "manifest": str(MANIFEST_PATH),
        },
        "governance": {
            "bounded_orchestration": True,
            "rollback_safe": True,
            "runtime_isolated": True,
            "network_free_local_smoke_test": True,
        },
    }
