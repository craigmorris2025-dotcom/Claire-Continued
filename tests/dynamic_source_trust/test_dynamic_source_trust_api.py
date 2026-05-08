from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.dynamic_source_trust import api_routes
from claire.dynamic_source_trust.service import DynamicSourceTrustService


def test_profiles_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_profiles(self):
        return [{"domain": "sec.gov", "adaptive_score": 0.96}]

    monkeypatch.setattr(DynamicSourceTrustService, "list_profiles", fake_profiles)

    client = TestClient(app)
    response = client.get("/internet/source-trust/profiles")

    assert response.status_code == 200
    assert response.json()["profiles"][0]["domain"] == "sec.gov"
