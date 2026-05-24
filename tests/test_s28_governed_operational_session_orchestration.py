from __future__ import annotations

import importlib


def test_s28_session_orchestration_preserves_blocked_authority():
    module = importlib.import_module("runtime_core.api.governed_operational_session_orchestration")

    result = module.build_governed_operational_session_orchestration({})

    assert result["version"] == "v19.89.8-S28"
    assert result["status"] == "active"
    assert result["authority"]["backend_owns_truth"] is True
    assert result["authority"]["cockpit_presentation_only"] is True
    assert result["authority"]["runtime_authority"] == "blocked"
    assert result["authority"]["browser_execution_authority"] == "blocked"
    assert result["authority"]["autonomous_execution_expansion"] is False
    assert result["authority"]["runtime_mutation_enabled"] is False


def test_s28_detects_stale_and_degraded_session_visibility():
    module = importlib.import_module("runtime_core.api.governed_operational_session_orchestration")

    result = module.build_governed_operational_session_orchestration(
        {
            "browser_session_persistence": {
                "session_id": "test-session",
                "stale": True,
            },
            "runtime_continuity_visualization": {
                "degraded": True,
            },
        }
    )

    assert result["summary"]["session_id"] == "test-session"
    assert result["summary"]["orchestration_state"] == "degraded"
    assert result["summary"]["stale_session_detected"] is True
    assert result["summary"]["degraded_session_detected"] is True
    assert result["recovery_visibility"]["automatic_recovery_enabled"] is False
    assert result["recovery_visibility"]["automatic_runtime_mutation_enabled"] is False


def test_s28_route_module_imports_without_app_factory_patch():
    module = importlib.import_module("runtime_core.api.governed_operational_session_orchestration_routes")

    assert hasattr(module, "router")
    assert module.router.prefix == "/api/governed/session-orchestration"
