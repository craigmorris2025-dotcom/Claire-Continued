from __future__ import annotations
from typing import Dict, Any, List

class ReviewerPacketBuilder:
    def build_packet(self, reviewer_type: str, artifacts: List[str]) -> Dict[str, Any]:
        return {"record_type": "reviewer_packet", "reviewer_type": reviewer_type, "artifacts": artifacts, "artifact_count": len(artifacts)}
