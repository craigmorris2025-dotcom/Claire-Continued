from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/discovery/discovery_campaign_manager.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DISCOVERY_CAMPAIGN_PATH = Path("data/discovery/discovery_campaigns.json")

VALID_CAMPAIGN_STATES = {
    "draft",
    "active",
    "paused",
    "completed",
    "blocked",
}


def _load_campaigns() -> List[Dict[str, Any]]:
    if not DISCOVERY_CAMPAIGN_PATH.exists():
        return []
    try:
        data = json.loads(DISCOVERY_CAMPAIGN_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def create_discovery_campaign(
    title: str,
    objective: str,
    domain: str,
    constraints: Dict[str, Any] | None = None,
    approved_sources: List[str] | None = None,
) -> Dict[str, Any]:
    campaign = {
        "version": "16.91",
        "campaign_id": f"campaign_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "objective": objective,
        "domain": domain,
        "constraints": constraints or {},
        "approved_sources": approved_sources or [],
        "state": "active",
        "campaign_events": [],
        "governance_note": "Campaign discovery must respect source governance, quarantine, and operator review.",
    }

    DISCOVERY_CAMPAIGN_PATH.parent.mkdir(parents=True, exist_ok=True)
    campaigns = _load_campaigns()
    campaigns.append(campaign)
    DISCOVERY_CAMPAIGN_PATH.write_text(json.dumps(campaigns, indent=2), encoding="utf-8")
    return campaign


def list_discovery_campaigns(state: str | None = None) -> List[Dict[str, Any]]:
    campaigns = _load_campaigns()
    if state is None:
        return campaigns
    return [campaign for campaign in campaigns if campaign.get("state") == state]


def update_discovery_campaign_state(campaign_id: str, state: str, note: str | None = None) -> Dict[str, Any]:
    if state not in VALID_CAMPAIGN_STATES:
        raise ValueError(f"Invalid campaign state: {state}")

    campaigns = _load_campaigns()
    for campaign in campaigns:
        if campaign.get("campaign_id") == campaign_id:
            campaign["state"] = state
            campaign["updated_at"] = datetime.now(timezone.utc).isoformat()
            if note:
                campaign.setdefault("campaign_events", []).append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "note": note,
                    "state": state,
                })
            DISCOVERY_CAMPAIGN_PATH.write_text(json.dumps(campaigns, indent=2), encoding="utf-8")
            return campaign

    raise ValueError(f"Campaign not found: {campaign_id}")
""")

print("v16.91 discovery campaign manager installed.")
