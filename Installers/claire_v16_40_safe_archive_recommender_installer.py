#!/usr/bin/env python3
"""
Claire v16.40_safe_archive_recommender
Safe Archive Recommender
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


VERSION = "v16.40_safe_archive_recommender"
FILES = {'tools/safe_archive_recommender.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\nPROTECTED = [\n    "src/claire/app.py",\n    "src/claire/api",\n    "src/claire/orchestrator",\n    "src/claire/lifecycle",\n]\n\ndef main() -> int:\n    dormant_path = ROOT / "data" / "runtime" / "orphan_dormant_modules.json"\n\n    candidates = []\n    if dormant_path.exists():\n        data = json.loads(dormant_path.read_text(encoding="utf-8"))\n        for item in data.get("candidates", []):\n            path = item["path"]\n            if any(path.startswith(p) for p in PROTECTED):\n                continue\n            candidates.append({\n                "path": path,\n                "recommendation": "review_before_archive",\n            })\n\n    payload = {\n        "recommender": "safe_archive_recommender",\n        "version": "v16.40",\n        "created_at": datetime.now().isoformat(),\n        "recommendation_count": len(candidates),\n        "recommendations": candidates,\n    }\n\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n\n    out = out_dir / "safe_archive_recommendations.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({\n        "recommender": payload["recommender"],\n        "recommendation_count": payload["recommendation_count"]\n    }, indent=2))\n\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/SAFE_ARCHIVE_RECOMMENDER.md': '# Claire Safe Archive Recommender\n\nv16.40 recommends non-protected dormant modules for human review before archive.\n', 'tests/regression/test_safe_archive_recommender.py': 'import subprocess, sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_safe_archive_recommender_runs():\n    subprocess.run([sys.executable, "tools/orphan_dormant_module_detector.py"], cwd=ROOT)\n    result = subprocess.run([sys.executable, "tools/safe_archive_recommender.py"], cwd=ROOT)\n    assert result.returncode == 0\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("safe_archive_recommender", [sys.executable, "tools/safe_archive_recommender.py"]),
        run_command("safe_archive_recommender_tests", [sys.executable, "-m", "pytest", "tests/regression/test_safe_archive_recommender.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Safe Archive Recommender",
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
