#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def load(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return {"error": repr(exc)}

def main() -> int:
    runtime = ROOT / "data" / "runtime"
    payload = {
        "control_center": "live_runtime_control_center",
        "version": "v16.36",
        "created_at": datetime.now().isoformat(),
        "runtime_state": load(runtime / "runtime_state.json"),
        "runtime_lock": load(runtime / "core_runtime_lock.json"),
        "runtime_dashboard": load(runtime / "unified_runtime_dashboard.json"),
        "runtime_intelligence": load(runtime / "runtime_intelligence.json"),
        "operator_status": "active",
    }
    runtime.mkdir(parents=True, exist_ok=True)
    out = runtime / "runtime_control_center.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"control_center": payload["control_center"], "operator_status": payload["operator_status"]}, indent=2))
    print(f"\\nRuntime control center written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
