#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def main() -> int:
    backups = ROOT / ".claire_install" / "backups"

    sets = []
    if backups.exists():
        for path in sorted(backups.iterdir(), reverse=True):
            if path.is_dir():
                sets.append({
                    "backup": path.name,
                    "file_count": sum(1 for p in path.rglob("*") if p.is_file()),
                })

    selected = sets[0] if sets else None

    payload = {
        "selector": "recovery_rollback_selector",
        "version": "v16.41",
        "created_at": datetime.now().isoformat(),
        "available_backup_sets": len(sets),
        "recommended_backup": selected,
        "backup_sets": sets[:50],
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "recovery_rollback_selector.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "selector": payload["selector"],
        "available_backup_sets": payload["available_backup_sets"]
    }, indent=2))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
