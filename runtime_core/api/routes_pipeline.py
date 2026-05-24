from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any, Dict
import uuid
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator
from runtime_core.domain.contract import ClaireIntent
from runtime_core.memory.store import Store
from runtime_core.memory.lifecycle_memory_signal import build_lifecycle_memory_sources
from runtime_core.ingestion.source_boundary import filter_sources
from runtime_core.validation.evidence_collector import EvidenceCollector
from runtime_core.validation.proof_binder import ProofBinder
from runtime_core.validation.run_quality_gate import evaluate_run_quality
from runtime_core.ingestion.live_ingestion_adapter import build_source_provenance

router = APIRouter(tags=["pipeline"])

orchestrator = PipelineOrchestrator()
memory_store = Store()
evidence_collector = EvidenceCollector()
proof_binder = ProofBinder()


class EvaluateRequest(BaseModel):
    raw_input: str
    mode: Optional[str] = "deterministic"
    source_mode: Optional[str] = "simulated_live_packet"
    sources: Optional[Dict[str, Any]] = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_to_dict(result: Any) -> Dict[str, Any]:
    if result is None:
        return {"status": "error", "message": "orchestrator returned no result"}

    if hasattr(result, "to_dict") and callable(result.to_dict):
        return result.to_dict()

    if isinstance(result, dict):
        return result

    return {"status": "success", "result": result}


def _request_payload(req: EvaluateRequest) -> Dict[str, Any]:
    return {
        "raw_input": req.raw_input,
        "mode": req.mode,
        "source_mode": req.source_mode,
        "sources": req.sources or {},
    }


def _attach_run_id_to_intent(intent: Any, run_id: str) -> None:
    try:
        setattr(intent, "run_id", run_id)
    except Exception:
        pass

    try:
        if not hasattr(intent, "metadata") or intent.metadata is None:
            setattr(intent, "metadata", {})
        if isinstance(intent.metadata, dict):
            intent.metadata["run_id"] = run_id
            intent.metadata["created_at"] = _utc_now_iso()
    except Exception:
        pass

    try:
        if not hasattr(intent, "context") or intent.context is None:
            setattr(intent, "context", {})
        if isinstance(intent.context, dict):
            intent.context["run_id"] = run_id
    except Exception:
        pass


def _force_run_id_into_response(response: Dict[str, Any], run_id: str, intent_id: str) -> Dict[str, Any]:
    if not isinstance(response, dict):
        response = {"status": "success", "result": response}

    if not response.get("run_id") or response.get("run_id") == "unknown":
        response["run_id"] = run_id

    response.setdefault("intent_id", intent_id)
    response.setdefault("executed_at", _utc_now_iso())

    response.setdefault("runtime_trace", {})
    if isinstance(response["runtime_trace"], dict):
        response["runtime_trace"].setdefault("run_id_source", "api_route")
        response["runtime_trace"].setdefault("intent_id", intent_id)
        response["runtime_trace"].setdefault(
            "orchestrator_file",
            inspect.getfile(PipelineOrchestrator),
        )

    return response


def _infer_route_selected(response: Dict[str, Any]) -> str:
    if response.get("breakthrough_synthesis"):
        return "breakthrough_to_acquisition_package"

    if response.get("opportunity_discovery"):
        return "opportunity_discovery_pipeline"

    if response.get("trend_discovery"):
        return "trend_discovery_pipeline"

    return "full_lifecycle_pipeline"


def _infer_terminal_state(response: Dict[str, Any]) -> str:
    if response.get("proof_package"):
        return "proof_package_ready"

    if response.get("acquirer_matches"):
        return "acquisition_targeting_ready"

    if response.get("productization_path"):
        return "productization_path_ready"

    if response.get("technical_feasibility"):
        return "technical_feasibility_ready"

    if response.get("breakthrough_synthesis"):
        return "breakthrough_package_ready"

    if response.get("opportunity_discovery"):
        return "opportunity_ready"

    if response.get("thesis_formation"):
        return "thesis_ready"

    if response.get("trend_discovery"):
        return "trend_discovery_ready"

    if response.get("signal_extraction"):
        return "signal_extraction_ready"

    return "pipeline_output_ready"


