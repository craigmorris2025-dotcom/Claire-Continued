from __future__ import annotations

import importlib
from pathlib import Path


def test_s534_schema_and_result_records_are_safe():
    module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    schema = module.build_s534_validation_result_schema()
    record = module.build_validation_result_record("declared_test_1", status="passed", evidence_refs=["manual_log"], operator_supplied=True)

    assert "passed" in schema["result_statuses"]
    assert "not_provided" in schema["result_statuses"]
    assert record["result_id"].startswith("validation_result_")
    assert record["status"] == "passed"
    assert record["execution_performed_by_claire"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert record[flag] is False


def test_s535_default_intake_creates_missing_result_placeholders_without_execution():
    module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    intake = module.intake_validation_results()
    assert intake["record_count"] >= 1
    assert intake["result_readiness_state"] == "awaiting_results"
    assert intake["operator_supplied_count"] == 0
    assert intake["validation_execution_performed"] is False
    assert intake["test_execution_performed"] is False
    assert intake["result_persistent_write_performed"] is False

    assert all(record["status"] == "not_provided" for record in intake["records"])


def test_s536_result_evidence_map_tracks_blockers_and_missing_refs():
    module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    intake = module.intake_validation_results()
    evidence_map = module.build_result_evidence_map(intake)

    assert evidence_map["evidence_count"] == intake["record_count"]
    assert "result_not_provided" in evidence_map["blockers"]
    assert evidence_map["all_results_have_evidence_refs"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert evidence_map[flag] is False


def test_s537_and_s538_assessment_and_packet_handle_passed_and_failed_results():
    module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")
    plan_module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    plan = plan_module.build_controlled_validation_execution_plan()
    commands = plan["command_manifest"]["commands"]

    passed_results = [
        {
            "command_id": command["command_id"],
            "status": "passed",
            "summary": "Operator supplied pass.",
            "evidence_refs": [f"manual_evidence_{command['command_id']}"],
        }
        for command in commands
    ]
    passed_intake = module.intake_validation_results(plan, passed_results)
    passed_map = module.build_result_evidence_map(passed_intake)
    passed_assessment = module.assess_validation_result_readiness(passed_intake, passed_map)
    passed_packet = module.build_result_review_packet(passed_intake, passed_map, passed_assessment)

    assert passed_intake["result_readiness_state"] == "all_passed_supplied"
    assert passed_assessment["promotion_decision_packet_ready"] is True
    assert passed_assessment["can_promote_update"] is False
    assert passed_packet["promotion_decision_packet_ready"] is True
    assert passed_packet["decision_execution_allowed"] is False

    failed_results = list(passed_results)
    failed_results[0] = {
        "command_id": commands[0]["command_id"],
        "status": "failed",
        "summary": "Operator supplied failure.",
        "evidence_refs": ["manual_failure_log"],
        "blockers": ["targeted_validation_failed"],
    }
    failed_intake = module.intake_validation_results(plan, failed_results)
    failed_packet = module.build_result_review_packet(failed_intake)

    assert failed_intake["result_readiness_state"] == "failed_validation"
    assert failed_packet["review_status"] == "blocked"


def test_s539_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_validation_result_intake.js"
    css = root / "frontend/cockpit/shell/assets/claire_validation_result_intake.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireValidationResultIntakeVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "validationExecutionPerformed: false" in text
    assert "testExecutionPerformed: false" in text
    assert "resultPersistentWritePerformed: false" in text


def test_s540_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    gate = module.build_s540_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["empty_results_wait"] is True
    assert gate["checks"]["passed_results_packet_ready"] is True
    assert gate["checks"]["failed_results_block"] is True
    assert gate["checks"]["no_execution_or_persistence"] is True
    assert (tmp_path / "s540_claire_validation_result_intake_stop_gate.json").exists()


def test_s534_s540_rollup_ready():
    module = importlib.import_module("runtime_core.api.validation_result_intake_s534_s540")

    rollup = module.build_validation_result_intake_s534_s540(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s534"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["validation_execution_performed"] is False
    assert rollup["result_persistent_write_performed"] is False
