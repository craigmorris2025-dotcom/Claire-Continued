#!/usr/bin/env python3
"""
Claire v16.30_live_runtime_dashboard Installer
Live Runtime Dashboard
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


VERSION = "v16.30_live_runtime_dashboard"
FILES = {'tools/live_runtime_dashboard_state.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json, subprocess, sys\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\ndef load_json(path: Path):\n    if not path.exists():\n        return None\n    try:\n        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n    except Exception as exc:\n        return {"error": repr(exc)}\n\ndef run_status(cmd):\n    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)\n    return {"cmd": cmd, "returncode": completed.returncode, "stdout_tail": completed.stdout[-2000:], "stderr_tail": completed.stderr[-2000:]}\n\ndef main() -> int:\n    runtime_dir = ROOT / "data" / "runtime"\n    health = {\n        "active_runtime_check": run_status([sys.executable, "tools/active_runtime_check.py"]),\n        "runtime_compile_check": run_status([sys.executable, "tools/runtime_compile_check.py"]),\n        "core_runtime_lock": run_status([sys.executable, "tools/core_runtime_lock.py"]),\n    }\n    state = {\n        "dashboard": "live_runtime_dashboard_state",\n        "version": "v16.30",\n        "created_at": datetime.now().isoformat(),\n        "status": "success" if all(v["returncode"] == 0 for v in health.values()) else "degraded",\n        "runtime_health": health,\n        "runtime_manifest": load_json(runtime_dir / "runtime_manifest.json"),\n        "active_module_registry": load_json(runtime_dir / "active_module_registry.json"),\n        "core_runtime_lock": load_json(runtime_dir / "core_runtime_lock.json"),\n        "rollback_validation": load_json(runtime_dir / "rollback_validation.json"),\n    }\n    runtime_dir.mkdir(parents=True, exist_ok=True)\n    out_path = runtime_dir / "live_runtime_dashboard_state.json"\n    out_path.write_text(json.dumps(state, indent=2), encoding="utf-8")\n    print(json.dumps({"dashboard": state["dashboard"], "status": state["status"], "health_checks": {k: v["returncode"] for k, v in health.items()}}, indent=2))\n    print(f"\\nLive runtime dashboard state written: {out_path}")\n    return 0 if state["status"] == "success" else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/dashboard/live_runtime_state.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef load_live_runtime_state(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "runtime" / "live_runtime_dashboard_state.json"\n    if not path.exists():\n        return {"status": "not_available", "message": "Run python tools/live_runtime_dashboard_state.py first."}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/runtime/LIVE_RUNTIME_DASHBOARD.md': '# Claire Live Runtime Dashboard\n\nv16.30 creates a machine-readable live dashboard state.\n', 'tests/regression/test_live_runtime_dashboard.py': 'import json, subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_live_runtime_dashboard_state_builds():\n    result = subprocess.run([sys.executable, "tools/live_runtime_dashboard_state.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    path = ROOT / "data" / "runtime" / "live_runtime_dashboard_state.json"\n    assert path.exists()\n    data = json.loads(path.read_text(encoding="utf-8"))\n    assert data["dashboard"] == "live_runtime_dashboard_state"\n\ndef test_live_runtime_state_loader_imports():\n    from claire.dashboard.live_runtime_state import load_live_runtime_state\n    state = load_live_runtime_state(ROOT)\n    assert "status" in state\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("live_runtime_dashboard_state", [sys.executable, "tools/live_runtime_dashboard_state.py"]),
        run_command("live_runtime_dashboard_tests", [sys.executable, "-m", "pytest", "tests/regression/test_live_runtime_dashboard.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Live Runtime Dashboard",
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
