from __future__ import annotations

import importlib


def test_governed_runtime_timeline_module_imports():
    module = importlib.import_module("claire.api.governed_runtime_timeline")
    assert hasattr(module, "project_governed_runtime_timeline")
    assert hasattr(module, "attach_governed_runtime_timeline")
    assert hasattr(module, "register_governed_runtime_timeline_routes")


def test_governed_runtime_timeline_preserves_blocked_authority():
    module = importlib.import_module("claire.api.governed_runtime_timeline")

    payload = {
        "runtime": {
            "route": "portfolio",
            "terminal_state": "portfolio_action_ready",
        },
        "governance": {
            "runtime_authority": "blocked",
            "backend_owns_truth": True,
            "fail_closed": True,
        },
        "telemetry": {
            "connection_state": "connected",
            "freshness": "fresh",
        },
        "event_stream": {
            "events": [{"type": "seed"}],
        },
    }

    timeline = module.project_governed_runtime_timeline(payload)

    assert timeline["version"] == "v19.89.8-S14"
    assert timeline["status"] == "active"
    assert timeline["authority"]["backend_owns_truth"] is True
    assert timeline["authority"]["cockpit_presentation_only"] is True
    assert timeline["authority"]["runtime_authority"] == "blocked"
    assert timeline["authority"]["fail_closed_governance"] is True
    assert timeline["authority"]["autonomous_execution_expansion"] is False
    assert timeline["summary"]["last_route"] == "portfolio"
    assert timeline["summary"]["last_terminal_state"] == "portfolio_action_ready"
    assert isinstance(timeline["events"], list)
    assert len(timeline["events"]) >= 1


def test_attach_governed_runtime_timeline_adds_projection_without_replacing_payload():
    module = importlib.import_module("claire.api.governed_runtime_timeline")

    payload = {
        "runtime": {"route": "discovery", "terminal_state": "discovery_ready"},
        "existing_key": "preserved",
    }

    updated = module.attach_governed_runtime_timeline(payload)

    assert updated["existing_key"] == "preserved"
    assert "governed_runtime_timeline" in updated
    assert updated["governed_runtime_timeline"]["authority"]["runtime_authority"] == "blocked"
    assert updated["governed_runtime_timeline"]["authority"]["autonomous_execution_expansion"] is False


def test_timeline_tracked_dimensions_are_present():
    module = importlib.import_module("claire.api.governed_runtime_timeline")
    timeline = module.project_governed_runtime_timeline({})

    required = {
        "runtime_state_transitions",
        "event_stream_evolution",
        "synchronization_changes",
        "payload_freshness_changes",
        "route_degradation_recovery",
    }

    assert required.issubset(set(timeline["tracked_dimensions"]))
