#!/usr/bin/env python3
"""
Claire v19.84.5 Duplicate Route Fail Test

This tool enforces the canonical route owner registry created in v19.84.4.
It imports the running FastAPI app object and fails if any critical method/path
route has duplicate mounted owners or is missing from the app.

It is read-only. It does not change routes.
"""

from __future__ import annotations

import importlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "runtime_authority" / "canonical_route_owner_registry.json"
REPORT_DIR = ROOT / "audits" / "v19_84_5_duplicate_route_fail_test"
REPORT_JSON = REPORT_DIR / "duplicate_route_fail_test_report.json"
REPORT_MD = REPORT_DIR / "duplicate_route_fail_test_report.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_import_path() -> None:
    for candidate in [ROOT, ROOT / "src"]:
        text = str(candidate)
        if candidate.exists() and text not in sys.path:
            sys.path.insert(0, text)


def load_app() -> Any:
    ensure_import_path()
    errors: List[str] = []

    try:
        module = importlib.import_module("runtime_core.app")
        if hasattr(module, "create_app"):
            return module.create_app()
        if hasattr(module, "app"):
            return module.app
    except Exception as exc:
        errors.append(f"runtime_core.app failed: {exc!r}")

    try:
        module = importlib.import_module("main")
        if hasattr(module, "app"):
            return module.app
        if hasattr(module, "create_app"):
            return module.create_app()
    except Exception as exc:
        errors.append(f"main failed: {exc!r}")

    raise RuntimeError("Could not load Claire FastAPI app. " + " | ".join(errors))


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Missing registry: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def route_methods(route: Any) -> List[str]:
    methods = getattr(route, "methods", None)
    if not methods:
        return []
    return sorted(str(method) for method in methods if str(method) not in {"HEAD", "OPTIONS"})


def route_endpoint_name(route: Any) -> str:
    endpoint = getattr(route, "endpoint", None)
    if endpoint is None:
        return ""
    module = getattr(endpoint, "__module__", "")
    qualname = getattr(endpoint, "__qualname__", getattr(endpoint, "__name__", ""))
    return f"{module}.{qualname}".strip(".")


def collect_routes(app: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        if not path:
            continue
        rows.append({
            "path": path,
            "methods": route_methods(route),
            "endpoint": route_endpoint_name(route),
            "name": getattr(route, "name", ""),
            "route_class": route.__class__.__name__,
        })
    return sorted(rows, key=lambda row: (row["path"], ",".join(row["methods"]), row["endpoint"]))


def method_path_key(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def group_by_method_path(routes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in routes:
        methods = row.get("methods") or [""]
        for method in methods:
            grouped[method_path_key(method, row["path"])].append(row)
    return grouped


def evaluate(routes: List[Dict[str, Any]], registry: Dict[str, Any]) -> Dict[str, Any]:
    grouped = group_by_method_path(routes)
    failures: List[Dict[str, Any]] = []
    passing: List[Dict[str, Any]] = []

    for path, spec in registry.get("routes", {}).items():
        for method in spec.get("methods", ["GET"]):
            key = method_path_key(method, path)
            owners = grouped.get(key, [])
            if not owners:
                failures.append({
                    "route": path,
                    "method": method,
                    "key": key,
                    "failure": "missing_route",
                    "expected": "exactly_one_owner",
                    "owner_count": 0,
                    "owners": [],
                })
            elif len(owners) > 1:
                failures.append({
                    "route": path,
                    "method": method,
                    "key": key,
                    "failure": "duplicate_route_owner",
                    "expected": "exactly_one_owner",
                    "owner_count": len(owners),
                    "owners": owners,
                })
            else:
                passing.append({
                    "route": path,
                    "method": method,
                    "key": key,
                    "state": "single_owner",
                    "owner": owners[0],
                })

    return {
        "status": "passed" if not failures else "failed",
        "failure_count": len(failures),
        "passing_count": len(passing),
        "failures": failures,
        "passing": passing,
    }


def write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Claire v19.84.5 Duplicate Route Fail Test")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Mounted route count: `{report['mounted_route_count']}`")
    lines.append(f"- Passing critical route keys: `{report['evaluation']['passing_count']}`")
    lines.append(f"- Failing critical route keys: `{report['evaluation']['failure_count']}`")
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if report["evaluation"]["failures"]:
        for failure in report["evaluation"]["failures"]:
            lines.append(f"- `{failure['key']}` â€” `{failure['failure']}` owner_count=`{failure['owner_count']}`")
            for owner in failure.get("owners", []):
                lines.append(f"  - `{owner.get('endpoint', '')}`")
    else:
        lines.append("No failures.")
    lines.append("")
    lines.append("## Passing Critical Routes")
    lines.append("")
    for item in report["evaluation"]["passing"]:
        lines.append(f"- `{item['key']}` â†’ `{item['owner'].get('endpoint', '')}`")
    lines.append("")
    lines.append("## Next Build")
    lines.append("")
    lines.append("If this report fails, v19.84.6 must demote duplicate owners or restore missing critical routes before cockpit binding work proceeds.")
    return "\n".join(lines) + "\n"


def run_check() -> Dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    app = load_app()
    routes = collect_routes(app)
    registry = load_registry()
    evaluation = evaluate(routes, registry)

    report = {
        "version": "v19.84.5",
        "build": "Duplicate Route Fail Test",
        "generated_at": utc_now(),
        "status": evaluation["status"],
        "read_only": True,
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "mounted_route_count": len(routes),
        "evaluation": evaluation,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(write_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    try:
        report = run_check()
    except Exception as exc:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        failure = {
            "version": "v19.84.5",
            "build": "Duplicate Route Fail Test",
            "generated_at": utc_now(),
            "status": "failed",
            "error": repr(exc),
            "read_only": True,
        }
        REPORT_JSON.write_text(json.dumps(failure, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(failure, indent=2))
        return 1

    print(json.dumps({
        "status": report["status"],
        "version": report["version"],
        "mounted_route_count": report["mounted_route_count"],
        "passing": report["evaluation"]["passing_count"],
        "failures": report["evaluation"]["failure_count"],
        "report": {
            "json": str(REPORT_JSON.relative_to(ROOT)),
            "markdown": str(REPORT_MD.relative_to(ROOT)),
        },
    }, indent=2))

    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
