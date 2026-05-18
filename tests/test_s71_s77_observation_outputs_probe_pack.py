from __future__ import annotations
import importlib

MODULES = [
    ("claire.api.s71_governed_continuous_runtime_observation", "build_s71r1_r8_plateau_report"),
    ("claire.api.s72_run_output_operator_review_bridge", "build_s72r1_r8_plateau_report"),
    ("claire.api.s73_useful_run_package_composer", "build_s73r1_r8_plateau_report"),
    ("claire.api.s74_governed_output_quality_scoring", "build_s74r1_r8_plateau_report"),
    ("claire.api.s75_cockpit_demo_run_packet", "build_s75r1_r8_plateau_report"),
    ("claire.api.s76_controlled_probe_arming_review", "build_s76r1_r8_plateau_report"),
    ("claire.api.s77_provider_probe_dry_run_action", "build_s77r1_r8_plateau_report"),
]

def test_s71_s77_all_ready_and_authority_blocked():
    for module_name, fn_name in MODULES:
        module = importlib.import_module(module_name)
        report = getattr(module, fn_name)()
        assert report["ready"] is True
        assert report["backend_owns_truth"] is True
        assert report["cockpit_presentation_only"] is True
        assert report["runtime_truth_mutation_allowed"] is False
        assert report["runtime_truth_write_allowed"] is False
        assert report["operator_mutation_enabled"] is False
        assert report["automatic_updates_enabled"] is False
        assert report["autonomous_execution_enabled"] is False
        assert report["live_web_execution_enabled"] is False
        assert report["verification"]["verification_ok"] is True
        assert report["verification"]["failures"] == []

def test_s75_demo_packet_visible_but_not_live_execution():
    module = importlib.import_module("claire.api.s75_cockpit_demo_run_packet")
    packet = module.build_cockpit_demo_run_packet()
    assert packet["demo_ready"] is True
    assert packet["has_dashboard"] is True
    assert packet["has_useful_outputs"] is True
    assert packet["actual_live_execution"] is False
    assert packet["actual_runtime_truth_write"] is False

def test_s77_dry_run_never_executes_network():
    module = importlib.import_module("claire.api.s77_provider_probe_dry_run_action")
    action = module.build_provider_probe_dry_run_action()
    assert action["dry_run_available"] is True
    assert action["executes_network"] is False
    assert action["reads_body"] is False
    assert action["writes_runtime_truth"] is False
    assert action["network_request_performed"] is False
