from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter


router = APIRouter(tags=["Claire Enterprise Cockpit Payload"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

RUNS_DIR = PROJECT_ROOT / "data" / "runs"
CONTINUOUS_DIR = PROJECT_ROOT / "data" / "continuous_runtime"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def latest_run_id() -> str | None:
    if not RUNS_DIR.exists():
        return None
    manifests = sorted(RUNS_DIR.glob("*/run_manifest.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not manifests:
        return None
    return manifests[0].parent.name


def load_latest_run() -> Dict[str, Any]:
    run_id = latest_run_id()
    if not run_id:
        return {
            "status": "no_active_run",
            "active_run_id": None,
            "runtime": None,
            "lifecycle": None,
            "gates": None,
            "missing_evidence": None,
            "enrichment": None,
            "artifacts": {},
        }

    path = RUNS_DIR / run_id
    manifest = read_json(path / "run_manifest.json", {})
    status = read_json(path / "status.json", {})
    lifecycle = read_json(path / "lifecycle_state.json", {})
    gates = read_json(path / "gate_decisions.json", {})
    missing = read_json(path / "missing_evidence.json", {})
    enrichment = read_json(path / "enrichment_log.json", {})

    return {
        "status": "active_run_loaded",
        "active_run_id": run_id,
        "run_id": run_id,
        "terminal_state": status.get("terminal_state", "runtime_initialized"),
        "selected_route": status.get("selected_route", "pending_evidence"),
        "route": status.get("route", "discovery_first"),
        "runtime": status,
        "run": manifest,
        "lifecycle": lifecycle,
        "gates": gates,
        "missing_evidence": missing,
        "enrichment": enrichment,
        "artifacts": manifest.get("artifact_paths", {}),
    }


def load_continuous_runtime() -> Dict[str, Any]:
    status = read_json(CONTINUOUS_DIR / "status.json", {
        "runtime": "continuous_intelligence",
        "status": "not_configured",
        "last_cycle_id": None,
        "last_cycle_at": None,
    })
    review_queue = read_json(CONTINUOUS_DIR / "review_queue.json", {"items": []})
    discovery = read_json(CONTINUOUS_DIR / "discovery_candidates.json", {"items": []})
    breakthrough = read_json(CONTINUOUS_DIR / "breakthrough_candidates.json", {"items": []})
    portfolio = read_json(CONTINUOUS_DIR / "portfolio_candidates.json", {"items": []})
    design = read_json(CONTINUOUS_DIR / "design_candidates.json", {"items": []})

    return {
        "status": status.get("status", "not_configured"),
        "runtime": status,
        "review_queue": review_queue,
        "candidate_sets": {
            "discovery": discovery,
            "breakthrough": breakthrough,
            "portfolio": portfolio,
            "design": design,
        },
        "candidate_counts": {
            "discoveries": len(discovery.get("items", [])),
            "breakthroughs": len(breakthrough.get("items", [])),
            "portfolios": len(portfolio.get("items", [])),
            "designs": len(design.get("items", [])),
            "packages": 0,
        },
    }


def build_operator_summary(run: Dict[str, Any], continuous: Dict[str, Any]) -> Dict[str, Any]:
    review_count = len(continuous.get("review_queue", {}).get("items", []))
    candidate_counts = continuous.get("candidate_counts", {})

    return {
        "headline": "Claire Enterprise Intelligence Cockpit",
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "active_run_id": run.get("active_run_id"),
        "manual_run_state": run.get("terminal_state") or run.get("status"),
        "selected_route": run.get("selected_route", "pending_evidence"),
        "route": run.get("route", "discovery_first"),
        "continuous_runtime_status": continuous.get("status", "not_configured"),
        "review_queue_count": review_count,
        "candidate_counts": candidate_counts,
        "operator_message": (
            "Continuous runtime and manual runs are separate. "
            "The cockpit displays backend truth only and does not fabricate outputs."
        ),
    }


def build_payload() -> Dict[str, Any]:
    run = load_latest_run()
    continuous = load_continuous_runtime()
    summary = build_operator_summary(run, continuous)

    return {
        "version": "v19.82B.8",
        "generated_at": utc_now(),
        "status": "ok",
        "payload_status": "operator_payload_online",
        "source": "enterprise_cockpit_payload_bridge",
        "operator_summary": summary,
        "active_run_id": run.get("active_run_id"),
        "run_id": run.get("run_id"),
        "terminal_state": run.get("terminal_state"),
        "selected_route": run.get("selected_route"),
        "route": run.get("route"),
        "runtime": run.get("runtime"),
        "run": run.get("run"),
        "lifecycle": run.get("lifecycle"),
        "gates": run.get("gates"),
        "missing_evidence": run.get("missing_evidence"),
        "enrichment": run.get("enrichment"),
        "artifacts": run.get("artifacts"),
        "continuous_runtime": continuous.get("runtime"),
        "review_queue": continuous.get("review_queue"),
        "candidate_sets": continuous.get("candidate_sets"),
        "candidate_counts": continuous.get("candidate_counts"),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
    }


@router.get("/api/cockpit/enterprise-payload")
async def dashboard_payload() -> Dict[str, Any]:
    return build_payload()


@router.get("/api/cockpit/enterprise-payload/status")
async def dashboard_payload_status() -> Dict[str, Any]:
    run = load_latest_run()
    continuous = load_continuous_runtime()
    return {
        "status": "ok",
        "payload_status": "operator_payload_online",
        "generated_at": utc_now(),
        "active_run_id": run.get("active_run_id"),
        "continuous_runtime_status": continuous.get("status"),
        "review_queue_count": len(continuous.get("review_queue", {}).get("items", [])),
        "backend_owns_truth": True,
    }
