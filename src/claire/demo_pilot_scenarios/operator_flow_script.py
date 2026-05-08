from __future__ import annotations
from typing import Any, Dict, List

class OperatorFlowScript:
    def build_flow(self, name: str, actions: List[str]) -> Dict[str, Any]:
        return {"record_type": "operator_flow", "name": name, "actions": actions}
