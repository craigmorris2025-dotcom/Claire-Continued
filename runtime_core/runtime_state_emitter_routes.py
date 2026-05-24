"""
Claire Syntalion v19.89.6
Runtime State Emitter Layer

Backend-owned runtime state emission.
This layer emits safe state truth only. It does not activate autonomous looping.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(tags=["Claire Runtime State Emitter"])

VERSION = "v19.89.6"
BUILD_NAME = "Runtime State Emitter Layer"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _runtime_state_path() -> Path:
    return _project_root() / "data" / "runtime" / "runtime_state.json"


def _runtime_state_history_path() -> Path:
    return _project_root() / "data" / "runtime" / "runtime_state_history.json"


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


def _existing_runtime_execution_summary() -> Dict[str, Any]:
    candidates = [
        _project_root() / "output" / "core_run_output.json",
        _project_root() / "outputs" / "core_run_output.json",
        _project_root() / "data" / "core_run_output.json",
        _project_root() / "runtime" / "core_run_output.json",
        _project_root() / "claire" / "runtime" / "core_run_output.json",
    ]
    for candidate in candidates:
        payload = _safe_read_json(candidate, None)
        if isinstance(payload, dict):
            return {
                "runtime_truth_available": True,
                "runtime_truth_source": str(candidate),
                "terminal_state": payload.get("terminal_state") or payload.get("status") or "unknown",
                "route": payload.get("route") or payload.get("selected_route") or payload.get("runtime_route") or "unknown",
                "confidence": payload.get("confidence") or payload.get("score"),
                "headline": payload.get("headline") or payload.get("title") or "Runtime output loaded",
                "summary": payload.get("summary") or payload.get("description") or "Runtime truth loaded from core output.",
            }
    return {
        "runtime_truth_available": False,
        "runtime_truth_source": None,
        "terminal_state": "no_runtime_output_loaded",
        "route": "not_started",
        "confidence": None,
        "headline": "Runtime state emitted from contract layer",
        "summary": "Runtime state exists, but no core_run_output.json has supplied active execution truth yet.",
    }


def _default_state() -> Dict[str, Any]:
    summary = _existing_runtime_execution_summary()
    now = _utc_now()
    return {
        "surface": "runtime_state",
        "version": VERSION,
        "build": BUILD_NAME,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_over_ui_assumptions": True,
        "fail_closed_governance": True,
        "autonomous_loop_enabled": False,
        "execution_mode": "state_emission_only",
        "runtime_session": {
            "session_id": "runtime-state-emitter",
            "state": "idle_waiting_for_runtime_execution",
            "started_at": None,
            "last_emitted_at": now,
            "last_transition_at": now,
        },
        "runtime_truth": summary,
        "route_state": {
            "selected_route": summary.get("route"),
            "terminal_state": summary.get("terminal_state"),
            "confidence": summary.get("confidence"),
            "review_required": True,
            "reason": "Runtime state emitter is active; execution output has not yet been propagated into a live run session.",
        },
        "lifecycle_state": {
            "current_stage_index": None,
            "current_stage_name": None,
            "stage_count": 30,
            "stage_source": "runtime_execution_contract",
            "stage_execution_active": False,
        },
        "review_queue_state": {
            "enabled": False,
            "pending_items": 0,
            "reason": "Review queue wiring is the next build layer after runtime state emission.",
        },
        "checked_at": now,
    }


def _emit_state() -> Dict[str, Any]:
    path = _runtime_state_path()
    existing = _safe_read_json(path, None)
    emitted = _default_state()

    if isinstance(existing, dict):
        previous_session = existing.get("runtime_session", {})
        emitted["runtime_session"]["started_at"] = previous_session.get("started_at")
        emitted["runtime_session"]["state"] = previous_session.get("state", emitted["runtime_session"]["state"])
        emitted["runtime_session"]["last_transition_at"] = previous_session.get("last_transition_at", emitted["runtime_session"]["last_transition_at"])

    _write_json(path, emitted)

    history_path = _runtime_state_history_path()
    history = _safe_read_json(history_path, [])
    if not isinstance(history, list):
        history = []
    history.append({
        "version": VERSION,
        "event": "runtime_state_emitted",
        "state": emitted["runtime_session"]["state"],
        "terminal_state": emitted["route_state"]["terminal_state"],
        "route": emitted["route_state"]["selected_route"],
        "emitted_at": emitted["checked_at"],
    })
    history = history[-100:]
    _write_json(history_path, history)
    return emitted



def _is_valid_runtime_state(state: Any) -> bool:
    if not isinstance(state, dict):
        return False
    required = [
        "surface",
        "version",
        "build",
        "runtime_session",
        "route_state",
        "lifecycle_state",
        "review_queue_state",
        "checked_at",
    ]
    return all(state.get(key) is not None for key in required)


@router.get("/system/runtime-state")
def runtime_state() -> Dict[str, Any]:
    state = _safe_read_json(_runtime_state_path(), None)
    if _is_valid_runtime_state(state):
        return state
    return _emit_state()


@router.get("/system/runtime-state/summary")
def runtime_state_summary() -> Dict[str, Any]:
    state = runtime_state()
    if not _is_valid_runtime_state(state):
        state = _emit_state()
    return {
        "surface": state.get("surface"),
        "version": state.get("version"),
        "build": state.get("build"),
        "backend_owns_truth": state.get("backend_owns_truth"),
        "cockpit_presentation_only": state.get("cockpit_presentation_only"),
        "autonomous_loop_enabled": state.get("autonomous_loop_enabled"),
        "execution_mode": state.get("execution_mode"),
        "runtime_session": state.get("runtime_session"),
        "route_state": state.get("route_state"),
        "lifecycle_state": state.get("lifecycle_state"),
        "review_queue_state": state.get("review_queue_state"),
        "checked_at": state.get("checked_at"),
    }


@router.get("/system/runtime-state/emit")
def runtime_state_emit() -> Dict[str, Any]:
    return _emit_state()
