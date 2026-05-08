from __future__ import annotations

import hashlib
from typing import Any, Awaitable, Callable, Dict, List, Optional

from claire.governed_campaign_scheduler.service import GovernedCampaignSchedulerService
from claire.persistent_internet_campaigns.service import PersistentInternetCampaignService

from .classifier import FailureClassifier
from .health import InternetRuntimeHealthChecker
from .journal import RecoveryJournal
from .models import FailureRecord, RetryPolicy, StabilityRunReport
from .models import utc_now


class InternetRuntimeStabilityService:
    def __init__(
        self,
        retry_policy: RetryPolicy | None = None,
        journal: RecoveryJournal | None = None,
        campaign_service: PersistentInternetCampaignService | None = None,
        scheduler_service: GovernedCampaignSchedulerService | None = None,
    ) -> None:
        self.retry_policy = retry_policy or RetryPolicy()
        self.classifier = FailureClassifier(self.retry_policy)
        self.journal = journal or RecoveryJournal()
        self.campaign_service = campaign_service or PersistentInternetCampaignService()
        self.scheduler_service = scheduler_service or GovernedCampaignSchedulerService(campaign_service=self.campaign_service)
        self.health_checker = InternetRuntimeHealthChecker()

    async def refresh_campaign_with_recovery(self, campaign_id: str) -> Dict[str, Any]:
        async def op():
            return await self.campaign_service.refresh_campaign(campaign_id)

        return await self._run_with_recovery(
            operation_type="campaign_refresh",
            target_id=campaign_id,
            operation=op,
        )

    async def run_scheduler_due_with_recovery(self, limit: Optional[int] = None) -> Dict[str, Any]:
        async def op():
            return await self.scheduler_service.run_due_once(limit=limit)

        return await self._run_with_recovery(
            operation_type="scheduler_run_due",
            target_id="due_campaigns",
            operation=op,
        )

    async def _run_with_recovery(
        self,
        operation_type: str,
        target_id: str,
        operation: Callable[[], Awaitable[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        run_id = "stability_" + hashlib.sha256(f"{operation_type}|{target_id}|{utc_now()}".encode("utf-8")).hexdigest()[:16]
        report = StabilityRunReport(
            stability_run_id=run_id,
            status="running",
            operation_type=operation_type,
        )

        last_result: Dict[str, Any] | None = None

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            report.attempted_count += 1
            try:
                result = await operation()
                last_result = result
                status = self._extract_status(result)

                if self._is_success(status):
                    report.succeeded_count += 1
                    report.recovered_count = max(0, attempt - 1)
                    report.status = "completed" if attempt == 1 else "recovered"
                    report.results.append(result)
                    break

                classification = self.classifier.classify(status, message=str(result))
                failure = self._failure_record(
                    run_id=run_id,
                    operation_type=operation_type,
                    target_id=target_id,
                    status=status,
                    classification=classification,
                    attempt=attempt,
                    message=str(result)[:1000],
                )
                self._record_failure(report, failure)

                if not classification["retryable"] or attempt >= self.retry_policy.max_attempts:
                    report.status = "degraded" if self._degraded_allowed(status) else "failed"
                    report.degraded_mode = report.status == "degraded"
                    report.results.append(result)
                    break

                report.retry_count += 1
            except Exception as exc:
                classification = self.classifier.classify("failed", message=str(exc))
                failure = self._failure_record(
                    run_id=run_id,
                    operation_type=operation_type,
                    target_id=target_id,
                    status="exception",
                    classification=classification,
                    attempt=attempt,
                    message=str(exc),
                )
                self._record_failure(report, failure)

                if attempt >= self.retry_policy.max_attempts:
                    report.status = "failed"
                    break

                report.retry_count += 1

        report.finished_at = utc_now()
        if report.status == "running":
            report.status = "failed"

        report_dict = report.to_dict()
        self.journal.save_report(report_dict)
        self.journal.audit("stability_run_completed", report_dict)
        return report_dict

    def _extract_status(self, result: Dict[str, Any]) -> str:
        if "refresh_report" in result:
            return str(result["refresh_report"].get("status", "unknown"))
        if "report" in result:
            return str(result["report"].get("status", "unknown"))
        if "run" in result:
            return str(result["run"].get("status", "unknown"))
        return str(result.get("status", "unknown"))

    def _is_success(self, status: str) -> bool:
        return status in {"completed", "recovered"}

    def _degraded_allowed(self, status: str) -> bool:
        return status in {"completed_no_evidence", "not_configured", "review_required"}

    def _failure_record(
        self,
        run_id: str,
        operation_type: str,
        target_id: str,
        status: str,
        classification: Dict[str, object],
        attempt: int,
        message: str,
    ) -> FailureRecord:
        return FailureRecord(
            operation_id=run_id,
            operation_type=operation_type,
            target_id=target_id,
            status=status,
            category=str(classification["category"]),
            message=message,
            attempt=attempt,
            retryable=bool(classification["retryable"]),
        )

    def _record_failure(self, report: StabilityRunReport, failure: FailureRecord) -> None:
        self.journal.save_failure(failure)
        report.failures.append(failure.to_dict())
        report.failed_count += 1

    def health(self) -> Dict[str, object]:
        return self.health_checker.check()

    def list_failures(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.journal.list_failures(limit=limit)

    def list_reports(self, limit: int = 25) -> List[Dict[str, Any]]:
        return self.journal.list_reports(limit=limit)
