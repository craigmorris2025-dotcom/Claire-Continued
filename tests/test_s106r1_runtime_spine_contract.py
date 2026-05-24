from __future__ import annotations

import importlib

from runtime_core.api.governed_runtime_spine_s106r1 import (
    build_runtime_spine_state,
    build_runtime_spine_contract_report,
)


def test_s106r1_module_imports_without_app_patch():
    module = importlib.import_module("runtime_core.api.governed_runtime_spine_s106r1")
    assert hasattr(module, "build_runtime_spine_state")
    assert hasattr(module, "build_runtime_spine_contract_report")


def test_s106r1_runtime_spine_contract_ready():
    state = build_runtime_spine_state(review_queue_total=3, export_count=6)
    assert state["spine_version"] == "S106R1"
    assert state["status"] == "runtime_spine_contract_ready"
    assert state["backend_module_only"] is True
    assert state["app_patch_performed"] is False
    assert state["automatic_route_registration"] is False
    assert state["stage_count"] == 12
    assert state["route_count"] == 3
    assert state["review_queue_total"] == 3
    assert state["export_count"] == 6


def test_s106r1_governance_locks_remain_blocked():
    state = build_runtime_spine_state()
    locks = state["locks"]
    assert locks["backend_owns_truth"] is True
    assert locks["cockpit_presentation_only"] is True
    assert locks["runtime_truth_write_blocked"] is True
    assert locks["runtime_truth_mutation_blocked"] is True
    assert locks["automatic_updates_blocked"] is True
    assert locks["autonomous_execution_blocked"] is True
    assert locks["manual_promotion_mandatory"] is True
    assert locks["quarantine_mandatory"] is True


def test_s106r1_contract_report_passes():
    report = build_runtime_spine_contract_report()
    assert report["contract_report_version"] == "S106R1"
    assert report["ok"] is True
    assert report["status"] == "passed"
    assert report["checks"]["app_patch_performed_false"] is True
    assert report["checks"]["automatic_route_registration_false"] is True
    assert report["next_safe_step"] == "S107R1 existing-registry discovery without app patching"
