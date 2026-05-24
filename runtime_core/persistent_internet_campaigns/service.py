from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_core.internet_runtime_integration import InternetRuntimeIntegrationService

from .drift import EvidenceDriftDetector
from .models import CampaignRefreshReport, InternetCampaign
from .models import utc_now
from .store import CampaignStore


class PersistentInternetCampaignService:
    def __init__(
        self,
        store: CampaignStore | None = None,
        integration_service: InternetRuntimeIntegrationService | None = None,
    ) -> None:
        self.store = store or CampaignStore()
        self.integration_service = integration_service or InternetRuntimeIntegrationService()
        self.drift = EvidenceDriftDetector()

    def create_campaign(
        self,
        name: str,
        query: str,
        urls: Optional[List[str]] = None,
        cadence: str = "manual",
        max_results: int = 5,
        notes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not name.strip():
            raise ValueError("campaign name is required")
        if not query.strip():
            raise ValueError("campaign query is required")

        campaign_id = "campaign_" + hashlib.sha256(f"{name}|{query}".encode("utf-8")).hexdigest()[:16]
        existing = self.store.load_campaign(campaign_id)
        if existing is not None:
            return existing.to_dict()

        campaign = InternetCampaign(
            campaign_id=campaign_id,
            name=name.strip(),
            query=query.strip(),
            urls=urls or [],
            cadence=cadence,
            max_results=max(1, max_results),
            notes=notes or [],
        )
        self.store.save_campaign(campaign)
        self.store.audit("campaign_created", campaign.to_dict())
        return campaign.to_dict()

    async def refresh_campaign(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self.store.load_campaign(campaign_id)
        if campaign is None:
            raise ValueError(f"Campaign not found: {campaign_id}")

        previous_evidence = self._load_existing_evidence(campaign.evidence_ids)
        previous_count = len(previous_evidence)
        previous_avg = self.drift.average_confidence(previous_evidence)

        result = await self.integration_service.run_and_build_dashboard(
            query=campaign.query,
            run_id=campaign.campaign_id,
            lifecycle_stage="persistent_campaign_refresh",
            urls=campaign.urls or None,
            max_results=campaign.max_results,
        )

        internet_output = result.get("internet_output", {})
        activation = internet_output.get("internet_activation_result", {})
        new_evidence = activation.get("evidence", [])
        new_ids = [str(item.get("evidence_id")) for item in new_evidence if item.get("evidence_id")]

        all_ids = list(dict.fromkeys(campaign.evidence_ids + new_ids))
        drift = self.drift.compare(previous_evidence, new_evidence)

        campaign.evidence_ids = all_ids
        campaign.refresh_count += 1
        campaign.last_refresh_at = utc_now()
        campaign.average_confidence = float(drift["new_average_confidence"]) if new_evidence else previous_avg
        self.store.save_campaign(campaign)

        report_id = "refresh_" + hashlib.sha256(
            f"{campaign.campaign_id}|{campaign.refresh_count}|{campaign.last_refresh_at}".encode("utf-8")
        ).hexdigest()[:16]
        activation_run = activation.get("run", {})

        report = CampaignRefreshReport(
            report_id=report_id,
            campaign_id=campaign.campaign_id,
            campaign_name=campaign.name,
            query=campaign.query,
            status=str(activation_run.get("status", "unknown")),
            previous_evidence_count=previous_count,
            new_evidence_count=len(new_evidence),
            total_evidence_count=len(all_ids),
            previous_average_confidence=previous_avg,
            new_average_confidence=float(drift["new_average_confidence"]),
            confidence_delta=float(drift["confidence_delta"]),
            new_sources=list(drift["new_sources"]),
            repeated_sources=list(drift["repeated_sources"]),
            removed_sources=list(drift["removed_sources"]),
            drift_status=str(drift["drift_status"]),
            warnings=list(activation_run.get("warnings", [])),
            errors=list(activation_run.get("errors", [])),
        )
        self.store.save_report(report)
        self.store.audit("campaign_refreshed", report.to_dict())

        return {
            "campaign": campaign.to_dict(),
            "refresh_report": report.to_dict(),
            "runtime_result": result,
        }

    def refresh_campaign_sync(self, campaign_id: str) -> Dict[str, Any]:
        import asyncio
        return asyncio.run(self.refresh_campaign(campaign_id))

    def list_campaigns(self) -> List[Dict[str, Any]]:
        return self.store.list_campaigns()

    def list_reports(self, campaign_id: str | None = None) -> List[Dict[str, Any]]:
        return self.store.list_reports(campaign_id=campaign_id)

    def _load_existing_evidence(self, evidence_ids: List[str]) -> List[Dict[str, Any]]:
        root = Path("data") / "internet_activation" / "evidence"
        records = []
        for evidence_id in evidence_ids:
            path = root / f"{evidence_id}.json"
            if not path.exists():
                continue
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return records
