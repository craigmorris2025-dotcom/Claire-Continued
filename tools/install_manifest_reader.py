#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORTS = ROOT / ".claire_install" / "reports"

def main() -> int:
    manifests = []
    if REPORTS.exists():
        for path in sorted(REPORTS.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            manifests.append({
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "installer": data.get("installer") or data.get("guard") or data.get("check") or data.get("inventory"),
                "status": data.get("status"),
                "created_at": data.get("created_at"),
            })
    payload = {
        "reader": "install_manifest_reader",
        "version": "v16.28",
        "created_at": datetime.now().isoformat(),
        "manifest_count": len(manifests),
        "manifests": manifests[-100:],
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "install_manifest_index.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nInstall manifest index written: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
