from __future__ import annotations

import importlib


def test_s15_classifies_degradation():
    module = importlib.import_module("claire.api.governed_timeline_classification")
    event = {
        "type": "synchronization_change",
        "field": "connection_state",
        "from": "connected",
        "to": "degraded",
    }
    classified = module.classify_timeline_event(event)
    assert classified["classification"] == "route_degradation"
    assert classified["severity"] == "warning"
    assert classified["runtime_authority"] == "blocked"
    assert classified["presentation_only"] is True


def test_s15_classifies_recovery():
    module = importlib.import_module("claire.api.governed_timeline_classification")
    event = {
        "type": "payload_freshness_change",
        "field": "freshness",
        "from": "stale",
        "to": "fresh",
    }
    classified = module.classify_timeline_event(event)
    assert classified["classification"] == "route_recovery"
    assert classified["severity"] == "recovered"


def test_s15_classifies_runtime_transition():
    module = importlib.import_module("claire.api.governed_timeline_classification")
    event = {
        "type": "runtime_state_transition",
        "field": "terminal_state",
        "from": "unknown",
        "to": "discovery_ready",
    }
    classified = module.classify_timeline_event(event)
    assert classified["classification"] == "runtime_transition"


def test_s15_attach_classification_preserves_blocked_authority():
    module = importlib.import_module("claire.api.governed_timeline_classification")
    payload = {
        "governed_runtime_timeline": {
            "authority": {"runtime_authority": "blocked"},
            "summary": {"last_route": "portfolio", "last_terminal_state": "portfolio_action_ready"},
            "events": [
                {"type": "heartbeat", "field": "timeline", "from": "stable", "to": "stable"},
                {"type": "synchronization_change", "field": "connection_state", "from": "connected", "to": "offline"},
            ],
        }
    }
    updated = module.attach_timeline_classification(payload)
    timeline = updated["governed_runtime_timeline"]
    assert timeline["authority"]["runtime_authority"] == "blocked"
    assert timeline["authority"]["cockpit_presentation_only"] is True
    assert timeline["authority"]["autonomous_execution_expansion"] is False
    assert timeline["classification_summary"]["runtime_authority"] == "blocked"
    assert timeline["classification_summary"]["counts"]["route_degradation"] == 1
