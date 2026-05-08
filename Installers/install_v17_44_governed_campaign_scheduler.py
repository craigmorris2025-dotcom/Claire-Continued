# Claire Syntalion Installer
# v17.44 Governed Campaign Scheduler + Update Runner
#
# Adds safe scheduling infrastructure for v17.43 persistent internet campaigns:
# - schedule definitions
# - due campaign detection
# - lock file to prevent overlapping runs
# - one-shot update runner
# - refresh batch reports
# - CLI and FastAPI routes
#
# This does NOT install a hidden background service.
# You run it manually or attach it to Windows Task Scheduler later.
#
# Place this file in Claire project root and run:
#
#     python install_v17_44_governed_campaign_scheduler.py
#
# Then test:
#
#     python -m pytest tests/governed_campaign_scheduler -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "governed_campaign_scheduler"
TESTS = ROOT / "tests" / "governed_campaign_scheduler"
DATA = ROOT / "data" / "governed_campaign_scheduler"
DOCS = ROOT / "docs" / "governed_campaign_scheduler"


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
    print("Installing Claire v17.44 Governed Campaign Scheduler + Update Runner...")

    write_file(LAYER / "__init__.py", '''
from .service import GovernedCampaignSchedulerService
from .models import CampaignSchedule, SchedulerRunReport
from .store import SchedulerStore
from .due import DueCampaignSelector
from .lock import SchedulerLock

__all__ = [
    "GovernedCampaignSchedulerService",
    "CampaignSchedule",
    "SchedulerRunReport",
    "SchedulerStore",
    "DueCampaignSelector",
    "SchedulerLock",
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
class CampaignSchedule:
    campaign_id: str
    enabled: bool = True
    cadence_minutes: int = 1440
    max_results: Optional[int] = None
    last_run_at: Optional[str] = None
    next_due_at: Optional[str] = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchedulerRunReport:
    scheduler_run_id: str
    status: str
    due_count: int
    refreshed_count: int
    skipped_count: int
    failed_count: int
    refreshed_campaign_ids: List[str] = field(default_factory=list)
    skipped_campaign_ids: List[str] = field(default_factory=list)
    failed_campaigns: List[Dict[str, str]] = field(default_factory=list)
    started_at: str = field(default_factory=utc_now)
    finished_at: Optional[str] = None
    lock_acquired: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
''')

    write_file(LAYER / "time_utils.py", '''
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def add_minutes(value: str | None, minutes: int) -> str:
    base = parse_utc(value) or datetime.now(timezone.utc)
    return (base + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def is_due(value: str | None, now_value: str | None = None) -> bool:
    if not value:
        return True
    due = parse_utc(value)
    now = parse_utc(now_value) or datetime.now(timezone.utc)
    if due is None:
        return True
    return due <= now
''')

    write_file(LAYER / "store.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import CampaignSchedule, SchedulerRunReport
from .time_utils import utc_now


class SchedulerStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "governed_campaign_scheduler"
        self.schedule_dir = self.root / "schedules"
        self.report_dir = self.root / "run_reports"
        self.audit_dir = self.root / "audit"
        for path in [self.schedule_dir, self.report_dir, self.audit_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def save_schedule(self, schedule: CampaignSchedule) -> Path:
        schedule.updated_at = utc_now()
        path = self.schedule_dir / f"{schedule.campaign_id}.json"
        path.write_text(json.dumps(schedule.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_schedule(self, campaign_id: str) -> Optional[CampaignSchedule]:
        path = self.schedule_dir / f"{campaign_id}.json"
        if not path.exists():
            return None
        return CampaignSchedule(**json.loads(path.read_text(encoding="utf-8")))

    def list_schedules(self) -> List[CampaignSchedule]:
        schedules = []
        for path in sorted(self.schedule_dir.glob("*.json")):
            try:
                schedules.append(CampaignSchedule(**json.loads(path.read_text(encoding="utf-8"))))
            except Exception:
                continue
        return schedules

    def save_report(self, report: SchedulerRunReport) -> Path:
        path = self.report_dir / f"{report.scheduler_run_id}.json"
        path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_reports(self, limit: int = 25) -> List[Dict[str, Any]]:
        reports = []
        for path in sorted(self.report_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                reports.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return reports

    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in event_type)
        path = self.audit_dir / f"{utc_now().replace(':', '').replace('.', '_')}_{safe}.json"
        path.write_text(json.dumps({
            "event_type": event_type,
            "created_at": utc_now(),
            "payload": payload,
        }, indent=2, sort_keys=True), encoding="utf-8")
        return path
''')

    write_file(LAYER / "due.py", '''
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
''')

    write_file(LAYER / "lock.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .time_utils import utc_now


class SchedulerLock:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "governed_campaign_scheduler"
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "scheduler.lock"

    def acquire(self, owner: str) -> Dict[str, object]:
        if self.path.exists():
            try:
                existing = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                existing = {"owner": "unknown"}
            return {
                "acquired": False,
                "reason": "Scheduler lock already exists.",
                "existing": existing,
            }

        payload = {"owner": owner, "acquired_at": utc_now()}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return {"acquired": True, "lock": payload}

    def release(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def status(self) -> Dict[str, object]:
        if not self.path.exists():
            return {"locked": False}
        try:
            return {"locked": True, "lock": json.loads(self.path.read_text(encoding="utf-8"))}
        except Exception:
            return {"locked": True, "lock": {"error": "unreadable lock"}}
''')

    write_file(LAYER / "service.py", '''
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
''')

    write_file(LAYER / "cli.py", '''
from __future__ import annotations

import argparse
import json

from .service import GovernedCampaignSchedulerService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire governed campaign scheduler")
    sub = parser.add_subparsers(dest="command", required=True)

    schedule = sub.add_parser("schedule")
    schedule.add_argument("--campaign-id", required=True)
    schedule.add_argument("--cadence-minutes", type=int, default=1440)
    schedule.add_argument("--disabled", action="store_true")

    run = sub.add_parser("run-due")
    run.add_argument("--limit", type=int, default=None)

    sub.add_parser("list")
    sub.add_parser("lock-status")

    reports = sub.add_parser("reports")
    reports.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    service = GovernedCampaignSchedulerService()

    if args.command == "schedule":
        result = service.set_schedule(
            campaign_id=args.campaign_id,
            cadence_minutes=args.cadence_minutes,
            enabled=not args.disabled,
        )
    elif args.command == "run-due":
        result = service.run_due_once_sync(limit=args.limit)
    elif args.command == "list":
        result = {"schedules": service.list_schedules()}
    elif args.command == "lock-status":
        result = service.lock_status()
    elif args.command == "reports":
        result = {"reports": service.list_reports(limit=args.limit)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
''')

    write_file(LAYER / "api_routes.py", '''
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import GovernedCampaignSchedulerService


router = APIRouter(prefix="/internet/scheduler", tags=["Governed Campaign Scheduler"])


class SetScheduleRequest(BaseModel):
    campaign_id: str = Field(..., min_length=1)
    cadence_minutes: int = Field(default=1440, ge=1)
    enabled: bool = True
    max_results: Optional[int] = None


@router.post("/schedule")
def set_schedule(request: SetScheduleRequest):
    service = GovernedCampaignSchedulerService()
    try:
        return service.set_schedule(
            campaign_id=request.campaign_id,
            cadence_minutes=request.cadence_minutes,
            enabled=request.enabled,
            max_results=request.max_results,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/schedules")
def list_schedules():
    service = GovernedCampaignSchedulerService()
    return {"schedules": service.list_schedules()}


@router.post("/run-due")
async def run_due(limit: Optional[int] = None):
    service = GovernedCampaignSchedulerService()
    return await service.run_due_once(limit=limit)


@router.get("/reports")
def list_reports(limit: int = 25):
    service = GovernedCampaignSchedulerService()
    return {"reports": service.list_reports(limit=limit)}


@router.get("/lock")
def lock_status():
    service = GovernedCampaignSchedulerService()
    return service.lock_status()
''')

    write_file(TESTS / "test_governed_campaign_scheduler.py", '''
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
''')

    write_file(TESTS / "test_governed_campaign_scheduler_api.py", '''
from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.governed_campaign_scheduler import api_routes
from claire.governed_campaign_scheduler.service import GovernedCampaignSchedulerService


def test_set_schedule_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_set(self, campaign_id, cadence_minutes=1440, enabled=True, max_results=None):
        return {"campaign_id": campaign_id, "cadence_minutes": cadence_minutes, "enabled": enabled}

    monkeypatch.setattr(GovernedCampaignSchedulerService, "set_schedule", fake_set)

    client = TestClient(app)
    response = client.post(
        "/internet/scheduler/schedule",
        json={"campaign_id": "campaign_test", "cadence_minutes": 60},
    )

    assert response.status_code == 200
    assert response.json()["campaign_id"] == "campaign_test"
    assert response.json()["cadence_minutes"] == 60
''')

    write_file(DOCS / "v17_44_governed_campaign_scheduler.md", '''
# Claire v17.44 — Governed Campaign Scheduler + Update Runner

This package adds a safe, explicit scheduler for v17.43 persistent internet campaigns.

## Capabilities

- Create campaign schedules
- Detect due campaigns
- Run due refreshes on demand
- Prevent overlapping scheduler runs with a lock file
- Save scheduler reports
- Provide CLI and API routes

## CLI

```bash
python -m claire.governed_campaign_scheduler.cli schedule --campaign-id campaign_x --cadence-minutes 1440
python -m claire.governed_campaign_scheduler.cli run-due
python -m claire.governed_campaign_scheduler.cli list
python -m claire.governed_campaign_scheduler.cli reports
```

## Windows Task Scheduler

This package does not install a background service. To automate safely, attach this command to Windows Task Scheduler:

```bash
python -m claire.governed_campaign_scheduler.cli run-due
```

## FastAPI Wiring

```python
from claire.governed_campaign_scheduler.api_routes import router as internet_scheduler_router
app.include_router(internet_scheduler_router)
```
''')

    write_json(DATA / "governed_campaign_scheduler_manifest.json", {
        "installed_at": utc_now(),
        "layer": "governed_campaign_scheduler",
        "version": "v17.44",
        "status": "installed",
        "requires": ["claire.persistent_internet_campaigns"],
        "capabilities": [
            "campaign_schedule_records",
            "due_campaign_detection",
            "lock_file_overlap_prevention",
            "one_shot_update_runner",
            "scheduler_reports",
            "cli_runner",
            "fastapi_routes",
            "tests"
        ],
        "governance_boundary": "explicit_manual_or_task_scheduler_invocation_no_hidden_background_service"
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.44 Governed Campaign Scheduler + Update Runner")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/governed_campaign_scheduler -q")
    print("")
    print("CLI examples:")
    print("    python -m claire.governed_campaign_scheduler.cli schedule --campaign-id <campaign_id> --cadence-minutes 1440")
    print("    python -m claire.governed_campaign_scheduler.cli run-due")


if __name__ == "__main__":
    main()
