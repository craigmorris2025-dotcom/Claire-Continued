from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter


router = APIRouter(tags=["Claire Plan Reconciliation"])

VERSION = "v19.89.8-R"
BUILD_NAME = "Plan Reconciliation + Missing-System Audit"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _report_path() -> Path:
    return _project_root() / "docs" / "audits" / "v19_89_8_R_plan_reconciliation_missing_system_audit.json"


def _safe_read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": str(exc), "path": str(path)}
    return fallback


@router.get("/system/plan-reconciliation")
def plan_reconciliation() -> Dict[str, Any]:
    return _safe_read_json(_report_path(), {
        "surface": "plan_reconciliation_missing_system_audit",
        "version": VERSION,
        "available": False,
        "reason": "Audit report has not been generated yet. Re-run v19.89.8-R installer.",
        "checked_at": _utc_now(),
    })


@router.get("/system/plan-reconciliation/summary")
def plan_reconciliation_summary() -> Dict[str, Any]:
    report = plan_reconciliation()
    return {
        "surface": report.get("surface"),
        "version": report.get("version"),
        "build": report.get("build"),
        "backend_owns_truth": report.get("backend_owns_truth"),
        "cockpit_presentation_only": report.get("cockpit_presentation_only"),
        "convergence_over_expansion": report.get("convergence_over_expansion"),
        "audited_at": report.get("audited_at"),
        "source_file_count": report.get("source_file_count"),
        "status_counts": report.get("status_counts"),
        "route_count": (report.get("route_audit") or {}).get("route_count"),
        "duplicate_route_count": (report.get("route_audit") or {}).get("duplicate_route_count"),
        "missing_critical_routes": (report.get("route_audit") or {}).get("missing_critical_routes"),
        "priority_next_actions": report.get("priority_next_actions"),
        "decision": report.get("decision"),
        "checked_at": _utc_now(),
    }


@router.get("/system/plan-reconciliation/missing")
def plan_reconciliation_missing() -> Dict[str, Any]:
    report = plan_reconciliation()
    missing = []
    for phase in report.get("phase_results", []):
        for item in phase.get("items", []):
            if item.get("status") in {"missing", "must_rebuild", "broken_or_regressed"}:
                missing.append({"phase": phase.get("phase"), **item})
    return {"surface": "plan_reconciliation_missing", "version": VERSION, "count": len(missing), "items": missing, "checked_at": _utc_now()}


@router.get("/system/plan-reconciliation/partial")
def plan_reconciliation_partial() -> Dict[str, Any]:
    report = plan_reconciliation()
    partial = []
    for phase in report.get("phase_results", []):
        for item in phase.get("items", []):
            if item.get("status") == "partial":
                partial.append({"phase": phase.get("phase"), **item})
    return {"surface": "plan_reconciliation_partial", "version": VERSION, "count": len(partial), "items": partial, "checked_at": _utc_now()}


@router.get("/system/plan-reconciliation/registration-proof")
def plan_reconciliation_registration_proof() -> Dict[str, Any]:
    return {
        "surface": "plan_reconciliation_registration_proof",
        "version": VERSION,
        "registered": True,
        "routes": [
            "/system/plan-reconciliation",
            "/system/plan-reconciliation/summary",
            "/system/plan-reconciliation/missing",
            "/system/plan-reconciliation/partial",
            "/system/plan-reconciliation/registration-proof",
        ],
        "checked_at": _utc_now(),
    }
