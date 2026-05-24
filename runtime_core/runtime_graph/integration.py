from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    from fastapi import Request
except Exception:  # pragma: no cover
    Request = Any

from .orchestrator import RuntimeGraphOrchestrator
from .state import RuntimeGraphStore, RuntimeGraphState


def _root_from_app_file() -> Path:
    return Path(__file__).resolve().parents[2]


def _route_paths(app: Any) -> set[str]:
    paths = set()
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        if path:
            paths.add(path)
    return paths


def _store() -> RuntimeGraphStore:
    store = RuntimeGraphStore(_root_from_app_file())
    store.ensure()
    return store


def _payload() -> Dict[str, Any]:
    store = _store()
    state = store.read_state()
    queue = store.read_queue()
    return {
        "status": "success",
        "source": "backend_runtime_graph",
        "version": "v19.84.0",
        "runtime": state,
        "review_queue": {
            "count": queue.get("count", 0),
            "items": queue.get("queue", []),
        },
        "cockpit_contract": {
            "backend_owns_truth": True,
            "fake_outputs_allowed": False,
            "direct_file_open_is_canonical": False,
            "dev_surface_contamination": False,
        },
        "truth_state": {
            "payload_live": True,
            "continuous_runtime_verified": bool(state.get("continuous_runtime", {}).get("implemented")),
            "web_governance_verified": state.get("web_governance", {}).get("provider_status") != "unverified",
            "current_terminal_state": state.get("terminal_state"),
            "active_route": state.get("active_route"),
        }
    }


def install_runtime_graph_routes(app: Any) -> Any:
    """Mount only missing routes; never replace stronger existing implementations."""

    paths = _route_paths(app)
    store = _store()
    orchestrator = RuntimeGraphOrchestrator()

    async def runtime_status() -> Dict[str, Any]:
        return store.read_state()

    async def review_queue() -> Dict[str, Any]:
        return store.read_queue()

    async def dashboard_payload() -> Dict[str, Any]:
        return _payload()

    async def dashboard_payload_status() -> Dict[str, Any]:
        payload = _payload()
        return {
            "status": "success",
            "payload_live": True,
            "runtime_state": payload["runtime"].get("state"),
            "active_route": payload["runtime"].get("active_route"),
            "terminal_state": payload["runtime"].get("terminal_state"),
            "review_queue_count": payload["review_queue"]["count"],
            "version": "v19.84.0",
        }

    async def graph_decide(request: Request) -> Dict[str, Any]:
        body = await request.json()
        raw_input = body.get("raw_input") or body.get("signal") or body.get("input") or ""
        mode = body.get("mode") or "deterministic"
        decision = orchestrator.decide_route(raw_input=raw_input, mode=mode)

        state = RuntimeGraphState(
            enabled=False,
            state="idle",
            mode=mode,
            last_cycle_at=decision.get("created_at"),
            active_route=decision.get("route"),
            terminal_state=decision.get("terminal_state"),
            governance_state=decision.get("governance_state", "ready"),
            latest_output_summary={
                "run_id": decision.get("run_id"),
                "route": decision.get("route"),
                "terminal_state": decision.get("terminal_state"),
                "confidence": decision.get("confidence"),
                "status": decision.get("status"),
            },
        ).to_dict()
        state["lifecycle"]["completed_stages"] = [
            s for s in decision.get("stage_status", []) if s.get("status") == "selected"
        ]
        state["lifecycle"]["skipped_by_route"] = [
            s for s in decision.get("stage_status", []) if s.get("status") == "skipped"
        ]
        store.write_state(state)

        return decision

    async def web_provider_status() -> Dict[str, Any]:
        return {
            "status": "success",
            "provider_status": "unverified",
            "live_available": False,
            "dry_run_available": None,
            "fail_closed": True,
            "note": "No provider adapter verified through this runtime graph route. Existing provider route may override if already mounted.",
            "version": "v19.84.0",
        }

    if "/runtime/continuous/status" not in paths:
        app.add_api_route("/runtime/continuous/status", runtime_status, methods=["GET"], tags=["runtime"])
    if "/runtime/continuous/review-queue" not in paths:
        app.add_api_route("/runtime/continuous/review-queue", review_queue, methods=["GET"], tags=["runtime"])
    if "/runtime/graph/decide" not in paths:
        app.add_api_route("/runtime/graph/decide", graph_decide, methods=["POST"], tags=["runtime"])
    if "/dashboard/payload" not in paths:
        app.add_api_route("/dashboard/payload", dashboard_payload, methods=["GET"], tags=["dashboard"])
    if "/dashboard/payload/status" not in paths:
        app.add_api_route("/dashboard/payload/status", dashboard_payload_status, methods=["GET"], tags=["dashboard"])
    if "/api/dashboard/search/provider/status" not in paths:
        app.add_api_route("/api/dashboard/search/provider/status", web_provider_status, methods=["GET"], tags=["search"])

    return app
