#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def run(cmd):
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": completed.returncode, "stdout_tail": completed.stdout[-2000:], "stderr_tail": completed.stderr[-2000:]}

def main() -> int:
    checks = {
        "runtime_lock": run([sys.executable, "tools/core_runtime_lock.py"]),
        "active_runtime": run([sys.executable, "tools/active_runtime_check.py"]),
        "compile": run([sys.executable, "tools/runtime_compile_check.py"]),
        "rollback": run([sys.executable, "tools/rollback_validation.py"]),
    }
    recovery_needed = any(c["returncode"] != 0 for c in checks.values())
    payload = {
        "engine": "runtime_recovery_engine",
        "version": "v16.34",
        "created_at": datetime.now().isoformat(),
        "status": "recovery_not_needed" if not recovery_needed else "recovery_needed",
        "checks": checks,
        "recommended_action": "continue" if not recovery_needed else "review latest backup set and protected runtime lock",
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "runtime_recovery_state.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"engine": payload["engine"], "status": payload["status"], "recommended_action": payload["recommended_action"]}, indent=2))
    print(f"\nRuntime recovery state written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
