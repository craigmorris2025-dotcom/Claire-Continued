#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

SIGNALS = ["trend", "thesis", "signal", "cluster", "market", "evidence", "confidence"]

def main() -> int:
    search_dirs = [
        ROOT / "src" / "claire" / "engines",
        ROOT / "src" / "claire" / "trends",
        ROOT / "src" / "claire" / "thesis",
        ROOT / "src" / "claire" / "feeds",
    ]

    evidence = []
    corpus = ""
    for d in search_dirs:
        if not d.exists():
            continue
        for path in d.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            corpus += text + "\n"
            hits = [s for s in SIGNALS if s in text]
            if hits:
                evidence.append({
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "signals": hits,
                })

    signal_coverage = {s: corpus.count(s) for s in SIGNALS}
    readiness = "strong" if signal_coverage.get("trend", 0) and signal_coverage.get("thesis", 0) else "partial"

    payload = {
        "upgrade": "trend_thesis_intelligence",
        "version": "v16.43",
        "created_at": datetime.now().isoformat(),
        "status": "available",
        "readiness": readiness,
        "signal_coverage": signal_coverage,
        "evidence_file_count": len(evidence),
        "evidence": evidence[:200],
        "recommendations": [
            "connect trend/thesis scoring to core_run_output",
            "track confidence and evidence per thesis",
            "separate trend discovery from breakthrough escalation",
            "preserve portfolio-first default route",
        ],
    }

    out_dir = ROOT / "data" / "intelligence"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "trend_thesis_intelligence.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"upgrade": payload["upgrade"], "readiness": payload["readiness"], "evidence_file_count": payload["evidence_file_count"]}, indent=2))
    print(f"\nTrend thesis intelligence written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
