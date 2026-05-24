from runtime_core.api.routes_pipeline import EvaluateRequest, _sources_with_lifecycle_memory
from runtime_core.ingestion.source_boundary import (
    INGESTION_ALLOWLIST,
    allowed_input_files,
    filter_sources,
    is_forbidden,
)
from pathlib import Path
import json


def test_stage1_boundary_blocks_system_zone_paths():
    for path in [
        "data/dashboard/state.json",
        "data/design/blueprints.json",
        "data/buyer/logic.json",
        "data/continuous_runtime/discovery_candidates.json",
        "data/runs/run-1/core_output.json",
        "claire/orchestrator/pipeline_v4.py",
        "backend/scoring/calibrator.py",
        "frontend/command_center/modern/platform_dashboard.js",
        "tools/run_claire_baseline.py",
        "docs/claire_system_contract_and_roadmap.md",
    ]:
        assert is_forbidden(path), path


def test_stage1_boundary_keeps_only_clean_source_packets():
    clean, boundary = filter_sources(
        {
            "market": {"source": "https://example.com/market", "growth": 0.2},
            "internal": {"source": "data/dashboard/runtime_payload.json", "summary": "dashboard binding"},
            "design_store": {"path": "data/continuous_runtime/design_candidates.json"},
        }
    )

    assert "market" in clean
    assert "internal" not in clean
    assert "design_store" not in clean
    assert boundary["rejected_sources"]["internal"]["reason"] == "source_boundary_forbidden_path"
    assert boundary["rejected_sources"]["design_store"]["reason"] == "source_boundary_forbidden_path"


def test_evaluate_sources_apply_boundary_before_stage1():
    req = EvaluateRequest(
        raw_input="market trend thesis",
        sources={
            "market": {"source": "data/source_universes/universe_index.json", "growth": 0.2},
            "dashboard": {"source": "frontend/command_center/modern/platform_dashboard.js"},
        },
    )

    sources, metadata = _sources_with_lifecycle_memory(req)

    assert "dashboard" not in sources
    assert metadata["source_boundary"]["status"] == "enforced"
    assert "dashboard" in metadata["source_boundary"]["rejected_sources"]


def test_allowlist_is_the_only_project_file_input_set():
    assert INGESTION_ALLOWLIST == [
        "data/continuous_runtime/lifecycle_memory.json",
        "data/source_universes/universe_index.json",
        "data/live/source_registry.json",
        "data/live_intelligence/latest_monitor_run.json",
        "data/internet_evidence/promoted_metadata_evidence_store.json",
    ]
    assert all(path.as_posix().endswith(tuple(INGESTION_ALLOWLIST)) for path in allowed_input_files())


def test_source_universe_registry_does_not_expose_system_zone_universes():
    payload = json.loads(Path("data/source_universes/universe_index.json").read_text(encoding="utf-8"))
    text = json.dumps(payload).lower()

    for forbidden in ["master system docs", "syntalion architecture", "claire-generated", "auto-invention technology database"]:
        assert forbidden not in text
