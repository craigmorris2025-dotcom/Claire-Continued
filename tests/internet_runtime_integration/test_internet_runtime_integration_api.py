from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.internet_runtime_integration import api_routes
from claire.internet_runtime_integration.integration_service import InternetRuntimeIntegrationService


def test_runtime_internet_dashboard_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    async def fake_run_and_build_dashboard(self, query, run_id, lifecycle_stage="research", urls=None, max_results=None, core_output_path=None):
        return {"dashboard_payload": {"panel": "internet_research", "status": "completed", "query": query, "evidence_count": 1}}

    monkeypatch.setattr(InternetRuntimeIntegrationService, "run_and_build_dashboard", fake_run_and_build_dashboard)
    client = TestClient(app)
    response = client.post("/runtime/internet/dashboard", json={"query": "AI disclosure", "run_id": "core_run_api", "urls": ["https://www.sec.gov/newsroom"], "max_results": 1})
    assert response.status_code == 200
    assert response.json()["panel"] == "internet_research"
    assert response.json()["evidence_count"] == 1
