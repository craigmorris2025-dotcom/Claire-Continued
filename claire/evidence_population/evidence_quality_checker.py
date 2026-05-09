from __future__ import annotations
from typing import Any, Dict, List

class EvidenceQualityChecker:
    REQUIRED = ["id", "source", "summary", "lineage"]

    def check(self, record: Dict[str, Any]) -> Dict[str, Any]:
        missing = [k for k in self.REQUIRED if not record.get(k)]
        return {
            "status": "pass" if not missing else "incomplete",
            "missing": missing,
            "field_count": len(record),
        }
