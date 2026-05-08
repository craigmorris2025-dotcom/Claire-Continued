from pathlib import Path

import pytest

from claire.governed_campaign_scheduler.service import GovernedCampaignSchedulerService
from claire.governed_campaign_scheduler.store import SchedulerStore
from claire.governed_campaign_scheduler.lock import SchedulerLock
from claire.governed_campaign_scheduler.due import DueCampaignSelector
from claire.governed_campaign_scheduler.models import CampaignSchedule


class FakeCampaignService:
    def __init__(self):
        self.refreshed = []

    async def refresh_campaign(self, campaign_id: str):
        self.refreshed.append(campaign_id)
        return {"campaign": {"campaign_id": campaign_id}, "refresh_report": {"status": "completed"}}


def test_set_schedule(tmp_path: Path):
    service = GovernedCampaignSchedulerService(
        store=SchedulerStore(tmp_path),
        campaign_service=FakeCampaignService(),
        lock=SchedulerLock(tmp_path),
    )
    schedule = service.set_schedule("campaign_test", cadence_minutes=60)

    assert schedule["campaign_id"] == "campaign_test"
    assert schedule["cadence_minutes"] == 60
    assert schedule["enabled"] is True


def test_due_selector():
    selector = DueCampaignSelector()
    schedules = [
        CampaignSchedule(campaign_id="a", next_due_at=None, enabled=True),
        CampaignSchedule(campaign_id="b", next_due_at="2999-01-01T00:00:00Z", enabled=True),
        CampaignSchedule(campaign_id="c", next_due_at=None, enabled=False),
    ]
    due = selector.select_due(schedules)

    assert [item.campaign_id for item in due] == ["a"]


@pytest.mark.asyncio
async def test_run_due_once_refreshes_due_campaign(tmp_path: Path):
    fake = FakeCampaignService()
    service = GovernedCampaignSchedulerService(
        store=SchedulerStore(tmp_path),
        campaign_service=fake,
        lock=SchedulerLock(tmp_path),
    )
    service.set_schedule("campaign_due", cadence_minutes=60)

    result = await service.run_due_once()

    assert result["report"]["status"] == "completed"
    assert result["report"]["refreshed_count"] == 1
    assert fake.refreshed == ["campaign_due"]


@pytest.mark.asyncio
async def test_lock_prevents_overlap(tmp_path: Path):
    fake = FakeCampaignService()
    lock = SchedulerLock(tmp_path)
    service = GovernedCampaignSchedulerService(
        store=SchedulerStore(tmp_path),
        campaign_service=fake,
        lock=lock,
    )
    lock.acquire("other")

    result = await service.run_due_once()

    assert result["report"]["status"] == "locked"
    assert result["report"]["lock_acquired"] is False
