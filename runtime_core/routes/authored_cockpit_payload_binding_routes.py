from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter


router = APIRouter(tags=["authored-cockpit-payload-binding"])


def _root() -> Path:
    return Path.cwd()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def _continuous_dir() -> Path:
    return _root() / "data" / "continuous_runtime"


def _latest_run() -> Dict[str, Any]:
    artifacts: List[Path] = []
    for base in [_root() / "data" / "runs", _root() / "output" / "runs", _root() / "runs"]:
        if base.exists():
            artifacts.extend(base.glob("**/run_manifest.json"))
            artifacts.extend(base.glob("**/status.json"))

    if not artifacts:
        return {"status": "no_active_run", "run_id": None, "truth_owner": "backend"}

    latest = max(artifacts, key=lambda p: p.stat().st_mtime)
    payload = _read_json(latest, {})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("status", "run_artifact_available")
    payload.setdefault("artifact_path", str(latest))
    payload.setdefault("truth_owner", "backend")
    return payload


def _continuous_status() -> Dict[str, Any]:
    payload = _read_json(_continuous_dir() / "status.json", None)
    if isinstance(payload, dict):
        payload.setdefault("truth_owner", "backend")
        payload.setdefault("candidate_generation", "not_fabricated")
        return payload
    return {
        "status": "available_waiting",
        "runtime_state": "not_started",
        "message": "Continuous runtime route is available; executor/cycle artifact has not produced candidates yet.",
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "updated_at": _now(),
    }


def _review_queue() -> Dict[str, Any]:
    payload = _read_json(_continuous_dir() / "review_queue.json", None)
    if isinstance(payload, dict):
        queue = payload.get("review_queue", payload.get("items", payload.get("candidates", [])))
        if not isinstance(queue, list):
            queue = []
        payload["review_queue"] = queue
        payload["total"] = len(queue)
        payload.setdefault("truth_owner", "backend")
        payload.setdefault("candidate_generation", "not_fabricated")
        return payload
    if isinstance(payload, list):
        return {"review_queue": payload, "total": len(payload), "truth_owner": "backend", "candidate_generation": "not_fabricated"}
    return {
        "review_queue": [],
        "total": 0,
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "message": "No validated review candidates exposed yet.",
        "updated_at": _now(),
    }


def _counts(queue: List[Dict[str, Any]]) -> Dict[str, int]:
    out = {"discovery": 0, "breakthrough": 0, "portfolio": 0, "design": 0, "package": 0}
    for item in queue:
        text = json.dumps(item, default=str).lower()
        if any(t in text for t in ["discovery", "gap", "trend", "signal"]):
            out["discovery"] += 1
        if "breakthrough" in text:
            out["breakthrough"] += 1
        if "portfolio" in text:
            out["portfolio"] += 1
        if any(t in text for t in ["design", "blueprint", "autodesign"]):
            out["design"] += 1
        if any(t in text for t in ["package", "acquisition"]):
            out["package"] += 1
    return out


def _payload() -> Dict[str, Any]:
    queue_payload = _review_queue()
    queue = queue_payload.get("review_queue", [])
    if not isinstance(queue, list):
        queue = []

    return {
        "status": "available",
        "payload_status": "available",
        "truth_owner": "backend",
        "build": "v19.82B.16.1",
        "selected_route": "pending_evidence",
        "terminal_state": "runtime_available_waiting_for_candidates",
        "latest_run": _latest_run(),
        "continuous_runtime": _continuous_status(),
        "review_queue": queue,
        "candidate_counts": _counts(queue),
        "lifecycle": {
            "stage_count": 30,
            "active_stage": "signal_ingestion_or_waiting",
            "terminal_state": "runtime_available_waiting_for_candidates",
            "protected_stages": {
                "16": "Auto Invention / Solution Generation",
                "17": "Solution Structuring",
                "18": "Buildability Assessment",
                "19": "Viability Assessment",
                "20": "Manufacturability / Deployability Assessment",
                "21": "Feasibility Validation",
                "22": "Design Portal Output / Blueprints / Specs",
            },
        },
        "rules": {
            "frontend_truth_mutation": False,
            "candidate_generation": "not_fabricated",
            "operator_review_required": True,
        },
        "updated_at": _now(),
    }


@router.get("/dashboard/payload/status")
async def dashboard_payload_status() -> Dict[str, Any]:
    return {"status": "available", "payload_status": "available", "truth_owner": "backend", "route": "/dashboard/payload/status", "updated_at": _now()}


@router.get("/api/dashboard/payload")
async def api_dashboard_payload() -> Dict[str, Any]:
    return _payload()


@router.get("/api/dashboard/payload/status")
async def api_dashboard_payload_status() -> Dict[str, Any]:
    return {"status": "available", "payload_status": "available", "truth_owner": "backend", "route": "/api/dashboard/payload/status", "updated_at": _now()}
