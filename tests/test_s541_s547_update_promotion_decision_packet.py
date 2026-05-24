from __future__ import annotations

import importlib
from pathlib import Path


def _passed_review_packet():
    plan_module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")
    intake_module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    plan = plan_module.build_controlled_validation_execution_plan()
    results = [
        {
            "command_id": command["command_id"],
            "status": "passed",
            "summary": "Operator supplied pass.",
            "evidence_refs": [f"manual_evidence_{command['command_id']}"],
        }
        for command in plan["command_manifest"]["commands"]
    ]
    intake = intake_module.intake_validation_results(plan, results)
    evidence_map = intake_module.build_result_evidence_map(intake)
    assessment = intake_module.assess_validation_result_readiness(intake, evidence_map)
    return intake_module.build_result_review_packet(intake, evidence_map, assessment)


def _failed_review_packet():
    plan_module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")
    intake_module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    plan = plan_module.build_controlled_validation_execution_plan()
    results = [
        {
            "command_id": command["command_id"],
            "status": "passed",
            "summary": "Operator supplied pass.",
            "evidence_refs": [f"manual_evidence_{command['command_id']}"],
        }
        for command in plan["command_manifest"]["commands"]
    ]
    results[0] = {
        "command_id": plan["command_manifest"]["commands"][0]["command_id"],
        "status": "failed",
        "summary": "Operator supplied failure.",
        "evidence_refs": ["manual_failure_log"],
        "blockers": ["targeted_validation_failed"],
    }
    intake = intake_module.intake_validation_results(plan, results)
    evidence_map = intake_module.build_result_evidence_map(intake)
    assessment = intake_module.assess_validation_result_readiness(intake, evidence_map)
    return intake_module.build_result_review_packet(intake, evidence_map, assessment)


def test_s541_schema_is_ready_and_safe():
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    schema = module.build_s541_promotion_decision_schema()
    assert "eligible_for_operator_promotion_review" in schema["promotion_decisions"]
    assert "promotion_review_ready" in schema["promotion_packet_statuses"]
    assert "promotion_packet_id" in schema["decision_packet_fields"]

    for flag in module.BLOCKED_AUTHORITY:
        assert schema[flag] is False


def test_s542_eligibility_allows_review_only_for_all_passed_results():
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    review_packet = _passed_review_packet()
    eligibility = module.build_promotion_eligibility_assessment(review_packet)

    assert eligibility["decision"] == "eligible_for_operator_promotion_review"
    assert eligibility["packet_status"] == "promotion_review_ready"
    assert eligibility["eligible_for_operator_review"] is True
    assert eligibility["promotion_allowed_now"] is False
    assert eligibility["update_apply_allowed"] is False
    assert eligibility["promotion_performed"] is False


def test_s543_promotion_decision_packet_is_review_only_and_cannot_apply():
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    packet = module.build_promotion_decision_packet(_passed_review_packet(), operator_note="review")
    assert packet["decision"] == "eligible_for_operator_promotion_review"
    assert packet["packet_status"] == "promotion_review_ready"
    assert packet["review_only"] is True
    assert packet["promotion_allowed_now"] is False
    assert packet["update_apply_allowed"] is False
    assert packet["promotion_performed"] is False
    assert packet["operator_approval_boundary"]["operator_approval_received"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert packet[flag] is False


def test_s544_failed_results_build_rejection_packet():
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    failed_review = _failed_review_packet()
    promotion_packet = module.build_promotion_decision_packet(failed_review)
    rejection = module.build_hold_or_rejection_packet(failed_review)

    assert promotion_packet["decision"] == "blocked_from_promotion"
    assert promotion_packet["packet_status"] == "blocked"
    assert rejection["disposition"] == "reject_or_rework"
    assert rejection["can_apply_update"] is False
    assert rejection["can_promote_update"] is False


def test_s545_approval_boundary_blocks_application():
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    boundary = module.build_operator_approval_boundary()
    assert boundary["operator_approval_required"] is True
    assert boundary["operator_approval_received"] is False
    assert boundary["rollback_proof_required"] is True
    assert boundary["separate_application_authority_required"] is True
    assert boundary["promotion_allowed_now"] is False
    assert boundary["update_apply_allowed"] is False


def test_s546_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_update_promotion_decision_packet.js"
    css = root / "frontend/cockpit/shell/assets/claire_update_promotion_decision_packet.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireUpdatePromotionDecisionPacketVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "promotionPerformed: false" in text
    assert "promotionAllowedNow: false" in text
    assert "updateApplyAllowed: false" in text


def test_s547_stop_gate_allows_forward_motion_and_marks_stop_point(tmp_path):
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    gate = module.build_s547_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert "STOP POINT B" in gate["stop_point"]
    assert gate["checks"]["passed_packet_enters_review_only"] is True
    assert gate["checks"]["failed_packet_blocks"] is True
    assert gate["checks"]["no_persistence_or_promotion"] is True
    assert (tmp_path / "s547_claire_update_promotion_decision_packet_stop_gate.json").exists()


def test_s541_s547_rollup_ready():
    module = importlib.import_module("runtime_core.api.update_promotion_decision_packet_s541_s547")

    rollup = module.build_update_promotion_decision_packet_s541_s547(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s541"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["promotion_performed"] is False
    assert rollup["update_apply_allowed"] is False
