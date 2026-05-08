from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import WatchlistItem


class OpportunityWatchlistEngine:
    def create_watchlist(self, opportunities: List[Dict[str, object]]) -> List[WatchlistItem]:
        items: List[WatchlistItem] = []
        for opportunity in opportunities:
            topic = str(opportunity.get("topic") or opportunity.get("title") or "untitled opportunity")
            thesis = str(opportunity.get("thesis") or opportunity.get("summary") or topic)
            watch_id = "watch_" + hashlib.sha256(f"{topic}|{thesis}".encode("utf-8")).hexdigest()[:12]
            confidence = float(opportunity.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
            items.append(
                WatchlistItem(
                    watch_id=watch_id,
                    topic=topic,
                    thesis=thesis,
                    cadence=str(opportunity.get("cadence", "daily")),
                    confidence=confidence,
                    notes=list(opportunity.get("notes", [])),
                )
            )
        return items
