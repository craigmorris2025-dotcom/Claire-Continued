from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.internet_runtime_stability import api_routes
from claire.internet_runtime_stability.service import InternetRuntimeStabilityService


def test_health_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_health(self):
        return {"status": "healthy"}

    monkeypatch.setattr(InternetRuntimeStabilityService, "health", fake_health)

    client = TestClient(app)
    response = client.get("/internet/stability/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
