from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLATEAU_LOCK_VERSION = "v19.89.8-S1265-S1292-full-project-plateau-lock"


KEY_ROUTES = [
    "/",
    "/health",
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/dashboard/actions/registry",
    "/dashboard/actions/summary",
    "/dashboard/actions/preview/plan_search",
    "/dashboard/operator-console/contract",
    "/dashboard/operator-console/summary",
    "/dashboard/operator-console/actions",
    "/dashboard/operator-console/preview/plan_search",
    "/dashboard/operator-action/result/plan_search",
    "/dashboard/actions/result/plan_search",
    "/dashboard/visibility/summary",
    "/dashboard/status/harmonized",
    "/api/dashboard/visibility/summary",
    "/api/dashboard/status/harmonized",
    "/api/governed/live-probe/status",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocked_authority() -> dict[str, str]:
    return {
        "live_web_execution": "blocked",
        "search_provider_execution": "blocked",
        "browser_execution": "blocked",
        "network_requests": "blocked",
        "body_reads": "blocked",
        "autonomous_crawling": "blocked",
        "automatic_updates": "blocked",
        "runtime_mutation": "blocked",
        "runtime_truth_mutation": "blocked",
        "package_download_install": "blocked",
        "command_execution": "blocked",
    }


def build_plateau_completion_lock(root: Path | None = None, *, write_audit_report: bool = True) -> dict[str, Any]:
    root = root or Path.cwd()

    from claire.audit.system_plateau_audit import run_audit

    audit = run_audit(root, write_report=write_audit_report)
    summary = audit.get("summary", {})
    issues = audit.get("issues", [])
    route_checks = audit.get("routes", {}).get("expected_get", {})
    python_syntax = audit.get("python_syntax", {})
    environment = audit.get("environment", {})
    static_risk = audit.get("static_risk_scan", {})

    key_route_status = {
        route: route_checks.get(route, {}).get("status_code")
        for route in KEY_ROUTES
    }
    missing_or_bad_routes = {
        route: status
        for route, status in key_route_status.items()
        if status != 200
    }

    blocker_count = int(summary.get("blocker_count", 0) or 0)
    warning_count = int(summary.get("warning_count", 0) or 0)
    syntax_failures = python_syntax.get("failures", [])
    dangerous_env = environment.get("dangerous_enabled", {})
    network_env = environment.get("network_probe_enabled", {})
    unreviewed_risks = int(static_risk.get("unreviewed_finding_count", 0) or 0)

    plateau_ready = (
        blocker_count == 0
        and warning_count == 0
        and not syntax_failures
        and not dangerous_env
        and not network_env
        and not missing_or_bad_routes
        and unreviewed_risks == 0
    )

    return {
        "ok": plateau_ready,
        "status": "locked" if plateau_ready else "blocked",
        "version": PLATEAU_LOCK_VERSION,
        "generated_at": _utc_now(),
        "plateau_ready": plateau_ready,
        "forward_motion_allowed": plateau_ready,
        "audit_version": audit.get("audit_version"),
        "audit_generated_at": audit.get("generated_at"),
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "issue_count": len(issues),
        "issues": issues,
        "python_syntax": {
            "checked_files": python_syntax.get("checked_files"),
            "failure_count": len(syntax_failures),
        },
        "environment": {
            "dangerous_enabled": dangerous_env,
            "network_probe_enabled": network_env,
        },
        "static_risk_scan": {
            "finding_count": static_risk.get("finding_count"),
            "reviewed_finding_count": static_risk.get("reviewed_finding_count"),
            "unreviewed_finding_count": static_risk.get("unreviewed_finding_count"),
            "all_findings_reviewed": static_risk.get("all_findings_reviewed"),
            "review_status": static_risk.get("review_status"),
        },
        "key_route_status": key_route_status,
        "missing_or_bad_routes": missing_or_bad_routes,
        "route_count": audit.get("routes", {}).get("route_count"),
        "active_tree_policy": audit.get("paths", {}).get("active_tree_policy", {}),
        "frontend_assets": audit.get("paths", {}).get("frontend_assets", {}),
        "blocked_authority": blocked_authority(),
        "next_phase": {
            "recommended": "S1293-S1320 dashboard operations active binding and result verification",
            "reason": "The project plateau is clean; next work should return to active cockpit operation controls and visual result binding.",
        },
        "message": "Full project plateau is locked only when audit blockers, warnings, syntax failures, unsafe env toggles, unreviewed risks, and key-route gaps are all zero.",
    }


def include_plateau_completion_lock_routes(app: Any) -> None:
    try:
        from fastapi import APIRouter

        router = APIRouter(tags=["Plateau Completion Lock"])

        @router.get("/api/audit/plateau-lock")
        def api_audit_plateau_lock() -> dict[str, Any]:
            return build_plateau_completion_lock(write_audit_report=False)

        @router.get("/dashboard/audit/plateau-lock")
        def dashboard_audit_plateau_lock() -> dict[str, Any]:
            return build_plateau_completion_lock(write_audit_report=False)

        app.include_router(router)
    except Exception:
        return None
