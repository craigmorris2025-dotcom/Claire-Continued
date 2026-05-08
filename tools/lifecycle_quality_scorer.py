#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

EXPECTED_STAGE_HINTS = [
    "signal",
    "normalization",
    "validation",
    "trend",
    "thesis",
    "portfolio",
    "breakthrough",
    "design",
    "acquisition",
    "package",
]

def main() -> int:
    lifecycle_dir = ROOT / "src" / "claire" / "lifecycle"
    files = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in lifecycle_dir.glob("*.py")) if lifecycle_dir.exists() else []

    text_blob = ""
    for path in lifecycle_dir.glob("*.py") if lifecycle_dir.exists() else []:
        text_blob += path.read_text(encoding="utf-8", errors="ignore").lower() + "\n"

    covered = [hint for hint in EXPECTED_STAGE_HINTS if hint in text_blob]
    missing = [hint for hint in EXPECTED_STAGE_HINTS if hint not in covered]

    score = round((len(covered) / len(EXPECTED_STAGE_HINTS)) * 100, 2)

    payload = {
        "scorer": "lifecycle_quality_scorer",
        "version": "v16.42",
        "created_at": datetime.now().isoformat(),
        "status": "available",
        "score": score,
        "covered_stage_hints": covered,
        "missing_stage_hints": missing,
        "lifecycle_file_count": len(files),
        "lifecycle_files": files,
        "recommendations": [
            "increase explicit lifecycle stage coverage",
            "ensure terminal states remain route-aware",
            "keep skipped_by_route reasons visible",
            "connect quality scoring to runtime outputs before UI expansion",
        ],
    }

    out_dir = ROOT / "data" / "intelligence"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "lifecycle_quality_score.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"scorer": payload["scorer"], "score": payload["score"], "missing": payload["missing_stage_hints"]}, indent=2))
    print(f"\nLifecycle quality score written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
