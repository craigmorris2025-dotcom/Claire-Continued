from __future__ import annotations
from typing import Dict, Any, List

class OperatorRoleRegistry:
    def build_roles(self) -> Dict[str, Any]:
        return {"record_type": "operator_roles", "roles": ["owner", "operator", "reviewer", "observer"], "rule": "least privilege by default"}
