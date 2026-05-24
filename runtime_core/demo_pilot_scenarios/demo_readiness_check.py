from __future__ import annotations
from typing import Dict, Any

class DemoReadinessCheck:
    REQUIRED = ["launcher", "dashboard", "sample_inputs", "scenario_pack", "proof_seed"]

    def evaluate(self, checks: Dict[str, bool]) -> Dict[str, Any]:
        missing = [k for k in self.REQUIRED if not checks.get(k, False)]
        return {"status": "ready" if not missing else "blocked", "missing": missing}
