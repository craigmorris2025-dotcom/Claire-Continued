from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    from fastapi import Request
except Exception:
    Request = Any

from .graph import decide_runtime_route
from .store import RuntimeTruthStore, default_state

VERSION = "v19.84.1"

def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def route_paths(app: Any) -> set[str]:
    paths = set()
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        if path:
            paths.add(path)
    return paths

def store() -> RuntimeTruthStore:
    s = RuntimeTruthStore(project_root())
    s.ensure()
    return s

def compose_dashboard_payload() -> Dict[str, Any]:
    s = store()
    runtime_state = s.read_state()
    review_queue = s.read_queue()
    return {
        "status": "success",
        "version": VERSION,
        "source": "backend_runtime_truth",
        "backend_owns_truth": True,
        "fake_outputs_allowed": False,
        "runtime": runtime_state,
        "review_queue": {
            "count": review_queue.get("count", 0),
            "items": review_queue.get("queue", [])
        },
        "cockpit_contract": {
            "canonical_source": "GET /dashboard/payload",
            "direct_file_open_canonical": False,
            "dev_surface_contamination_allowed": False
        },
        "plateau_truth": {
            "app_boots": True,
            "runtime_truth_endpoint_live": True,
            "continuous_runtime_active": bool(runtime_state.get("continuous_runtime", {}).get("implemented")),
            "web_governance_verified": runtime_state.get("web_governance", {}).get("provider_status") != "unverified",
            "active_route": runtime_state.get("active_route"),
            "terminal_state": runtime_state.get("terminal_state")
        }
    }

def install_runtime_truth_routes(app: Any) -> Any:
    paths = route_paths(app)

    async def runtime_status() -> Dict[str, Any]:
        return store().read_state()

    async def review_queue() -> Dict[str, Any]:
        return store().read_queue()

    async def dashboard_payload() -> Dict[str, Any]:
        return compose_dashboard_payload()

    async def dashboard_payload_status() -> Dict[str, Any]:
        payload = compose_dashboard_payload()
        return {
            "status": "success",
            "version": VERSION,
            "payload_live": True,
            "active_route": payload["runtime"].get("active_route"),
            "terminal_state": payload["runtime"].get("terminal_state"),
            "review_queue_count": payload["review_queue"].get("count", 0),
            "backend_owns_truth": True
        }

    async def runtime_decide(request: Request) -> Dict[str, Any]:
        body = await request.json()
        raw_input = body.get("raw_input") or body.get("signal") or body.get("input") or ""
        mode = body.get("mode") or "deterministic"
        decision = decide_runtime_route(raw_input, mode)

        current = default_state()
        current["mode"] = mode
        current["last_cycle_at"] = decision.get("created_at")
        current["active_route"] = decision.get("route")
        current["terminal_state"] = decision.get("terminal_state")
        current["governance_state"] = decision.get("governance_state")
        current["lifecycle"]["selected_route_stages"] = decision.get("selected_route_stages", [])
        current["lifecycle"]["skipped_by_route"] = decision.get("skipped_by_route", [])
        current["latest_output_summary"] = {
            "run_id": decision.get("run_id"),
            "status": decision.get("status"),
            "route": decision.get("route"),
            "terminal_state": decision.get("terminal_state"),
            "confidence": decision.get("confidence")
        }
        store().write_state(current)
        return decision

    async def provider_status() -> Dict[str, Any]:
        return {
            "status": "success",
            "version": VERSION,
            "provider_status": "unverified",
            "live_available": False,
            "fail_closed": True,
            "truthful_note": "No live provider is marked active by this endpoint."
        }

    if "/runtime/continuous/status" not in paths:
        app.add_api_route("/runtime/continuous/status", runtime_status, methods=["GET"], tags=["runtime"])
    if "/runtime/continuous/review-queue" not in paths:
        app.add_api_route("/runtime/continuous/review-queue", review_queue, methods=["GET"], tags=["runtime"])
    if "/runtime/graph/decide" not in paths:
        app.add_api_route("/runtime/graph/decide", runtime_decide, methods=["POST"], tags=["runtime"])
    if "/dashboard/payload" not in paths:
        app.add_api_route("/dashboard/payload", dashboard_payload, methods=["GET"], tags=["dashboard"])
    if "/dashboard/payload/status" not in paths:
        app.add_api_route("/dashboard/payload/status", dashboard_payload_status, methods=["GET"], tags=["dashboard"])
    if "/api/dashboard/search/provider/status" not in paths:
        app.add_api_route("/api/dashboard/search/provider/status", provider_status, methods=["GET"], tags=["search"])

    return app
