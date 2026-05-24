from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.api.governed_cockpit_attachment_gate_s128_s134 import build_s128_s134_stop_gate

def main() -> int:
    report = build_s128_s134_stop_gate(
        report_dir=Path("reports"),
        store_path=Path("data/s128_s134_review_queue.json"),
        export_dir=Path("exports/s128_s134"),
    )
    print(json.dumps({
        "status": report["status"],
        "ok": report["ok"],
        "forward_motion_allowed": report["forward_motion_allowed"],
        "next_allowed_phase": report["next_allowed_phase"],
        "report_path": report.get("report_path"),
    }, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
