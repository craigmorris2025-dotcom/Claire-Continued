from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import InternetCampaign, CampaignRefreshReport
from .models import utc_now


class CampaignStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "persistent_internet_campaigns"
        self.campaign_dir = self.root / "campaigns"
        self.report_dir = self.root / "refresh_reports"
        self.audit_dir = self.root / "audit"
        for path in [self.campaign_dir, self.report_dir, self.audit_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def save_campaign(self, campaign: InternetCampaign) -> Path:
        campaign.updated_at = utc_now()
        path = self.campaign_dir / f"{campaign.campaign_id}.json"
        path.write_text(json.dumps(campaign.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_campaign(self, campaign_id: str) -> Optional[InternetCampaign]:
        path = self.campaign_dir / f"{campaign_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return InternetCampaign(**data)

    def list_campaigns(self) -> List[Dict[str, Any]]:
        campaigns = []
        for path in sorted(self.campaign_dir.glob("*.json")):
            try:
                campaigns.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return campaigns

    def save_report(self, report: CampaignRefreshReport) -> Path:
        path = self.report_dir / f"{report.report_id}.json"
        path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_reports(self, campaign_id: str | None = None) -> List[Dict[str, Any]]:
        reports = []
        for path in sorted(self.report_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if campaign_id is None or data.get("campaign_id") == campaign_id:
                    reports.append(data)
            except Exception:
                continue
        return reports

    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        name = f"{utc_now().replace(':', '').replace('.', '_')}_{event_type}.json"
        path = self.audit_dir / name
        path.write_text(json.dumps({
            "event_type": event_type,
            "created_at": utc_now(),
            "payload": payload,
        }, indent=2, sort_keys=True), encoding="utf-8")
        return path
