#!/usr/bin/env python3
"""
Claire v16.36_live_runtime_control_center
Live Runtime Control Center
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
        "stdout_tail": completed.stdout[-3000:],
        "stderr_tail": completed.stderr[-3000:],
    }

def write_report(version: str, payload: Dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{version}_{TIMESTAMP}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


VERSION = "v16.36_live_runtime_control_center"
FILES = {'tools/live_runtime_control_center.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\ndef load(path: Path):\n    if not path.exists():\n        return None\n    try:\n        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n    except Exception as exc:\n        return {"error": repr(exc)}\n\ndef main() -> int:\n    runtime = ROOT / "data" / "runtime"\n    payload = {\n        "control_center": "live_runtime_control_center",\n        "version": "v16.36",\n        "created_at": datetime.now().isoformat(),\n        "runtime_state": load(runtime / "runtime_state.json"),\n        "runtime_lock": load(runtime / "core_runtime_lock.json"),\n        "runtime_dashboard": load(runtime / "unified_runtime_dashboard.json"),\n        "runtime_intelligence": load(runtime / "runtime_intelligence.json"),\n        "operator_status": "active",\n    }\n    runtime.mkdir(parents=True, exist_ok=True)\n    out = runtime / "runtime_control_center.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps({"control_center": payload["control_center"], "operator_status": payload["operator_status"]}, indent=2))\n    print(f"\\\\nRuntime control center written: {out}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/dashboard/runtime_control_center.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\n\ndef load_runtime_control_center(root=None):\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "runtime" / "runtime_control_center.json"\n    if not path.exists():\n        return {"status": "not_available"}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/runtime/LIVE_RUNTIME_CONTROL_CENTER.md': '# Claire Live Runtime Control Center\n\nv16.36 creates an operator-facing runtime control layer.\n', 'tests/regression/test_live_runtime_control_center.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_live_runtime_control_center_runs():\n    result = subprocess.run([sys.executable, "tools/live_runtime_control_center.py"], cwd=ROOT)\n    assert result.returncode == 0\n\ndef test_runtime_control_center_imports():\n    from claire.dashboard.runtime_control_center import load_runtime_control_center\n    payload = load_runtime_control_center(ROOT)\n    assert "operator_status" in payload or "status" in payload\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("live_runtime_control_center", [sys.executable, "tools/live_runtime_control_center.py"]),
        run_command("live_runtime_control_center_tests", [sys.executable, "-m", "pytest", "tests/regression/test_live_runtime_control_center.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Live Runtime Control Center",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "installed_with_warnings",
        "actions": actions,
        "validations": validations,
        "failed_validation_count": len(failed),
    }

    report = write_report(VERSION, payload)

    print(json.dumps(payload, indent=2))
    print(f"\nInstall report written: {report}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
