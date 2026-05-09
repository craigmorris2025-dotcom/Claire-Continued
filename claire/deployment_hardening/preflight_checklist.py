from __future__ import annotations
from typing import Dict, Any

class PreflightChecklist:
    ITEMS = ["launcher", "dashboard", "pytest", "version_lock", "rollback", "audit_report"]

    def build(self, results: Dict[str, bool]) -> Dict[str, Any]:
        missing = [item for item in self.ITEMS if not results.get(item, False)]
        return {"status": "pass" if not missing else "blocked", "missing": missing, "results": results}
