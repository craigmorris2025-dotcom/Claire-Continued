from pathlib import Path

import pytest

from claire.persistent_internet_campaigns.service import PersistentInternetCampaignService
from claire.persistent_internet_campaigns.store import CampaignStore
from claire.persistent_internet_campaigns.drift import EvidenceDriftDetector


class FakeIntegrationService:
    async def run_and_build_dashboard(self, query, run_id, lifecycle_stage="research", urls=None, max_results=None, core_output_path=None):
        return {
            "internet_output": {
                "internet_activation_result": {
                    "run": {
                        "status": "completed",
                        "warnings": [],
                        "errors": [],
                    },
                    "evidence": [
                        {
                            "evidence_id": "ev_new",
                            "source_url": "https://www.sec.gov/newsroom",
                            "source_domain": "sec.gov",
                            "confidence": 0.88,
                            "source_reliability": 0.96,
                        }
                    ],
                }
            },
            "dashboard_payload": {
                "status": "completed",
                "evidence_count": 1,
            },
        }


def test_create_campaign(tmp_path: Path):
    service = PersistentInternetCampaignService(
        store=CampaignStore(tmp_path),
        integration_service=FakeIntegrationService(),
    )
    campaign = service.create_campaign(
        name="AI Policy Watch",
        query="AI disclosure rules",
        urls=["https://www.sec.gov/newsroom"],
    )

    assert campaign["campaign_id"].startswith("campaign_")
    assert campaign["query"] == "AI disclosure rules"
    assert campaign["urls"] == ["https://www.sec.gov/newsroom"]


@pytest.mark.asyncio
async def test_refresh_campaign_creates_report(tmp_path: Path):
    service = PersistentInternetCampaignService(
        store=CampaignStore(tmp_path),
        integration_service=FakeIntegrationService(),
    )
    campaign = service.create_campaign(
        name="AI Policy Watch",
        query="AI disclosure rules",
        urls=["https://www.sec.gov/newsroom"],
    )

    result = await service.refresh_campaign(campaign["campaign_id"])

    assert result["refresh_report"]["new_evidence_count"] == 1
    assert result["campaign"]["refresh_count"] == 1
    assert result["campaign"]["evidence_ids"] == ["ev_new"]


def test_drift_detector_detects_source_change():
    detector = EvidenceDriftDetector()
    result = detector.compare(
        [{"evidence_id": "a", "source_url": "https://old.example", "confidence": 0.5}],
        [{"evidence_id": "b", "source_url": "https://new.example", "confidence": 0.7}],
    )

    assert result["drift_status"] in {"confidence_shift", "source_change", "new_evidence"}
    assert result["confidence_delta"] == 0.2
