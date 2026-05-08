from pathlib import Path

import pytest

from claire.internet_runtime_stability.classifier import FailureClassifier
from claire.internet_runtime_stability.health import InternetRuntimeHealthChecker
from claire.internet_runtime_stability.journal import RecoveryJournal
from claire.internet_runtime_stability.models import RetryPolicy
from claire.internet_runtime_stability.service import InternetRuntimeStabilityService


class FlakyCampaignService:
    def __init__(self):
        self.calls = 0

    async def refresh_campaign(self, campaign_id):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary timeout")
        return {
            "refresh_report": {
                "status": "completed",
                "campaign_id": campaign_id,
            }
        }


class AlwaysDegradedCampaignService:
    async def refresh_campaign(self, campaign_id):
        return {
            "refresh_report": {
                "status": "not_configured",
                "campaign_id": campaign_id,
            }
        }


def test_failure_classifier_governance_block_not_retryable():
    classifier = FailureClassifier()
    result = classifier.classify("review_required", "unknown domain")
    assert result["category"] == "governance_block"
    assert result["retryable"] is False


@pytest.mark.asyncio
async def test_recovery_after_retry(tmp_path: Path):
    service = InternetRuntimeStabilityService(
        retry_policy=RetryPolicy(max_attempts=3),
        journal=RecoveryJournal(tmp_path),
        campaign_service=FlakyCampaignService(),
    )

    result = await service.refresh_campaign_with_recovery("campaign_test")

    assert result["status"] == "recovered"
    assert result["retry_count"] == 1
    assert result["succeeded_count"] == 1


@pytest.mark.asyncio
async def test_degraded_mode_for_not_configured(tmp_path: Path):
    service = InternetRuntimeStabilityService(
        retry_policy=RetryPolicy(max_attempts=2),
        journal=RecoveryJournal(tmp_path),
        campaign_service=AlwaysDegradedCampaignService(),
    )

    result = await service.refresh_campaign_with_recovery("campaign_test")

    assert result["status"] == "degraded"
    assert result["degraded_mode"] is True


def test_journal_saves_reports_and_failures(tmp_path: Path):
    journal = RecoveryJournal(tmp_path)
    journal.save_report({"stability_run_id": "abc", "status": "completed"})
    reports = journal.list_reports()
    assert reports[0]["stability_run_id"] == "abc"


def test_health_checker_reports_missing_paths(tmp_path: Path):
    checker = InternetRuntimeHealthChecker(project_root=tmp_path)
    result = checker.check()
    assert result["status"] == "not_ready"
    assert result["missing_required_paths"]
