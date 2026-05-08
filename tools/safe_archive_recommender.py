#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

PROTECTED = [
    "src/claire/app.py",
    "src/claire/api",
    "src/claire/orchestrator",
    "src/claire/lifecycle",
]

def main() -> int:
    dormant_path = ROOT / "data" / "runtime" / "orphan_dormant_modules.json"

    candidates = []
    if dormant_path.exists():
        data = json.loads(dormant_path.read_text(encoding="utf-8"))
        for item in data.get("candidates", []):
            path = item["path"]
            if any(path.startswith(p) for p in PROTECTED):
                continue
            candidates.append({
                "path": path,
                "recommendation": "review_before_archive",
            })

    payload = {
        "recommender": "safe_archive_recommender",
        "version": "v16.40",
        "created_at": datetime.now().isoformat(),
        "recommendation_count": len(candidates),
        "recommendations": candidates,
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "safe_archive_recommendations.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "recommender": payload["recommender"],
        "recommendation_count": payload["recommendation_count"]
    }, indent=2))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
