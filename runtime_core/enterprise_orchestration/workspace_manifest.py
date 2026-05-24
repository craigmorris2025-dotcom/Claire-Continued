from __future__ import annotations
from typing import Dict, Any

class WorkspaceManifest:
    def build_manifest(self, workspace_id: str, purpose: str) -> Dict[str, Any]:
        return {"record_type": "workspace_manifest", "workspace_id": workspace_id, "purpose": purpose, "isolation": "logical"}
