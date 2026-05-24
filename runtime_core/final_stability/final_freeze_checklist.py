from __future__ import annotations
from typing import Any, Dict

class FinalFreezeChecklist:
    REQUIRED = ["git_commit", "launcher_test", "dashboard_test", "pytest_targeted", "version_file", "install_reports"]

    def evaluate(self, checks: Dict[str, bool]) -> Dict[str, Any]:
        missing = [k for k in self.REQUIRED if not checks.get(k, False)]
        return {"status": "freeze_ready" if not missing else "not_ready", "missing": missing}
