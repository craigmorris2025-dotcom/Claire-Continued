# Claire Syntalion Installer
# v17.45 Internet Runtime Stability + Failure Recovery
#
# Adds launch-critical stability around governed internet update operations:
# - retry policy
# - failure classification
# - degraded-mode handling
# - recovery journal
# - operation health checks
# - safe batch execution wrapper
# - CLI and FastAPI routes
#
# Place this file in Claire project root and run:
#
#     python install_v17_45_internet_runtime_stability.py
#
# Then test:
#
#     python -m pytest tests/internet_runtime_stability -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "internet_runtime_stability"
TESTS = ROOT / "tests" / "internet_runtime_stability"
DATA = ROOT / "data" / "internet_runtime_stability"
DOCS = ROOT / "docs" / "internet_runtime_stability"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    print("Installing Claire v17.45 Internet Runtime Stability + Failure Recovery...")

    write_file(LAYER / "__init__.py", '''
from .service import InternetRuntimeStabilityService
from .models import StabilityRunReport, FailureRecord, RetryPolicy
from .classifier import FailureClassifier
from .journal import RecoveryJournal
from .health import InternetRuntimeHealthChecker

__all__ = [
    "InternetRuntimeStabilityService",
    "StabilityRunReport",
    "FailureRecord",
    "RetryPolicy",
    "FailureClassifier",
    "RecoveryJournal",
    "InternetRuntimeHealthChecker",
]
''')

    write_file(LAYER / "models.py", '''
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    retry_statuses: List[str] = field(default_factory=lambda: [
        "timeout",
        "fetch_error",
        "http_error",
        "completed_with_failures",
        "failed",
    ])
    non_retry_statuses: List[str] = field(default_factory=lambda: [
        "blocked",
        "review_required",
        "not_configured",
        "completed",
    ])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FailureRecord:
    operation_id: str
    operation_type: str
    target_id: str
    status: str
    category: str
    message: str
    attempt: int
    retryable: bool
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StabilityRunReport:
    stability_run_id: str
    status: str
    operation_type: str
    attempted_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0
    degraded_count: int = 0
    retry_count: int = 0
    recovered_count: int = 0
    failures: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=utc_now)
    finished_at: Optional[str] = None
    degraded_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
''')

    write_file(LAYER / "classifier.py", '''
from __future__ import annotations

from typing import Any, Dict

from .models import RetryPolicy


class FailureClassifier:
    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self.retry_policy = retry_policy or RetryPolicy()

    def classify(self, status: str, message: str = "") -> Dict[str, object]:
        normalized = (status or "unknown").lower()
        text = (message or "").lower()

        if normalized in {"timeout"} or "timed out" in text or "timeout" in text:
            category = "timeout"
            retryable = True
        elif normalized in {"blocked", "review_required"}:
            category = "governance_block"
            retryable = False
        elif normalized in {"not_configured"}:
            category = "configuration"
            retryable = False
        elif normalized in {"http_error"}:
            category = "remote_http_error"
            retryable = True
        elif normalized in {"fetch_error", "failed", "completed_with_failures"}:
            category = "runtime_failure"
            retryable = True
        elif normalized in {"completed_no_evidence"}:
            category = "no_evidence"
            retryable = False
        else:
            category = "unknown"
            retryable = normalized in self.retry_policy.retry_statuses

        if normalized in self.retry_policy.non_retry_statuses:
            retryable = False

        return {
            "category": category,
            "retryable": retryable,
            "status": normalized,
        }
''')

    write_file(LAYER / "journal.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import FailureRecord
from .models import utc_now


class RecoveryJournal:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "internet_runtime_stability"
        self.failure_dir = self.root / "failures"
        self.report_dir = self.root / "reports"
        self.audit_dir = self.root / "audit"
        for path in [self.failure_dir, self.report_dir, self.audit_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def save_failure(self, failure: FailureRecord) -> Path:
        path = self.failure_dir / f"{failure.operation_id}_{failure.attempt}.json"
        path.write_text(json.dumps(failure.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def save_report(self, report: Dict[str, Any]) -> Path:
        report_id = str(report.get("stability_run_id", "unknown_report"))
        path = self.report_dir / f"{report_id}.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in event_type)
        path = self.audit_dir / f"{utc_now().replace(':', '').replace('.', '_')}_{safe}.json"
        path.write_text(json.dumps({
            "event_type": event_type,
            "created_at": utc_now(),
            "payload": payload,
        }, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_failures(self, limit: int = 50) -> List[Dict[str, Any]]:
        failures = []
        for path in sorted(self.failure_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                failures.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return failures

    def list_reports(self, limit: int = 25) -> List[Dict[str, Any]]:
        reports = []
        for path in sorted(self.report_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                reports.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return reports
''')

    write_file(LAYER / "health.py", '''
from __future__ import annotations

from pathlib import Path
from typing import Dict, List


class InternetRuntimeHealthChecker:
    def __init__(self, project_root: Path | None = None) -> None:
        self.root = project_root or Path.cwd()

    def check(self) -> Dict[str, object]:
        required_paths = [
            "src/claire/internet_activation",
            "src/claire/internet_runtime_integration",
            "src/claire/persistent_internet_campaigns",
            "src/claire/governed_campaign_scheduler",
        ]

        data_paths = [
            "data/internet_activation",
            "data/persistent_internet_campaigns",
            "data/governed_campaign_scheduler",
        ]

        missing_required = [path for path in required_paths if not (self.root / path).exists()]
        missing_data = [path for path in data_paths if not (self.root / path).exists()]

        status = "healthy"
        if missing_required:
            status = "not_ready"
        elif missing_data:
            status = "degraded"

        return {
            "status": status,
            "missing_required_paths": missing_required,
            "missing_data_paths": missing_data,
            "checks": {
                "internet_activation_present": (self.root / "src/claire/internet_activation").exists(),
                "internet_runtime_integration_present": (self.root / "src/claire/internet_runtime_integration").exists(),
                "persistent_campaigns_present": (self.root / "src/claire/persistent_internet_campaigns").exists(),
                "scheduler_present": (self.root / "src/claire/governed_campaign_scheduler").exists(),
            },
        }
''')

    write_file(LAYER / "service.py", '''
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
''')

    write_file(LAYER / "cli.py", '''
from __future__ import annotations

import argparse
import json

from .service import InternetRuntimeStabilityService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire internet runtime stability")
    sub = parser.add_subparsers(dest="command", required=True)

    refresh = sub.add_parser("refresh-campaign")
    refresh.add_argument("--campaign-id", required=True)

    due = sub.add_parser("run-due")
    due.add_argument("--limit", type=int, default=None)

    sub.add_parser("health")

    failures = sub.add_parser("failures")
    failures.add_argument("--limit", type=int, default=50)

    reports = sub.add_parser("reports")
    reports.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    service = InternetRuntimeStabilityService()

    if args.command == "refresh-campaign":
        result = service.refresh_campaign_with_recovery_sync(args.campaign_id) if hasattr(service, "refresh_campaign_with_recovery_sync") else _run(service.refresh_campaign_with_recovery(args.campaign_id))
    elif args.command == "run-due":
        result = _run(service.run_scheduler_due_with_recovery(limit=args.limit))
    elif args.command == "health":
        result = service.health()
    elif args.command == "failures":
        result = {"failures": service.list_failures(limit=args.limit)}
    elif args.command == "reports":
        result = {"reports": service.list_reports(limit=args.limit)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


def _run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    main()
''')

    # Add sync helper as separate patch content in service to avoid CLI awkwardness
    write_file(LAYER / "sync_helpers.py", '''
from __future__ import annotations

import asyncio
from typing import Optional

from .service import InternetRuntimeStabilityService


def refresh_campaign_with_recovery_sync(service: InternetRuntimeStabilityService, campaign_id: str):
    return asyncio.run(service.refresh_campaign_with_recovery(campaign_id))


def run_scheduler_due_with_recovery_sync(service: InternetRuntimeStabilityService, limit: Optional[int] = None):
    return asyncio.run(service.run_scheduler_due_with_recovery(limit=limit))
''')

    write_file(LAYER / "api_routes.py", '''
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from .service import InternetRuntimeStabilityService


router = APIRouter(prefix="/internet/stability", tags=["Internet Runtime Stability"])


@router.get("/health")
def health():
    service = InternetRuntimeStabilityService()
    return service.health()


@router.post("/campaigns/{campaign_id}/refresh")
async def refresh_campaign_with_recovery(campaign_id: str):
    service = InternetRuntimeStabilityService()
    return await service.refresh_campaign_with_recovery(campaign_id)


@router.post("/scheduler/run-due")
async def run_scheduler_due_with_recovery(limit: Optional[int] = None):
    service = InternetRuntimeStabilityService()
    return await service.run_scheduler_due_with_recovery(limit=limit)


@router.get("/failures")
def failures(limit: int = 50):
    service = InternetRuntimeStabilityService()
    return {"failures": service.list_failures(limit=limit)}


@router.get("/reports")
def reports(limit: int = 25):
    service = InternetRuntimeStabilityService()
    return {"reports": service.list_reports(limit=limit)}
''')

    write_file(TESTS / "test_internet_runtime_stability.py", '''
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
''')

    write_file(TESTS / "test_internet_runtime_stability_api.py", '''
from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.internet_runtime_stability import api_routes
from claire.internet_runtime_stability.service import InternetRuntimeStabilityService


def test_health_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_health(self):
        return {"status": "healthy"}

    monkeypatch.setattr(InternetRuntimeStabilityService, "health", fake_health)

    client = TestClient(app)
    response = client.get("/internet/stability/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
''')

    write_file(DOCS / "v17_45_internet_runtime_stability.md", '''
# Claire v17.45 — Internet Runtime Stability + Failure Recovery

This package adds launch-critical reliability around Claire's governed internet update operations.

## Capabilities

- Retry policy
- Failure classification
- Degraded-mode handling
- Recovery journal
- Stability run reports
- Internet runtime health checks
- Safe wrapper around campaign refresh
- Safe wrapper around scheduler run-due
- CLI and FastAPI routes

## CLI

```bash
python -m claire.internet_runtime_stability.cli health
python -m claire.internet_runtime_stability.cli refresh-campaign --campaign-id campaign_x
python -m claire.internet_runtime_stability.cli run-due
python -m claire.internet_runtime_stability.cli failures
python -m claire.internet_runtime_stability.cli reports
```

## FastAPI Wiring

```python
from claire.internet_runtime_stability.api_routes import router as internet_stability_router
app.include_router(internet_stability_router)
```

## Boundary

This package does not bypass governance blocks. It does not retry blocked/review-required sources. It makes internet updates more reliable without making unsafe actions automatic.
''')

    write_json(DATA / "internet_runtime_stability_manifest.json", {
        "installed_at": utc_now(),
        "layer": "internet_runtime_stability",
        "version": "v17.45",
        "status": "installed",
        "requires": [
            "claire.internet_activation",
            "claire.internet_runtime_integration",
            "claire.persistent_internet_campaigns",
            "claire.governed_campaign_scheduler"
        ],
        "capabilities": [
            "retry_policy",
            "failure_classification",
            "degraded_mode",
            "recovery_journal",
            "stability_reports",
            "health_checks",
            "campaign_refresh_recovery_wrapper",
            "scheduler_recovery_wrapper",
            "cli",
            "fastapi_routes",
            "tests"
        ],
        "governance_boundary": "no_retry_for_governance_blocks_no_unapproved_external_action"
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.45 Internet Runtime Stability + Failure Recovery")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/internet_runtime_stability -q")
    print("")
    print("CLI examples:")
    print("    python -m claire.internet_runtime_stability.cli health")
    print("    python -m claire.internet_runtime_stability.cli run-due")


if __name__ == "__main__":
    main()
