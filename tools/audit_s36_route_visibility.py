from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_PATH = ROOT / "runtime" / "governed_live_probe" / "s36_route_visibility_audit.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    try:
        from claire.app import create_app
    except Exception as exc:
        print(f"[S36-ROUTE-AUDIT][FAILED] could not import create_app: {exc}")
        return 1

    try:
        app = create_app()
    except Exception as exc:
        print(f"[S36-ROUTE-AUDIT][FAILED] create_app failed: {exc}")
        return 1

    routes = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])
        name = getattr(route, "name", "")
        if "governed/live-probe" in path:
            routes.append({
                "path": path,
                "methods": methods,
                "name": name,
            })

    expected_status = "/api/governed/live-probe/status"
    expected_head = "/api/governed/live-probe/head"

    found_status = any(item["path"] == expected_status and "GET" in item["methods"] for item in routes)
    found_head = any(item["path"] == expected_head and "POST" in item["methods"] for item in routes)

    report = {
        "version": "v19.89.8-S36R6-R8.1-bootstrap-fix",
        "audited_at": _utc_now(),
        "bootstrap_root": str(ROOT),
        "create_app_imported": True,
        "app_created": True,
        "expected_status_route": expected_status,
        "expected_head_route": expected_head,
        "found_status_route": found_status,
        "found_head_route": found_head,
        "matched_routes": routes,
        "body_reads_allowed": False,
        "browser_execution_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "automatic_updates_allowed": False,
        "continuous_crawling_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if not found_status or not found_head:
        print("[S36-ROUTE-AUDIT][FAILED] governed live probe routes not fully visible")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print("[S36-ROUTE-AUDIT] PASS")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
