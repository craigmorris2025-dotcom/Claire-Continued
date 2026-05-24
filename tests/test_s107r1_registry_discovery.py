from __future__ import annotations

from runtime_core.api.governed_runtime_registry_discovery_s107r1 import (
    discover_existing_registry_surfaces,
    build_safe_attachment_plan,
    build_registry_discovery_report,
)


def test_s107r1_discovers_registry_surfaces_without_patching():
    discovery = discover_existing_registry_surfaces()
    assert discovery["discovery_version"] == "S107R1"
    assert discovery["status"] == "registry_discovery_complete"
    assert discovery["direct_app_patch_blocked"] is True
    assert discovery["automatic_route_registration_blocked"] is True
    assert len(discovery["registry_candidates"]) >= 3


def test_s107r1_safe_attachment_plan_blocks_app_patch():
    plan = build_safe_attachment_plan()
    assert plan["attachment_plan_version"] == "S107R1"
    assert plan["ok"] is True
    direct_patch_steps = [item for item in plan["plan"] if item["method"] == "app_py_direct_patch"]
    assert direct_patch_steps
    assert direct_patch_steps[0]["allowed_now"] is False
    assert direct_patch_steps[0]["patches_app"] is True


def test_s107r1_report_passes_and_points_to_s108r1():
    report = build_registry_discovery_report()
    assert report["report_version"] == "S107R1"
    assert report["ok"] is True
    assert report["safe_to_continue"] is True
    assert report["plan"]["next_safe_step"] == "S108R1 dashboard payload read-model compatibility proof"
