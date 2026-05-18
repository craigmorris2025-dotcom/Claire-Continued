"""
Claire Syntalion v18.03
Search Bar Governed Web Review Controls

Purpose:
- Adds explicit operator review controls for governed web review queue items.
- Does not execute live web search.
- Does not promote evidence automatically.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json

from claire.search.search_bar_governed_web_review_queue import (
    SearchBarGovernedWebReviewQueue,
)


class SearchBarGovernedWebReviewControls:
    def __init__(
        self,
        queue_path: str | Path = "data/search/governed_web_review_queue.json",
    ) -> None:
        self.queue = SearchBarGovernedWebReviewQueue(queue_path)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def approve(self, review_queue_id: str, approved_by: str) -> Dict[str, Any]:
        items = self.queue.list_queue()

        for item in items:
            if item.get("review_queue_id") == review_queue_id:
                item["review_status"] = "approved_for_future_execution"
                item["approved_by"] = approved_by
                item["approved_at"] = self._utc_now()
                item["live_web_execution_enabled"] = False
                item["automatic_updates_enabled"] = False
                item["autonomous_agent_execution_enabled"] = False

        payload = {
            "version": "v18.03",
            "queue": items,
        }

        self.queue._write_queue(payload)

        return {
            "status": "REVIEW_ITEM_APPROVED",
            "review_queue_id": review_queue_id,
            "approved_by": approved_by,
            "live_web_execution_enabled": False,
        }

    def reject(self, review_queue_id: str, rejected_by: str) -> Dict[str, Any]:
        items = self.queue.list_queue()

        for item in items:
            if item.get("review_queue_id") == review_queue_id:
                item["review_status"] = "rejected"
                item["rejected_by"] = rejected_by
                item["rejected_at"] = self._utc_now()

        payload = {
            "version": "v18.03",
            "queue": items,
        }

        self.queue._write_queue(payload)

        return {
            "status": "REVIEW_ITEM_REJECTED",
            "review_queue_id": review_queue_id,
            "rejected_by": rejected_by,
        }
