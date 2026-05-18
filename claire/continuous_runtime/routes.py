from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    from fastapi import Request
except Exception:
    Request = Any

from .cycle import ensure_continuous_runtime_files, run_once

VERSION = "v19.84.2"

def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def route_paths(app: Any) -> set[str]:
    return {getattr(route, "path", "") for route in getattr(app, "routes", [])}

def install_continuous_runtime_cycle_routes(app: Any) -> Any:
    paths = route_paths(app)
    root = project_root()
    ensure_continuous_runtime_files(root)

    async def run_once_endpoint(request: Request) -> Dict[str, Any]:
        body = await request.json()
        raw_input = body.get("raw_input") or body.get("signal") or body.get("input") or ""
        source = body.get("source") or "operator_manual"
        return run_once(root=root, raw_input=raw_input, source=source)

    if "/runtime/continuous/run-once" not in paths:
        app.add_api_route("/runtime/continuous/run-once", run_once_endpoint, methods=["POST"], tags=["runtime"])
    return app
