from claire.internet_operations_dashboard.payloads import DashboardPayloadBuilder
from claire.internet_operations_dashboard.service import InternetOperationsDashboardService


class FakeCampaigns:
    def list_campaigns(self):
        return [{"campaign_id": "c1", "name": "Campaign"}]


class FakeScheduler:
    def list_schedules(self):
        return [{"campaign_id": "c1", "cadence_minutes": 1440}]

    def list_reports(self):
        return [{"scheduler_run_id": "r1", "status": "completed"}]


class FakeStability:
    def health(self):
        return {"status": "healthy"}

    async def run_scheduler_due_with_recovery(self, limit=None):
        return {"status": "completed"}


class FakeTrust:
    def list_profiles(self):
        return [{"domain": "sec.gov", "status": "active"}]

    def list_events(self, domain=None, limit=25):
        return [{"domain": "sec.gov", "event_type": "confirmed"}]


def test_payload_builder_snapshot():
    builder = DashboardPayloadBuilder()
    snap = builder.build(
        campaigns=[{"campaign_id": "c1"}],
        schedules=[{"campaign_id": "c1"}],
        scheduler_reports=[],
        stability={"status": "healthy"},
        source_trust_profiles=[],
        source_trust_events=[],
    )
    assert snap["status"] == "healthy"
    assert len(snap["panels"]) == 6


def test_dashboard_service_snapshot():
    service = InternetOperationsDashboardService(
        campaign_service=FakeCampaigns(),
        scheduler_service=FakeScheduler(),
        stability_service=FakeStability(),
        source_trust_service=FakeTrust(),
    )
    snap = service.snapshot()
    assert snap["campaigns"][0]["campaign_id"] == "c1"
    assert snap["stability"]["status"] == "healthy"
    assert snap["source_trust_profiles"][0]["domain"] == "sec.gov"
