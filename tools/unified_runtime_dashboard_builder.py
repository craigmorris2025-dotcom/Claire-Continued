#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def main() -> int:
    subprocess.run([sys.executable, "tools/runtime_state_engine.py"], cwd=ROOT)
    subprocess.run([sys.executable, "tools/live_runtime_dashboard_state.py"], cwd=ROOT)
    from claire.dashboard.unified_runtime_dashboard import build_unified_runtime_dashboard
    payload = build_unified_runtime_dashboard(ROOT)
    payload["version"] = "v16.32"
    payload["created_at"] = datetime.now().isoformat()
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "unified_runtime_dashboard.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"dashboard": payload["dashboard"], "status": payload["status"], "created_at": payload["created_at"]}, indent=2))
    print(f"\nUnified runtime dashboard written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
