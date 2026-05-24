from __future__ import annotations

from runtime_core.api.governed_unified_cockpit_preview_s110r1 import (
    REQUIRED_PREVIEW_PANELS,
    build_unified_cockpit_payload_preview,
    validate_unified_cockpit_payload_preview,
    build_unified_cockpit_preview_report,
)


def test_s110r1_unified_preview_contains_required_panels():
    payload = build_unified_cockpit_payload_preview()
    assert payload["preview_version"] == "S110R1"
    assert payload["status"] == "unified_cockpit_payload_preview_ready"
    assert payload["preview_only"] is True
    assert payload["live_dashboard_rewire_performed"] is False
    assert payload["app_patch_performed"] is False
    assert payload["route_registration_performed"] is False
    for panel_id in REQUIRED_PREVIEW_PANELS:
        assert panel_id in payload["panels"]


def test_s110r1_preview_panels_are_read_only():
    payload = build_unified_cockpit_payload_preview()
    for panel_id in REQUIRED_PREVIEW_PANELS:
        panel = payload["panels"][panel_id]
        assert panel["read_only"] is True
        assert panel["cockpit_presentation_only"] is True


def test_s110r1_preview_validation_passes():
    validation = validate_unified_cockpit_payload_preview()
    assert validation["validation_version"] == "S110R1"
    assert validation["ok"] is True
    assert validation["panels_present"] is True
    assert validation["panels_read_only"] is True
    assert validation["no_live_rewire"] is True
    assert validation["locks_ok"] is True


def test_s110r1_preview_report_passes():
    report = build_unified_cockpit_preview_report()
    assert report["preview_report_version"] == "S110R1"
    assert report["ok"] is True
    assert report["adapter_ok"] is True
    assert report["validation"]["ok"] is True
    assert report["next_safe_step"] == "S111R1 cockpit preview export artifact without live rewiring"
