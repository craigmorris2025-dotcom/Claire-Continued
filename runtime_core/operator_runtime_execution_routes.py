"""
Claire Syntalion v19.89.5
Runtime Execution Contract Surface
Read-only runtime execution truth endpoints.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["Claire Runtime Execution Contract"])

CANONICAL_30_STAGES = [
    "Signal Ingestion",
    "Signal Normalization",
    "Source Validation & Weighting",
    "Context Expansion",
    "Signal Consolidation",
    "Entity Extraction",
    "Relationship Mapping",
    "Trend Discovery",
    "Cluster Formation",
    "Insight/Thesis Structuring",
    "Gap Detection",
    "Gap Qualification",
    "Discovery Generation",
    "Breakthrough Identification & Classification",
    "Advancement Path Selection",
    "Auto Invention/Solution Generation",
    "Solution Structuring",
    "Buildability Assessment",
    "Viability Assessment",
    "Manufacturability/Deployability Assessment",
    "Feasibility Validation",
    "Design Portal Output/Blueprints/Specs",
    "Market Positioning",
    "Moat & Differentiation",
    "Business Model & Value Capture",
    "Competitor Analysis",
    "Portfolio Creation/Optimization",
    "Acquirer Identification",
    "Acquisition Fit & Rationale",
    "Final Package Construction",
]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def _safe_read_json(path: Path) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"read_error": str(exc), "path": str(path)}
    return None

def _candidate_runtime_outputs(root: Path) -> List[Path]:
    return [
        root / "output" / "core_run_output.json",
        root / "outputs" / "core_run_output.json",
        root / "data" / "core_run_output.json",
        root / "runtime" / "core_run_output.json",
        root / "claire" / "runtime" / "core_run_output.json",
    ]

def _normalize_stage(stage: Any, index: int) -> Dict[str, Any]:
    if isinstance(stage, dict):
        return {
            "index": stage.get("index") or stage.get("stage") or index,
            "name": stage.get("name") or stage.get("stage_name") or stage.get("title") or f"Stage {index}",
            "status": stage.get("status") or stage.get("state") or "unknown",
            "reason": stage.get("reason") or stage.get("route_applicability") or stage.get("notes") or "",
            "raw": stage,
        }
    return {"index": index, "name": str(stage), "status": "unknown", "reason": "", "raw": stage}

def _load_runtime_truth() -> Dict[str, Any]:
    root = _project_root()
    selected_path = None
    selected_payload = None
    for path in _candidate_runtime_outputs(root):
        payload = _safe_read_json(path)
        if payload is not None:
            selected_path = path
            selected_payload = payload
            break

    if isinstance(selected_payload, dict):
        raw_stages = selected_payload.get("stages") or selected_payload.get("lifecycle_stages") or []
        stages = [_normalize_stage(stage, i + 1) for i, stage in enumerate(raw_stages)] if isinstance(raw_stages, list) else []
        return {
            "surface": "runtime_execution_contract",
            "version": "v19.89.5",
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_truth_available": True,
            "runtime_truth_source": str(selected_path),
            "terminal_state": selected_payload.get("terminal_state") or selected_payload.get("status") or "unknown",
            "route": selected_payload.get("route") or selected_payload.get("selected_route") or selected_payload.get("runtime_route") or "unknown",
            "confidence": selected_payload.get("confidence") or selected_payload.get("score"),
            "headline": selected_payload.get("headline") or selected_payload.get("title") or "Runtime output loaded",
            "summary": selected_payload.get("summary") or selected_payload.get("description") or "Existing runtime truth file found and exposed read-only.",
            "stage_count": len(stages),
            "stages": stages,
            "raw": selected_payload,
            "checked_at": _utc_now(),
        }

    return {
        "surface": "runtime_execution_contract",
        "version": "v19.89.5",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_available": False,
        "runtime_truth_source": None,
        "terminal_state": "no_runtime_output_loaded",
        "route": "not_started",
        "confidence": None,
        "headline": "Runtime execution contract ready",
        "summary": "No core runtime output file was found in standard output locations. The surface is waiting for runtime output truth.",
        "stage_count": 30,
        "stages": [
            {
                "index": index + 1,
                "name": name,
                "status": "contract_ready",
                "reason": "Stage exists in canonical lifecycle contract; runtime output has not yet supplied execution status.",
            }
            for index, name in enumerate(CANONICAL_30_STAGES)
        ],
        "checked_paths": [str(path) for path in _candidate_runtime_outputs(root)],
        "checked_at": _utc_now(),
    }

@router.get("/system/runtime-execution")
def runtime_execution() -> Dict[str, Any]:
    return _load_runtime_truth()

@router.get("/system/runtime-execution/summary")
def runtime_execution_summary() -> Dict[str, Any]:
    truth = _load_runtime_truth()
    return {
        "surface": truth.get("surface"),
        "version": truth.get("version"),
        "backend_owns_truth": truth.get("backend_owns_truth"),
        "cockpit_presentation_only": truth.get("cockpit_presentation_only"),
        "runtime_truth_available": truth.get("runtime_truth_available"),
        "terminal_state": truth.get("terminal_state"),
        "route": truth.get("route"),
        "confidence": truth.get("confidence"),
        "headline": truth.get("headline"),
        "summary": truth.get("summary"),
        "stage_count": truth.get("stage_count"),
        "checked_at": truth.get("checked_at"),
    }

@router.get("/system/runtime-execution/stages")
def runtime_execution_stages() -> Dict[str, Any]:
    truth = _load_runtime_truth()
    stages = truth.get("stages") or []
    if not isinstance(stages, list):
        stages = []
    return {
        "surface": "runtime_execution_stages",
        "version": "v19.89.5",
        "backend_owns_truth": True,
        "stage_count": len(stages),
        "stages": stages,
        "checked_at": _utc_now(),
    }
