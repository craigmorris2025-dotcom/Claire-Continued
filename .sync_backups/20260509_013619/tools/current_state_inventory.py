#!/usr/bin/env python3
"""
Current State Inventory

Produces a compact inventory of Claire's current tree without changing files.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())


def main() -> int:
    top = []
    for child in ROOT.iterdir():
        if child.is_dir():
            top.append({
                "folder": child.name,
                "files": count_files(child),
            })

    top.sort(key=lambda item: item["files"], reverse=True)

    payload = {
        "inventory": "current_state_inventory",
        "created_at": datetime.now().isoformat(),
        "root": str(ROOT),
        "total_files": count_files(ROOT),
        "top_folders_by_file_count": top,
        "key_paths": {
            "main.py": (ROOT / "main.py").exists(),
            "src/claire": (ROOT / "src" / "claire").exists(),
            "src/frontend": (ROOT / "src" / "frontend").exists(),
            "tests": (ROOT / "tests").exists(),
            "archive": (ROOT / "archive").exists(),
            ".claire_install": (ROOT / ".claire_install").exists(),
        },
    }

    out_dir = ROOT / ".claire_install" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"current_state_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nReport written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
