from __future__ import annotations

import importlib
from pathlib import Path


def test_s513_sandbox_profile_contract_and_builder_are_safe():
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")

    contract = module.build_s513_sandbox_profile_contract()
    profile = module.build_validation_sandbox_profile()

    assert "sandbox_id" in contract["sandbox_profile_fields"]
    assert profile["sandbox_status"] in module.SANDBOX_STATUSES
    assert profile["can_create_sandbox_now"] is False
    assert profile["sandbox_created"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert profile[flag] is False


def test_s514_file_impact_map_detects_protected_paths_without_writes():
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")
    inspector = importlib.import_module("runtime_core.api.governed_update_inspector_s506_s512")

    inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="protected_path_test",
            target_paths=["claire/api/dashboard_payload_bridge.py", "frontend/cockpit/shell/assets/demo.js"],
        )
    )
    impact = module.build_staged_file_impact_map(inspection)

    assert impact["protected_path_count"] >= 1
    assert impact["impact_level"] == "protected"
    assert impact["write_allowed_now"] is False
    assert impact["sandbox_file_write_performed"] is False


def test_s515_dry_run_validation_steps_do_not_execute_tests_or_create_sandbox():
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")

    plan = module.build_dry_run_validation_steps()
    assert plan["step_count"] >= 6
    assert plan["can_execute_now"] is False
    assert plan["can_create_sandbox_now"] is False
    assert plan["test_execution_performed"] is False

    for step in plan["steps"]:
        assert step["execution_performed"] is False


def test_s516_promotion_readiness_never_promotes_from_contract():
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")

    decision = module.build_promotion_readiness_decision()
    assert decision["promotion_ready"] is False
    assert decision["promotion_performed"] is False
    assert "tests_not_executed" in decision["blockers"]
    assert "sandbox_not_created" in decision["blockers"]

    for flag in module.BLOCKED_AUTHORITY:
        assert decision[flag] is False


def test_s517_rejection_quarantine_identifies_bad_candidate_without_quarantine_write():
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")
    inspector = importlib.import_module("runtime_core.api.governed_update_inspector_s506_s512")

    blocked = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="bad_candidate",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )
    decision = module.build_rejection_or_quarantine_decision(blocked)

    assert decision["decision"] == "reject_candidate"
    assert decision["quarantine_required"] is True
    assert decision["quarantine_write_performed"] is False
    assert "forbidden_authority_requested" in decision["reasons"]


def test_s518_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_staged_update_sandbox.js"
    css = root / "frontend/cockpit/shell/assets/claire_staged_update_sandbox.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireStagedUpdateSandboxVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "sandboxCreated: false" in text
    assert "testExecutionPerformed: false" in text
    assert "promotionPerformed: false" in text


def test_s519_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")

    gate = module.build_s519_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["sandbox_profile_no_creation"] is True
    assert gate["checks"]["dry_run_no_execution"] is True
    assert gate["checks"]["promotion_not_performed"] is True
    assert (tmp_path / "s519_claire_staged_update_sandbox_contract_stop_gate.json").exists()


def test_s513_s519_rollup_ready():
    module = importlib.import_module("runtime_core.api.staged_update_sandbox_contract_s513_s519")

    rollup = module.build_staged_update_sandbox_contract_s513_s519(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s513"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["sandbox_created"] is False
    assert rollup["test_execution_performed"] is False
    assert rollup["promotion_performed"] is False
