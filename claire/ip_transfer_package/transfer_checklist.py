from __future__ import annotations
from typing import Dict, Any

class TransferChecklist:
    REQUIRED = ["repo_inventory", "version_lock", "readme", "license_note", "demo_artifacts", "pytest_proof"]
    def evaluate(self, checks: Dict[str, bool]) -> Dict[str, Any]:
        missing = [x for x in self.REQUIRED if not checks.get(x, False)]
        return {"status": "ready" if not missing else "incomplete", "missing": missing}
