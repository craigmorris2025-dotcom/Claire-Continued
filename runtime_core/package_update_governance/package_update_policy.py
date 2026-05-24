from __future__ import annotations
from typing import Any, Dict, List

class PackageUpdatePolicy:
    def build_policy(self) -> Dict[str, Any]:
        return {
            "record_type": "package_update_policy",
            "rule": "No blind updates. Snapshot, audit, test, rollback point, then commit.",
            "required_steps": ["dependency_snapshot", "pip_audit", "targeted_pytest", "rollback_point", "git_commit"],
            "default_update_decision": "manual_review_required",
        }

    def evaluate(self, completed_steps: List[str]) -> Dict[str, Any]:
        required = self.build_policy()["required_steps"]
        missing = [step for step in required if step not in completed_steps]
        return {"status": "ready" if not missing else "blocked", "missing": missing}
