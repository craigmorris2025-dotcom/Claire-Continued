from __future__ import annotations

import importlib


def test_s17_registry_imports_and_builds():
    module = importlib.import_module("claire.api.canonical_cockpit_surface_registry")
    registry = module.build_cockpit_surface_registry()

    assert registry["version"] == "v19.89.8-S17"
    assert registry["status"] == "active"
    assert registry["authority"]["backend_owns_truth"] is True
    assert registry["authority"]["cockpit_presentation_only"] is True
    assert registry["authority"]["runtime_authority"] == "blocked"
    assert registry["authority"]["autonomous_execution_expansion"] is False
    assert registry["summary"]["surface_total"] >= 8


def test_s17_registry_has_no_duplicate_surface_ids():
    module = importlib.import_module("claire.api.canonical_cockpit_surface_registry")
    registry = module.build_cockpit_surface_registry()

    assert registry["summary"]["duplicate_surface_ids"] == []
    assert registry["summary"]["missing_authority_locks"] == []
    assert registry["summary"]["registry_health"] == "healthy"


def test_s17_registry_contains_required_operational_surfaces():
    module = importlib.import_module("claire.api.canonical_cockpit_surface_registry")
    registry = module.build_cockpit_surface_registry()
    surface_ids = {item["surface_id"] for item in registry["surfaces"]}

    required = {
        "main_result",
        "runtime_surface",
        "operator_timeline",
        "event_stream",
        "source_surfaces",
        "search_surface",
        "portfolio_surface",
        "breakthrough_surface",
        "design_surface",
        "acquisition_surface",
    }

    assert required.issubset(surface_ids)


def test_s17_attach_registry_preserves_payload():
    module = importlib.import_module("claire.api.canonical_cockpit_surface_registry")
    payload = {"existing": "preserved"}
    updated = module.attach_cockpit_surface_registry(payload)

    assert updated["existing"] == "preserved"
    assert "canonical_cockpit_surface_registry" in updated
    assert updated["canonical_cockpit_surface_registry"]["authority"]["runtime_authority"] == "blocked"
