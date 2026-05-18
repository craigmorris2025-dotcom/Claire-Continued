from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter


router = APIRouter(tags=["Claire Continuous Intelligence Runtime"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

CONTINUOUS_DIR = PROJECT_ROOT / "data" / "continuous_runtime"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def read_json(path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def default_status() -> Dict[str, Any]:
    return {
        "runtime": "continuous_intelligence",
        "status": "configured_not_running",
        "mode": "governed_24_7_discovery_monitoring",
        "backend_owns_truth": True,
        "operator_approval_required": True,
        "continuous_objectives": [
            "discover emerging trends",
            "detect gaps",
            "identify breakthrough candidates",
            "identify needed solutions",
            "identify technological solution candidates",
            "identify portfolio opportunities",
            "identify acquisition/package candidates",
            "store lifecycle memory",
            "support recursive self-ingestion",
        ],
        "guardrails": [
            "no uncontrolled web mutation",
            "no automatic active-code updates",
            "no frontend-owned route truth",
            "no fake discoveries",
            "missing evidence enriches before failure",
            "operator review required before promotion",
        ],
        "last_cycle_id": None,
        "last_cycle_at": None,
        "next_cycle_policy": "operator_or_scheduler_triggered",
        "artifact_paths": {
            "status": "data/continuous_runtime/status.json",
            "review_queue": "data/continuous_runtime/review_queue.json",
            "discovery_candidates": "data/continuous_runtime/discovery_candidates.json",
            "breakthrough_candidates": "data/continuous_runtime/breakthrough_candidates.json",
            "portfolio_candidates": "data/continuous_runtime/portfolio_candidates.json",
            "design_candidates": "data/continuous_runtime/design_candidates.json",
        },
        "updated_at": utc_now(),
    }


def ensure_runtime_files() -> Dict[str, Any]:
    status_path = CONTINUOUS_DIR / "status.json"
    status = read_json(status_path, default_status())
    status.setdefault("updated_at", utc_now())
    write_json(status_path, status)

    empty_sets = {
        "review_queue.json": {"items": [], "policy": "operator_review_required_before_promotion"},
        "discovery_candidates.json": {"items": [], "candidate_type": "discovery"},
        "breakthrough_candidates.json": {"items": [], "candidate_type": "breakthrough"},
        "portfolio_candidates.json": {"items": [], "candidate_type": "portfolio"},
        "design_candidates.json": {"items": [], "candidate_type": "design"},
    }
    for filename, payload in empty_sets.items():
        path = CONTINUOUS_DIR / filename
        if not path.exists():
            payload = dict(payload)
            payload["updated_at"] = utc_now()
            write_json(path, payload)
    return status


def create_cycle_payload(trigger: str = "operator") -> Dict[str, Any]:
    ensure_runtime_files()
    cycle_id = "cycle_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    now = utc_now()

    cycle = {
        "cycle_id": cycle_id,
        "created_at": now,
        "trigger": trigger,
        "status": "recorded",
        "purpose": "continuous intelligence monitoring cycle placeholder",
        "result": "cycle_artifact_created_waiting_for_source_universe_and_governed_probe",
        "candidate_counts": {
            "discoveries": 0,
            "breakthroughs": 0,
            "portfolios": 0,
            "designs": 0,
            "packages": 0,
        },
        "missing_evidence": [
            "source universe selection",
            "governed source probe results",
            "validated signal set",
        ],
        "rule": "continuous runtime records truthful state only; it does not fabricate discoveries",
    }

    cycle_path = CONTINUOUS_DIR / "cycles" / f"{cycle_id}.json"
    write_json(cycle_path, cycle)

    status = read_json(CONTINUOUS_DIR / "status.json", default_status())
    status["status"] = "active"
    status["last_cycle_id"] = cycle_id
    status["last_cycle_at"] = now
    status["updated_at"] = now
    write_json(CONTINUOUS_DIR / "status.json", status)

    review_queue = read_json(CONTINUOUS_DIR / "review_queue.json", {"items": []})
    review_queue.setdefault("items", []).append({
        "id": cycle_id,
        "type": "continuous_cycle",
        "status": "awaiting_sources",
        "created_at": now,
        "summary": "Continuous intelligence cycle created; waiting for source universe and governed probe results.",
        "artifact": f"data/continuous_runtime/cycles/{cycle_id}.json",
    })
    review_queue["updated_at"] = now
    write_json(CONTINUOUS_DIR / "review_queue.json", review_queue)

    return {
        "status": "continuous_cycle_created",
        "continuous_runtime": status,
        "cycle": cycle,
        "review_queue": review_queue,
        "backend_owns_truth": True,
    }


@router.get("/runtime/continuous/status")
async def continuous_status() -> Dict[str, Any]:
    return ensure_runtime_files()


@router.post("/runtime/continuous/start")
async def continuous_start(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    trigger = "operator"
    if payload and isinstance(payload, dict):
        trigger = str(payload.get("trigger", "operator"))
    return create_cycle_payload(trigger=trigger)


@router.post("/runtime/continuous/pause")
async def continuous_pause() -> Dict[str, Any]:
    status = ensure_runtime_files()
    status["status"] = "paused"
    status["updated_at"] = utc_now()
    write_json(CONTINUOUS_DIR / "status.json", status)
    return status


@router.get("/runtime/continuous/cycles")
async def continuous_cycles() -> Dict[str, Any]:
    ensure_runtime_files()
    cycle_dir = CONTINUOUS_DIR / "cycles"
    cycles = []
    if cycle_dir.exists():
        for path in sorted(cycle_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            cycles.append(read_json(path, {"cycle_id": path.stem}))
    return {"status": "ok", "cycles": cycles}


@router.get("/runtime/continuous/review-queue")
async def continuous_review_queue() -> Dict[str, Any]:
    ensure_runtime_files()
    return read_json(CONTINUOUS_DIR / "review_queue.json", {"items": []})
