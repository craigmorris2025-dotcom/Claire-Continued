from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List

class PopulationReportBuilder:
    def build_report(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        reviewed = sum(1 for r in records if r.get("review_status") == "reviewed")
        return {
            "record_type": "evidence_population_report",
            "record_count": len(records),
            "reviewed_count": reviewed,
            "review_coverage": round(reviewed / len(records), 4) if records else 0,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
