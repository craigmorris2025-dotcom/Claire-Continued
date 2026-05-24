from __future__ import annotations


def test_canonical_pipeline_source_index_maps_route_conditions_and_operator_rules():
    from runtime_core.pipeline.canonical_pipeline_sources import build_canonical_pipeline_source_index

    payload = build_canonical_pipeline_source_index()

    assert payload["schema_version"] == "claire.canonical_pipeline_sources.v1"
    assert payload["route_contracts"]["portfolio_normal_path"]["required_stage_outputs"] == [1, 2, 3, 4, 5, 8, 9, 10, 23, 26, 27]
    assert "design_portal_output" in payload["route_contracts"]["breakthrough_design_path"]["must_produce"]
    assert "acquirer_identification" in payload["route_contracts"]["acquisition_package_path"]["must_produce"]
    replacement = payload["route_contracts"]["existing_system_replacement_path"]
    assert "Existing System Ingestion  Replacement Pipeline.txt" in replacement["required_sources"]
    assert "existing_system_decomposition" in replacement["required_stage_outputs"]
    assert "superior_system_design" in replacement["must_produce"]
    assert any(item["filename"] == "Branch Logic.txt" and item["exists"] for item in payload["sources"])
    assert payload["operator_rules"]["nothing_auto_promotes"] is True
    assert payload["operator_rules"]["runtime_truth_write_requires_promotion"] is True
    assert "executive_summary" in payload["final_package_requirements"]
    assert "acquirer_targets" in payload["final_package_requirements"]
    assert any(item["role"] == "full_data_model_map" for item in payload["master_sources"])
