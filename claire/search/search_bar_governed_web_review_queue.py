"""
Claire Syntalion v18.02
Search Bar Governed Web Review Queue

Purpose:
- Creates a review queue for governed web-search requests from the permanent search bar.
- Does not execute live web search.
- Stores operator-review candidates only.
- Preserves manual-review-only evidence flow.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json
import uuid


class SearchBarGovernedWebReviewQueue:
    def __init__(
        self,
        queue_path: str | Path = "data/search/governed_web_review_queue.json",
    ) -> None:
        self.queue_path = Path(queue_path)

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _read_queue(self) -> Dict[str, Any]:
        if not self.queue_path.exists():
            return {
                "version": "v18.02",
                "queue": [],
            }
        try:
            payload = json.loads(self.queue_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload.setdefault("queue", [])
                return payload
        except Exception:
            pass
        return {
            "version": "v18.02",
            "queue": [],
        }

    def _write_queue(self, payload: Dict[str, Any]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def enqueue_request(self, query: str, requested_mode: str = "normal_web_search") -> Dict[str, Any]:
        payload = self._read_queue()

        item = {
            "review_queue_id": f"gwq-{uuid.uuid4().hex[:12]}",
            "created_at": self._utc_now(),
            "query": query,
            "requested_mode": requested_mode,
            "review_status": "pending_operator_review",
            "execution_status": "not_executed",
            "read_only": True,
            "live_web_execution_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
        }

        payload["version"] = "v18.02"
        payload.setdefault("queue", []).append(item)

        self._write_queue(payload)

        return item

    def list_queue(self) -> List[Dict[str, Any]]:
        payload = self._read_queue()
        queue = payload.get("queue", [])
        if not isinstance(queue, list):
            return []
        return [item for item in queue if isinstance(item, dict)]
