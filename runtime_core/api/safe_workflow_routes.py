from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/workflow", tags=["safe-workflow"])

AUTHORITY_LOCKS: Dict[str, Any] = {
    "runtime_truth_write_allowed": False,
    "runtime_mutation_allowed": False,
    "automatic_updates_allowed": False,
    "autonomous_execution_allowed": False,
    "continuous_crawling_allowed": False,
    "workflow_actions_mode": "proposal_only",
}

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "pytest.ini").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

RUNTIME_DIR = PROJECT_ROOT / "runtime" / "safe_workflow"
EXPORT_DIR = PROJECT_ROOT / "exports" / "safe_workflow"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

REVIEW_QUEUE_PATH = RUNTIME_DIR / "review_queue.json"
BOUNDED_JOBS_PATH = RUNTIME_DIR / "bounded_jobs.json"
AUDIT_TRAIL_PATH = RUNTIME_DIR / "audit_trail.json"
EXPORT_INDEX_PATH = EXPORT_DIR / "export_index.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _audit(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    event = {
        "event_type": event_type,
        "timestamp": _now(),
        "proposal_only": True,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "payload": payload,
    }
    trail = _read_json(AUDIT_TRAIL_PATH, [])
    if not isinstance(trail, list):
        trail = []
    trail.append(event)
    _write_json(AUDIT_TRAIL_PATH, trail[-250:])
    return event


class ReviewDecisionRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    decision: str = Field(..., pattern="^(approve|reject|hold|needs_more_evidence)$")
    reason: str = ""


class BoundedJobRequest(BaseModel):
    job_type: str = Field(..., min_length=1)
    scope: str = "operator_requested"
    max_items: int = Field(default=10, ge=1, le=100)
    notes: str = ""


class ExportRequest(BaseModel):
    export_type: str = "review_snapshot"
    include_audit_tail: bool = True


@router.get("/authority-locks")
def get_authority_locks() -> Dict[str, Any]:
    return {"ok": True, "authority_locks": AUTHORITY_LOCKS}


@router.get("/counts")
def get_workflow_counts() -> Dict[str, Any]:
    review_queue = _read_json(REVIEW_QUEUE_PATH, [])
    bounded_jobs = _read_json(BOUNDED_JOBS_PATH, [])
    audit_trail = _read_json(AUDIT_TRAIL_PATH, [])
    export_index = _read_json(EXPORT_INDEX_PATH, [])

    if not isinstance(review_queue, list):
        review_queue = []
    if not isinstance(bounded_jobs, list):
        bounded_jobs = []
    if not isinstance(audit_trail, list):
        audit_trail = []
    if not isinstance(export_index, list):
        export_index = []

    pending_reviews = [x for x in review_queue if isinstance(x, dict) and x.get("state", "pending") == "pending"]
    proposed_jobs = [x for x in bounded_jobs if isinstance(x, dict) and x.get("state", "proposed") == "proposed"]

    return {
        "ok": True,
        "version": "S289-S295",
        "authority_locks": AUTHORITY_LOCKS,
        "counts": {
            "review_queue_total": len(review_queue),
            "review_queue_pending": len(pending_reviews),
            "bounded_jobs_total": len(bounded_jobs),
            "bounded_jobs_proposed": len(proposed_jobs),
            "exports_total": len(export_index),
            "audit_events_total": len(audit_trail),
        },
        "last_refreshed": _now(),
    }


@router.get("/review-queue")
def get_review_queue() -> Dict[str, Any]:
    queue = _read_json(REVIEW_QUEUE_PATH, [])
    if not isinstance(queue, list):
        queue = []
    return {
        "ok": True,
        "proposal_only": True,
        "authority_locks": AUTHORITY_LOCKS,
        "items": queue[-100:],
        "count": len(queue),
    }


@router.post("/review-decision")
def propose_review_decision(request: ReviewDecisionRequest) -> Dict[str, Any]:
    event = _audit("review_decision_proposed", request.model_dump())
    return {
        "ok": True,
        "state": "proposal_recorded",
        "proposal_only": True,
        "runtime_truth_modified": False,
        "authority_locks": AUTHORITY_LOCKS,
        "event": event,
    }


@router.post("/bounded-job")
def propose_bounded_job(request: BoundedJobRequest) -> Dict[str, Any]:
    jobs = _read_json(BOUNDED_JOBS_PATH, [])
    if not isinstance(jobs, list):
        jobs = []
    job = {
        "job_id": f"bounded_job_{len(jobs) + 1}",
        "state": "proposed",
        "proposal_only": True,
        "created_at": _now(),
        "request": request.model_dump(),
        "authority_locks": AUTHORITY_LOCKS,
    }
    jobs.append(job)
    _write_json(BOUNDED_JOBS_PATH, jobs[-250:])
    _audit("bounded_job_proposed", job)
    return {
        "ok": True,
        "state": "job_proposal_recorded",
        "job": job,
        "runtime_mutation_started": False,
        "autonomous_execution_started": False,
    }


@router.post("/export")
def write_export_artifact(request: ExportRequest) -> Dict[str, Any]:
    counts = get_workflow_counts()
    audit_tail = _read_json(AUDIT_TRAIL_PATH, [])
    if not isinstance(audit_tail, list):
        audit_tail = []
    artifact = {
        "export_type": request.export_type,
        "created_at": _now(),
        "proposal_only": True,
        "authority_locks": AUTHORITY_LOCKS,
        "counts": counts.get("counts", {}),
        "audit_tail": audit_tail[-25:] if request.include_audit_tail else [],
        "runtime_truth_modified": False,
    }
    filename = f"{request.export_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path = EXPORT_DIR / filename
    _write_json(path, artifact)

    index = _read_json(EXPORT_INDEX_PATH, [])
    if not isinstance(index, list):
        index = []
    record = {
        "filename": filename,
        "path": str(path),
        "created_at": artifact["created_at"],
        "export_type": request.export_type,
        "proposal_only": True,
    }
    index.append(record)
    _write_json(EXPORT_INDEX_PATH, index[-250:])
    _audit("export_artifact_written", record)

    return {
        "ok": True,
        "state": "export_artifact_written",
        "artifact": record,
        "runtime_truth_modified": False,
        "authority_locks": AUTHORITY_LOCKS,
    }


@router.get("/monitoring")
def get_monitoring_panel() -> Dict[str, Any]:
    counts = get_workflow_counts()
    return {
        "ok": True,
        "panel": "safe_workflow_monitoring",
        "live_refresh_supported": True,
        "refresh_interval_ms": 15000,
        "authority_locks": AUTHORITY_LOCKS,
        "counts": counts.get("counts", {}),
        "last_refreshed": _now(),
    }
