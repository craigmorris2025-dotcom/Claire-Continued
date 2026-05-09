from __future__ import annotations

from typing import Any, Dict

from claire.dynamic_source_trust.service import DynamicSourceTrustService
from claire.governed_campaign_scheduler.service import GovernedCampaignSchedulerService
from claire.internet_runtime_stability.service import InternetRuntimeStabilityService
from claire.persistent_internet_campaigns.service import PersistentInternetCampaignService

from .payloads import DashboardPayloadBuilder


class InternetOperationsDashboardService:
    def __init__(
        self,
        campaign_service: PersistentInternetCampaignService | None = None,
        scheduler_service: GovernedCampaignSchedulerService | None = None,
        stability_service: InternetRuntimeStabilityService | None = None,
        source_trust_service: DynamicSourceTrustService | None = None,
    ) -> None:
        self.campaign_service = campaign_service or PersistentInternetCampaignService()
        self.scheduler_service = scheduler_service or GovernedCampaignSchedulerService()
        self.stability_service = stability_service or InternetRuntimeStabilityService()
        self.source_trust_service = source_trust_service or DynamicSourceTrustService()
        self.builder = DashboardPayloadBuilder()

    def snapshot(self) -> Dict[str, Any]:
        campaigns = self._safe(self.campaign_service.list_campaigns, [])
        schedules = self._safe(self.scheduler_service.list_schedules, [])
        scheduler_reports = self._safe(self.scheduler_service.list_reports, [])
        stability = self._safe(self.stability_service.health, {"status": "unknown"})
        profiles = self._safe(self.source_trust_service.list_profiles, [])
        events = self._safe(lambda: self.source_trust_service.list_events(limit=25), [])

        return self.builder.build(
            campaigns=campaigns,
            schedules=schedules,
            scheduler_reports=scheduler_reports,
            stability=stability,
            source_trust_profiles=profiles,
            source_trust_events=events,
        )

    async def run_due_and_snapshot(self, limit: int | None = None) -> Dict[str, Any]:
        run_result = await self.stability_service.run_scheduler_due_with_recovery(limit=limit)
        snap = self.snapshot()
        snap["last_operation"] = {"operation": "run_due_with_recovery", "result": run_result}
        return snap

    async def refresh_campaign_and_snapshot(self, campaign_id: str) -> Dict[str, Any]:
        refresh_result = await self.stability_service.refresh_campaign_with_recovery(campaign_id)
        snap = self.snapshot()
        snap["last_operation"] = {
            "operation": "refresh_campaign_with_recovery",
            "campaign_id": campaign_id,
            "result": refresh_result,
        }
        return snap

    def _safe(self, fn, fallback):
        try:
            return fn()
        except Exception:
            return fallback
