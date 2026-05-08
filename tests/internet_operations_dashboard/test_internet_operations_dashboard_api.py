from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.internet_operations_dashboard import api_routes
from claire.internet_operations_dashboard.service import InternetOperationsDashboardService


def test_snapshot_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_snapshot(self):
        return {"status": "healthy", "panels": []}

    monkeypatch.setattr(InternetOperationsDashboardService, "snapshot", fake_snapshot)

    client = TestClient(app)
    response = client.get("/internet/ops/snapshot")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_page_route():
    app = FastAPI()
    app.include_router(api_routes.router)

    client = TestClient(app)
    response = client.get("/internet/ops/dashboard")
    assert response.status_code == 200
    assert "Claire Internet Operations Dashboard" in response.text
