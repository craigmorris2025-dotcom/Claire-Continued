#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path.cwd()
AUDIT_DIR = PROJECT_ROOT / "docs" / "audits" / "v19_88_1_active_app_route_reality"

REQUIRED_OPERATIONAL_ENDPOINTS = [
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/dashboard/payload/status",
    "/dashboard/payload",
    "/runtime/continuous/status",
    "/runtime/continuous/start",
    "/runtime/continuous/review-queue",
    "/api/dashboard/search/provider/status",
    "/api/dashboard/search/provider/probe",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
    "/api/feeds/live-source-catalog/status",
    "/api/feeds/live-source-catalog/health",
    "/api/live-intelligence/status",
]

REQUIRED_SURFACES = {
    "boot_core": ["/", "/health", "/docs", "/openapi.json"],
    "dashboard_payload": ["/dashboard/payload/status", "/dashboard/payload"],
    "continuous_runtime": ["/runtime/continuous/status", "/runtime/continuous/start", "/runtime/continuous/review-queue"],
    "governed_search": [
        "/api/dashboard/search/provider/status",
        "/api/dashboard/search/provider/probe",
        "/api/dashboard/search/live",
        "/api/dashboard/search/smoke/google",
    ],
    "live_source_catalog": ["/api/feeds/live-source-catalog/status", "/api/feeds/live-source-catalog/health"],
    "live_intelligence": ["/api/live-intelligence/status"],
}


@dataclass
class RouteReality:
    path: str
    methods: list[str]
    name: str
    endpoint: str


def ensure_import_path() -> None:
    root = str(PROJECT_ROOT)
    src = str(PROJECT_ROOT / "src")
    for item in [root, src]:
        if item not in sys.path:
            sys.path.insert(0, item)


def load_create_app() -> tuple[Any | None, str, str]:
    ensure_import_path()
    candidates = [
        ("claire.app", "create_app"),
        ("src.claire.app", "create_app"),
        ("main", "app"),
    ]

    errors: list[str] = []
    for module_name, attr_name in candidates:
        try:
            module = importlib.import_module(module_name)
            target = getattr(module, attr_name)
            if attr_name == "create_app":
                return target(), module_name, attr_name
            return target, module_name, attr_name
        except Exception as exc:
            errors.append(f"{module_name}:{attr_name} -> {type(exc).__name__}: {exc}")

    return None, "", " | ".join(errors)


def inspect_routes(app: Any) -> list[RouteReality]:
    realities: list[RouteReality] = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        methods = sorted(list(getattr(route, "methods", []) or []))
        name = str(getattr(route, "name", ""))
        endpoint = getattr(route, "endpoint", None)
        endpoint_name = ""
        if endpoint is not None:
            endpoint_name = f"{getattr(endpoint, '__module__', '')}.{getattr(endpoint, '__name__', repr(endpoint))}"
        if path:
            realities.append(RouteReality(path=path, methods=methods, name=name, endpoint=endpoint_name))
    return sorted(realities, key=lambda r: (r.path, ",".join(r.methods), r.name))


def classify(routes: list[RouteReality]) -> dict[str, Any]:
    route_paths = {r.path for r in routes}
    # FastAPI automatically exposes docs/openapi if enabled; they may appear as routes.
    missing = [p for p in REQUIRED_OPERATIONAL_ENDPOINTS if p not in route_paths]

    surface_status = {}
    for surface, endpoints in REQUIRED_SURFACES.items():
        present = [p for p in endpoints if p in route_paths]
        absent = [p for p in endpoints if p not in route_paths]
        surface_status[surface] = {
            "required": endpoints,
            "present": present,
            "missing": absent,
            "complete": len(absent) == 0,
        }

    return {
        "route_count": len(routes),
        "required_missing": missing,
        "required_present": [p for p in REQUIRED_OPERATIONAL_ENDPOINTS if p in route_paths],
        "surfaces": surface_status,
        "operational_readiness": {
            "boot_core_ready": surface_status["boot_core"]["complete"],
            "dashboard_payload_ready": surface_status["dashboard_payload"]["complete"],
            "continuous_runtime_ready": surface_status["continuous_runtime"]["complete"],
            "governed_search_ready": surface_status["governed_search"]["complete"],
            "live_source_catalog_ready": surface_status["live_source_catalog"]["complete"],
            "live_intelligence_ready": surface_status["live_intelligence"]["complete"],
        },
        "next_repair_rule": "Repair only missing required operational endpoints in the active create_app route stack. Do not restore archived routes blindly.",
    }


def write_reports() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    app, source_module, source_attr_or_error = load_create_app()

    if app is None:
        report = {
            "version": "19.88.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policy": {
                "audit_only": True,
                "mutated_files": False,
                "mounted_routes": False,
                "rewired_dashboard": False,
                "enabled_live_internet": False,
                "runtime_truth_mutated": False,
            },
            "active_app_loaded": False,
            "source_module": source_module,
            "source_attr": "",
            "load_error": source_attr_or_error,
            "routes": [],
            "classification": {},
        }
    else:
        routes = inspect_routes(app)
        report = {
            "version": "19.88.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policy": {
                "audit_only": True,
                "mutated_files": False,
                "mounted_routes": False,
                "rewired_dashboard": False,
                "enabled_live_internet": False,
                "runtime_truth_mutated": False,
            },
            "active_app_loaded": True,
            "source_module": source_module,
            "source_attr": source_attr_or_error,
            "routes": [asdict(r) for r in routes],
            "classification": classify(routes),
        }

    (AUDIT_DIR / "ACTIVE_APP_ROUTE_REALITY.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = []
    md.append("# Claire v19.88.1 Active App Route Reality")
    md.append("")
    md.append(f"Generated: {report['generated_at']}")
    md.append("")
    md.append("## Policy")
    for k, v in report["policy"].items():
        md.append(f"- {k}: **{v}**")
    md.append("")
    md.append(f"- Active app loaded: **{report['active_app_loaded']}**")
    md.append(f"- Source: `{report.get('source_module', '')}:{report.get('source_attr', '')}`")
    if not report["active_app_loaded"]:
        md.append(f"- Load error: `{report.get('load_error', '')}`")
    else:
        classification = report["classification"]
        md.append(f"- Active mounted route count: **{classification['route_count']}**")
        md.append("")
        md.append("## Missing Required Operational Endpoints")
        for p in classification["required_missing"]:
            md.append(f"- `{p}`")
        md.append("")
        md.append("## Surface Readiness")
        for surface, data in classification["surfaces"].items():
            md.append(f"### {surface}")
            md.append(f"- Complete: **{data['complete']}**")
            md.append(f"- Present: {', '.join(data['present']) if data['present'] else 'none'}")
            md.append(f"- Missing: {', '.join(data['missing']) if data['missing'] else 'none'}")
            md.append("")
        md.append("## Next Repair Rule")
        md.append(classification["next_repair_rule"])
    (AUDIT_DIR / "ACTIVE_APP_ROUTE_REALITY_SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("Claire v19.88.1 active app route reality audit complete.")
    print(f"Audit directory: {AUDIT_DIR}")
    print(f"Active app loaded: {report['active_app_loaded']}")
    if report["active_app_loaded"]:
        print(f"Route count: {report['classification']['route_count']}")
        print(f"Missing required: {len(report['classification']['required_missing'])}")
    else:
        print(f"Load error: {report.get('load_error', '')}")


if __name__ == "__main__":
    write_reports()
