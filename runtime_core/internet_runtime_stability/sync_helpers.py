from __future__ import annotations

import asyncio
from typing import Optional

from .service import InternetRuntimeStabilityService


def refresh_campaign_with_recovery_sync(service: InternetRuntimeStabilityService, campaign_id: str):
    return asyncio.run(service.refresh_campaign_with_recovery(campaign_id))


def run_scheduler_due_with_recovery_sync(service: InternetRuntimeStabilityService, limit: Optional[int] = None):
    return asyncio.run(service.run_scheduler_due_with_recovery(limit=limit))
