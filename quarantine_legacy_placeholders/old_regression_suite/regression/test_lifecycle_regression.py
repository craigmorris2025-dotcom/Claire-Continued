"""
Lifecycle regression tests for Claire v5.28+.

Run from the project root:

    python -m pytest tests/regression/test_lifecycle_regression.py -q

The tests assume Claire's project root has src/ on the Python path. If needed:

    $env:PYTHONPATH = ".\src"
    python -m pytest tests/regression/test_lifecycle_regression.py -q

These tests are intentionally black-box at the pipeline contract level. They do
not assert exact scores except where the score represents a lifecycle invariant.
"""

from __future__ import annotations

import importlib
from typing import Any, Dict, Iterable, List

import pytest

from tests.regression.fixtures.lifecycle_inputs import ALL_FIXTURES


EXPECTED_TOP_LEVEL_ENGINE_KEYS: List[str] = [
    "knowledge_ingestion",
    "signal_extraction",
    "market_gap",
    "trend_trajectory",
    "market_formation",
    "opportunity_discovery",
    "breakthrough_synthesis",
    "technical_feasibility",
    "moat",
    "risk_regulation",
    "business_model",
    "deal_exit_modeling",
    "productization_path",
    "strategic_positioning",
    "design_output",
    "portfolio_binder",
]

EXPECTED_SCORES: List[str] = [
    "knowledge_quality_score",
    "source_quality_score",
    "coverage_score",
    "signal_quality_score",
    "routing_confidence_score",
    "opportunity_score",
    "breakthrough_synthesis_score",
    "technical_feasibility_score",
    "productization_score",
    "strategic_positioning_score",
    "portfolio_score",
]

EXPECTED_STAGE_OUTPUT_KEYS: List[str] = [
    "knowledge_ingestion",
    "signal_extraction",
    "market_gap",
    "trend_trajectory",
    "market_formation",
    "opportunity_discovery",
    "breakthrough_synthesis",
    "technical_feasibility",
    "design_output",
    "productization_path",
    "strategic_positioning",
    "portfolio_binder",
]


def _load_pipeline_classes():
    pipeline_mod = importlib.import_module("claire.orchestrator.pipeline_v4")
    contract_mod = importlib.import_module("claire.domain.contract")
    return pipeline_mod.PipelineOrchestrator, contract_mod.ContractValidator


def _run_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    PipelineOrchestrator, ContractValidator = _load_pipeline_classes()
    intent = ContractValidator().validate_intent(payload)
    result = PipelineOrchestrator().execute(intent)
    if hasattr(result, "to_dict"):
        return result.to_dict()
    if isinstance(result, dict):
        return result
    raise TypeError(f"Unsupported pipeline result type: {type(result)!r}")


