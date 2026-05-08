from __future__ import annotations
from typing import Dict, Any

class SynthesisReviewQueue:
    def queue_item(self, item_id: str, summary: str) -> Dict[str, Any]:
        return {"record_type": "synthesis_review_item", "item_id": item_id, "summary": summary, "status": "queued_for_review"}
