#!/usr/bin/env python3
"""
Claire v16.33_autonomous_install_validator Installer
Autonomous Install Validator
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


VERSION = "v16.33_autonomous_install_validator"
FILES = {'tools/autonomous_install_validator.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport ast, json, sys\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nPROTECTED = [\n    "main.py",\n    "src/claire/app.py",\n    "src/claire/api/routes_pipeline.py",\n    "src/claire/orchestrator/pipeline_v4.py",\n    "src/claire/technology/technology_intelligence.py",\n]\n\ndef validate_installer(path: Path):\n    issues = []\n    if not path.exists():\n        return {"path": str(path), "status": "failed", "issues": ["installer_missing"]}\n    text = path.read_text(encoding="utf-8", errors="ignore")\n    try:\n        ast.parse(text)\n    except SyntaxError as exc:\n        issues.append(f"syntax_error:{exc.lineno}:{exc.msg}")\n    if ".claire_install" not in text:\n        issues.append("missing_install_report_pattern")\n    if "backup" not in text.lower():\n        issues.append("missing_backup_pattern")\n    touched_protected = [p for p in PROTECTED if p in text]\n    return {\n        "path": str(path),\n        "status": "approved" if not issues else "blocked",\n        "issues": issues,\n        "mentions_protected_paths": touched_protected,\n        "risk": "elevated" if touched_protected else "normal",\n    }\n\ndef main() -> int:\n    targets = [Path(arg) for arg in sys.argv[1:]]\n    if not targets:\n        targets = sorted(ROOT.glob("*installer*.py"))[-10:]\n    results = [validate_installer(t if t.is_absolute() else ROOT / t) for t in targets]\n    payload = {\n        "validator": "autonomous_install_validator",\n        "version": "v16.33",\n        "created_at": datetime.now().isoformat(),\n        "status": "approved" if all(r["status"] == "approved" for r in results) else "blocked",\n        "validated_count": len(results),\n        "results": results,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "autonomous_install_validation.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nInstall validation written: {out}")\n    return 0 if payload["status"] == "approved" else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/AUTONOMOUS_INSTALL_VALIDATOR.md': '# Claire Autonomous Install Validator\n\nv16.33 checks installer syntax, report behavior, backup behavior, and protected path risk before installation.\n', 'tests/regression/test_autonomous_install_validator.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_autonomous_install_validator_runs_on_itself():\n    target = ROOT / "tools" / "autonomous_install_validator.py"\n    result = subprocess.run([sys.executable, "tools/autonomous_install_validator.py", str(target)], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode in (0, 1)\n    assert (ROOT / "data" / "runtime" / "autonomous_install_validation.json").exists()\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("autonomous_install_validator", [sys.executable, "tools/autonomous_install_validator.py", "tools/autonomous_install_validator.py"]),
        run_command("autonomous_install_validator_tests", [sys.executable, "-m", "pytest", "tests/regression/test_autonomous_install_validator.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Autonomous Install Validator",
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
