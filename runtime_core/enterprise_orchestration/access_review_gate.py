from __future__ import annotations
from typing import Dict, Any

class AccessReviewGate:
    def evaluate(self, reviewed: bool, owner_approved: bool) -> Dict[str, Any]:
        return {"status": "pass" if reviewed and owner_approved else "blocked"}
