from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter


router = APIRouter(tags=["Claire Enterprise Runs"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

RUNS_DIR = PROJECT_ROOT / "data" / "runs"


CANONICAL_STAGES = [
    "Signal Ingestion",
    "Signal Normalization",
    "Source Validation & Weighting",
    "Context Expansion",
    "Signal Consolidation",
    "Entity Extraction",
    "Relationship Mapping",
    "Trend Discovery",
    "Cluster Formation",
    "Insight / Thesis Structuring",
    "Gap Detection",
    "Gap Qualification",
    "Discovery Generation",
    "Breakthrough Identification & Classification",
    "Advancement Path Selection",
    "Auto Invention / Solution Generation",
    "Solution Structuring",
    "Buildability Assessment",
    "Viability Assessment",
    "Manufacturability / Deployability Assessment",
    "Feasibility Validation",
    "Design Portal Output / Blueprints / Specs",
    "Market Positioning",
    "Moat & Differentiation",
    "Business Model & Value Capture",
    "Competitor Analysis",
    "Portfolio Creation / Optimization",
    "Acquirer Identification",
    "Acquisition Fit & Rationale",
    "Final Package Construction",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_dir(run_id: str) -> Path:
    return RUNS_DIR / run_id


def write_json(path: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def read_json(path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def latest_run_id() -> str | None:
    if not RUNS_DIR.exists():
        return None
    manifests = sorted(RUNS_DIR.glob("*/run_manifest.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not manifests:
        return None
    return manifests[0].parent.name


def build_lifecycle(run_id: str) -> Dict[str, Any]:
    stages = []
    for index, name in enumerate(CANONICAL_STAGES, start=1):
        if index == 1:
            status = "initialized"
            reason = "Run accepted by enterprise cockpit start action."
        elif index in (2, 3, 4, 5):
            status = "waiting"
            reason = "Awaiting source universe and governed enrichment inputs."
        else:
            status = "not_started"
            reason = "Stage is preserved in canonical lifecycle and awaits runtime execution."
        stages.append({
            "stage_number": index,
            "stage_name": name,
            "status": status,
            "reason": reason,
        })
    return {
        "run_id": run_id,
        "generated_at": utc_now(),
        "stage_count": len(stages),
        "stages": stages,
        "protected_design_stages": {
            "16": "Auto Invention / Solution Generation",
            "17": "Solution Structuring",
            "18": "Buildability Assessment",
            "19": "Viability Assessment",
            "20": "Manufacturability / Deployability Assessment",
            "21": "Feasibility Validation",
            "22": "Design Portal Output / Blueprints / Specs",
        },
    }


def create_run_payload(request_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    run_id = "run_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    path = run_dir(run_id)
    now = utc_now()
    request_payload = request_payload or {}

    manifest = {
        "run_id": run_id,
        "created_at": now,
        "source": request_payload.get("source", "enterprise_cockpit"),
        "mode": request_payload.get("mode", "discovery_first"),
        "requested_by": request_payload.get("requested_by", "operator"),
        "contract": "endpoint_artifact_payload_cockpit_pytest",
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "artifact_paths": {
            "manifest": f"data/runs/{run_id}/run_manifest.json",
            "status": f"data/runs/{run_id}/status.json",
            "lifecycle": f"data/runs/{run_id}/lifecycle_state.json",
            "gates": f"data/runs/{run_id}/gate_decisions.json",
            "missing_evidence": f"data/runs/{run_id}/missing_evidence.json",
            "enrichment": f"data/runs/{run_id}/enrichment_log.json",
        },
    }

    status = {
        "run_id": run_id,
        "created_at": now,
        "updated_at": now,
        "status": "accepted",
        "terminal_state": "runtime_initialized",
        "selected_route": "pending_evidence",
        "route": "discovery_first",
        "message": "Run initialized. Awaiting source universe, evidence, and lifecycle execution.",
    }

    lifecycle = build_lifecycle(run_id)

    gates = {
        "run_id": run_id,
        "generated_at": now,
        "gate_decisions": [
            {
                "gate": "runtime_start",
                "status": "pass",
                "reason": "Operator requested run through enterprise cockpit.",
                "evidence_refs": [manifest["artifact_paths"]["manifest"]],
                "route_effect": "initialize_discovery_first_runtime",
            },
            {
                "gate": "source_universe",
                "status": "waiting",
                "reason": "No source universe selected yet.",
                "evidence_refs": [],
                "route_effect": "hold_before_signal_governance",
            },
        ],
    }

    missing = {
        "run_id": run_id,
        "generated_at": now,
        "missing_evidence": [
            {
                "id": "source_universe_required",
                "severity": "required",
                "reason": "A source universe is required before signal governance can proceed.",
                "suggested_action": "Select or create a governed source universe.",
            },
            {
                "id": "initial_signal_set_required",
                "severity": "required",
                "reason": "Initial signals are required before trend discovery can run.",
                "suggested_action": "Run governed source probe or provide input signals.",
            },
        ],
        "policy": "missing_evidence_enrichment_before_failure",
    }

    enrichment = {
        "run_id": run_id,
        "generated_at": now,
        "enrichment_log": [],
        "status": "not_started",
        "policy": "operator_review_required_for_source_expansion",
    }

    write_json(path / "run_manifest.json", manifest)
    write_json(path / "status.json", status)
    write_json(path / "lifecycle_state.json", lifecycle)
    write_json(path / "gate_decisions.json", gates)
    write_json(path / "missing_evidence.json", missing)
    write_json(path / "enrichment_log.json", enrichment)

    return {
        "status": "run_started",
        "run_id": run_id,
        "active_run_id": run_id,
        "terminal_state": status["terminal_state"],
        "selected_route": status["selected_route"],
        "route": status["route"],
        "runtime": status,
        "run": manifest,
        "lifecycle": lifecycle,
        "gates": gates,
        "missing_evidence": missing,
        "enrichment": enrichment,
        "artifacts": manifest["artifact_paths"],
        "backend_owns_truth": True,
    }


@router.post("/runs/start")
async def start_run(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return create_run_payload(payload)


@router.get("/runs/latest")
async def get_latest_run() -> Dict[str, Any]:
    run_id = latest_run_id()
    if not run_id:
        return {"status": "no_runs", "active_run_id": None}
    status = read_json(run_dir(run_id) / "status.json", {})
    return {"status": "latest_run_found", "active_run_id": run_id, "runtime": status}


@router.get("/runs/{run_id}/status")
async def get_run_status(run_id: str) -> Dict[str, Any]:
    return read_json(run_dir(run_id) / "status.json", {"status": "missing", "run_id": run_id})


@router.get("/runs/{run_id}/lifecycle")
async def get_run_lifecycle(run_id: str) -> Dict[str, Any]:
    return read_json(run_dir(run_id) / "lifecycle_state.json", {"status": "missing", "run_id": run_id})


@router.get("/runs/{run_id}/gates")
async def get_run_gates(run_id: str) -> Dict[str, Any]:
    return read_json(run_dir(run_id) / "gate_decisions.json", {"status": "missing", "run_id": run_id})


@router.get("/runs/{run_id}/missing-evidence")
async def get_run_missing_evidence(run_id: str) -> Dict[str, Any]:
    return read_json(run_dir(run_id) / "missing_evidence.json", {"status": "missing", "run_id": run_id})


@router.post("/runs/{run_id}/enrich")
async def enrich_run(run_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    path = run_dir(run_id) / "enrichment_log.json"
    existing = read_json(path, {"run_id": run_id, "enrichment_log": [], "status": "not_started"})
    event = {
        "timestamp": utc_now(),
        "status": "requested",
        "payload": payload or {},
        "result": "enrichment_request_recorded",
        "rule": "no_uncontrolled_web_mutation",
    }
    existing.setdefault("enrichment_log", []).append(event)
    existing["status"] = "requested"
    write_json(path, existing)
    return existing
