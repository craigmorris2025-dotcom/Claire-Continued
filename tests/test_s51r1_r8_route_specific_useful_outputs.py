from __future__ import annotations

import importlib


def test_s51r1_route_specific_useful_output_surfaces_are_ready():
    module = importlib.import_module("claire.api.s51_route_specific_useful_outputs")
    payload = module.build_route_specific_useful_output_surfaces()

    assert payload["version"] == "v19.89.8-S51R1-R8"
    assert payload["status"] == "route_specific_useful_output_surfaces_ready"
    assert payload["surface_count"] == 7
    assert payload["backend_owns_truth"] is True
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["operator_mutation_enabled"] is False

    route_ids = {surface["route_id"] for surface in payload["surfaces"]}
    assert "trend_thesis" in route_ids
    assert "portfolio_action" in route_ids
    assert "breakthrough_classification" in route_ids
    assert "design_output" in route_ids
    assert "acquisition_package" in route_ids

    for surface in payload["surfaces"]:
        assert surface["useful_output_ready"] is True
        assert surface["fabricated_evidence_allowed"] is False
        assert surface["manual_promotion_required"] is True
        assert surface["quarantine_required"] is True
        assert surface["runtime_truth_mutation_allowed"] is False
        assert surface["required_sections"]


def test_s51r5_output_previews_have_sections_and_review_state():
    module = importlib.import_module("claire.api.s51_route_specific_useful_outputs")
    previews = module.build_all_route_output_previews()

    assert previews["status"] == "all_route_output_previews_ready"
    assert previews["preview_count"] == 7

    for preview in previews["previews"]:
        assert preview["status"] == "route_output_preview_ready"
        assert preview["section_count"] > 0
        assert preview["review_state"] == "operator_review_required"
        assert preview["evidence_state"] == "required_before_runtime_truth"
        assert preview["runtime_truth_mutation_allowed"] is False


def test_s51r8_plateau_report_ready():
    module = importlib.import_module("claire.api.s51_route_specific_useful_outputs")
    report = module.build_s51r1_r8_plateau_report()

    assert report["status"] == "s51r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S52 useful output quality gate and proof requirements"
