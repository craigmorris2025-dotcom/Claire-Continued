from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List

class ValuationMemoBuilder:
    def build_memo(self, valuation_range: str, assumptions: List[str]) -> Dict[str, Any]:
        return {"record_type": "valuation_memo", "valuation_range": valuation_range, "assumptions": assumptions, "created_at_utc": datetime.now(timezone.utc).isoformat(), "disclaimer": "Preliminary strategic estimate, not financial advice."}
