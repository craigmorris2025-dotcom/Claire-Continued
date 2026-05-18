from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "v19.89.8-A2"
CRITICAL_ROUTES = ['/dashboard/payload', '/dashboard/payload/status', '/runtime/continuous/status', '/runtime/continuous/review-queue', '/runs/start', '/universes']
TEMPORARY_GRANDFATHERED = {'/dashboard/payload': ['claire\\api\\routes_enterprise_cockpit_payload.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/dashboard/payload/status': ['claire\\api\\routes_enterprise_cockpit_payload.py', 'claire\\routes\\authored_cockpit_payload_binding_routes.py'], '/runtime/continuous/status': ['claire\\api\\routes_continuous_runtime.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/runtime/continuous/review-queue': ['claire\\api\\routes_continuous_runtime.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/runs/start': ['claire\\api\\routes_enterprise_runs.py', 'claire\\routes\\authored_cockpit_compat_routes.py'], '/universes': ['claire\\api\\routes_source_universes.py', 'claire\\routes\\authored_cockpit_compat_routes.py']}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def discover_routes(root: Path):
    active_dirs = [root / "claire", root / "src" / "claire", root / "backend"]
    pattern = re.compile("@(?:router|app)\\.(get|post|put|delete|patch)\\(\\s*[\\\"']([^\\\"']+)[\\\"']")
    routes = {}
    for base in active_dirs:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = read_text(path)
            for method, route in pattern.findall(text):
                rel = str(path.relative_to(root))
                routes.setdefault(route, []).append({"method": method.upper(), "file": rel})
    return routes

def evaluate(root: Path):
    routes = discover_routes(root)
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
    return {
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
        "checked_at": utc_now(),
    }

def main() -> int:
    root = Path.cwd()
    report = evaluate(root)
    out = root / "data" / "authority" / "duplicate_route_fail_test_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if report.get("status") == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
