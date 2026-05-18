from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["Claire Runtime Execution Propagation"])
VERSION = "v19.89.7.2"
BUILD_NAME = "app.py Syntax Recovery + Safe Runtime Propagation Router Registration"
CANONICAL_30_STAGES = ['Signal Ingestion', 'Signal Normalization', 'Source Validation & Weighting', 'Context Expansion', 'Signal Consolidation', 'Entity Extraction', 'Relationship Mapping', 'Trend Discovery', 'Cluster Formation', 'Insight/Thesis Structuring', 'Gap Detection', 'Gap Qualification', 'Discovery Generation', 'Breakthrough Identification & Classification', 'Advancement Path Selection', 'Auto Invention/Solution Generation', 'Solution Structuring', 'Buildability Assessment', 'Viability Assessment', 'Manufacturability/Deployability Assessment', 'Feasibility Validation', 'Design Portal Output/Blueprints/Specs', 'Market Positioning', 'Moat & Differentiation', 'Business Model & Value Capture', 'Competitor Analysis', 'Portfolio Creation/Optimization', 'Acquirer Identification', 'Acquisition Fit & Rationale', 'Final Package Construction']


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _runtime_dir() -> Path:
    return _project_root() / "data" / "runtime"


def _propagation_path() -> Path:
    return _runtime_dir() / "runtime_execution_propagation.json"


def _history_path() -> Path:
    return _runtime_dir() / "runtime_transition_history.json"


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


def _default_propagation() -> Dict[str, Any]:
    now = _utc_now()
    return {
        "surface": "runtime_execution_propagation",
        "version": VERSION,
        "build": BUILD_NAME,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "autonomous_loop_enabled": False,
        "propagation_mode": "manual_governed_step",
        "execution_active": False,
        "current_stage_index": 0,
        "current_stage_name": None,
        "completed_stage_count": 0,
        "stage_count": 30,
        "terminal_state": "not_started",
        "selected_route": "not_started",
        "last_transition": None,
        "created_at": now,
        "updated_at": now,
        "stages": [
            {
                "index": index + 1,
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "reason": "Waiting for governed propagation.",
            }
            for index, name in enumerate(CANONICAL_30_STAGES)
        ],
    }


def _load_propagation() -> Dict[str, Any]:
    payload = _safe_read_json(_propagation_path(), None)
    if isinstance(payload, dict) and payload.get("surface") == "runtime_execution_propagation":
        return payload
    payload = _default_propagation()
    _write_json(_propagation_path(), payload)
    return payload


def _append_history(event: Dict[str, Any]) -> None:
    history = _safe_read_json(_history_path(), [])
    if not isinstance(history, list):
        history = []
    history.append(event)
    _write_json(_history_path(), history[-200:])


def _advance_one_stage() -> Dict[str, Any]:
    propagation = _load_propagation()
    now = _utc_now()
    completed = int(propagation.get("completed_stage_count", 0) or 0)
    if completed >= 30:
        propagation["execution_active"] = False
        propagation["terminal_state"] = "propagation_complete_waiting_for_review"
        propagation["updated_at"] = now
        _write_json(_propagation_path(), propagation)
        return propagation
    next_index = completed + 1
    stages: List[Dict[str, Any]] = propagation.get("stages", [])
    if len(stages) < 30:
        propagation = _default_propagation()
        stages = propagation["stages"]
    stage = stages[next_index - 1]
    stage["status"] = "propagated"
    stage["started_at"] = stage.get("started_at") or now
    stage["completed_at"] = now
    stage["reason"] = "Stage propagated through governed runtime transition."
    propagation["execution_active"] = next_index < 30
    propagation["current_stage_index"] = next_index
    propagation["current_stage_name"] = stage["name"]
    propagation["completed_stage_count"] = next_index
    propagation["stage_count"] = 30
    propagation["terminal_state"] = "propagation_in_progress" if next_index < 30 else "propagation_complete_waiting_for_review"
    propagation["selected_route"] = "lifecycle_contract_route"
    propagation["last_transition"] = {
        "stage_index": next_index,
        "stage_name": stage["name"],
        "transition": "stage_propagated",
        "at": now,
    }
    propagation["updated_at"] = now
    _write_json(_propagation_path(), propagation)
    _append_history(propagation["last_transition"])
    return propagation


@router.get("/system/runtime-propagation")
def runtime_propagation() -> Dict[str, Any]:
    return _load_propagation()


@router.get("/system/runtime-propagation/summary")
def runtime_propagation_summary() -> Dict[str, Any]:
    propagation = _load_propagation()
    return {
        "surface": propagation.get("surface"),
        "version": propagation.get("version"),
        "build": propagation.get("build"),
        "backend_owns_truth": propagation.get("backend_owns_truth"),
        "cockpit_presentation_only": propagation.get("cockpit_presentation_only"),
        "autonomous_loop_enabled": propagation.get("autonomous_loop_enabled"),
        "propagation_mode": propagation.get("propagation_mode"),
        "execution_active": propagation.get("execution_active"),
        "current_stage_index": propagation.get("current_stage_index"),
        "current_stage_name": propagation.get("current_stage_name"),
        "completed_stage_count": propagation.get("completed_stage_count"),
        "stage_count": propagation.get("stage_count"),
        "terminal_state": propagation.get("terminal_state"),
        "selected_route": propagation.get("selected_route"),
        "last_transition": propagation.get("last_transition"),
        "updated_at": propagation.get("updated_at"),
    }


@router.get("/system/runtime-propagation/advance")
def runtime_propagation_advance() -> Dict[str, Any]:
    return _advance_one_stage()


@router.get("/system/runtime-propagation/history")
def runtime_propagation_history() -> Dict[str, Any]:
    history = _safe_read_json(_history_path(), [])
    if not isinstance(history, list):
        history = []
    return {
        "surface": "runtime_transition_history",
        "version": VERSION,
        "count": len(history),
        "events": history,
        "checked_at": _utc_now(),
    }


@router.get("/system/runtime-propagation/registration-proof")
def runtime_propagation_registration_proof() -> Dict[str, Any]:
    return {
        "surface": "runtime_propagation_registration_proof",
        "version": VERSION,
        "registered": True,
        "routes": [
            "/system/runtime-propagation",
            "/system/runtime-propagation/summary",
            "/system/runtime-propagation/advance",
            "/system/runtime-propagation/history",
            "/system/runtime-propagation/registration-proof",
        ],
        "checked_at": _utc_now(),
    }
