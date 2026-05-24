from __future__ import annotations

from runtime_core.api.governed_payload_bridge_adapter_s109r1 import (
    build_runtime_spine_payload_panel,
    build_runtime_spine_payload_bridge,
    validate_runtime_spine_payload_bridge,
    build_payload_bridge_adapter_report,
)


def test_s109r1_panel_has_canonical_shape():
    panel = build_runtime_spine_payload_panel()
    assert panel["panel_id"] == "runtime_spine"
    assert panel["version"] == "S109R1"
    assert panel["read_only"] is True
    assert panel["backend_owned"] is True
    assert panel["cockpit_presentation_only"] is True
    assert "summary" in panel
    assert "data" in panel


def test_s109r1_bridge_does_not_patch_or_rewire():
    bridge = build_runtime_spine_payload_bridge()
    assert bridge["bridge_adapter_version"] == "S109R1"
    assert bridge["status"] == "payload_bridge_adapter_ready"
    assert bridge["patch_performed"] is False
    assert bridge["route_registration_performed"] is False
    assert bridge["dashboard_rewire_performed"] is False
    assert "governed_runtime_spine" in bridge["canonical_payload_fragment"]


def test_s109r1_bridge_validation_passes():
    validation = validate_runtime_spine_payload_bridge()
    assert validation["validation_version"] == "S109R1"
    assert validation["ok"] is True
    assert validation["panel_keys_ok"] is True
    assert validation["flags_ok"] is True
    assert validation["locks_ok"] is True


def test_s109r1_adapter_report_passes():
    report = build_payload_bridge_adapter_report()
    assert report["adapter_report_version"] == "S109R1"
    assert report["ok"] is True
    assert report["compatibility_ok"] is True
    assert report["validation"]["ok"] is True
    assert report["next_safe_step"] == "S110R1 unified cockpit payload preview without live rewiring"
