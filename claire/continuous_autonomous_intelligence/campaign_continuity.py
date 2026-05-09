from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import CampaignState
from .models import utc_now


class CampaignContinuityManager:
    def __init__(self) -> None:
        self.campaigns: Dict[str, CampaignState] = {}

    def create_campaign(self, name: str, topics: List[str], confidence: float = 0.5) -> CampaignState:
        campaign_id = "campaign_" + hashlib.sha256(f"{name}|{topics}".encode("utf-8")).hexdigest()[:12]
        campaign = CampaignState(
            campaign_id=campaign_id,
            name=name,
            topics=topics,
            confidence=max(0.0, min(1.0, confidence)),
            last_checkpoint_at=utc_now(),
        )
        self.campaigns[campaign_id] = campaign
        return campaign

    def record_event(self, campaign_id: str) -> None:
        campaign = self.campaigns[campaign_id]
        campaign.event_count += 1
        campaign.last_checkpoint_at = utc_now()

    def record_escalation(self, campaign_id: str) -> None:
        campaign = self.campaigns[campaign_id]
        campaign.escalation_count += 1
        campaign.last_checkpoint_at = utc_now()

    def snapshot(self) -> List[dict]:
        return [campaign.to_dict() for campaign in self.campaigns.values()]
