#!/usr/bin/env python3
"""
Canonical Route Mount Audit

Read-only tool. It imports the Claire FastAPI app, inventories mounted routes,
finds duplicate method/path owners, scans cockpit endpoint references, and writes
JSON/Markdown audit reports for v19.84.4 canonical owner selection.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "audits" / "v19_84_3_canonical_route_mount_audit"
REPORT_JSON = REPORT_DIR / "canonical_route_mount_audit_report.json"
REPORT_MD = REPORT_DIR / "canonical_route_mount_audit_report.md"

CRITICAL_ROUTES = [
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/runtime/continuous/status",
    "/runtime/continuous/review-queue",
    "/runs/start",
    "/universes",
]

FRONTEND_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".html", ".css"}
PYTHON_SUFFIXES = {".py"}


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
    raise RuntimeError("Could not load Claire FastAPI app. " + " | ".join(errors))


def route_methods(route: Any) -> List[str]:
    methods = getattr(route, "methods", None)
    if not methods:
        return []
    return sorted(str(m) for m in methods if str(m) not in {"HEAD", "OPTIONS"})


def route_endpoint_name(route: Any) -> str:
    endpoint = getattr(route, "endpoint", None)
    if endpoint is None:
        return ""
    module = getattr(endpoint, "__module__", "")
    qualname = getattr(endpoint, "__qualname__", getattr(endpoint, "__name__", ""))
    return f"{module}.{qualname}".strip(".")


def collect_mounted_routes(app: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        if not path:
            continue
        rows.append({
            "path": path,
            "name": getattr(route, "name", ""),
            "methods": route_methods(route),
            "endpoint": route_endpoint_name(route),
            "route_class": route.__class__.__name__,
        })
    return sorted(rows, key=lambda x: (x["path"], ",".join(x["methods"]), x["endpoint"]))


def route_key(row: Dict[str, Any]) -> str:
    return f"{','.join(row.get('methods') or [''])} {row.get('path', '')}".strip()


def find_duplicate_mounted_routes(routes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in routes:
        grouped[route_key(row)].append(row)
    return {k: v for k, v in grouped.items() if len(v) > 1}


def critical_route_status(routes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    by_path: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in routes:
        by_path[row["path"]].append(row)
    status: Dict[str, Dict[str, Any]] = {}
    for path in CRITICAL_ROUTES:
        owners = by_path.get(path, [])
        state = "missing" if not owners else "single_owner" if len(owners) == 1 else "duplicate_owner"
        status[path] = {"mounted": bool(owners), "owner_count": len(owners), "owners": owners, "state": state}
    return status


def iter_files(base: Path, suffixes: set[str]) -> Iterable[Path]:
    if not base.exists():
        return []
    ignored = {"__pycache__", ".git", ".venv", "venv", "node_modules", "backups", "archive"}
    result: List[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored for part in path.parts):
            continue
        if path.suffix.lower() in suffixes:
            result.append(path)
    return result


def static_python_route_scan() -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    route_re = re.compile(r"\.(get|post|put|delete|patch|options|head)\(\s*['\"]([^'\"]+)['\"]")
    include_re = re.compile(r"include_router\((.*?)\)")
    seen = set()
    for base in [ROOT / "claire", ROOT / "src" / "claire", ROOT / "backend"]:
        for path in iter_files(base, PYTHON_SUFFIXES):
            if path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for match in route_re.finditer(text):
                findings.append({"file": str(path.relative_to(ROOT)), "method": match.group(1).upper(), "path": match.group(2), "line": text[:match.start()].count("\n") + 1, "kind": "decorated_route"})
            for match in include_re.finditer(text):
                findings.append({"file": str(path.relative_to(ROOT)), "method": None, "path": None, "line": text[:match.start()].count("\n") + 1, "kind": "include_router", "snippet": match.group(0)[:240]})
    return findings


def frontend_endpoint_dependency_scan() -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    endpoint_re = re.compile(r"[\'\"`](/(?:api/)?(?:dashboard|runtime|runs|universes|internet|health|docs|deployment|launch)[^\'\"`\s<>){}]*)[\'\"`]")
    seen = set()
    for base in [ROOT / "frontend", ROOT / "src" / "frontend"]:
        for path in iter_files(base, FRONTEND_SUFFIXES):
            if path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for match in endpoint_re.finditer(text):
                findings.append({"file": str(path.relative_to(ROOT)), "route": match.group(1), "line": text[:match.start()].count("\n") + 1})
    deduped = {(x["file"], x["route"], x["line"]): x for x in findings}
    return sorted(deduped.values(), key=lambda x: (x["route"], x["file"], x["line"]))


def build_recommendations(critical: Dict[str, Dict[str, Any]], duplicates: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    for path, row in critical.items():
        if row["state"] == "missing":
            recs.append({"priority": "high", "area": "critical_route", "route": path, "recommendation": "Route is missing. Decide whether to restore it or remove cockpit dependency."})
        elif row["state"] == "duplicate_owner":
            recs.append({"priority": "critical", "area": "critical_route", "route": path, "recommendation": "Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others."})
    if duplicates:
        recs.append({"priority": "critical", "area": "route_registry", "route": "*", "recommendation": "Duplicate method/path route keys exist. Add enforcement before runtime/cockpit expansion."})
    if not recs:
        recs.append({"priority": "medium", "area": "route_registry", "route": "*", "recommendation": "No duplicate mounted critical routes detected. Proceed to canonical owner registry lock."})
    return recs


def write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Claire v19.84.3 Canonical Route Mount Audit")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Mounted route count: `{report['mounted_route_count']}`")
    lines.append(f"- Duplicate mounted route keys: `{len(report['duplicate_mounted_routes'])}`")
    lines.append("")
    lines.append("## Critical Route Status")
    lines.append("")
    lines.append("| Route | State | Owner Count |")
    lines.append("|---|---:|---:|")
    for path, row in report["critical_route_status"].items():
        lines.append(f"| `{path}` | `{row['state']}` | `{row['owner_count']}` |")
    lines.append("")
    lines.append("## Duplicate Mounted Routes")
    lines.append("")
    if report["duplicate_mounted_routes"]:
        for key, rows in report["duplicate_mounted_routes"].items():
            lines.append(f"### `{key}`")
            for row in rows:
                lines.append(f"- `{row.get('endpoint', '')}` via `{row.get('route_class', '')}`")
            lines.append("")
    else:
        lines.append("No duplicate mounted method/path route keys detected.")
        lines.append("")
    lines.append("## Cockpit Endpoint Dependencies")
    lines.append("")
    lines.append(f"- Frontend endpoint references found: `{len(report['frontend_endpoint_dependencies'])}`")
    lines.append("")
    for item in report["frontend_endpoint_dependencies"][:80]:
        lines.append(f"- `{item['route']}` in `{item['file']}` line `{item['line']}`")
    if len(report["frontend_endpoint_dependencies"]) > 80:
        lines.append(f"- ... {len(report['frontend_endpoint_dependencies']) - 80} more references omitted; see JSON report.")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for item in report["recommendations"]:
        lines.append(f"- **{item['priority']}** `{item['area']}` `{item.get('route', '')}` — {item['recommendation']}")
    lines.append("")
    lines.append("## Next Build")
    lines.append("")
    lines.append("v19.84.4 should create the Canonical Route Owner Registry using this audit as evidence.")
    return "\n".join(lines) + "\n"


def run_audit() -> Dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    app = load_app()
    mounted_routes = collect_mounted_routes(app)
    duplicates = find_duplicate_mounted_routes(mounted_routes)
    critical = critical_route_status(mounted_routes)
    report = {
        "version": "v19.84.3",
        "build": "Canonical Route Mount Audit",
        "generated_at": utc_now(),
        "status": "ok",
        "read_only": True,
        "mounted_route_count": len(mounted_routes),
        "mounted_routes": mounted_routes,
        "duplicate_mounted_routes": duplicates,
        "critical_routes": CRITICAL_ROUTES,
        "critical_route_status": critical,
        "python_route_static_scan": static_python_route_scan(),
        "frontend_endpoint_dependencies": frontend_endpoint_dependency_scan(),
        "recommendations": build_recommendations(critical, duplicates),
        "report_paths": {"json": str(REPORT_JSON.relative_to(ROOT)), "markdown": str(REPORT_MD.relative_to(ROOT))},
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(write_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    try:
        report = run_audit()
    except Exception as exc:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        failure = {"version": "v19.84.3", "build": "Canonical Route Mount Audit", "generated_at": utc_now(), "status": "failed", "error": repr(exc), "read_only": True}
        REPORT_JSON.write_text(json.dumps(failure, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(failure, indent=2))
        return 1
    print(json.dumps({
        "status": report["status"],
        "version": report["version"],
        "mounted_route_count": report["mounted_route_count"],
        "duplicate_mounted_route_count": len(report["duplicate_mounted_routes"]),
        "critical_route_status": {path: row["state"] for path, row in report["critical_route_status"].items()},
        "report": report["report_paths"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
