#!/usr/bin/env python3
"""
Claire v19.84.7 Cockpit Binding Readiness Gate

Purpose:
- Read the canonical owner registry and route consolidation reports.
- Decide whether Claire is allowed to proceed into cockpit binding work.
- Prevent dashboard/cockpit rewrites while critical route authority is unresolved.
- Remain read-only.

This build does not change routes or frontend files.
"""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "runtime_authority" / "canonical_route_owner_registry.json"
FAIL_REPORT_PATH = ROOT / "audits" / "v19_84_5_duplicate_route_fail_test" / "duplicate_route_fail_test_report.json"
PLAN_PATH = ROOT / "audits" / "v19_84_6_critical_route_consolidation_plan" / "critical_route_consolidation_plan.json"
OUT_DIR = ROOT / "audits" / "v19_84_7_cockpit_binding_readiness_gate"
OUT_JSON = OUT_DIR / "cockpit_binding_readiness_gate.json"
OUT_MD = OUT_DIR / "cockpit_binding_readiness_gate.md"

REQUIRED_PAYLOAD_FIELDS = [
    "backend_owns_truth",
    "cockpit_owns_presentation_only",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def ensure_import_path() -> None:
    for candidate in [ROOT, ROOT / "src"]:
        text = str(candidate)
        if candidate.exists() and text not in sys.path:
            sys.path.insert(0, text)


def load_app() -> Any:
    ensure_import_path()
    errors: List[str] = []
    try:
        module = importlib.import_module("claire.app")
        if hasattr(module, "create_app"):
            return module.create_app()
        if hasattr(module, "app"):
            return module.app
    except Exception as exc:
        errors.append(f"claire.app failed: {exc!r}")

    try:
        module = importlib.import_module("main")
        if hasattr(module, "app"):
            return module.app
        if hasattr(module, "create_app"):
            return module.create_app()
    except Exception as exc:
        errors.append(f"main failed: {exc!r}")

    raise RuntimeError("Could not load Claire app: " + " | ".join(errors))


def collect_route_paths(app: Any) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {}
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not path or not methods:
            continue
        clean_methods = sorted(str(m) for m in methods if str(m) not in {"HEAD", "OPTIONS"})
        results.setdefault(path, [])
        for method in clean_methods:
            if method not in results[path]:
                results[path].append(method)
    return results


def mounted_route_status(registry: Dict[str, Any]) -> Dict[str, Any]:
    try:
        app = load_app()
        path_methods = collect_route_paths(app)
    except Exception as exc:
        return {
            "status": "failed",
            "error": repr(exc),
            "routes": {},
        }

    route_status: Dict[str, Any] = {}
    for route, spec in registry.get("routes", {}).items():
        expected_methods = set(spec.get("methods", ["GET"]))
        mounted_methods = set(path_methods.get(route, []))
        missing_methods = sorted(expected_methods - mounted_methods)
        route_status[route] = {
            "expected_methods": sorted(expected_methods),
            "mounted_methods": sorted(mounted_methods),
            "missing_methods": missing_methods,
            "mounted": not missing_methods,
        }

    return {
        "status": "ok",
        "routes": route_status,
    }


def evaluate_readiness(
    registry: Dict[str, Any],
    fail_report: Dict[str, Any],
    consolidation_plan: Dict[str, Any],
    live_status: Dict[str, Any],
) -> Dict[str, Any]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    if not registry:
        blockers.append({
            "area": "registry",
            "reason": "missing_canonical_route_owner_registry",
            "required_action": "Run v19.84.4 before cockpit binding work.",
        })

    if registry.get("backend_owns_truth") is not True:
        blockers.append({
            "area": "authority",
            "reason": "backend_owns_truth_not_locked",
            "required_action": "Restore backend truth ownership in canonical registry.",
        })

    if registry.get("cockpit_owns_presentation_only") is not True:
        blockers.append({
            "area": "authority",
            "reason": "cockpit_presentation_boundary_not_locked",
            "required_action": "Restore cockpit presentation-only boundary.",
        })

    evaluation = fail_report.get("evaluation", {}) if isinstance(fail_report, dict) else {}
    fail_count = int(evaluation.get("failure_count", 0) or 0)
    failures = evaluation.get("failures", []) or []
    if fail_count > 0:
        blockers.append({
            "area": "route_authority",
            "reason": "critical_route_failures_present",
            "failure_count": fail_count,
            "required_action": "Resolve v19.84.5 critical duplicate/missing route failures before cockpit binding.",
            "failures": failures,
        })

    if consolidation_plan.get("status") == "consolidation_required":
        blockers.append({
            "area": "consolidation",
            "reason": "v19_84_6_consolidation_required",
            "required_action": consolidation_plan.get("recommendation", "Complete route consolidation before proceeding."),
        })

    if live_status.get("status") != "ok":
        blockers.append({
            "area": "live_app",
            "reason": "could_not_verify_live_route_mounts",
            "required_action": "Fix app import/boot before cockpit binding.",
            "error": live_status.get("error"),
        })
    else:
        for route, state in live_status.get("routes", {}).items():
            if not state.get("mounted"):
                blockers.append({
                    "area": "live_route_mount",
                    "route": route,
                    "reason": "critical_route_not_mounted_for_expected_methods",
                    "missing_methods": state.get("missing_methods", []),
                    "required_action": "Restore route or update canonical registry only if intentionally superseded.",
                })

    if not fail_report:
        warnings.append({
            "area": "route_fail_test",
            "reason": "missing_v19_84_5_report",
            "recommended_action": "Run python tools/duplicate_route_fail_test.py before cockpit binding.",
        })

    if not consolidation_plan:
        warnings.append({
            "area": "consolidation_plan",
            "reason": "missing_v19_84_6_plan",
            "recommended_action": "Run python tools/critical_route_consolidation_plan.py before cockpit binding.",
        })

    ready = not blockers

    return {
        "ready_for_cockpit_binding": ready,
        "status": "ready" if ready else "blocked",
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "allowed_next_build": "v19.84.8 Cockpit Canonical Fetch Map" if ready else "v19.84.8 Critical Route Resolution",
    }


def build_gate() -> Dict[str, Any]:
    registry = load_json(REGISTRY_PATH)
    fail_report = load_json(FAIL_REPORT_PATH)
    consolidation_plan = load_json(PLAN_PATH)
    live_status = mounted_route_status(registry)

    readiness = evaluate_readiness(registry, fail_report, consolidation_plan, live_status)

    return {
        "version": "v19.84.7",
        "build": "Cockpit Binding Readiness Gate",
        "generated_at": utc_now(),
        "read_only": True,
        "backend_owns_truth": registry.get("backend_owns_truth") is True,
        "cockpit_owns_presentation_only": registry.get("cockpit_owns_presentation_only") is True,
        "inputs": {
            "registry": str(REGISTRY_PATH.relative_to(ROOT)),
            "registry_present": REGISTRY_PATH.exists(),
            "duplicate_route_fail_report": str(FAIL_REPORT_PATH.relative_to(ROOT)),
            "duplicate_route_fail_report_present": FAIL_REPORT_PATH.exists(),
            "consolidation_plan": str(PLAN_PATH.relative_to(ROOT)),
            "consolidation_plan_present": PLAN_PATH.exists(),
        },
        "live_route_status": live_status,
        "readiness": readiness,
    }


def write_markdown(gate: Dict[str, Any]) -> str:
    r = gate["readiness"]
    lines: List[str] = []
    lines.append("# Claire v19.84.7 Cockpit Binding Readiness Gate")
    lines.append("")
    lines.append(f"- Generated: `{gate['generated_at']}`")
    lines.append(f"- Status: `{r['status']}`")
    lines.append(f"- Ready for cockpit binding: `{r['ready_for_cockpit_binding']}`")
    lines.append(f"- Backend owns truth: `{gate['backend_owns_truth']}`")
    lines.append(f"- Cockpit owns presentation only: `{gate['cockpit_owns_presentation_only']}`")
    lines.append(f"- Allowed next build: `{r['allowed_next_build']}`")
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if r["blockers"]:
        for blocker in r["blockers"]:
            lines.append(f"- `{blocker.get('area')}` — `{blocker.get('reason')}`")
            if blocker.get("route"):
                lines.append(f"  - Route: `{blocker.get('route')}`")
            if blocker.get("required_action"):
                lines.append(f"  - Required action: {blocker.get('required_action')}")
    else:
        lines.append("No blockers.")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if r["warnings"]:
        for warning in r["warnings"]:
            lines.append(f"- `{warning.get('area')}` — `{warning.get('reason')}`")
            if warning.get("recommended_action"):
                lines.append(f"  - Recommended action: {warning.get('recommended_action')}")
    else:
        lines.append("No warnings.")
    lines.append("")
    return "\n".join(lines)


def write_gate() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gate = build_gate()
    OUT_JSON.write_text(json.dumps(gate, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(gate), encoding="utf-8")
    return gate


def main() -> int:
    gate = write_gate()
    r = gate["readiness"]
    print(json.dumps({
        "status": r["status"],
        "version": gate["version"],
        "ready_for_cockpit_binding": r["ready_for_cockpit_binding"],
        "blockers": r["blocker_count"],
        "warnings": r["warning_count"],
        "allowed_next_build": r["allowed_next_build"],
        "report": {
            "json": str(OUT_JSON.relative_to(ROOT)),
            "markdown": str(OUT_MD.relative_to(ROOT)),
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
