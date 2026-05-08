#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def main() -> int:
    reports = ROOT / ".claire_install" / "reports"
    entries = []
    if reports.exists():
        for path in sorted(reports.glob("*.json"))[-100:]:
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            entries.append({
                "report": str(path.relative_to(ROOT)).replace("\\", "/"),
                "installer": data.get("installer"),
                "status": data.get("status"),
            })

    payload = {
        "dashboard": "install_governance_dashboard",
        "version": "v16.37",
        "created_at": datetime.now().isoformat(),
        "report_count": len(entries),
        "entries": entries,
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "install_governance_dashboard.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"dashboard": payload["dashboard"], "report_count": payload["report_count"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
