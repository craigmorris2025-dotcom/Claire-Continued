#!/usr/bin/env python3
"""
Claire v16.39_orphan_dormant_module_detector
Orphan Dormant Module Detector
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

def write_file(path: Path, content: str, version: str):
    action = {
        "action": "write_file",
        "path": rel(path),
        "existed_before": path.exists(),
        "backup_path": backup(path, version),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return action

def run_command(name: str, cmd: list[str]):
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-3000:],
        "stderr_tail": completed.stderr[-3000:],
    }

def write_report(version: str, payload: dict):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{version}_{TIMESTAMP}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


VERSION = "v16.39_orphan_dormant_module_detector"
FILES = {'tools/orphan_dormant_module_detector.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\nKEYWORDS = ["placeholder", "legacy", "deprecated", "unused", "proof", "demo"]\n\ndef main() -> int:\n    candidates = []\n    src = ROOT / "src" / "claire"\n\n    if src.exists():\n        for path in src.rglob("*.py"):\n            rel = str(path.relative_to(ROOT)).replace("\\\\", "/")\n            lowered = rel.lower()\n            if any(k in lowered for k in KEYWORDS):\n                candidates.append({\n                    "path": rel,\n                    "reason": "keyword_match",\n                })\n\n    payload = {\n        "detector": "orphan_dormant_module_detector",\n        "version": "v16.39",\n        "created_at": datetime.now().isoformat(),\n        "candidate_count": len(candidates),\n        "candidates": candidates[:500],\n    }\n\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n\n    out = out_dir / "orphan_dormant_modules.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({\n        "detector": payload["detector"],\n        "candidate_count": payload["candidate_count"]\n    }, indent=2))\n\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/ORPHAN_DORMANT_MODULE_DETECTOR.md': '# Claire Orphan/Dormant Module Detector\n\nv16.39 identifies potential dormant or legacy runtime modules for review.\n', 'tests/regression/test_orphan_dormant_module_detector.py': 'import subprocess, sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_orphan_dormant_module_detector_runs():\n    result = subprocess.run([sys.executable, "tools/orphan_dormant_module_detector.py"], cwd=ROOT)\n    assert result.returncode == 0\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("orphan_dormant_module_detector", [sys.executable, "tools/orphan_dormant_module_detector.py"]),
        run_command("orphan_dormant_module_detector_tests", [sys.executable, "-m", "pytest", "tests/regression/test_orphan_dormant_module_detector.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Orphan Dormant Module Detector",
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
