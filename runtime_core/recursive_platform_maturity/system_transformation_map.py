from __future__ import annotations
from typing import Dict, Any, List

class SystemTransformationMap:
    def build_map(self, source_system: str, improvement_targets: List[str]) -> Dict[str, Any]:
        return {"record_type": "system_transformation_map", "source_system": source_system, "improvement_targets": improvement_targets}
