#!/usr/bin/env python3
"""
Claire v16.31_runtime_state_engine Installer
Runtime State Engine
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

ROOT = Path.cwd()
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = ROOT / ".claire_install" / "reports"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def backup_dir(version: str) -> Path:
    return ROOT / ".claire_install" / "backups" / f"{version}_{TIMESTAMP}"


def backup(path: Path, version: str) -> str | None:
    if not path.exists():
        return None
    target = backup_dir(version) / rel(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return rel(target)


def write_file(path: Path, content: str, version: str) -> Dict[str, Any]:
    action = {
        "action": "write_file",
        "path": rel(path),
        "existed_before": path.exists(),
        "backup_path": backup(path, version),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return action


def run_command(name: str, cmd: List[str]) -> Dict[str, Any]:
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-5000:],
        "stderr_tail": completed.stderr[-5000:],
    }


def write_report(version: str, payload: Dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{version}_{TIMESTAMP}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


VERSION = "v16.31_runtime_state_engine"
FILES = {'tools/runtime_state_engine.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json, subprocess, sys\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\ndef run(cmd):\n    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)\n    return {"cmd": cmd, "returncode": completed.returncode, "stdout_tail": completed.stdout[-2000:], "stderr_tail": completed.stderr[-2000:]}\n\ndef load(path):\n    if not path.exists():\n        return None\n    try:\n        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n    except Exception as exc:\n        return {"error": repr(exc)}\n\ndef main() -> int:\n    runtime = ROOT / "data" / "runtime"\n    checks = {\n        "active_runtime": run([sys.executable, "tools/active_runtime_check.py"]),\n        "compile": run([sys.executable, "tools/runtime_compile_check.py"]),\n        "runtime_lock": run([sys.executable, "tools/core_runtime_lock.py"]),\n        "manifest": run([sys.executable, "tools/runtime_manifest_builder.py"]),\n        "modules": run([sys.executable, "tools/active_module_registry.py"]),\n    }\n    status = "healthy" if all(c["returncode"] == 0 for c in checks.values()) else "degraded"\n    payload = {\n        "engine": "runtime_state_engine",\n        "version": "v16.31",\n        "created_at": datetime.now().isoformat(),\n        "status": status,\n        "checks": checks,\n        "runtime_manifest_summary": load(runtime / "runtime_manifest.json"),\n        "active_module_registry": load(runtime / "active_module_registry.json"),\n        "core_runtime_lock": load(runtime / "core_runtime_lock.json"),\n    }\n    runtime.mkdir(parents=True, exist_ok=True)\n    out = runtime / "runtime_state.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps({"engine": payload["engine"], "status": status, "created_at": payload["created_at"]}, indent=2))\n    print(f"\\nRuntime state written: {out}")\n    return 0 if status == "healthy" else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/runtime/runtime_state_engine.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef load_runtime_state(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "runtime" / "runtime_state.json"\n    if not path.exists():\n        return {"status": "not_available", "message": "Run python tools/runtime_state_engine.py first."}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/runtime/RUNTIME_STATE_ENGINE.md': '# Claire Runtime State Engine\n\nv16.31 aggregates runtime health, compile state, manifest state, active modules, and runtime lock state.\n', 'tests/regression/test_runtime_state_engine.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_runtime_state_engine_runs():\n    result = subprocess.run([sys.executable, "tools/runtime_state_engine.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "runtime" / "runtime_state.json").exists()\n\ndef test_runtime_state_loader_imports():\n    from claire.runtime.runtime_state_engine import load_runtime_state\n    state = load_runtime_state(ROOT)\n    assert "status" in state\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("runtime_state_engine", [sys.executable, "tools/runtime_state_engine.py"]),
        run_command("runtime_state_engine_tests", [sys.executable, "-m", "pytest", "tests/regression/test_runtime_state_engine.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Runtime State Engine",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "installed_with_warnings",
        "root": str(ROOT),
        "actions": actions,
        "validations": validations,
        "failed_validation_count": len(failed),
    }
    report_path = write_report(VERSION, report)
    print(json.dumps(report, indent=2))
    print(f"\nInstall report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
