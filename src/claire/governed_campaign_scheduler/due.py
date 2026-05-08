from __future__ import annotations

from typing import List

from .models import CampaignSchedule
from .time_utils import is_due


class DueCampaignSelector:
    def select_due(self, schedules: List[CampaignSchedule], now_value: str | None = None) -> List[CampaignSchedule]:
        return [
            schedule
            for schedule in schedules
            if schedule.enabled and is_due(schedule.next_due_at, now_value=now_value)
        ]
