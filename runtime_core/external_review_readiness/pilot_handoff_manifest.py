from __future__ import annotations
from typing import Dict, Any, List

class PilotHandoffManifest:
    def build_manifest(self, scope: str, limitations: List[str]) -> Dict[str, Any]:
        return {"record_type": "pilot_handoff_manifest", "scope": scope, "limitations": limitations}
