from __future__ import annotations
from typing import Any, Dict

class ReleaseGateEvaluator:
    REQUIRED = {
        "pytest_passed": True,
        "launcher_verified": True,
        "dashboard_verified": True,
        "version_locked": True,
        "rollback_point_exists": True,
    }

    def evaluate(self, checks: Dict[str, bool]) -> Dict[str, Any]:
        failures = [k for k, required in self.REQUIRED.items() if bool(checks.get(k)) != required]
        return {"status": "pass" if not failures else "blocked", "failures": failures}
