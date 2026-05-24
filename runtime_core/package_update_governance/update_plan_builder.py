from __future__ import annotations
from typing import Any, Dict, List

class UpdatePlanBuilder:
    def build_plan(self, packages: List[str], reason: str) -> Dict[str, Any]:
        return {
            "record_type": "package_update_plan",
            "packages": packages,
            "reason": reason,
            "required_validation": ["pip_audit", "pytest", "launcher_test", "dashboard_test"],
            "rollback_required": True,
        }
