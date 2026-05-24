from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(tags=["Claire Duplicate Route Fail Test"])

VERSION = "v19.89.8-A2"
BUILD_NAME = "Duplicate Route Fail Test"
CRITICAL_ROUTES = ['/dashboard/payload', '/dashboard/payload/status', '/runtime/continuous/status', '/runtime/continuous/review-queue', '/runs/start', '/universes']
TEMPORARY_GRANDFATHERED = {'/dashboard/payload': ['claire\\api\\routes_enterprise_cockpit_payload.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/dashboard/payload/status': ['claire\\api\\routes_enterprise_cockpit_payload.py', 'claire\\routes\\authored_cockpit_payload_binding_routes.py'], '/runtime/continuous/status': ['claire\\api\\routes_continuous_runtime.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/runtime/continuous/review-queue': ['claire\\api\\routes_continuous_runtime.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/runs/start': ['claire\\api\\routes_enterprise_runs.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/universes': ['claire\\api\\routes_source_universes.py', 'claire\\routes\\authored_cockpit_compat_routes.py']}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def _discover_routes(root: Path):
    active_dirs = [root / "claire", root / "src" / "claire", root / "backend"]
    pattern = re.compile("@(?:router|app)\\.(get|post|put|delete|patch)\\(\\s*[\\\"']([^\\\"']+)[\\\"']")
    routes = {}
    for base in active_dirs:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = _read_text(path)
            for method, route in pattern.findall(text):
                rel = str(path.relative_to(root))
                routes.setdefault(route, []).append({"method": method.upper(), "file": rel})
    return routes

def _evaluate():
    root = _project_root()
    routes = _discover_routes(root)
    duplicates = {route: entries for route, entries in routes.items() if len({entry["file"] for entry in entries}) > 1}
    critical_failures = {}
    grandfathered = {}
    critical_passes = {}
    for route in CRITICAL_ROUTES:
        entries = duplicates.get(route, [])
        if not entries:
            critical_passes[route] = {"status": "pass", "owners": routes.get(route, []), "reason": "No duplicate owner detected."}
            continue
        files = sorted({entry["file"] for entry in entries})
        allowed = sorted(TEMPORARY_GRANDFATHERED.get(route, []))
        if files == allowed:
            grandfathered[route] = {"status": "grandfathered_temporary", "owners": entries, "allowed_files": allowed, "reason": "Known temporary compatibility duplicate."}
        else:
            critical_failures[route] = {"status": "fail", "owners": entries, "allowed_files": allowed, "reason": "Critical route has unapproved duplicate owners."}
    status = "fail" if critical_failures else ("pass_with_grandfathered_duplicates" if grandfathered else "pass")
    report = {
        "surface": "duplicate_route_fail_test",
        "version": VERSION,
        "status": status,
        "critical_route_count": len(CRITICAL_ROUTES),
        "discovered_route_count": len(routes),
        "duplicate_route_count": len(duplicates),
        "critical_failures": critical_failures,
        "grandfathered_temporary_duplicates": grandfathered,
        "critical_passes": critical_passes,
        "safe_to_expand_runtime_authority": status == "pass",
        "reason": "No critical duplicate routes remain." if status == "pass" else ("Critical duplicates remain but are temporarily grandfathered." if status == "pass_with_grandfathered_duplicates" else "Critical duplicate route ownership failure detected."),
        "checked_at": _utc_now(),
    }
    out = root / "data" / "authority" / "duplicate_route_fail_test_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

@router.get("/system/duplicate-route-fail-test")
def duplicate_route_fail_test() -> Dict[str, Any]:
    return _evaluate()

@router.get("/system/duplicate-route-fail-test/report")
def duplicate_route_fail_test_report() -> Dict[str, Any]:
    return _evaluate()

@router.get("/system/duplicate-route-fail-test/summary")
def duplicate_route_fail_test_summary() -> Dict[str, Any]:
    report = _evaluate()
    return {
        "surface": report.get("surface"),
        "version": report.get("version"),
        "status": report.get("status"),
        "critical_route_count": report.get("critical_route_count"),
        "discovered_route_count": report.get("discovered_route_count"),
        "duplicate_route_count": report.get("duplicate_route_count"),
        "critical_failure_count": len(report.get("critical_failures", {})),
        "grandfathered_temporary_count": len(report.get("grandfathered_temporary_duplicates", {})),
        "safe_to_expand_runtime_authority": report.get("safe_to_expand_runtime_authority"),
        "reason": report.get("reason"),
        "checked_at": _utc_now(),
    }

@router.get("/system/duplicate-route-fail-test/critical-failures")
def duplicate_route_fail_test_critical_failures() -> Dict[str, Any]:
    report = _evaluate()
    return {
        "surface": "duplicate_route_critical_failures",
        "version": report.get("version"),
        "count": len(report.get("critical_failures", {})),
        "critical_failures": report.get("critical_failures", {}),
        "checked_at": _utc_now(),
    }

@router.get("/system/duplicate-route-fail-test/grandfathered")
def duplicate_route_fail_test_grandfathered() -> Dict[str, Any]:
    report = _evaluate()
    return {
        "surface": "duplicate_route_grandfathered_temporary",
        "version": report.get("version"),
        "count": len(report.get("grandfathered_temporary_duplicates", {})),
        "grandfathered_temporary_duplicates": report.get("grandfathered_temporary_duplicates", {}),
        "checked_at": _utc_now(),
    }

@router.get("/system/duplicate-route-fail-test/registration-proof")
def duplicate_route_fail_test_registration_proof() -> Dict[str, Any]:
    return {
        "surface": "duplicate_route_fail_test_registration_proof",
        "version": VERSION,
        "registered": True,
        "routes": [
            "/system/duplicate-route-fail-test",
            "/system/duplicate-route-fail-test/report",
            "/system/duplicate-route-fail-test/summary",
            "/system/duplicate-route-fail-test/critical-failures",
            "/system/duplicate-route-fail-test/grandfathered",
            "/system/duplicate-route-fail-test/registration-proof",
        ],
        "checked_at": _utc_now(),
    }
