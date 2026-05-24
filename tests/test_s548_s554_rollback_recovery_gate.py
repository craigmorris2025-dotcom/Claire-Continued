from __future__ import annotations

import importlib
from pathlib import Path


def test_s548_schema_is_ready_and_safe():
    module = importlib.import_module("runtime_core.api.rollback_recovery_gate_s548_s554")

    schema = module.build_s548_rollback_proof_schema()
    assert "rollback_packet_id" in schema["rollback_packet_fields"]
    assert "proof_packet_ready_for_operator_review" in schema["rollback_proof_statuses"]
    assert "blocked_missing_rollback_proof" in schema["recovery_gate_states"]

    for flag in module.BLOCKED_AUTHORITY:
        assert schema[flag] is False


def test_s549_backup_restore_maps_are_declarative_only():
    module = importlib.import_module("runtime_core.api.rollback_recovery_gate_s548_s554")

    backup_map = module.build_target_file_backup_map(target_paths=["claire/api/example.py", "tests/test_example.py"])
    restore_map = module.build_restore_instruction_map(backup_map)

    assert backup_map["target_path_count"] == 2
    assert backup_map["protected_path_count"] >= 1
    assert backup_map["all_backups_created"] is False
    assert backup_map["backup_created"] is False

    assert restore_map["entry_count"] == 2
    assert restore_map["all_restore_instructions_declared"] is False
    assert restore_map["restore_performed"] is False


def test_s550_rollback_packet_blocks_apply_and_marks_incomplete_proof():
    module = importlib.import_module("runtime_core.api.rollback_recovery_gate_s548_s554")

    packet = module.build_rollback_proof_packet(target_paths=["claire/api/example.py"])
    assert packet["rollback_packet_id"].startswith("rollback_proof_packet_")
    assert packet["proof_status"] in module.ROLLBACK_PROOF_STATUSES
    assert packet["rollback_proven"] is False
    assert packet["backup_created"] is False
    assert packet["restore_performed"] is False
    assert packet["update_apply_allowed"] is False
    assert packet["blockers"]

    for flag in module.BLOCKED_AUTHORITY:
        assert packet[flag] is False


def test_s551_completeness_and_s552_recovery_gate_block_until_proof_complete():
    module = importlib.import_module("runtime_core.api.rollback_recovery_gate_s548_s554")

    packet = module.build_rollback_proof_packet()
    assessment = module.assess_rollback_proof_completeness(packet)
    gate = module.build_recovery_gate(packet, assessment)

    assert assessment["rollback_proof_complete"] is False
    assert assessment["rollback_proven"] is False
    assert assessment["can_advance_to_application_gate"] is False
    assert assessment["update_apply_allowed"] is False

    assert gate["gate_state"] == "blocked_missing_rollback_proof"
    assert gate["recovery_execution_allowed"] is False
    assert gate["recovery_execution_performed"] is False
    assert gate["update_apply_allowed"] is False


def test_s553_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_rollback_recovery_gate.js"
    css = root / "frontend/cockpit/shell/assets/claire_rollback_recovery_gate.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireRollbackRecoveryGateVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "backupCreated: false" in text
    assert "restorePerformed: false" in text
    assert "recoveryExecutionPerformed: false" in text
    assert "updateApplyAllowed: false" in text


def test_s554_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.rollback_recovery_gate_s548_s554")

    gate = module.build_s554_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["rollback_packet_not_proven"] is True
    assert gate["checks"]["recovery_gate_blocked"] is True
    assert gate["checks"]["no_backup_restore_recovery"] is True
    assert (tmp_path / "s554_claire_rollback_recovery_gate_stop_gate.json").exists()


def test_s548_s554_rollup_ready():
    module = importlib.import_module("runtime_core.api.rollback_recovery_gate_s548_s554")

    rollup = module.build_rollback_recovery_gate_s548_s554(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s548"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["backup_created"] is False
    assert rollup["restore_performed"] is False
    assert rollup["update_apply_allowed"] is False
