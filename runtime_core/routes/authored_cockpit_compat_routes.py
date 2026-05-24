"""
Claire Syntalion v19.82B.16
Authored Cockpit Backend Route Availability Repair

Truthful backend compatibility routes for the authored enterprise cockpit.
These routes intentionally return empty/waiting states when deeper runtime artifacts
are unavailable. They do not fabricate discoveries, breakthroughs, portfolios,
designs, packages, route scoring, or runtime truth.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter


router = APIRouter(tags=["authored-cockpit-compat"])


def _root() -> Path:
    return Path.cwd()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _continuous_dir() -> Path:
    return _root() / "data" / "continuous_runtime"


def _runs_dir() -> Path:
    return _root() / "data" / "runs"


def _latest_manual_run() -> Dict[str, Any]:
    candidates: List[Path] = []

    for base in [
        _root() / "data" / "runs",
        _root() / "output" / "runs",
        _root() / "runs",
    ]:
        if base.exists():
            candidates.extend(base.glob("**/run_manifest.json"))
            candidates.extend(base.glob("**/status.json"))

    if not candidates:
        return {
            "status": "no_active_run",
            "run_id": None,
            "message": "No manual run artifact is available yet.",
        }

    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    payload = _read_json(latest, {})
    if not isinstance(payload, dict):
        payload = {}

    payload.setdefault("status", payload.get("state", "run_artifact_available"))
    payload.setdefault("artifact_path", str(latest))
    return payload


def _continuous_status() -> Dict[str, Any]:
    status_path = _continuous_dir() / "status.json"
    payload = _read_json(status_path, None)

    if isinstance(payload, dict):
        payload.setdefault("source", "data/continuous_runtime/status.json")
        payload.setdefault("truth_owner", "backend")
        return payload

    return {
        "status": "available_waiting",
        "runtime_state": "not_started",
        "message": "Continuous runtime route is available, but no active runtime artifact exists yet.",
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "updated_at": _utc_now(),
    }


def _review_queue_payload() -> Dict[str, Any]:
    queue_path = _continuous_dir() / "review_queue.json"
    payload = _read_json(queue_path, None)

    if isinstance(payload, dict):
        payload.setdefault("review_queue", payload.get("items", payload.get("candidates", [])))
        payload.setdefault("truth_owner", "backend")
        return payload

    if isinstance(payload, list):
        return {
            "review_queue": payload,
            "total": len(payload),
            "truth_owner": "backend",
        }

    return {
        "review_queue": [],
        "total": 0,
        "message": "No review items exposed yet. Empty means no backend-validated candidates are available.",
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "updated_at": _utc_now(),
    }


def _candidate_counts(review_queue: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {
        "discovery": 0,
        "breakthrough": 0,
        "portfolio": 0,
        "design": 0,
        "package": 0,
    }

    for item in review_queue:
        text = json.dumps(item, default=str).lower()
        if any(token in text for token in ["discovery", "gap", "trend", "signal"]):
            counts["discovery"] += 1
        if "breakthrough" in text:
            counts["breakthrough"] += 1
        if "portfolio" in text:
            counts["portfolio"] += 1
        if any(token in text for token in ["design", "blueprint", "autodesign"]):
            counts["design"] += 1
        if any(token in text for token in ["package", "acquisition"]):
            counts["package"] += 1

    return counts


def _universes_payload() -> Dict[str, Any]:
    candidates = [
        _root() / "data" / "source_universes" / "universes.json",
        _root() / "data" / "universes.json",
        _root() / "data" / "source_universe_registry.json",
    ]

    for path in candidates:
        payload = _read_json(path, None)
        if isinstance(payload, dict):
            universes = payload.get("universes") or payload.get("source_universes") or []
            return {
                "universes": universes,
                "total": len(universes) if isinstance(universes, list) else 0,
                "truth_owner": "backend",
                "source": str(path),
            }
        if isinstance(payload, list):
            return {
                "universes": payload,
                "total": len(payload),
                "truth_owner": "backend",
                "source": str(path),
            }

    default_universes = [
        {
            "id": "market_intelligence",
            "name": "Market Intelligence",
            "status": "registered",
            "governance": "operator_review_required",
            "description": "Market, competitive, portfolio, and acquisition signal universe.",
        },
        {
            "id": "technology_breakthroughs",
            "name": "Technology Breakthroughs",
            "status": "registered",
            "governance": "operator_review_required",
            "description": "Technology, invention, design, and buildability signal universe.",
        },
        {
            "id": "existing_systems",
            "name": "Existing Systems",
            "status": "registered",
            "governance": "operator_review_required",
            "description": "Existing-system replacement and superior-system discovery universe.",
        },
        {
            "id": "acquisition_targets",
            "name": "Acquisition Targets",
            "status": "registered",
            "governance": "operator_review_required",
            "description": "Acquirer fit, packaging, and acquisition-route universe.",
        },
    ]

    return {
        "universes": default_universes,
        "total": len(default_universes),
        "truth_owner": "backend",
        "source": "compat_default_registry",
        "note": "Registry is available as default governed universe metadata; no candidates are fabricated.",
    }


@router.get("/dashboard/payload")
async def authored_dashboard_payload() -> Dict[str, Any]:
    continuous = _continuous_status()
    review_payload = _review_queue_payload()
    review_queue = review_payload.get("review_queue", [])
    if not isinstance(review_queue, list):
        review_queue = []

    counts = _candidate_counts(review_queue)
    latest_run = _latest_manual_run()

    return {
        "status": "available",
        "truth_owner": "backend",
        "build": "v19.82B.16",
        "selected_route": "pending_evidence",
        "terminal_state": "runtime_available_waiting_for_candidates",
        "latest_run": latest_run,
        "continuous_runtime": continuous,
        "review_queue": review_queue,
        "candidate_counts": counts,
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
        "updated_at": _utc_now(),
    }


@router.get("/runtime/continuous/status")
async def authored_continuous_status() -> Dict[str, Any]:
    return _continuous_status()


@router.post("/runtime/continuous/start")
async def authored_continuous_start() -> Dict[str, Any]:
    existing = _continuous_status()
    payload = {
        **existing,
        "status": "available_waiting",
        "runtime_state": "requested_start",
        "message": "Continuous runtime start request recorded. Deeper executor activation remains governed by runtime implementation.",
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "updated_at": _utc_now(),
    }
    _write_json(_continuous_dir() / "status.json", payload)
    return payload


@router.post("/runtime/continuous/pause")
async def authored_continuous_pause() -> Dict[str, Any]:
    existing = _continuous_status()
    payload = {
        **existing,
        "status": "available_paused",
        "runtime_state": "pause_requested",
        "message": "Continuous runtime pause request recorded.",
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "updated_at": _utc_now(),
    }
    _write_json(_continuous_dir() / "status.json", payload)
    return payload


@router.get("/runtime/continuous/review-queue")
async def authored_review_queue() -> Dict[str, Any]:
    return _review_queue_payload()


@router.get("/universes")
async def authored_universes() -> Dict[str, Any]:
    return _universes_payload()


@router.post("/runs/start")
async def authored_start_run() -> Dict[str, Any]:
    run_id = "manual_run_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    payload = {
        "status": "manual_run_requested",
        "run_id": run_id,
        "message": "Manual run request recorded for cockpit availability. Full lifecycle executor remains backend-owned.",
        "truth_owner": "backend",
        "candidate_generation": "not_fabricated",
        "created_at": _utc_now(),
    }
    run_dir = _runs_dir() / run_id
    _write_json(run_dir / "status.json", payload)
    _write_json(run_dir / "run_manifest.json", payload)
    return payload
