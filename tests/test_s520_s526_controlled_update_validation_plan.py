from __future__ import annotations

import importlib
from pathlib import Path


def test_s520_authority_matrix_blocks_execution():
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    matrix = module.build_s520_execution_authority_matrix_contract()
    assert "run_validation_commands" in matrix["blocked_now"]
    assert "apply_automatic_update" in matrix["blocked_now"]
    assert "build_validation_plan" in matrix["allowed_now"]

    for flag in module.BLOCKED_AUTHORITY:
        assert matrix[flag] is False


def test_s521_command_manifest_declares_commands_without_execution():
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    manifest = module.build_validation_command_manifest()
    assert manifest["command_count"] >= 4
    assert manifest["execution_allowed_now"] is False
    assert manifest["execution_performed"] is False
    assert any(command["command_id"] == "full_regression_future_check" for command in manifest["commands"])

    for command in manifest["commands"]:
        assert command["execution_allowed_now"] is False
        assert command["execution_performed"] is False


def test_s522_controlled_validation_plan_uses_previous_update_contracts_safely():
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    plan = module.build_controlled_validation_execution_plan()
    assert plan["execution_plan_id"].startswith("controlled_validation_plan_")
    assert plan["sandbox_profile"]["can_create_sandbox_now"] is False
    assert plan["command_manifest"]["execution_performed"] is False
    assert plan["validation_execution_performed"] is False
    assert plan["test_execution_performed"] is False
    assert plan["promotion_allowed"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert plan[flag] is False


def test_s523_preflight_and_s524_rollback_do_not_enable_execution_or_apply():
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    plan = module.build_controlled_validation_execution_plan()
    preflight = module.build_validation_preflight_decision(plan)
    rollback = module.build_rollback_proof_checklist()

    assert preflight["execution_allowed_now"] is False
    assert preflight["operator_approval_required"] is True
    assert preflight["decision"] in {"eligible_for_future_manual_execution_owner", "not_ready_for_execution_owner"}

    assert rollback["rollback_proven"] is False
    assert rollback["can_apply_without_rollback_proof"] is False
    assert rollback["required_count"] >= 5


def test_s525_operator_gate_blocks_validation_execution():
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    gate = module.build_operator_controlled_execution_gate()
    assert gate["gate_state"] == "blocked"
    assert gate["operator_approved"] is False
    assert gate["execution_allowed_now"] is False
    assert gate["validation_execution_performed"] is False
    assert gate["can_promote_after_execution"] is False
    assert "rollback_not_proven" in gate["blockers"]
    assert "operator_approval_required" in gate["blockers"]

    for flag in module.BLOCKED_AUTHORITY:
        assert gate[flag] is False


def test_s526_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_controlled_update_validation_plan.js"
    css = root / "frontend/cockpit/shell/assets/claire_controlled_update_validation_plan.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireControlledUpdateValidationPlanVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "validationExecutionPerformed: false" in text
    assert "testExecutionPerformed: false" in text
    assert "promotionPerformed: false" in text


def test_s526_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    gate = module.build_s526_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["no_command_execution"] is True
    assert gate["checks"]["no_validation_execution"] is True
    assert (tmp_path / "s526_claire_controlled_update_validation_plan_stop_gate.json").exists()


def test_s520_s526_rollup_ready():
    module = importlib.import_module("runtime_core.api.controlled_update_validation_plan_s520_s526")

    rollup = module.build_controlled_update_validation_plan_s520_s526(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s520"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["validation_execution_performed"] is False
    assert rollup["test_execution_performed"] is False
