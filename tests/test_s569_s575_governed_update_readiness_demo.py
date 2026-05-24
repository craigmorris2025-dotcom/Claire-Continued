from __future__ import annotations

import importlib
from pathlib import Path


def test_s569_schema_preserves_current_plan_and_web_handoff():
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    schema = module.build_s569_readiness_demo_schema()
    assert schema["demo_chain_stages"] == module.DEMO_CHAIN_STAGES
    assert "S569-S575" in schema["demo_chain_stages"]
    assert schema["next_phase_after_s575"] == module.NEXT_PHASE_AFTER_S575

    for flag in module.BLOCKED_AUTHORITY:
        assert schema[flag] is False


def test_s570_passed_path_demo_is_complete_but_cannot_apply():
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    demo = module.build_s570_demo_chain_packet(project_root=Path.cwd())
    assert demo["final_status"] == "readiness_demo_complete_review_only"
    assert demo["promotion_packet"]["decision"] == "eligible_for_operator_promotion_review"
    assert demo["validation_result_intake"]["result_readiness_state"] == "all_passed_supplied"
    assert demo["pre_application_blockers"]["safe_to_apply"] is False
    assert demo["update_apply_allowed"] is False
    assert demo["package_install_performed"] is False
    assert demo["network_request_performed"] is False
    assert demo["can_move_to_web_issues_after_s575"] is True


def test_s571_blocked_path_remains_visible_and_rejected():
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    blocked = module.build_s571_blocked_path_demo_packet(project_root=Path.cwd())
    assert blocked["final_status"] == "blocked_path_visible_review_only"
    assert blocked["inspection"]["risk_level"] == "blocked"
    assert blocked["validation_result_intake"]["result_readiness_state"] in {"blocked", "failed_validation"}
    assert blocked["promotion_packet"]["decision"] == "blocked_from_promotion"
    assert blocked["rejection_packet"]["disposition"] == "reject_or_rework"
    assert blocked["update_apply_allowed"] is False


def test_s572_summary_and_s573_authority_audit_are_ready():
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    summary = module.build_s572_demo_summary_payload(project_root=Path.cwd())
    audit = module.build_s573_final_blocked_authority_audit(project_root=Path.cwd())

    assert summary["primary_status"] == "complete_review_only"
    assert summary["passed_path"]["apply_allowed"] is False
    assert summary["blocked_path"]["apply_allowed"] is False
    assert summary["next_phase_after_s575"] == module.NEXT_PHASE_AFTER_S575

    assert audit["all_update_and_web_blocks_preserved"] is True
    assert audit["unexpected_enabled"] == []
    assert "governed internet search evidence-only" in audit["blocks_to_revisit_after_s575"]


def test_s574_web_phase_handoff_contract_points_to_web_source_search_issues():
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    handoff = module.build_s574_web_phase_handoff_contract()
    assert handoff["next_session_focus"] == "web_source_search_issues"
    assert handoff["do_not_change_s575_plan"] is True
    assert handoff["next_phase_after_s575"] == module.NEXT_PHASE_AFTER_S575
    assert handoff["automatic_updates_enabled"] is False
    assert handoff["live_web_execution_enabled"] is False


def test_s575_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_governed_update_readiness_demo.js"
    css = root / "frontend/cockpit/shell/assets/claire_governed_update_readiness_demo.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireGovernedUpdateReadinessDemoVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "liveWebExecutionEnabled: false" in text
    assert "packageInstallPerformed: false" in text
    assert "updateApplyAllowed: false" in text


def test_s575_stop_gate_allows_forward_motion_to_web_issues(tmp_path):
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    gate = module.build_s575_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert "STOP POINT D" in gate["stop_point"]
    assert gate["checks"]["s570_passed_path_still_cannot_apply"] is True
    assert gate["checks"]["s571_blocked_path_visible"] is True
    assert gate["checks"]["s573_all_blocks_preserved"] is True
    assert gate["checks"]["ready_to_move_to_web_issues"] is True
    assert (tmp_path / "s575_claire_governed_update_readiness_demo_stop_gate.json").exists()


def test_s569_s575_rollup_ready():
    module = importlib.import_module("runtime_core.api.governed_update_readiness_demo_s569_s575")

    rollup = module.build_governed_update_readiness_demo_s569_s575(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s569"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["live_web_execution_enabled"] is False
    assert rollup["update_apply_allowed"] is False
