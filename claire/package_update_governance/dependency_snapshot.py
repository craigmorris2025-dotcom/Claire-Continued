from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class DependencySnapshot:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_snapshot(self) -> Dict[str, Any]:
        try:
            proc = subprocess.run([sys.executable, "-m", "pip", "freeze"], text=True, capture_output=True, timeout=60)
            packages = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
            status = "success" if proc.returncode == 0 else "failed"
        except Exception as exc:
            packages = []
            status = "failed"
            proc = type("Proc", (), {"stderr": str(exc)})()
        return {
            "record_type": "dependency_snapshot",
            "status": status,
            "package_count": len(packages),
            "packages": packages,
            "error": getattr(proc, "stderr", ""),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_snapshot(self, snapshot: Dict[str, Any]) -> Path:
        out = self.root / "data" / "package_update_governance" / "dependency_snapshots" / "dependency_snapshot.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
        return out
