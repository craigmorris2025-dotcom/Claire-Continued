from __future__ import annotations
import json, platform, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class EnvironmentManifestBuilder:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_manifest(self) -> Dict[str, Any]:
        return {
            "record_type": "environment_manifest",
            "python": sys.version,
            "platform": platform.platform(),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_manifest(self, manifest: Dict[str, Any]) -> Path:
        out = self.root / "data" / "deployment_hardening" / "environment_manifests" / "environment_manifest.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        return out
