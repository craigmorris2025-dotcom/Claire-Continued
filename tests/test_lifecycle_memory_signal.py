from runtime_core.api import routes_pipeline
from runtime_core.domain.contract import ClaireIntent
import json

from runtime_core.memory import lifecycle_memory_signal
from runtime_core.memory.lifecycle_memory_signal import LifecycleMemorySignalBuilder
from runtime_core.memory.store import Store
from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator


def _valid_result():
    return {
        "run_id": "run-prior",
        "status": "success",
        "domain": "technology",
        "keywords": ["automation", "portfolio", "workflow"],
        "route_selected": "portfolio_creation_optimization",
        "terminal_state": "proof_package_ready",
        "source_authority": {
            "live_truth_eligible": True,
            "live_evidence_present": True,
            "source_evidence_present": True,
            "effective_source_count": 3,
        },
        "run_quality": {
            "status": "valid_run",
            "memory_feedback_eligible": True,
        },
        "user_facing_result": {
            "headline": "workflow automation portfolio signal",
            "summary": "Validated live evidence supports a portfolio intelligence route.",
        },
    }


def _write_curated_lifecycle_memory(root, record):
    path = root / "data" / "continuous_runtime" / "lifecycle_memory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"records": [record]}, indent=2), encoding="utf-8")


def test_lifecycle_memory_signal_builder_outputs_stage_1_source_packet(tmp_path, monkeypatch):
    monkeypatch.setattr(lifecycle_memory_signal, "PROJECT_ROOT", tmp_path)
    store = Store(memory_root=tmp_path / "memory")
    _write_curated_lifecycle_memory(tmp_path, {
        "run_id": "run-prior",
        "status": "success",
        "result": _valid_result(),
        "raw_input": "workflow automation market signal",
    })

    sources = LifecycleMemorySignalBuilder(store=store).build_sources(
        current_raw_input="find adjacent workflow automation opportunities"
    )

    packet = sources["prior_claire_output"]
    assert packet["source_type"] == "internal_verified_memory"
    assert packet["data"]["governance"]["stage_1_use"] == "context_seed_and_pattern_reference"
    assert packet["data"]["governance"]["live_truth"] is False
    assert packet["data"]["source_run_ids"] == ["run-prior"]
    assert "automation" in packet["data"]["keywords"]
    assert packet["signals"][0]["memory_feedback_eligible"] is True


def test_pipeline_route_attaches_verified_memory_sources_without_overwriting_request_sources(tmp_path, monkeypatch):
    store = Store(memory_root=tmp_path / "memory")
    _write_curated_lifecycle_memory(tmp_path, {
        "run_id": "run-prior",
        "status": "success",
        "result": _valid_result(),
        "raw_input": "workflow automation market signal",
    })
    monkeypatch.setattr(lifecycle_memory_signal, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(routes_pipeline, "memory_store", store)

    req = routes_pipeline.EvaluateRequest(
        raw_input="find the next workflow automation opportunity",
        sources={"market": {"source_type": "operator_packet", "signals": ["buyer workflow backlog"]}},
    )

    sources, metadata = routes_pipeline._sources_with_lifecycle_memory(req)

    assert "prior_claire_output" in sources
    assert sources["market"]["source_type"] == "operator_packet"
    assert metadata["status"] == "attached"
    assert metadata["stage_1_ingestion"] is True


def test_recursive_memory_source_is_authoritative_context_not_live_truth():
    orchestrator = PipelineOrchestrator.__new__(PipelineOrchestrator)
    intent = ClaireIntent(
        raw_input="continue portfolio scan",
        source_mode="deterministic",
        sources={"prior_claire_output": {"source_type": "internal_verified_memory"}},
    )

    authority = orchestrator._build_source_authority(
        intent=intent,
        request_sources={"prior_claire_output": {"source_type": "internal_verified_memory"}},
        external={"prior_claire_output": {"source_type": "internal_verified_memory"}},
        source_count=0,
        source_quality_score=0.7,
        coverage_score=0.7,
        evidence_signal_score=0.7,
        market_growth=0.5,
        patent_activity=0.5,
        patent_novelty=0.5,
    )

    assert authority["source_evidence_present"] is True
    assert authority["live_evidence_present"] is False
    assert authority["recursive_memory_source_present"] is True
    assert authority["recursive_memory_stage_1_role"] == "context_seed_and_pattern_reference_only"
