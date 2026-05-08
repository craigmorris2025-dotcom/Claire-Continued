#!/usr/bin/env python3
"""
Claire v16.37_install_governance_dashboard
Install Governance Dashboard
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


VERSION = "v16.37_install_governance_dashboard"
FILES = {'tools/install_governance_dashboard.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\ndef main() -> int:\n    reports = ROOT / ".claire_install" / "reports"\n    entries = []\n    if reports.exists():\n        for path in sorted(reports.glob("*.json"))[-100:]:\n            try:\n                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n            except Exception:\n                continue\n            entries.append({\n                "report": str(path.relative_to(ROOT)).replace("\\\\", "/"),\n                "installer": data.get("installer"),\n                "status": data.get("status"),\n            })\n\n    payload = {\n        "dashboard": "install_governance_dashboard",\n        "version": "v16.37",\n        "created_at": datetime.now().isoformat(),\n        "report_count": len(entries),\n        "entries": entries,\n    }\n\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "install_governance_dashboard.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({"dashboard": payload["dashboard"], "report_count": payload["report_count"]}, indent=2))\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/INSTALL_GOVERNANCE_DASHBOARD.md': '# Claire Install Governance Dashboard\n\nv16.37 creates visibility into installer execution history and governance state.\n', 'tests/regression/test_install_governance_dashboard.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_install_governance_dashboard_runs():\n    result = subprocess.run([sys.executable, "tools/install_governance_dashboard.py"], cwd=ROOT)\n    assert result.returncode == 0\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("install_governance_dashboard", [sys.executable, "tools/install_governance_dashboard.py"]),
        run_command("install_governance_dashboard_tests", [sys.executable, "-m", "pytest", "tests/regression/test_install_governance_dashboard.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Install Governance Dashboard",
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
