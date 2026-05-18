from __future__ import annotations

from claire.api.governed_dashboard_payload_spine_compat_s108r1 import (
    discover_dashboard_payload_surfaces,
    build_spine_dashboard_read_model,
    build_dashboard_payload_compatibility_report,
)


def test_s108r1_discovers_dashboard_payload_surfaces_without_patch():
    discovery = discover_dashboard_payload_surfaces()
    assert discovery["surface_discovery_version"] == "S108R1"
    assert discovery["patch_performed"] is False
    assert len(discovery["surfaces"]) >= 3
    assert any(item["exists"] for item in discovery["surfaces"])


def test_s108r1_builds_dashboard_read_model_from_spine():
    read_model = build_spine_dashboard_read_model(review_queue_total=3, export_count=6)
    assert read_model["read_model_version"] == "S108R1"
    assert read_model["status"] == "dashboard_spine_read_model_ready"
    assert read_model["spine_version"] == "S106R1"
    assert read_model["stage_count"] == 12
    assert read_model["route_count"] == 3
    assert read_model["review_queue_total"] == 3
    assert read_model["export_count"] == 6
    assert read_model["patch_performed"] is False
    assert read_model["route_registration_performed"] is False


def test_s108r1_compatibility_report_passes():
    report = build_dashboard_payload_compatibility_report()
    assert report["compatibility_report_version"] == "S108R1"
    assert report["ok"] is True
    assert report["status"] == "dashboard_payload_compatibility_ready"
    assert report["candidate_surface_count"] >= 1
    assert report["required_keys_present"] is True
    assert report["locks_ok"] is True
    assert report["next_safe_step"] == "S109R1 payload bridge adapter module without app patching"
