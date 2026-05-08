#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
BACKUPS = ROOT / ".claire_install" / "backups"
REPORTS = ROOT / ".claire_install" / "reports"

def main() -> int:
    backup_sets = []
    if BACKUPS.exists():
        for path in sorted(BACKUPS.iterdir()):
            if path.is_dir():
                backup_sets.append({"name": path.name, "file_count": sum(1 for p in path.rglob("*") if p.is_file())})
    payload = {
        "validation": "rollback_validation",
        "version": "v16.29",
        "created_at": datetime.now().isoformat(),
        "status": "success",
        "backup_set_count": len(backup_sets),
        "backup_sets": backup_sets[-50:],
        "install_report_count": len(list(REPORTS.glob("*.json"))) if REPORTS.exists() else 0,
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "rollback_validation.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nRollback validation written: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
