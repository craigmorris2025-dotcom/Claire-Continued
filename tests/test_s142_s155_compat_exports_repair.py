from __future__ import annotations

from claire.api.governed_payload_bridge_live_patch_s142_s148 import (
    apply_governed_payload_bridge_live_patch,
    build_governed_payload_bridge_live_patch_s142_s148,
    build_s142_s148_live_payload_visibility,
    build_s142_s148_stop_gate,
    get_governed_payload_bridge_live_patch_s142_s148,
)


def test_s142_s155_compat_exports_exist_and_preserve_locks():
    stop_gate = build_s142_s148_stop_gate()
    visibility = build_s142_s148_live_payload_visibility()
    patch = build_governed_payload_bridge_live_patch_s142_s148()
    getter = get_governed_payload_bridge_live_patch_s142_s148()
    applied = apply_governed_payload_bridge_live_patch({"existing": True})

    assert stop_gate["runtime_mutation_enabled"] is False
    assert stop_gate["automatic_updates_enabled"] is False
    assert visibility["live_payload_visibility"] is True
    assert patch["patch_id"] == "governed_payload_bridge_live_patch_s142_s148"
    assert getter["backend_owns_truth"] is True
    assert applied["existing"] is True
    assert applied["runtime_truth_write_enabled"] is False
