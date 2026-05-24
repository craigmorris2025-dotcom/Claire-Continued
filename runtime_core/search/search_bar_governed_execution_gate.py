"""
Claire Syntalion v18.04
Search Bar Governed Execution Gate

Purpose:
- Creates a governed execution gate for reviewed web queue items.
- Approval alone still does not execute anything.
- This gate verifies whether an item is eligible for a future execution step.
- Live web execution remains disabled in this build.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from runtime_core.search.search_bar_governed_web_review_queue import (
    SearchBarGovernedWebReviewQueue,
)


REQUIRED_CONFIRM_TEXT = "AUTHORIZE GOVERNED WEB EXECUTION REVIEW ONLY"


class SearchBarGovernedExecutionGate:
    def __init__(
        self,
        queue_path: str | Path = "data/search/governed_web_review_queue.json",
    ) -> None:
        self.queue = SearchBarGovernedWebReviewQueue(queue_path)

    def evaluate_item(
        self,
        review_queue_id: str,
        confirm_text: str,
    ) -> Dict[str, Any]:
        items = self.queue.list_queue()

        target = None
        for item in items:
            if item.get("review_queue_id") == review_queue_id:
                target = item
                break

        if target is None:
            return {
                "version": "v18.04",
                "status": "REVIEW_QUEUE_ITEM_NOT_FOUND",
                "review_queue_id": review_queue_id,
                "eligible_for_future_execution": False,
                "live_web_execution_enabled": False,
                "automatic_updates_enabled": False,
                "autonomous_agent_execution_enabled": False,
                "runtime_truth_mutation_enabled": False,
                "reasons": ["missing_review_queue_item"],
            }

        reasons: List[str] = []

        if target.get("review_status") != "approved_for_future_execution":
            reasons.append("review_status_not_approved_for_future_execution")

        if not target.get("approved_by"):
            reasons.append("missing_approved_by")

        if not target.get("approved_at"):
            reasons.append("missing_approved_at")

        if target.get("execution_status") != "not_executed":
            reasons.append("execution_status_not_clean")

        if confirm_text != REQUIRED_CONFIRM_TEXT:
            reasons.append("invalid_confirm_text")

        eligible = len(reasons) == 0

        return {
            "version": "v18.04",
            "status": (
                "GOVERNED_EXECUTION_GATE_READY_BUT_EXECUTION_DISABLED"
                if eligible
                else "GOVERNED_EXECUTION_GATE_BLOCKED"
            ),
            "review_queue_id": review_queue_id,
            "eligible_for_future_execution": eligible,
            "live_web_execution_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "execution_performed": False,
            "required_confirm_text": REQUIRED_CONFIRM_TEXT,
            "reasons": reasons,
        }
