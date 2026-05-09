from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

class QuarantineRecord:
    def build_record(self, source: str, reason: str) -> Dict[str, Any]:
        return {
            "record_type": "live_source_quarantine",
            "source": source,
            "reason": reason,
            "status": "quarantined",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
