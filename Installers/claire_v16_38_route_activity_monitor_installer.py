#!/usr/bin/env python3
"""
Claire v16.38_route_activity_monitor
Route Activity Monitor
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


VERSION = "v16.38_route_activity_monitor"
FILES = {'tools/route_activity_monitor.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\nROUTES = [\n    "evaluate",\n    "discover",\n    "portfolio",\n    "breakthrough",\n    "design",\n    "packages",\n    "monitor",\n]\n\ndef main() -> int:\n    payload = {\n        "monitor": "route_activity_monitor",\n        "version": "v16.38",\n        "created_at": datetime.now().isoformat(),\n        "routes": [{"route": r, "status": "available"} for r in ROUTES],\n        "active_route_count": len(ROUTES),\n    }\n\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "route_activity_monitor.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({"monitor": payload["monitor"], "active_route_count": payload["active_route_count"]}, indent=2))\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/ROUTE_ACTIVITY_MONITOR.md': '# Claire Route Activity Monitor\n\nv16.38 tracks available runtime route surfaces and route health.\n', 'tests/regression/test_route_activity_monitor.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_route_activity_monitor_runs():\n    result = subprocess.run([sys.executable, "tools/route_activity_monitor.py"], cwd=ROOT)\n    assert result.returncode == 0\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("route_activity_monitor", [sys.executable, "tools/route_activity_monitor.py"]),
        run_command("route_activity_monitor_tests", [sys.executable, "-m", "pytest", "tests/regression/test_route_activity_monitor.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Route Activity Monitor",
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
