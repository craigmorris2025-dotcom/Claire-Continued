from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Request


router = APIRouter(tags=["active-route-truth"])


REQUIRED_ROUTES = [
    {"method": "GET", "path": "/dashboard/payload", "purpose": "primary authored cockpit payload"},
    {"method": "GET", "path": "/dashboard/payload/status", "purpose": "payload status"},
    {"method": "GET", "path": "/api/dashboard/payload", "purpose": "payload fallback"},
    {"method": "GET", "path": "/api/dashboard/payload/status", "purpose": "payload fallback status"},
    {"method": "GET", "path": "/runtime/continuous/status", "purpose": "continuous runtime status"},
    {"method": "POST", "path": "/runtime/continuous/start", "purpose": "continuous runtime start request"},
    {"method": "POST", "path": "/runtime/continuous/pause", "purpose": "continuous runtime pause request"},
    {"method": "GET", "path": "/runtime/continuous/review-queue", "purpose": "operator review queue"},
    {"method": "POST", "path": "/runs/start", "purpose": "manual run start"},
    {"method": "GET", "path": "/runs/latest", "purpose": "latest manual run"},
    {"method": "GET", "path": "/universes", "purpose": "source universe registry"},
]


def _root() -> Path:
    return Path.cwd()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_text(path: Path, limit: int = 250_000) -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""
    return ""


def _route_table(request: Request) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for route in request.app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        name = getattr(route, "name", None)
        endpoint = getattr(route, "endpoint", None)
        endpoint_name = getattr(endpoint, "__name__", None)
        endpoint_module = getattr(endpoint, "__module__", None)

        if not path:
            continue

        method_list = sorted([m for m in (methods or []) if m not in {"HEAD", "OPTIONS"}])
        rows.append({
            "path": path,
            "methods": method_list,
            "name": name,
            "endpoint_name": endpoint_name,
            "endpoint_module": endpoint_module,
        })

    return sorted(rows, key=lambda r: (r["path"], ",".join(r["methods"])))


def _matches(required: Dict[str, str], route: Dict[str, Any]) -> bool:
    return route["path"] == required["path"] and required["method"] in route.get("methods", [])


def _required_status(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for required in REQUIRED_ROUTES:
        matches = [r for r in routes if _matches(required, r)]
        out.append({
            **required,
            "mounted": len(matches) > 0,
            "match_count": len(matches),
            "matches": matches,
            "duplicate": len(matches) > 1,
        })
    return out


def _duplicate_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Dict[str, List[Dict[str, Any]]] = {}
    for route in routes:
        for method in route.get("methods", []):
            key = method + " " + route["path"]
            seen.setdefault(key, []).append(route)

    return [
        {"route": key, "count": len(items), "matches": items}
        for key, items in sorted(seen.items())
        if len(items) > 1
    ]


def _cockpit_files() -> Dict[str, Any]:
    root = _root()
    shell = root / "frontend" / "cockpit" / "shell" / "cockpit_shell.html"
    authored_js = root / "frontend" / "cockpit" / "shell" / "assets" / "claire_authored_enterprise_cockpit_shell.js"
    authored_css = root / "frontend" / "cockpit" / "shell" / "assets" / "claire_authored_enterprise_cockpit_shell.css"
    launcher = root / "LAUNCH_CLAIRE.bat"
    main_py = root / "main.py"
    app_py = root / "claire" / "app.py"

    shell_text = _safe_read_text(shell)
    js_text = _safe_read_text(authored_js)
    launcher_text = _safe_read_text(launcher)
    main_text = _safe_read_text(main_py)

    return {
        "canonical_shell": {
            "path": str(shell),
            "exists": shell.exists(),
            "contains_authored_cockpit": "claire-enterprise-cockpit" in shell_text,
            "contains_dev_terms": any(term in shell_text.lower() for term in ["swagger", "openapi", "/docs"]),
        },
        "authored_js": {
            "path": str(authored_js),
            "exists": authored_js.exists(),
            "contains_dashboard_payload": "/dashboard/payload" in js_text,
            "contains_api_payload_fallback": "/api/dashboard/payload" in js_text,
            "contains_continuous_runtime": "/runtime/continuous/status" in js_text,
            "contains_dev_terms": any(term in js_text.lower() for term in ["swagger", "openapi", "/docs"]),
        },
        "authored_css": {"path": str(authored_css), "exists": authored_css.exists()},
        "launcher": {
            "path": str(launcher),
            "exists": launcher.exists(),
            "mentions_cockpit_shell": "cockpit_shell" in launcher_text,
            "mentions_port_8000": "8000" in launcher_text,
        },
        "entrypoints": {
            "main_py": {
                "path": str(main_py),
                "exists": main_py.exists(),
                "mentions_uvicorn": "uvicorn" in main_text.lower(),
                "mentions_main_app": "main:app" in main_text,
            },
            "app_py": {"path": str(app_py), "exists": app_py.exists()},
        },
    }


@router.get("/system/route-truth")
async def active_route_truth(request: Request) -> Dict[str, Any]:
    routes = _route_table(request)
    required = _required_status(routes)
    duplicates = _duplicate_routes(routes)
    return {
        "status": "available",
        "truth_owner": "backend",
        "build": "v19.83.2",
        "generated_at": _now(),
        "active_app": {"route_count": len(routes), "cwd": str(_root())},
        "required_routes": required,
        "missing_required_routes": [r for r in required if not r["mounted"]],
        "duplicate_required_routes": [r for r in required if r["duplicate"]],
        "duplicate_routes": duplicates,
        "route_table": routes,
        "rules": {
            "frontend_truth_mutation": False,
            "candidate_generation": "not_fabricated",
            "dev_surface_exposed_in_cockpit": False,
        },
    }


@router.get("/system/route-truth/required")
async def active_required_route_truth(request: Request) -> Dict[str, Any]:
    routes = _route_table(request)
    required = _required_status(routes)
    return {
        "status": "available",
        "truth_owner": "backend",
        "build": "v19.83.2",
        "generated_at": _now(),
        "required_routes": required,
        "all_required_mounted": all(r["mounted"] for r in required),
        "duplicates_present": any(r["duplicate"] for r in required),
    }


@router.get("/system/cockpit-truth")
async def active_cockpit_truth(request: Request) -> Dict[str, Any]:
    routes = _route_table(request)
    required = _required_status(routes)
    cockpit = _cockpit_files()
    return {
        "status": "available",
        "truth_owner": "backend",
        "build": "v19.83.2",
        "generated_at": _now(),
        "cockpit": cockpit,
        "required_route_summary": {
            "all_required_mounted": all(r["mounted"] for r in required),
            "missing": [r for r in required if not r["mounted"]],
            "duplicates": [r for r in required if r["duplicate"]],
        },
        "operator_message": "This panel verifies active cockpit/backend synchronization. It is not a dev dashboard.",
    }
