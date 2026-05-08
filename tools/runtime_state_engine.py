#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def run(cmd):
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": completed.returncode, "stdout_tail": completed.stdout[-2000:], "stderr_tail": completed.stderr[-2000:]}

def load(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return {"error": repr(exc)}

def main() -> int:
    runtime = ROOT / "data" / "runtime"
    checks = {
        "active_runtime": run([sys.executable, "tools/active_runtime_check.py"]),
        "compile": run([sys.executable, "tools/runtime_compile_check.py"]),
        "runtime_lock": run([sys.executable, "tools/core_runtime_lock.py"]),
        "manifest": run([sys.executable, "tools/runtime_manifest_builder.py"]),
        "modules": run([sys.executable, "tools/active_module_registry.py"]),
    }
    status = "healthy" if all(c["returncode"] == 0 for c in checks.values()) else "degraded"
    payload = {
        "engine": "runtime_state_engine",
        "version": "v16.31",
        "created_at": datetime.now().isoformat(),
        "status": status,
        "checks": checks,
        "runtime_manifest_summary": load(runtime / "runtime_manifest.json"),
        "active_module_registry": load(runtime / "active_module_registry.json"),
        "core_runtime_lock": load(runtime / "core_runtime_lock.json"),
    }
    runtime.mkdir(parents=True, exist_ok=True)
    out = runtime / "runtime_state.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"engine": payload["engine"], "status": status, "created_at": payload["created_at"]}, indent=2))
    print(f"\nRuntime state written: {out}")
    return 0 if status == "healthy" else 1

if __name__ == "__main__":
    raise SystemExit(main())
