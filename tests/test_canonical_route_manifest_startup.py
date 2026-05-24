from __future__ import annotations

from fastapi.testclient import TestClient
from pathlib import Path

from runtime_core.design.portal import DesignPortal
from runtime_core.lifecycle.lifecycle_runner import CoreLifecycleRunner
from main import app


def test_startup_uses_canonical_route_manifest_not_api_autodiscovery():
    report = getattr(app.state, "claire_route_report", {})

    assert report["mode"] == "canonical_manifest"
    assert len(app.routes) <= 353
    route_paths = {route.path for route in app.routes}
    assert "/api/sources/registry" in route_paths
    assert "/api/search/providers/status" in route_paths
    assert "/api/strategic-world/status" in route_paths
    assert "/api/system/endpoint-reconciliation" in route_paths
    assert "/api/system/industry-standard-endpoint-package" in route_paths
    assert "/api/technology/reemergence-taxonomy" in route_paths
    assert "/api/technology/reemergence-classify" in route_paths
    assert "/api/lifecycle/center-route-contract" in route_paths
    assert "/api/lifecycle/route-contracts" in route_paths
    assert "/api/lifecycle/select-route" in route_paths
    assert not any("routes_dashboard_v4" in item for item in report.get("included_modules", []))
    assert not any("routes_dashboard_v5" in item for item in report.get("included_modules", []))
    assert not any(item.get("module") == "claire.api" for item in report.get("skipped_modules", []))


def test_legacy_dashboard_generations_are_not_mounted_by_default():
    client = TestClient(app)

    for path in ["/dashboard/v4", "/dashboard/v5", "/dashboard/operator-v4", "/dashboard/final-user"]:
        assert client.get(path).status_code == 404


def test_operational_readiness_measures_usefulness_not_only_safety():
    client = TestClient(app)
    payload = client.get("/api/operational/readiness").json()

    assert payload["status"] in {"operational_useful", "operational_gaps_present"}
    assert payload["percent"] == 100
    assert payload["checks"]["lifecycle_30_stage"] is True
    assert payload["checks"]["discovery_candidates_present"] is True
    assert payload["checks"]["portfolio_candidates_present"] is True
    assert "governed_provider_ready" in payload["checks"]
    assert payload["readiness_definition"].startswith("usefulness")


def test_dashboard_platform_completion_uses_operational_proof_not_surface_binding():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    assert payload["platform_completion"]["pass_name"] == "operational_readiness_proof"
    assert payload["surface_completion"]["pass_name"] == "dashboard_surface_binding"
    assert payload["platform_completion"]["percent"] <= payload["surface_completion"]["percent"]
    assert "Surface completion" in payload["surface_completion"]["note"]


def test_dashboard_state_exposes_project_file_bindings():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    bindings = payload["project_file_bindings"]
    assert bindings["bound_count"] > 0
    assert "project_files" in payload["records"]
    paths = {item["path"] for item in bindings["bindings"]}
    assert "data/continuous_runtime/portfolio_candidates.json" in paths
    assert "data/source_universes/universe_index.json" in paths
    assert payload["metrics"]["project_files_bound"]["value"] == bindings["bound_count"]


def test_canonical_dashboard_does_not_ship_obvious_demo_claims():
    root = Path(__file__).resolve().parents[1]
    js = (root / "frontend" / "command_center" / "modern" / "platform_dashboard.js").read_text(encoding="utf-8")
    html = (root / "frontend" / "command_center" / "modern" / "platform_dashboard.html").read_text(encoding="utf-8")
    combined = js + "\n" + html

    for phrase in [
        "Force Breakthrough",
        "HYBRID MODE ACTIVE",
        "ALL SYSTEMS NOMINAL",
        "99.97%",
        "CYCLE 1847",
        "Singularity-Aligned",
        "Acquirer Fit: Google, MSFT",
        "Strategic Timing: NOW",
        "PCO #247",
        "BO #244",
    ]:
        assert phrase not in combined


def test_intelligence_modes_define_deterministic_connected_and_hybrid():
    client = TestClient(app)
    payload = client.get("/api/intelligence/modes").json()

    modes = payload["operator_selectable_modes"]
    assert set(modes) == {"deterministic", "connected", "hybrid"}
    assert modes["deterministic"]["enabled"] is True
    assert payload["platform_mode_completion_percent"] == 100
    assert payload["activation_mode_completion_percent"] == 100
    assert payload["live_execution_completion_percent"] == 100
    assert modes["connected"]["operator_surface_ready"] is True
    assert modes["hybrid"]["operator_surface_ready"] is True
    assert modes["connected"]["activation_ready"] is True
    assert modes["hybrid"]["activation_ready"] is True
    assert "governed_provider_not_ready" in modes["connected"]["blockers"] or modes["connected"]["enabled"] is True
    assert payload["active_mode"] in {"deterministic", "connected", "hybrid"}
    assert payload["operator_workflow_order"][0] == "finish_platform_and_dashboard_operator_surface"


def test_design_portal_preserves_portfolio_recommendation():
    result = DesignPortal().evaluate({
        "scores": {"breakthrough_score": 0.92, "_confidence": 0.91, "portfolio_score": 0.88},
        "system_design": {"status": "success"},
        "market_gap": {"status": "success"},
        "thesis_formation": {"route_recommendation": "portfolio_intelligence"},
    })

    assert result["route_to_design"] is False
    assert result["status"] == "not_ready"
    assert "portfolio path preserved" in result["reason"]


def test_lifecycle_route_detection_requires_explicit_design_recommendation():
    runner = CoreLifecycleRunner()
    outputs = {
        "design_portal": {"route_to_design": True},
        "design_output": {"status": "success"},
        "thesis_formation": {"route_recommendation": "portfolio_intelligence"},
    }

    assert runner.detect_route(outputs) == "portfolio_creation_optimization"

    outputs["thesis_formation"]["route_recommendation"] = "breakthrough_escalation_candidate"
    assert runner.detect_route(outputs) == "breakthrough_design"
