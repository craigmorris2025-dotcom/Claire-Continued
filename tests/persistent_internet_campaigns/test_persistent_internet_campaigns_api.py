from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.persistent_internet_campaigns import api_routes
from claire.persistent_internet_campaigns.service import PersistentInternetCampaignService


def test_create_campaign_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_create(self, name, query, urls=None, cadence="manual", max_results=5, notes=None):
        return {"campaign_id": "campaign_test", "name": name, "query": query, "urls": urls or []}

    monkeypatch.setattr(PersistentInternetCampaignService, "create_campaign", fake_create)

    client = TestClient(app)
    response = client.post(
        "/internet/campaigns",
        json={"name": "AI Watch", "query": "AI disclosure", "urls": ["https://www.sec.gov/newsroom"]},
    )

    assert response.status_code == 200
    assert response.json()["campaign_id"] == "campaign_test"
