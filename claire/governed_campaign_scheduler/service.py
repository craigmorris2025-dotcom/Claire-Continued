from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from claire.persistent_internet_campaigns.service import PersistentInternetCampaignService

from .due import DueCampaignSelector
from .lock import SchedulerLock
from .models import CampaignSchedule, SchedulerRunReport
from .store import SchedulerStore
from .time_utils import add_minutes, utc_now


class GovernedCampaignSchedulerService:
    def __init__(
        self,
        store: SchedulerStore | None = None,
        campaign_service: PersistentInternetCampaignService | None = None,
        lock: SchedulerLock | None = None,
    ) -> None:
        self.store = store or SchedulerStore()
        self.campaign_service = campaign_service or PersistentInternetCampaignService()
        self.lock = lock or SchedulerLock(self.store.root)
        self.selector = DueCampaignSelector()

    def set_schedule(
        self,
        campaign_id: str,
        cadence_minutes: int = 1440,
        enabled: bool = True,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        if cadence_minutes < 1:
            raise ValueError("cadence_minutes must be at least 1")

        existing = self.store.load_schedule(campaign_id)
        if existing:
            schedule = existing
            schedule.cadence_minutes = cadence_minutes
            schedule.enabled = enabled
            schedule.max_results = max_results
        else:
            schedule = CampaignSchedule(
                campaign_id=campaign_id,
                enabled=enabled,
                cadence_minutes=cadence_minutes,
                max_results=max_results,
            )

        if schedule.next_due_at is None:
            schedule.next_due_at = utc_now()

        self.store.save_schedule(schedule)
        self.store.audit("schedule_set", schedule.to_dict())
        return schedule.to_dict()

    def list_schedules(self) -> List[Dict[str, Any]]:
        return [schedule.to_dict() for schedule in self.store.list_schedules()]

    async def run_due_once(self, limit: Optional[int] = None) -> Dict[str, Any]:
        run_id = "scheduler_run_" + hashlib.sha256(utc_now().encode("utf-8")).hexdigest()[:16]
        lock_result = self.lock.acquire(run_id)

        if not lock_result.get("acquired"):
            report = SchedulerRunReport(
                scheduler_run_id=run_id,
                status="locked",
                due_count=0,
                refreshed_count=0,
                skipped_count=0,
                failed_count=0,
                lock_acquired=False,
            )
            report.finished_at = utc_now()
            self.store.save_report(report)
            return {"report": report.to_dict(), "lock": lock_result}

        report = SchedulerRunReport(
            scheduler_run_id=run_id,
            status="running",
            due_count=0,
            refreshed_count=0,
            skipped_count=0,
            failed_count=0,
            lock_acquired=True,
        )

        try:
            schedules = self.store.list_schedules()
            due = self.selector.select_due(schedules)
            if limit is not None:
                due = due[:limit]
            report.due_count = len(due)

            for schedule in due:
                try:
                    result = await self.campaign_service.refresh_campaign(schedule.campaign_id)
                    schedule.last_run_at = utc_now()
                    schedule.next_due_at = add_minutes(schedule.last_run_at, schedule.cadence_minutes)
                    self.store.save_schedule(schedule)
                    report.refreshed_count += 1
                    report.refreshed_campaign_ids.append(schedule.campaign_id)
                except Exception as exc:
                    report.failed_count += 1
                    report.failed_campaigns.append({
                        "campaign_id": schedule.campaign_id,
                        "error": str(exc),
                    })

            report.skipped_count = max(0, len(schedules) - report.due_count)
            report.status = "completed" if report.failed_count == 0 else "completed_with_failures"
            report.finished_at = utc_now()
            self.store.save_report(report)
            self.store.audit("scheduler_run", report.to_dict())
            return {"report": report.to_dict()}
        finally:
            self.lock.release()

    def run_due_once_sync(self, limit: Optional[int] = None) -> Dict[str, Any]:
        import asyncio
        return asyncio.run(self.run_due_once(limit=limit))

    def list_reports(self, limit: int = 25) -> List[Dict[str, Any]]:
        return self.store.list_reports(limit=limit)

    def lock_status(self) -> Dict[str, object]:
        return self.lock.status()
