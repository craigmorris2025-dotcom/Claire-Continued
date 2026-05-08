from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.governed_campaign_scheduler import api_routes
from claire.governed_campaign_scheduler.service import GovernedCampaignSchedulerService


def test_set_schedule_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_set(self, campaign_id, cadence_minutes=1440, enabled=True, max_results=None):
        return {"campaign_id": campaign_id, "cadence_minutes": cadence_minutes, "enabled": enabled}

    monkeypatch.setattr(GovernedCampaignSchedulerService, "set_schedule", fake_set)

    client = TestClient(app)
    response = client.post(
        "/internet/scheduler/schedule",
        json={"campaign_id": "campaign_test", "cadence_minutes": 60},
    )

    assert response.status_code == 200
    assert response.json()["campaign_id"] == "campaign_test"
    assert response.json()["cadence_minutes"] == 60
