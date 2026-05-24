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
