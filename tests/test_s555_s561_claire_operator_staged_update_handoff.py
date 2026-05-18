from __future__ import annotations

import importlib
from pathlib import Path


def test_s555_approval_text_contract_and_evaluation_are_safe():
    module = importlib.import_module("claire.api.claire_operator_staged_update_handoff_s555_s561")

    contract = module.build_s555_operator_approval_text_contract()
    good = module.evaluate_operator_approval_text(module.REQUIRED_APPROVAL_TEXT)
    bad = module.evaluate_operator_approval_text("approve it")

    assert contract["required_approval_text"] == module.REQUIRED_APPROVAL_TEXT
    assert good["approval_text_matched"] is True
    assert good["approval_recorded_for_review"] is True
    assert good["update_apply_allowed"] is False
    assert bad["approval_text_matched"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert good[flag] is False


def test_s556_handoff_eligibility_records_approval_but_blocks_apply():
    module = importlib.import_module("claire.api.claire_operator_staged_update_handoff_s555_s561")

    approval = module.evaluate_operator_approval_text(module.REQUIRED_APPROVAL_TEXT)
    eligibility = module.assess_staged_handoff_eligibility(operator_approval=approval)

    assert eligibility["operator_approval_recorded_for_review"] is True
    assert eligibility["update_apply_allowed"] is False
    assert eligibility["application_handoff_performed"] is False
    assert "rollback_not_proven" in eligibility["blockers"]

    for flag in module.BLOCKED_AUTHORITY:
        assert eligibility[flag] is False


def test_s557_handoff_packet_is_review_only_and_never_applies():
    module = importlib.import_module("claire.api.claire_operator_staged_update_handoff_s555_s561")

    packet = module.build_operator_staged_update_handoff_packet(
        operator_approval_text=module.REQUIRED_APPROVAL_TEXT,
        operator_note="test handoff",
    )

    assert packet["handoff_packet_id"].startswith("staged_update_handoff_")
    assert packet["operator_approval"]["approval_text_matched"] is True
    assert packet["review_only"] is True
    assert packet["application_owner_required"] is True
    assert packet["application_owner_enabled"] is False
    assert packet["update_apply_allowed"] is False
    assert packet["package_install_performed"] is False
    assert packet["handoff_persistent_write_performed"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert packet[flag] is False


def test_s558_application_owner_boundary_and_s559_blockers_remain_closed():
    module = importlib.import_module("claire.api.claire_operator_staged_update_handoff_s555_s561")

    packet = module.build_operator_staged_update_handoff_packet(operator_approval_text=module.REQUIRED_APPROVAL_TEXT)
    boundary = module.build_application_owner_boundary(packet)
    blockers = module.build_final_pre_application_blocker_packet(packet)

    assert boundary["application_owner_required"] is True
    assert boundary["application_owner_enabled"] is False
    assert boundary["update_apply_allowed"] is False
    assert boundary["package_install_performed"] is False
    assert boundary["runtime_mutation_enabled"] is False

    assert blockers["safe_to_apply"] is False
    assert blockers["safe_to_install"] is False
    assert blockers["safe_to_mutate_runtime"] is False
    assert blockers["blockers"]


def test_s560_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_operator_staged_update_handoff.js"
    css = root / "frontend/cockpit/shell/assets/claire_operator_staged_update_handoff.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireOperatorStagedUpdateHandoffVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "handoffExecutionPerformed: false" in text
    assert "applicationHandoffPerformed: false" in text
    assert "updateApplyAllowed: false" in text


def test_s561_stop_gate_allows_forward_motion_and_marks_stop_point(tmp_path):
    module = importlib.import_module("claire.api.claire_operator_staged_update_handoff_s555_s561")

    gate = module.build_s561_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert "STOP POINT C" in gate["stop_point"]
    assert gate["checks"]["approved_handoff_records_approval_only"] is True
    assert gate["checks"]["pre_application_blockers_visible"] is True
    assert gate["checks"]["no_handoff_execution_or_apply"] is True
    assert (tmp_path / "s561_claire_operator_staged_update_handoff_stop_gate.json").exists()


def test_s555_s561_rollup_ready():
    module = importlib.import_module("claire.api.claire_operator_staged_update_handoff_s555_s561")

    rollup = module.build_claire_operator_staged_update_handoff_s555_s561(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s555"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["handoff_execution_performed"] is False
    assert rollup["application_handoff_performed"] is False
    assert rollup["update_apply_allowed"] is False
