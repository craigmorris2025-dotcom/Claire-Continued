from __future__ import annotations
import importlib

MODULES = [
    ("claire.api.s64_route_execution_payload_bridge", "build_s64r1_r8_plateau_report"),
    ("claire.api.s65_runtime_output_rendering", "build_s65r1_r8_plateau_report"),
    ("claire.api.s66_cockpit_evidence_rendering", "build_s66r1_r8_plateau_report"),
    ("claire.api.s67_operator_review_dashboard", "build_s67r1_r8_plateau_report"),
    ("claire.api.s68_dashboard_navigation_stabilization", "build_s68r1_r8_plateau_report"),
    ("claire.api.s69_cockpit_loading_reconciliation", "build_s69r1_r8_plateau_report"),
    ("claire.api.s70_modern_governed_cockpit_proof", "build_s70r1_r8_plateau_report"),
]

def test_s64_s70_all_ready_and_safe():
    for module_name, fn in MODULES:
        module = importlib.import_module(module_name)
        report = getattr(module, fn)()
        assert report["ready"] is True
        assert report["backend_owns_truth"] is True
        assert report["cockpit_presentation_only"] is True
        assert report["runtime_truth_mutation_allowed"] is False
        assert report["runtime_truth_write_allowed"] is False
        assert report["verification"]["verification_ok"] is True
