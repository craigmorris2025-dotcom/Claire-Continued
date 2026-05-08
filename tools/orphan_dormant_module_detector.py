#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

KEYWORDS = ["placeholder", "legacy", "deprecated", "unused", "proof", "demo"]

def main() -> int:
    candidates = []
    src = ROOT / "src" / "claire"

    if src.exists():
        for path in src.rglob("*.py"):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            lowered = rel.lower()
            if any(k in lowered for k in KEYWORDS):
                candidates.append({
                    "path": rel,
                    "reason": "keyword_match",
                })

    payload = {
        "detector": "orphan_dormant_module_detector",
        "version": "v16.39",
        "created_at": datetime.now().isoformat(),
        "candidate_count": len(candidates),
        "candidates": candidates[:500],
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "orphan_dormant_modules.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "detector": payload["detector"],
        "candidate_count": payload["candidate_count"]
    }, indent=2))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
