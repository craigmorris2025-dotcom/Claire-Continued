from __future__ import annotations

from fastapi.testclient import TestClient


def test_dashboard_v4_payload_normalizes_current_and_future_payloads():
    from claire.dashboard.payload_compatibility import normalize_dashboard_payload

    payload = normalize_dashboard_payload(
        {
            "backend_owns_truth": True,
            "runtime_focus": "governed_signal_governance_and_trend_discovery",
            "lifecycle": {"stage_count": 30, "stages": []},
            "operating_model": {
                "default_path": [
                    "signal_governance",
                    "trend_discovery",
                    "thesis_formation",
                    "portfolio_creation_optimization",
                ],
                "acquisition_path": "downstream_package_after_portfolio_and_fit_validation",
            },
            "route_policy": {
                "breakthrough_is_default": False,
                "portfolio_is_normal_early_path": True,
                "operator_review_required_for_escalation": True,
            },
            "future_unknown_payload": {"still": "retained"},
        }
    )

    assert payload["schema_version"] == "claire_dashboard_payload_v4"
    assert payload["completion_percent"] == 100
    assert payload["scores"]["future_payload_compatibility"] == 100
    assert payload["domains"]["future_payloads"]["signals"]["raw_key_count"] >= 1
    assert payload["raw_payload"]["future_unknown_payload"]["still"] == "retained"


def test_dashboard_v4_routes_and_assets_mount_through_create_app():
    from claire.app import create_app

    client = TestClient(create_app())

    assert client.get("/api/dashboard/v4/payload").status_code == 200
    assert client.get("/dashboard/v4").status_code == 200
    assert client.get("/dashboard/operator-v4").status_code == 200
    assert client.get("/dashboard/v4/assets/dashboard_v4.css").status_code == 200
    assert client.get("/dashboard/v4/assets/dashboard_v4.js").status_code == 200

    payload = client.get("/api/dashboard/v4/payload").json()
    assert payload["completion_percent"] == 100
    assert payload["scores"]["dashboard_functionality"] == 100
    assert payload["scores"]["repository_organization"] == 100


def test_complete_system_gate_reports_all_categories_at_100():
    from tools.plateau.complete_system_gate import run_gate

    report = run_gate()

    assert report["status"] == "complete"
    assert report["completion_percent"] == 100
    assert set(report["scores"].values()) == {100}
    assert report["plateau_lock"]["plateau_ready"] is True
