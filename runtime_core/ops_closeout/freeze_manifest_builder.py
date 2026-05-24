from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class FreezeManifestBuilder:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_manifest(self, version: str) -> Dict[str, Any]:
        return {
            "record_type": "freeze_manifest",
            "version": version,
            "state": "maintenance_freeze",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "rule": "Only bug fixes, evidence population, and documentation updates during freeze."
        }

    def export_manifest(self, manifest: Dict[str, Any]) -> Path:
        out = self.root / "data" / "ops_closeout" / "freeze_manifests" / f"freeze_{manifest['version'].replace('.','_')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        return out
