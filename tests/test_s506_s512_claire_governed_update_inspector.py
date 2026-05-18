from __future__ import annotations

import importlib
from pathlib import Path


def test_s506_manifest_schema_is_ready_and_safe():
    module = importlib.import_module("claire.api.claire_governed_update_inspector_s506_s512")

    schema = module.build_s506_update_package_manifest_schema()
    assert "expected_hash" in schema["required_fields"]
    assert "rollback_plan_present" in schema["required_fields"]
    assert "operator_provided_local_metadata" in schema["allowed_source_types"]

    for flag in module.BLOCKED_AUTHORITY:
        assert schema[flag] is False


def test_s507_zero_trust_inspection_accepts_metadata_only_and_blocks_unsafe_authority():
    module = importlib.import_module("claire.api.claire_governed_update_inspector_s506_s512")

    inspection = module.inspect_update_package_candidate()
    assert inspection["inspection_scope"] == "metadata_only"
    assert inspection["risk_level"] in module.UPDATE_RISK_LEVELS
    assert inspection["download_allowed"] is False
    assert inspection["install_allowed"] is False
    assert inspection["apply_allowed"] is False

    blocked = module.inspect_update_package_candidate(
        module.build_sample_update_candidate(
            package_id="unsafe_update",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
            download_allowed=True,
        )
    )
    assert blocked["risk_level"] == "blocked"
    assert blocked["forbidden_authority_requested"]["apply_allowed"] is True

    for output in [inspection, blocked]:
        for flag in module.BLOCKED_AUTHORITY:
            assert output[flag] is False


def test_s508_validation_plan_and_s509_rollback_remain_non_executing():
    module = importlib.import_module("claire.api.claire_governed_update_inspector_s506_s512")

    inspection = module.inspect_update_package_candidate()
    plan = module.build_update_validation_plan(inspection)
    rollback = module.build_rollback_readiness_assessment(inspection)

    assert len(plan["validation_steps"]) >= 7
    assert plan["can_apply_update"] is False
    assert plan["network_required"] is False
    assert plan["download_required"] is False

    assert rollback["rollback_required"] is True
    assert rollback["rollback_validated"] is False
    assert rollback["can_apply_without_rollback_validation"] is False


def test_s510_operator_approval_gate_does_not_enable_application():
    module = importlib.import_module("claire.api.claire_governed_update_inspector_s506_s512")

    inspection = module.inspect_update_package_candidate()
    plan = module.build_update_validation_plan(inspection)
    gate = module.build_operator_approval_gate(inspection, plan)

    assert gate["approval_required"] is True
    assert gate["operator_approved"] is False
    assert gate["can_apply_update"] is False
    assert gate["can_download_package"] is False
    assert gate["can_mutate_runtime"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert gate[flag] is False


def test_s511_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_governed_update_inspector.js"
    css = root / "frontend/cockpit/shell/assets/claire_governed_update_inspector.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireGovernedUpdateInspectorVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "automaticUpdatesEnabled: false" in text
    assert "packageDownloadPerformed: false" in text
    assert "packageInstallPerformed: false" in text


def test_s512_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_governed_update_inspector_s506_s512")

    gate = module.build_s512_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["blocked_candidate_blocked"] is True
    assert gate["checks"]["no_download_or_apply"] is True
    assert (tmp_path / "s512_claire_governed_update_inspector_stop_gate.json").exists()


def test_s506_s512_rollup_ready():
    module = importlib.import_module("claire.api.claire_governed_update_inspector_s506_s512")

    rollup = module.build_claire_governed_update_inspector_s506_s512(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s506"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
    assert rollup["package_download_performed"] is False
    assert rollup["package_install_performed"] is False
