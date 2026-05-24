from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s19_overlay_builds_and_preserves_authority():
    module = importlib.import_module("runtime_core.api.governed_route_activity_overlay")
    overlay = module.build_governed_route_activity_overlay({})

    assert overlay["version"] == "v19.89.8-S19"
    assert overlay["status"] == "active"
    assert overlay["authority"]["runtime_authority"] == "blocked"
    assert overlay["authority"]["cockpit_presentation_only"] is True
    assert overlay["authority"]["autonomous_execution_expansion"] is False
    assert overlay["summary"]["route_total"] >= 8
    assert isinstance(overlay["routes"], list)


def test_s19_overlay_uses_registry_surface_ownership():
    registry_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_registry")
    health_module = importlib.import_module("runtime_core.api.canonical_cockpit_surface_health")
    overlay_module = importlib.import_module("runtime_core.api.governed_route_activity_overlay")

    registry = registry_module.build_cockpit_surface_registry()
    health = health_module.evaluate_surface_registry_health(registry)
    payload = {
        "canonical_cockpit_surface_registry": registry,
        "canonical_cockpit_surface_health": health,
        "runtime": {"route": "portfolio", "terminal_state": "portfolio_action_ready"},
        "governed_runtime_timeline": {"summary": {"last_payload_freshness": "fresh", "last_connection_state": "connected"}},
    }

    overlay = overlay_module.build_governed_route_activity_overlay(payload)
    portfolio = next(item for item in overlay["routes"] if item["route"] == "portfolio")

    assert portfolio["selected"] is True
    assert portfolio["state"] == "active"
    assert portfolio["owned_surface_count"] >= 1


def test_s19_js_is_presentation_only_get_payload_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_route_activity_overlay.js"
    assert js_path.exists()
    text = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S19" in text
    assert "/dashboard/payload" in text
    assert "presentation_only_runtime_authority_blocked" in text
    assert "POST" not in text
    assert "PUT" not in text
    assert "DELETE" not in text
