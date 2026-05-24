from __future__ import annotations

from runtime_core.api.governed_payload_bridge_live_patch_s142_s148 import (
    governed_operations_payload_fragment,
    build_s142_s148_stop_gate,
)

def test_s142_s148_compatibility_module_restored():
    fragment = governed_operations_payload_fragment()
    assert fragment["status"] == "readonly_cockpit_payload_ready"
    assert fragment["read_only"] is True
    assert fragment["runtime_truth_write"] == "blocked"

def test_s142_s148_compatibility_stop_gate_passes(tmp_path):
    report = build_s142_s148_stop_gate(report_dir=tmp_path)
    assert report["stage_version"] == "S148"
    assert report["ok"] is True
    assert report["compatibility_repair"] is True
