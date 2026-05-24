
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["Claire Review Queue Runtime Ingestion"])

VERSION = "v19.89.8"
BUILD_NAME = "Review Queue Runtime Ingestion Layer"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _runtime_dir() -> Path:
    return _project_root() / "data" / "runtime"


def _review_dir() -> Path:
    return _project_root() / "data" / "review_queue"


def _runtime_state_path() -> Path:
    return _runtime_dir() / "runtime_state.json"


def _propagation_path() -> Path:
    return _runtime_dir() / "runtime_execution_propagation.json"


def _queue_path() -> Path:
    return _review_dir() / "review_queue.json"


def _history_path() -> Path:
    return _review_dir() / "review_queue_history.json"


def _safe_read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": str(exc), "path": str(path)}
    return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _empty_queue() -> Dict[str, Any]:
    now = _utc_now()
    return {
        "surface": "review_queue",
        "version": VERSION,
        "build": BUILD_NAME,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_over_ui_assumptions": True,
        "fail_closed_governance": True,
        "autonomous_loop_enabled": False,
        "queue_mode": "governed_runtime_review",
        "enabled": True,
        "pending_items": 0,
        "acknowledged_items": 0,
        "rejected_items": 0,
        "items": [],
        "created_at": now,
        "updated_at": now,
    }


def _load_queue() -> Dict[str, Any]:
    queue = _safe_read_json(_queue_path(), None)
    if isinstance(queue, dict) and queue.get("surface") == "review_queue":
        return queue
    queue = _empty_queue()
    _write_json(_queue_path(), queue)
    return queue


def _save_queue(queue: Dict[str, Any]) -> Dict[str, Any]:
    items = queue.get("items", [])
    queue["pending_items"] = len([i for i in items if i.get("status") == "pending_review"])
    queue["acknowledged_items"] = len([i for i in items if i.get("status") == "acknowledged"])
    queue["rejected_items"] = len([i for i in items if i.get("status") == "rejected"])
    queue["updated_at"] = _utc_now()
    _write_json(_queue_path(), queue)
    return queue


def _append_history(event: Dict[str, Any]) -> None:
    history = _safe_read_json(_history_path(), [])
    if not isinstance(history, list):
        history = []
    history.append(event)
    _write_json(_history_path(), history[-300:])


def _runtime_snapshot() -> Dict[str, Any]:
    runtime_state = _safe_read_json(_runtime_state_path(), {})
    propagation = _safe_read_json(_propagation_path(), {})
    if not isinstance(runtime_state, dict):
        runtime_state = {}
    if not isinstance(propagation, dict):
        propagation = {}
    return {"runtime_state": runtime_state, "propagation": propagation}


