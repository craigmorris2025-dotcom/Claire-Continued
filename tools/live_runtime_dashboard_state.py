#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return {"error": repr(exc)}

def run_status(cmd):
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": completed.returncode, "stdout_tail": completed.stdout[-2000:], "stderr_tail": completed.stderr[-2000:]}

def main() -> int:
    runtime_dir = ROOT / "data" / "runtime"
    health = {
        "active_runtime_check": run_status([sys.executable, "tools/active_runtime_check.py"]),
        "runtime_compile_check": run_status([sys.executable, "tools/runtime_compile_check.py"]),
        "core_runtime_lock": run_status([sys.executable, "tools/core_runtime_lock.py"]),
    }
    state = {
        "dashboard": "live_runtime_dashboard_state",
        "version": "v16.30",
        "created_at": datetime.now().isoformat(),
        "status": "success" if all(v["returncode"] == 0 for v in health.values()) else "degraded",
        "runtime_health": health,
        "runtime_manifest": load_json(runtime_dir / "runtime_manifest.json"),
        "active_module_registry": load_json(runtime_dir / "active_module_registry.json"),
        "core_runtime_lock": load_json(runtime_dir / "core_runtime_lock.json"),
        "rollback_validation": load_json(runtime_dir / "rollback_validation.json"),
    }
    runtime_dir.mkdir(parents=True, exist_ok=True)
    out_path = runtime_dir / "live_runtime_dashboard_state.json"
    out_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({"dashboard": state["dashboard"], "status": state["status"], "health_checks": {k: v["returncode"] for k, v in health.items()}}, indent=2))
    print(f"\nLive runtime dashboard state written: {out_path}")
    return 0 if state["status"] == "success" else 1

if __name__ == "__main__":
    raise SystemExit(main())
