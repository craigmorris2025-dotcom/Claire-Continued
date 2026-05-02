"""Production readiness manifest reader and scorer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json


class ProductionReadiness:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.manifest_path = project_root / "data" / "production_readiness_manifest.json"

    def status(self) -> Dict[str, Any]:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        blockers = manifest.get("production_blockers", [])
        required = manifest.get("required_capabilities", [])
        return {
            "status": "success",
            "readiness_version": manifest.get("readiness_version"),
            "target_state": manifest.get("target_state"),
            "required_capability_count": len(required),
            "known_blocker_count": len(blockers),
            "production_posture": "plateau_ready_not_deployed" if blockers else "production_ready",
            "manifest": manifest,
        }


__all__ = ["ProductionReadiness"]
