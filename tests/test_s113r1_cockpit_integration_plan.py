from __future__ import annotations

from claire.api.governed_cockpit_integration_plan_s113r1 import (
    build_controlled_cockpit_integration_plan,
    validate_controlled_cockpit_integration_plan,
)

def test_s113r1_controlled_integration_plan_ready():
    plan = build_controlled_cockpit_integration_plan()
    assert plan["integration_plan_version"] == "S113R1"
    assert plan["ok"] is True
    assert plan["status"] == "controlled_integration_plan_ready"
    assert plan["checks"]["no_direct_app_patch"] is True
    assert plan["checks"]["no_live_rewire_yet"] is True
    assert plan["checks"]["no_runtime_truth_write"] is True
    assert plan["next_safe_step"] == "S114R1 read-only preview payload registry module"

def test_s113r1_blocks_direct_app_patch_and_live_rewire():
    plan = build_controlled_cockpit_integration_plan()
    blocked_ids = {step["id"] for step in plan["blocked_actions"]}
    assert "direct_app_patch" in blocked_ids
    assert "live_dashboard_attachment_gate" in blocked_ids
    for step in plan["steps"]:
        assert step["rewires_live_dashboard"] is False
        assert step["writes_runtime_truth"] is False

def test_s113r1_validation_passes():
    validation = validate_controlled_cockpit_integration_plan()
    assert validation["validation_version"] == "S113R1"
    assert validation["ok"] is True
    assert validation["checks"]["direct_app_patch_blocked"] is True
    assert validation["checks"]["next_step_correct"] is True
