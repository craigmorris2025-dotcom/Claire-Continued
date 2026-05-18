from __future__ import annotations

from fastapi.testclient import TestClient


def test_dashboard_payload_exposes_uploaded_docs_end_state_alignment():
    from claire.app import create_app

    client = TestClient(create_app())
    payload = client.get("/dashboard/payload").json()

    assert payload["backend_owns_truth"] is True
    assert payload["runtime_focus"] == "governed_signal_governance_and_trend_discovery"

    alignment = payload["end_state_alignment"]
    assert alignment["system_identity"]["product_center"] == "canonical_lifecycle_runtime"
    assert alignment["operating_model"]["default_path"][:2] == [
        "signal_governance",
        "trend_discovery",
    ]
    assert alignment["route_policy"]["breakthrough_is_default"] is False
    assert alignment["route_policy"]["portfolio_is_normal_early_path"] is True
    assert alignment["runtime_spine"]["stage_count"] == 30
