from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List

class BatchIntakeManifest:
    def build_manifest(self, batch_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "record_type": "batch_intake_manifest",
            "batch_id": batch_id,
            "item_count": len(items),
            "items": items,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
