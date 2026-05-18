from __future__ import annotations

import importlib


def test_s48r1_route_browser_index_is_read_only():
    module = importlib.import_module("claire.api.s48_dashboard_route_payload_browser")
    index = module.build_dashboard_route_browser_index()

    assert index["version"] == "v19.89.8-S48R1-R8"
    assert index["status"] == "dashboard_route_browser_index_ready"
    assert index["route_count"] == 7
    assert index["backend_owns_truth"] is True
    assert index["cockpit_presentation_only"] is True
    assert index["runtime_truth_mutation_allowed"] is False

    for route in index["routes"]:
        assert route["method"] == "GET"
        assert route["display_mode"] == "payload_card"
        assert route["response_mode"] == "read_only_artifact"
        assert route["runtime_truth_mutation_allowed"] is False
        assert route["operator_mutation_enabled"] is False


def test_s48r3_payload_browser_previews_available():
    module = importlib.import_module("claire.api.s48_dashboard_route_payload_browser")
    previews = module.build_dashboard_payload_browser_previews()

    assert previews["status"] == "dashboard_payload_browser_previews_ready"
    assert previews["preview_count"] == 7
    assert previews["ok_count"] == 7
    assert previews["failure_count"] == 0
    assert previews["failures"] == []
    assert previews["live_server_required"] is False

    for preview in previews["previews"]:
        assert preview["available"] is True
        assert preview["status_code"] == 200
        assert preview["mutating"] is False
        assert preview["runtime_truth_mutation_allowed"] is False
        assert preview["response_mode"] == "read_only_artifact"


def test_s48r8_plateau_report_ready():
    module = importlib.import_module("claire.api.s48_dashboard_route_payload_browser")
    report = module.build_s48r1_r8_plateau_report()

    assert report["status"] == "s48r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S49 governed web and evidence panels visible in cockpit"
