from __future__ import annotations

import importlib
from pathlib import Path


def test_s562_panel_registry_covers_update_runway():
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    registry = module.build_s562_update_control_panel_registry()
    assert registry["panel_count"] == len(module.COCKPIT_PANEL_ORDER)
    assert registry["panel_order"] == module.COCKPIT_PANEL_ORDER
    assert any(panel["panel_id"] == "operator_staged_update_handoff" for panel in registry["panels"])

    for flag in module.BLOCKED_AUTHORITY:
        assert registry[flag] is False


def test_s563_runway_readiness_imports_existing_stage_modules():
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    summary = module.build_update_runway_readiness_summary(project_root=Path.cwd())
    assert summary["module_count"] == len(module.UPDATE_CONTROL_RUNWAY)
    assert summary["all_modules_import"] is True
    assert summary["ready_stage_count"] == len(module.UPDATE_CONTROL_RUNWAY)
    assert summary["authority_state"] == "blocked_review_only"

    for item in summary["modules"]:
        assert item["import_ok"] is True


def test_s564_action_buttons_are_review_or_disabled_and_do_not_execute():
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    buttons = module.build_cockpit_action_button_contracts()
    assert buttons["button_count"] == len(module.ACTION_BUTTONS)
    assert any(button["button_id"] == "apply_update_disabled" and button["enabled"] is False for button in buttons["buttons"])
    assert all(button["execution_allowed"] is False for button in buttons["buttons"])
    assert all(button["execution_performed"] is False for button in buttons["buttons"])


def test_s565_blocked_authority_matrix_is_all_blocked():
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    matrix = module.build_blocked_authority_matrix()
    assert matrix["all_blocked"] is True
    assert matrix["unexpected_enabled"] == []
    assert matrix["item_count"] == len(module.BLOCKED_AUTHORITY)


def test_s566_payload_is_review_only_backend_truth():
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    payload = module.build_update_control_cockpit_payload(project_root=Path.cwd())
    assert payload["primary_status"] == "review_only_ready"
    assert payload["panel_registry"]["panel_count"] == len(module.COCKPIT_PANEL_ORDER)
    assert payload["action_buttons"]["button_count"] == len(module.ACTION_BUTTONS)
    assert payload["blocked_authority_matrix"]["all_blocked"] is True
    assert payload["cockpit_persistent_write_performed"] is False
    assert payload["cockpit_action_execution_performed"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert payload[flag] is False


def test_s567_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_update_control_cockpit_wiring.js"
    css = root / "frontend/cockpit/shell/assets/claire_update_control_cockpit_wiring.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireUpdateControlCockpitWiringVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "packageInstallPerformed: false" in text
    assert "updateApplyAllowed: false" in text
    assert "cockpitActionExecutionPerformed: false" in text


def test_s568_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    gate = module.build_s568_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["s563_runway_modules_import"] is True
    assert gate["checks"]["s565_authority_matrix_all_blocked"] is True
    assert gate["checks"]["no_update_authority"] is True
    assert (tmp_path / "s568_claire_update_control_cockpit_wiring_stop_gate.json").exists()


def test_s562_s568_rollup_ready():
    module = importlib.import_module("runtime_core.api.update_control_cockpit_wiring_s562_s568")

    rollup = module.build_update_control_cockpit_wiring_s562_s568(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s562"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["cockpit_action_execution_performed"] is False
    assert rollup["update_apply_allowed"] is False