def _build_review_item(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    now = _utc_now()
    propagation = snapshot.get("propagation") or {}
    runtime_state = snapshot.get("runtime_state") or {}
    route_state = runtime_state.get("route_state") if isinstance(runtime_state.get("route_state"), dict) else {}
    completed = propagation.get("completed_stage_count", 0)
    stage_count = propagation.get("stage_count", 30)
    current_stage = propagation.get("current_stage_name")
    terminal_state = propagation.get("terminal_state") or route_state.get("terminal_state") or "unknown"
    selected_route = propagation.get("selected_route") or route_state.get("selected_route") or "unknown"
    item_id = f"runtime-review-{now.replace(':', '').replace('.', '-')}"
    return {
        "id": item_id,
        "type": "runtime_propagation_review",
        "status": "pending_review",
        "created_at": now,
        "updated_at": now,
        "requires_operator_review": True,
        "source": "runtime_execution_propagation",
        "summary": {
            "terminal_state": terminal_state,
            "selected_route": selected_route,
            "current_stage_name": current_stage,
            "completed_stage_count": completed,
            "stage_count": stage_count,
            "execution_active": propagation.get("execution_active", False),
            "autonomous_loop_enabled": False,
        },
        "review_questions": [
            "Does the runtime propagation state match expected lifecycle behavior?",
            "Is the current terminal state acceptable for the next governed handoff?",
            "Should this runtime state be acknowledged, rejected, or held for deeper inspection?",
        ],
        "snapshot": snapshot,
    }


def _sync_runtime_state_review(queue: Dict[str, Any]) -> None:
    path = _runtime_state_path()
    state = _safe_read_json(path, {})
    if not isinstance(state, dict):
        state = {}
    review = state.setdefault("review_queue_state", {})
    review["enabled"] = True
    review["pending_items"] = queue.get("pending_items", 0)
    review["acknowledged_items"] = queue.get("acknowledged_items", 0)
    review["rejected_items"] = queue.get("rejected_items", 0)
    review["reason"] = "Review queue runtime ingestion is active and backend-owned."
    state["checked_at"] = _utc_now()
    _write_json(path, state)


def _ingest_runtime() -> Dict[str, Any]:
    queue = _load_queue()
    snapshot = _runtime_snapshot()
    item = _build_review_item(snapshot)
    items: List[Dict[str, Any]] = queue.setdefault("items", [])
    prop = snapshot.get("propagation") or {}
    fingerprint = {
        "terminal_state": item["summary"]["terminal_state"],
        "selected_route": item["summary"]["selected_route"],
        "completed_stage_count": item["summary"]["completed_stage_count"],
        "propagation_updated_at": prop.get("updated_at"),
    }
    item["fingerprint"] = fingerprint
    for existing in items:
        if existing.get("fingerprint") == fingerprint and existing.get("status") == "pending_review":
            queue = _save_queue(queue)
            _sync_runtime_state_review(queue)
            return {
                "surface": "review_queue_ingest_runtime",
                "version": VERSION,
                "ingested": False,
                "reason": "Matching pending runtime review item already exists.",
                "existing_item_id": existing.get("id"),
                "queue": queue,
                "checked_at": _utc_now(),
            }
    items.insert(0, item)
    queue = _save_queue(queue)
    _append_history({"event": "runtime_review_item_ingested", "item_id": item["id"], "fingerprint": fingerprint, "at": item["created_at"]})
    _sync_runtime_state_review(queue)
    return {"surface": "review_queue_ingest_runtime", "version": VERSION, "ingested": True, "item": item, "queue": queue, "checked_at": _utc_now()}


@router.get("/system/review-queue")
def review_queue() -> Dict[str, Any]:
    queue = _load_queue()
    _sync_runtime_state_review(queue)
    return queue


@router.get("/system/review-queue/summary")
def review_queue_summary() -> Dict[str, Any]:
    queue = _load_queue()
    return {
        "surface": queue.get("surface"),
        "version": queue.get("version"),
        "build": queue.get("build"),
        "backend_owns_truth": queue.get("backend_owns_truth"),
        "cockpit_presentation_only": queue.get("cockpit_presentation_only"),
        "autonomous_loop_enabled": queue.get("autonomous_loop_enabled"),
        "queue_mode": queue.get("queue_mode"),
        "enabled": queue.get("enabled"),
        "pending_items": queue.get("pending_items"),
        "acknowledged_items": queue.get("acknowledged_items"),
        "rejected_items": queue.get("rejected_items"),
        "latest_item": queue.get("items", [None])[0] if queue.get("items") else None,
        "updated_at": queue.get("updated_at"),
    }


@router.get("/system/review-queue/ingest-runtime")
def review_queue_ingest_runtime() -> Dict[str, Any]:
    return _ingest_runtime()


@router.get("/system/review-queue/history")
def review_queue_history() -> Dict[str, Any]:
    history = _safe_read_json(_history_path(), [])
    if not isinstance(history, list):
        history = []
    return {"surface": "review_queue_history", "version": VERSION, "count": len(history), "events": history, "checked_at": _utc_now()}


@router.get("/system/review-queue/registration-proof")
def review_queue_registration_proof() -> Dict[str, Any]:
    return {
        "surface": "review_queue_registration_proof",
        "version": VERSION,
        "registered": True,
        "routes": [
            "/system/review-queue",
            "/system/review-queue/summary",
            "/system/review-queue/ingest-runtime",
            "/system/review-queue/history",
            "/system/review-queue/registration-proof",
        ],
        "checked_at": _utc_now(),
    }
