from __future__ import annotations

import importlib


def test_s18_health_evaluates_clean_registry_as_healthy():
    registry_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_registry")
    health_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_health")

    registry = registry_module.build_cockpit_surface_registry()
    health = health_module.evaluate_surface_registry_health(registry)

    assert health["version"] == "v19.89.8-S18"
    assert health["status"] == "active"
    assert health["health"] == "healthy"
    assert health["authority"]["runtime_authority"] == "blocked"
    assert health["authority"]["cockpit_presentation_only"] is True
    assert health["authority"]["autonomous_execution_expansion"] is False
    assert health["summary"]["critical_count"] == 0


def test_s18_detects_runtime_authority_drift():
    health_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_health")

    registry = {
        "surfaces": [
            {
                "surface_id": "bad_surface",
                "label": "Bad Surface",
                "payload_owner": "test",
                "route_owner": "test",
                "sidebar_owner": "test",
                "telemetry_owner": "test",
                "visibility": "active",
                "sync_state": "canonical",
                "runtime_authority": "enabled",
            }
        ]
    }

    health = health_module.evaluate_surface_registry_health(registry)

    assert health["health"] == "blocked"
    assert health["summary"]["critical_count"] == 1
    assert any(issue["issue"] == "runtime_authority_drift" for issue in health["issues"])


def test_s18_detects_duplicate_surface_ids():
    health_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_health")

    base = {
        "surface_id": "duplicate",
        "label": "Duplicate",
        "payload_owner": "test",
        "route_owner": "test",
        "sidebar_owner": "test",
        "telemetry_owner": "test",
        "visibility": "active",
        "sync_state": "canonical",
        "runtime_authority": "blocked",
    }
    registry = {"surfaces": [dict(base), dict(base)]}

    health = health_module.evaluate_surface_registry_health(registry)

    assert health["health"] == "blocked"
    assert "duplicate" in health["summary"]["duplicate_surface_ids"]
    assert any(issue["issue"] == "duplicate_surface_id" for issue in health["issues"])


def test_s18_attach_surface_health_preserves_payload():
    registry_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_registry")
    health_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_health")

    payload = {
        "existing": "preserved",
        "canonical_cockpit_surface_registry": registry_module.build_cockpit_surface_registry(),
    }

    updated = health_module.attach_surface_health(payload)

    assert updated["existing"] == "preserved"
    assert "canonical_cockpit_surface_health" in updated
    assert updated["canonical_cockpit_surface_health"]["authority"]["runtime_authority"] == "blocked"
