# Claire Syntalion Installer
# v17.43 Persistent Internet Campaigns + Update Cycles
#
# Place this file in Claire project root and run:
#
#     python install_v17_43_persistent_internet_campaigns.py
#
# Then test:
#
#     python -m pytest tests/persistent_internet_campaigns -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "persistent_internet_campaigns"
TESTS = ROOT / "tests" / "persistent_internet_campaigns"
DATA = ROOT / "data" / "persistent_internet_campaigns"
DOCS = ROOT / "docs" / "persistent_internet_campaigns"


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
    print("Installing Claire v17.43 Persistent Internet Campaigns + Update Cycles...")

    write_file(LAYER / "__init__.py", '''
from .service import PersistentInternetCampaignService
from .models import InternetCampaign, CampaignRefreshReport
from .store import CampaignStore
from .drift import EvidenceDriftDetector

__all__ = [
    "PersistentInternetCampaignService",
    "InternetCampaign",
    "CampaignRefreshReport",
    "CampaignStore",
    "EvidenceDriftDetector",
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
class InternetCampaign:
    campaign_id: str
    name: str
    query: str
    urls: List[str] = field(default_factory=list)
    cadence: str = "manual"
    status: str = "active"
    max_results: int = 5
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    last_refresh_at: Optional[str] = None
    refresh_count: int = 0
    evidence_ids: List[str] = field(default_factory=list)
    average_confidence: float = 0.0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignRefreshReport:
    report_id: str
    campaign_id: str
    campaign_name: str
    query: str
    status: str
    previous_evidence_count: int
    new_evidence_count: int
    total_evidence_count: int
    previous_average_confidence: float
    new_average_confidence: float
    confidence_delta: float
    new_sources: List[str] = field(default_factory=list)
    repeated_sources: List[str] = field(default_factory=list)
    removed_sources: List[str] = field(default_factory=list)
    drift_status: str = "stable"
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    refreshed_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
''')

    write_file(LAYER / "store.py", '''
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
''')

    write_file(LAYER / "drift.py", '''
from __future__ import annotations

from typing import Dict, List


class EvidenceDriftDetector:
    def compare(self, previous_evidence: List[Dict[str, object]], new_evidence: List[Dict[str, object]]) -> Dict[str, object]:
        previous_ids = {str(item.get("evidence_id")) for item in previous_evidence if item.get("evidence_id")}
        new_ids = {str(item.get("evidence_id")) for item in new_evidence if item.get("evidence_id")}

        previous_sources = {str(item.get("source_url")) for item in previous_evidence if item.get("source_url")}
        new_sources_set = {str(item.get("source_url")) for item in new_evidence if item.get("source_url")}

        previous_conf = self.average_confidence(previous_evidence)
        new_conf = self.average_confidence(new_evidence)
        delta = round(new_conf - previous_conf, 4)

        added_sources = sorted(new_sources_set - previous_sources)
        repeated_sources = sorted(new_sources_set & previous_sources)
        removed_sources = sorted(previous_sources - new_sources_set)

        if abs(delta) >= 0.15:
            drift_status = "confidence_shift"
        elif added_sources or removed_sources:
            drift_status = "source_change"
        elif new_ids - previous_ids:
            drift_status = "new_evidence"
        else:
            drift_status = "stable"

        return {
            "previous_average_confidence": previous_conf,
            "new_average_confidence": new_conf,
            "confidence_delta": delta,
            "new_sources": added_sources,
            "repeated_sources": repeated_sources,
            "removed_sources": removed_sources,
            "drift_status": drift_status,
        }

    def average_confidence(self, evidence: List[Dict[str, object]]) -> float:
        if not evidence:
            return 0.0
        values = []
        for item in evidence:
            try:
                values.append(float(item.get("confidence", 0.0)))
            except Exception:
                values.append(0.0)
        if not values:
            return 0.0
        return round(sum(values) / len(values), 4)
''')

    write_file(LAYER / "service.py", '''
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from claire.internet_runtime_integration import InternetRuntimeIntegrationService

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
''')

    write_file(LAYER / "api_routes.py", '''
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import PersistentInternetCampaignService


router = APIRouter(prefix="/internet/campaigns", tags=["Persistent Internet Campaigns"])


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    urls: Optional[List[str]] = None
    cadence: str = "manual"
    max_results: int = Field(default=5, ge=1, le=20)
    notes: Optional[List[str]] = None


@router.post("")
def create_campaign(request: CreateCampaignRequest):
    service = PersistentInternetCampaignService()
    try:
        return service.create_campaign(
            name=request.name,
            query=request.query,
            urls=request.urls,
            cadence=request.cadence,
            max_results=request.max_results,
            notes=request.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("")
def list_campaigns():
    service = PersistentInternetCampaignService()
    return {"campaigns": service.list_campaigns()}


@router.post("/{campaign_id}/refresh")
async def refresh_campaign(campaign_id: str):
    service = PersistentInternetCampaignService()
    try:
        return await service.refresh_campaign(campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{campaign_id}/reports")
def list_campaign_reports(campaign_id: str):
    service = PersistentInternetCampaignService()
    return {"reports": service.list_reports(campaign_id=campaign_id)}
''')

    write_file(LAYER / "cli.py", '''
from __future__ import annotations

import argparse
import json

from .service import PersistentInternetCampaignService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire persistent internet campaigns")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--query", required=True)
    create.add_argument("--url", action="append", default=[])
    create.add_argument("--cadence", default="manual")
    create.add_argument("--max-results", type=int, default=5)

    refresh = sub.add_parser("refresh")
    refresh.add_argument("--campaign-id", required=True)

    sub.add_parser("list")

    reports = sub.add_parser("reports")
    reports.add_argument("--campaign-id", default=None)

    args = parser.parse_args()
    service = PersistentInternetCampaignService()

    if args.command == "create":
        result = service.create_campaign(
            name=args.name,
            query=args.query,
            urls=args.url,
            cadence=args.cadence,
            max_results=args.max_results,
        )
    elif args.command == "refresh":
        result = service.refresh_campaign_sync(args.campaign_id)
    elif args.command == "list":
        result = {"campaigns": service.list_campaigns()}
    elif args.command == "reports":
        result = {"reports": service.list_reports(args.campaign_id)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
''')

    write_file(TESTS / "test_persistent_internet_campaigns.py", '''
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
''')

    write_file(TESTS / "test_persistent_internet_campaigns_api.py", '''
from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.persistent_internet_campaigns import api_routes
from claire.persistent_internet_campaigns.service import PersistentInternetCampaignService


def test_create_campaign_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_create(self, name, query, urls=None, cadence="manual", max_results=5, notes=None):
        return {"campaign_id": "campaign_test", "name": name, "query": query, "urls": urls or []}

    monkeypatch.setattr(PersistentInternetCampaignService, "create_campaign", fake_create)

    client = TestClient(app)
    response = client.post(
        "/internet/campaigns",
        json={"name": "AI Watch", "query": "AI disclosure", "urls": ["https://www.sec.gov/newsroom"]},
    )

    assert response.status_code == 200
    assert response.json()["campaign_id"] == "campaign_test"
''')

    write_file(DOCS / "v17_43_persistent_internet_campaigns.md", '''
# Claire v17.43 — Persistent Internet Campaigns + Update Cycles

This package turns the v17.41/v17.42 internet runtime into persistent manually refreshable campaigns.

## Capabilities

- Create named internet campaigns
- Save campaign state
- Refresh campaign evidence on demand
- Link refreshes into the v17.42 runtime integration path
- Compare new evidence against prior evidence
- Detect confidence drift, source changes, new evidence, and stable evidence state
- Save refresh reports
- Provide CLI and API routes

## CLI

```bash
python -m claire.persistent_internet_campaigns.cli create --name "AI policy watch" --query "AI disclosure rules" --url https://www.sec.gov/newsroom
python -m claire.persistent_internet_campaigns.cli list
python -m claire.persistent_internet_campaigns.cli refresh --campaign-id campaign_x
```

## FastAPI Wiring

```python
from claire.persistent_internet_campaigns.api_routes import router as internet_campaigns_router
app.include_router(internet_campaigns_router)
```

## Boundary

This package does not install a hidden background scheduler. Refresh is explicit through CLI/API. That keeps the system safe and auditable while making update cycles real.
''')

    write_json(DATA / "persistent_internet_campaigns_manifest.json", {
        "installed_at": utc_now(),
        "layer": "persistent_internet_campaigns",
        "version": "v17.43",
        "status": "installed",
        "requires": [
            "claire.internet_activation",
            "claire.internet_runtime_integration"
        ],
        "capabilities": [
            "persistent_campaign_state",
            "manual_refresh_cycles",
            "evidence_drift_detection",
            "source_change_detection",
            "confidence_delta_tracking",
            "refresh_reports",
            "cli_runner",
            "fastapi_routes",
            "tests"
        ],
        "governance_boundary": "manual_or_api_refresh_only_no_hidden_background_browsing"
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.43 Persistent Internet Campaigns + Update Cycles")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/persistent_internet_campaigns -q")
    print("")
    print("CLI examples:")
    print('    python -m claire.persistent_internet_campaigns.cli create --name "AI policy watch" --query "AI disclosure rules" --url https://www.sec.gov/newsroom')
    print("    python -m claire.persistent_internet_campaigns.cli list")
    print("    python -m claire.persistent_internet_campaigns.cli refresh --campaign-id <campaign_id>")


if __name__ == "__main__":
    main()
