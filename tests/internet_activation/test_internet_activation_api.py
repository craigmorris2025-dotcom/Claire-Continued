from fastapi import FastAPI
from fastapi.testclient import TestClient
from claire.internet_activation import api_routes
from claire.internet_activation.service import InternetResearchService


def test_api_route_research_with_mocked_service(monkeypatch):
    app=FastAPI(); app.include_router(api_routes.router)
    async def fake_research(self, query, urls=None, max_results=None):
        return {"layer":"internet_activation","version":"v17.41","run":{"run_id":"test","query":query,"status":"completed","evidence_count":1,"evidence_ids":["ev_test"]},"evidence":[{"evidence_id":"ev_test","claim":"test claim"}]}
    monkeypatch.setattr(InternetResearchService, "research", fake_research)
    response=TestClient(app).post("/research/internet", json={"query":"ai policy","urls":["https://www.sec.gov/newsroom"],"max_results":1})
    assert response.status_code == 200
    assert response.json()["run"]["status"] == "completed"