def _stages(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    stages = result.get("lifecycle_stages") or result.get("lifecycle", {}).get("stages") or []
    assert isinstance(stages, list), "lifecycle stages should be a list"
    return stages


def _stage_by_number(result: Dict[str, Any], stage_number: int) -> Dict[str, Any]:
    for stage in _stages(result):
        if stage.get("stage") == stage_number:
            return stage
    raise AssertionError(f"Stage {stage_number} not found")


def _section_ids(result: Dict[str, Any]) -> List[str]:
    binder = result.get("portfolio_binder") or {}
    sections = binder.get("sections") or []
    return [section.get("id") for section in sections if isinstance(section, dict)]


def _artifact_ids(result: Dict[str, Any]) -> List[str]:
    binder = result.get("portfolio_binder") or {}
    manifest = binder.get("artifact_manifest") or []
    if isinstance(manifest, dict):
        # Support both list-style and dict-style manifests.
        return list(manifest.keys())
    return [item.get("section_id") or item.get("id") for item in manifest if isinstance(item, dict)]


@pytest.mark.parametrize("fixture_name", sorted(ALL_FIXTURES.keys()))
def test_pipeline_contract_and_all_lifecycle_stages_active(fixture_name: str):
    result = _run_pipeline(ALL_FIXTURES[fixture_name])

    assert result["status"] == "success"
    assert result["mode"] == "deterministic"
    assert result.get("decision_classification") in {"GO", "REVIEW", "HOLD", "NO_GO", "UNKNOWN"}

    lifecycle_summary = result.get("lifecycle_summary") or result.get("lifecycle", {}).get("summary") or {}
    assert lifecycle_summary.get("implemented_stage_count") == 21
    assert lifecycle_summary.get("active_stage_count") == 21
    assert lifecycle_summary.get("partial_stage_count") == 0
    assert lifecycle_summary.get("pending_stage_count") == 0

    stages = _stages(result)
    assert len(stages) == 21
    assert all(stage.get("status") == "active" for stage in stages), [
        (stage.get("stage"), stage.get("name"), stage.get("status"), stage.get("evidence"))
        for stage in stages
        if stage.get("status") != "active"
    ]

    for output_key in EXPECTED_STAGE_OUTPUT_KEYS:
        assert any(stage.get("output_key") == output_key for stage in stages), f"missing lifecycle output_key {output_key}"


@pytest.mark.parametrize("fixture_name", sorted(ALL_FIXTURES.keys()))
def test_required_engine_outputs_scores_and_binder_sections_exist(fixture_name: str):
    result = _run_pipeline(ALL_FIXTURES[fixture_name])

    for key in EXPECTED_TOP_LEVEL_ENGINE_KEYS:
        assert key in result, f"missing top-level key: {key}"
        assert isinstance(result[key], dict), f"{key} should be a dict"
        assert result[key].get("status") in {"success", "design_ready"}, f"{key} returned unexpected status: {result[key].get('status')}"

    scores = result.get("scores", {})
    for score_key in EXPECTED_SCORES:
        assert score_key in scores, f"missing score: {score_key}"
        assert isinstance(scores[score_key], (int, float)), f"{score_key} should be numeric"

    section_ids = _section_ids(result)
    for section_id in [
        "knowledge_ingestion",
        "signal_extraction",
        "opportunity_discovery",
        "breakthrough_synthesis",
        "technical_feasibility",
        "productization_path",
        "strategic_positioning",
    ]:
        assert section_id in section_ids, f"missing binder section: {section_id}"

    assert result["portfolio_binder"]["status"] == "success"


def test_defense_control_gated_route_and_controls_are_preserved():
    result = _run_pipeline(ALL_FIXTURES["defense_control_gated"])

    assert result["signal_extraction"]["dominant_sector"] == "defense_autonomy"
    assert result["signal_extraction"]["routing_evidence"]["cross_sector_ambiguity"] is False
    assert result["market_gap"]["sector"] == "defense_autonomy"

    assert result["risk_regulation"]["blocker_assessment"]["blocker_level"] == "conditional"
    assert result["technical_feasibility"]["feasibility_classification"]["readiness_modifier"] == "control_gated"
    assert result["productization_path"]["productization_classification"]["readiness_modifier"] == "control_gated"
    assert result["productization_path"]["launch_controls"]["control_level"] == "strict"
    assert result["strategic_positioning"]["positioning_classification"]["readiness_modifier"] == "control_gated_positioning"

    top_acquirers = [item.get("name") for item in result.get("acquirer_matches", [])[:5]]
    assert any(name in top_acquirers for name in {"Lockheed Martin", "Northrop Grumman", "Anduril", "RTX", "Palantir"})


@pytest.mark.parametrize(
    "fixture_name",
    ["climate_insurance", "routing_stress_insurance"],
)
def test_insurance_routes_to_climate_insurance_even_with_mixed_signals(fixture_name: str):
    result = _run_pipeline(ALL_FIXTURES[fixture_name])

    assert result["signal_extraction"]["dominant_sector"] == "climate_insurance"
    assert result["market_gap"]["sector"] == "climate_insurance"
    assert result["opportunity_discovery"]["sector"] == "climate_insurance"
    assert result["risk_regulation"]["sector"] == "climate_insurance"

    buyer_segments = result["market_gap"].get("buyer_segments", [])
    assert any("insur" in str(segment).lower() or "reinsur" in str(segment).lower() for segment in buyer_segments)


def test_stage_1_and_stage_2_have_dedicated_output_keys_and_evidence():
    result = _run_pipeline(ALL_FIXTURES["defense_control_gated"])

    stage_1 = _stage_by_number(result, 1)
    stage_2 = _stage_by_number(result, 2)

    assert stage_1["name"] == "Knowledge Ingestion"
    assert stage_1["status"] == "active"
    assert stage_1["output_key"] == "knowledge_ingestion"
    assert any("knowledge_ingestion generated successfully" in item for item in stage_1.get("evidence", []))

    assert stage_2["name"] == "Signal Extraction"
    assert stage_2["status"] == "active"
    assert stage_2["output_key"] == "signal_extraction"
    assert any("signal_extraction generated successfully" in item for item in stage_2.get("evidence", []))


def test_knowledge_and_signal_contracts_are_safe_for_downstream_scoring():
    result = _run_pipeline(ALL_FIXTURES["defense_control_gated"])

    knowledge = result["knowledge_ingestion"]
    assert knowledge["ingestion_contract"]["has_raw_input"] is True
    assert knowledge["ingestion_contract"]["has_connector_sources"] is True
    assert knowledge["ingestion_contract"]["safe_for_downstream_scoring"] is True
    assert knowledge["source_inventory"]["source_count"] >= 1
    assert knowledge["knowledge_quality_score"]["score"] >= 0.40

    signal = result["signal_extraction"]
    contract = signal["signal_contract"]
    assert contract["has_buyer_signal"] is True
    assert contract["has_product_signal"] is True
    assert contract["has_control_signal"] is True
    assert contract["has_evidence_signal"] is True
    assert contract["has_technical_signal"] is True


def test_binder_artifact_manifest_has_ready_core_sections():
    result = _run_pipeline(ALL_FIXTURES["defense_control_gated"])

    section_ids = _section_ids(result)
    assert "knowledge_ingestion" in section_ids
    assert "signal_extraction" in section_ids
    assert "strategic_positioning" in section_ids

    # Artifact manifest may be list-style or dict-style depending on binder evolution.
    artifact_ids = _artifact_ids(result)
    if artifact_ids:
        for expected_id in ["knowledge_ingestion", "signal_extraction", "strategic_positioning"]:
            assert expected_id in artifact_ids
