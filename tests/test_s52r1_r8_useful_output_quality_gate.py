from __future__ import annotations

import importlib


def test_s52r1_quality_gate_passes_all_useful_outputs():
    module = importlib.import_module("claire.api.s52_useful_output_quality_gate")
    gate = module.build_useful_output_quality_gate()

    assert gate["version"] == "v19.89.8-S52R1-R8"
    assert gate["status"] == "useful_output_quality_gate_ready"
    assert gate["output_count"] == 7
    assert gate["passed_count"] == 7
    assert gate["failure_count"] == 0
    assert gate["quality_gate_passed"] is True
    assert gate["runtime_truth_mutation_allowed"] is False
    assert gate["fabricated_evidence_allowed"] is False

    for check in gate["checks"]:
        assert check["quality_gate_passed"] is True
        assert check["missing_required_keys"] == []
        assert check["section_count"] > 0
        assert check["runtime_truth_mutation_allowed"] is False
        assert check["operator_mutation_enabled"] is False


def test_s52r5_output_proof_requirements_block_auto_promotion():
    module = importlib.import_module("claire.api.s52_useful_output_quality_gate")
    proof = module.build_output_proof_requirements()

    assert proof["status"] == "output_proof_requirements_ready"
    assert proof["requirement_count"] == 4
    assert proof["source_quality_gate_passed"] is True

    for requirement in proof["requirements"]:
        assert requirement["required"] is True
        assert requirement["auto_promotion_allowed"] is False
        assert requirement["runtime_truth_write_allowed"] is False
        assert requirement["manual_promotion_required"] is True


def test_s52r8_plateau_report_ready():
    module = importlib.import_module("claire.api.s52_useful_output_quality_gate")
    report = module.build_s52r1_r8_plateau_report()

    assert report["status"] == "s52r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S53 cockpit useful output browser and export registry"