def _attach_source_provenance(response: Dict[str, Any], req: EvaluateRequest, sources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = _request_payload(req)
    if sources is not None:
        payload["sources"] = sources

    response["source_provenance"] = build_source_provenance(
        raw_payload=payload,
        source_mode=req.source_mode,
    )

    return response


def _attach_runtime_proof(response: Dict[str, Any]) -> Dict[str, Any]:
    core_output = response.get("core_output") if isinstance(response.get("core_output"), dict) else {}
    core_route = core_output.get("route_selected")
    if core_route and not response.get("route_selected"):
        response["route_selected"] = core_route
    if response.get("proof_package") and not response.get("terminal_state"):
        response["terminal_state"] = "proof_package_ready"
    source_authority = response.get("source_authority") if isinstance(response.get("source_authority"), dict) else {}
    live_ingestion_ready = bool(source_authority.get("live_evidence_present"))
    response["runtime_proof"] = {
        "pipeline_executed": response.get("status") in {"success", "ok"},
        "route_selected": response.get("route_selected") or _infer_route_selected(response),
        "terminal_state": response.get("terminal_state") or _infer_terminal_state(response),
        "live_ingestion_ready": live_ingestion_ready,
        "proof_phase_ready": True,
        "full_lifecycle_output": True,
        "runtime_wrapper_version": "v6.1.0",
    }

    return response


def _attach_run_quality(response: Dict[str, Any]) -> Dict[str, Any]:
    response["run_quality"] = evaluate_run_quality(response)
    core_output = response.get("core_output")
    if isinstance(core_output, dict):
        core_output["source_authority"] = response.get("source_authority", {})
        core_output["run_quality"] = response["run_quality"]
    return response


def _attach_validation(response: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    try:
        validation_output = evidence_collector.collect(response, run_id=run_id)

        response["validation"] = {
            "status": validation_output.get("status"),
            "confidence": validation_output.get("confidence"),
            "evidence_count": validation_output.get("payload", {}).get("evidence_count"),
            "evidence_strength": validation_output.get("payload", {}).get("evidence_strength"),
            "validation_ready": validation_output.get("payload", {}).get("validation_ready"),
            "audit_ready": validation_output.get("payload", {}).get("audit_ready"),
            "missing_sections": validation_output.get("payload", {}).get("missing_sections", []),
            "timestamp": validation_output.get("timestamp"),
        }

        response["evidence_chain"] = validation_output.get("evidence", [])

    except Exception as exc:
        response["validation"] = {
            "status": "failed",
            "error": str(exc),
            "timestamp": _utc_now_iso(),
        }

    return response


def _attach_proof_binder(response: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    try:
        binder_output = proof_binder.bind(
            result=response,
            validation=response.get("validation"),
            evidence_chain=response.get("evidence_chain"),
            run_id=run_id,
        )

        response["proof"] = {
            "status": binder_output.get("status"),
            "confidence": binder_output.get("confidence"),
            "audit_ready": binder_output.get("payload", {}).get("audit_ready"),
            "validation_ready": binder_output.get("payload", {}).get("validation_ready"),
            "proof_confidence": binder_output.get("payload", {}).get("proof_confidence"),
            "summary": binder_output.get("payload", {}).get("summary"),
        }

        response["proof_package"] = binder_output.get("payload")

    except Exception as exc:
        response["proof"] = {
            "status": "failed",
            "error": str(exc),
            "timestamp": _utc_now_iso(),
        }

    return response


def _sources_with_lifecycle_memory(req: EvaluateRequest) -> tuple[Dict[str, Any], Dict[str, Any]]:
    provided_sources, source_boundary = filter_sources(req.sources if isinstance(req.sources, dict) else {})
    recursive_sources = build_lifecycle_memory_sources(
        store=memory_store,
        current_raw_input=req.raw_input,
        provided_sources=provided_sources,
    )
    sources = {
        **recursive_sources,
        **provided_sources,
    }
    metadata = {
        "status": "attached" if recursive_sources else "not_attached",
        "source_keys": sorted(recursive_sources.keys()),
        "stage_1_ingestion": bool(recursive_sources),
        "live_truth": False,
        "promotion_requires_fresh_validation": bool(recursive_sources),
        "source_boundary": source_boundary,
    }
    if not recursive_sources:
        metadata["reason"] = "no_verified_memory_feedback_sources"
    return sources, metadata


def _persist_run(response: Dict[str, Any], run_id: str, intent_id: str, raw_input: str, mode: str) -> Dict[str, Any]:
    try:
        quality = response.get("run_quality") if isinstance(response.get("run_quality"), dict) else {}
        if quality.get("memory_feedback_eligible") is False:
            response["memory"] = {
                "status": "skipped",
                "reason": "run_quality_gate_blocked_memory_feedback",
                "run_quality_status": quality.get("status"),
            }
            _persist_dashboard_run_state(response, run_id, intent_id, raw_input, mode)
            return response

        memory_result = memory_store.save_run(
            run_id=run_id,
            result=response,
            intent_id=intent_id,
            raw_input=raw_input,
            mode=mode,
        )

        response["memory"] = {
            "status": "stored",
            "memory_path": memory_result.get("memory_path"),
            "stored_at": memory_result.get("stored_at"),
        }

    except Exception as exc:
        response["memory"] = {
            "status": "failed",
            "error": str(exc),
        }

    _persist_dashboard_run_state(response, run_id, intent_id, raw_input, mode)
    return response


def _persist_dashboard_run_state(response: Dict[str, Any], run_id: str, intent_id: str, raw_input: str, mode: str) -> None:
    run_dir = Path("data") / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    lifecycle = response.get("core_lifecycle") if isinstance(response.get("core_lifecycle"), dict) else {}
    core_output = response.get("core_output") if isinstance(response.get("core_output"), dict) else {}
    export_package = response.get("export_package") if isinstance(response.get("export_package"), dict) else {}
    lifecycle_state = {
        "run_id": run_id,
        "intent_id": intent_id,
        "raw_input": raw_input,
        "mode": mode,
        "status": response.get("status"),
        "route_selected": lifecycle.get("route") or response.get("route_selected"),
        "presentation_route_selected": response.get("route_selected"),
        "terminal_state": response.get("terminal_state"),
        "stage_count": lifecycle.get("stage_count", 0),
        "summary": lifecycle.get("summary", {}),
        "completion_gate": lifecycle.get("completion_gate", {}),
        "stages": lifecycle.get("stages", []),
        "generated_at": _utc_now_iso(),
    }
    artifacts = {
        "lifecycle_state.json": lifecycle_state,
        "core_output.json": core_output,
        "export_package.json": export_package,
        "run_summary.json": {
            "run_id": run_id,
            "intent_id": intent_id,
            "status": response.get("status"),
            "route_selected": lifecycle.get("route") or response.get("route_selected"),
            "presentation_route_selected": response.get("route_selected"),
            "terminal_state": response.get("terminal_state"),
            "memory": response.get("memory", {}),
            "runtime_proof": response.get("runtime_proof", {}),
            "core_completion_gate": response.get("core_completion_gate", {}),
        },
    }
    for filename, payload in artifacts.items():
        (run_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


async def _evaluate_impl(req: EvaluateRequest):
    if not req.raw_input or len(req.raw_input.strip()) < 5:
        return {"status": "error", "message": "raw_input is empty or too short"}

    clean_input = req.raw_input.strip()
    mode = req.mode or "deterministic"
    sources, lifecycle_memory_feedback = _sources_with_lifecycle_memory(req)

    run_id = f"run-{uuid.uuid4().hex[:12]}"
    intent_id = f"intent-{uuid.uuid4().hex[:8]}"

    intent = ClaireIntent(
        intent_id=intent_id,
        raw_input=clean_input,
        mode=mode,
        sources=sources,
        source_mode=req.source_mode,
    )

    _attach_run_id_to_intent(intent, run_id)

    print(">>> RUN ID:", run_id)
    print(">>> INTENT ID:", intent_id)
    print(">>> INPUT RECEIVED:", clean_input)
    print(">>> ORCHESTRATOR FILE:", inspect.getfile(PipelineOrchestrator))

    try:
        result = orchestrator.execute(intent)

        response = _safe_to_dict(result)
        response = _force_run_id_into_response(response, run_id, intent_id)
        response["lifecycle_memory_feedback"] = lifecycle_memory_feedback

        # v6.1.0 additions
        response = _attach_source_provenance(response, req, sources=sources)
        response = _attach_runtime_proof(response)
        response = _attach_run_quality(response)

        # ORDER MATTERS
        response = _attach_validation(response, run_id)
        response = _attach_proof_binder(response, run_id)

        # Refresh runtime proof after proof package exists
        response = _attach_runtime_proof(response)
        response = _attach_run_quality(response)

        response = _persist_run(response, run_id, intent_id, clean_input, mode)

        return response

    except Exception as exc:
        error_response = {
            "run_id": run_id,
            "intent_id": intent_id,
            "status": "error",
            "message": "pipeline execution failed",
            "error": str(exc),
            "executed_at": _utc_now_iso(),
            "lifecycle_memory_feedback": lifecycle_memory_feedback,
        }

        error_response = _attach_source_provenance(error_response, req, sources=sources)
        error_response = _attach_runtime_proof(error_response)
        error_response = _attach_run_quality(error_response)
        error_response = _attach_validation(error_response, run_id)
        error_response = _attach_proof_binder(error_response, run_id)
        error_response = _persist_run(error_response, run_id, intent_id, clean_input, mode)

        return error_response


@router.post("/pipeline/evaluate")
async def evaluate(req: EvaluateRequest):
    return await _evaluate_impl(req)


@router.post("/evaluate")
async def evaluate_alias(req: EvaluateRequest):
    return await _evaluate_impl(req)
