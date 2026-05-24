from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNTIME_DIR = ROOT / "runtime" / "governed_system_inventory"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_system_inventory"
INVENTORY_REPORT = RUNTIME_DIR / "s37_system_self_inventory.json"
QUARANTINE_REPORT = QUARANTINE_DIR / "s37_system_self_inventory_quarantine.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_parse(path: Path) -> dict:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return {"path": str(path.relative_to(ROOT)), "parse_ok": True, "error": None}
    except Exception as exc:
        return {"path": str(path.relative_to(ROOT)), "parse_ok": False, "error": str(exc)}


def _collect_python_parse_status(limit: int = 500) -> list[dict]:
    results = []
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT)
        if any(part in {".git", "__pycache__", ".venv", "venv", "backups"} for part in rel.parts):
            continue
        results.append(_safe_parse(path))
        if len(results) >= limit:
            break
    return results


def _collect_routes() -> list[dict]:
    routes = []
    try:
        from runtime_core.app import create_app
        app = create_app()
        for route in getattr(app, "routes", []):
            routes.append({
                "path": getattr(route, "path", ""),
                "methods": sorted(getattr(route, "methods", []) or []),
                "name": getattr(route, "name", ""),
            })
    except Exception as exc:
        routes.append({"error": str(exc), "path": None, "methods": [], "name": "route_collection_failed"})
    return routes


def _collect_expected_surfaces() -> dict:
    expected = {
        "app": "claire/app.py",
        "dashboard_payload_bridge": "claire/api/dashboard_payload_bridge.py",
        "governed_live_probe_router": "claire/api/routes/governed_live_probe.py",
        "first_live_preflight": "tools/s36_first_live_preflight.py",
        "first_live_runner": "tools/run_s36_single_head_probe.py",
        "first_live_plateau": "tools/run_s36_first_live_operator_plateau.py",
        "probe_quarantine_verifier": "tools/verify_s36_probe_quarantine.py",
        "first_probe_report_compiler": "tools/compile_s36_first_probe_report.py",
    }
    return {name: {"path": rel, "exists": (ROOT / rel).exists()} for name, rel in expected.items()}


def _classify_local_gaps(parse_status: list[dict], surfaces: dict, routes: list[dict]) -> list[dict]:
    gaps = []
    for item in parse_status:
        if not item["parse_ok"]:
            gaps.append({
                "category": "broken_python_syntax",
                "severity": "high",
                "summary": "Python syntax/parse failure in " + item["path"],
                "path": item["path"],
                "web_research_needed": False,
                "reason": "Local syntax issue should be repaired from local source context first.",
            })

    for name, item in surfaces.items():
        if not item["exists"]:
            gaps.append({
                "category": "missing_expected_surface",
                "severity": "medium",
                "summary": "Expected surface missing: " + name,
                "path": item["path"],
                "web_research_needed": False,
                "reason": "Missing local project surface should be resolved from Claire architecture state first.",
            })

    route_paths = {r.get("path") for r in routes}
    for expected_route in ["/api/governed/live-probe/status", "/api/governed/live-probe/head"]:
        if expected_route not in route_paths:
            gaps.append({
                "category": "missing_expected_route",
                "severity": "high",
                "summary": "Expected governed route not visible: " + expected_route,
                "path": expected_route,
                "web_research_needed": False,
                "reason": "Route registration issue is local architecture, not web research.",
            })
    return gaps


def main() -> int:
    parse_status = _collect_python_parse_status()
    surfaces = _collect_expected_surfaces()
    routes = _collect_routes()
    gaps = _classify_local_gaps(parse_status, surfaces, routes)

    report = {
        "version": "v19.89.8-S37R1-R4-self-inventory-need-classifier",
        "generated_at": _utc_now(),
        "scope": "local_self_inventory_only",
        "live_web_execution": False,
        "automatic_updates_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "project_root": str(ROOT),
        "summary": {
            "python_files_scanned": len(parse_status),
            "parse_failures": len([x for x in parse_status if not x["parse_ok"]]),
            "expected_surfaces": len(surfaces),
            "missing_expected_surfaces": len([x for x in surfaces.values() if not x["exists"]]),
            "routes_collected": len(routes),
            "local_gaps": len(gaps),
        },
        "expected_surfaces": surfaces,
        "routes": routes,
        "python_parse_status": parse_status,
        "local_gaps": gaps,
    }

    INVENTORY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    QUARANTINE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    QUARANTINE_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("[S37-INVENTORY] PASS")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
