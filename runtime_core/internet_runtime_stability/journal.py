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
