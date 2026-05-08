#!/usr/bin/env python3
"""
Claire v16.29_core_runtime_lock Installer
Core Runtime Lock
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


VERSION = "v16.29_core_runtime_lock"
FILES = {'tools/core_runtime_lock.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport importlib, json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nPROTECTED_CONTRACTS = [\n    {"path": "main.py", "type": "launch_entrypoint"},\n    {"path": "src/claire/app.py", "type": "app_factory"},\n    {"path": "src/claire/api/routes_pipeline.py", "type": "api_route"},\n    {"path": "src/claire/orchestrator/pipeline_v4.py", "type": "runtime_orchestrator"},\n    {"path": "src/claire/technology/technology_intelligence.py", "type": "runtime_dependency"},\n]\nREQUIRED_IMPORTS = [\n    "claire.app",\n    "claire.api.routes_pipeline",\n    "claire.orchestrator.pipeline_v4",\n    "claire.technology.technology_intelligence",\n]\n\ndef main() -> int:\n    path_results = []\n    for item in PROTECTED_CONTRACTS:\n        p = ROOT / item["path"]\n        path_results.append({**item, "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0})\n    import_results = []\n    for module in REQUIRED_IMPORTS:\n        try:\n            importlib.import_module(module)\n            import_results.append({"module": module, "status": "success"})\n        except Exception as exc:\n            import_results.append({"module": module, "status": "failed", "error": repr(exc)})\n    payload = {\n        "lock": "core_runtime_lock",\n        "version": "v16.29",\n        "created_at": datetime.now().isoformat(),\n        "status": "locked" if all(p["exists"] for p in path_results) and all(i["status"] == "success" for i in import_results) else "failed",\n        "protected_contracts": path_results,\n        "required_imports": import_results,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "core_runtime_lock.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nRuntime lock written: {out_path}")\n    return 0 if payload["status"] == "locked" else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/lifecycle_enforcement_check.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport importlib, json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nMODULES = [\n    "claire.lifecycle.lifecycle_runner",\n    "claire.lifecycle.stage_registry",\n    "claire.lifecycle.stage_contracts",\n    "claire.lifecycle.stage_status",\n]\n\ndef main() -> int:\n    results = []\n    for module in MODULES:\n        try:\n            importlib.import_module(module)\n            results.append({"module": module, "status": "success"})\n        except Exception as exc:\n            results.append({"module": module, "status": "failed", "error": repr(exc)})\n    payload = {\n        "check": "lifecycle_enforcement_check",\n        "version": "v16.29",\n        "created_at": datetime.now().isoformat(),\n        "status": "success" if all(r["status"] == "success" for r in results) else "failed",\n        "modules": results,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "lifecycle_enforcement_check.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nLifecycle enforcement check written: {out_path}")\n    return 0 if payload["status"] == "success" else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/rollback_validation.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nBACKUPS = ROOT / ".claire_install" / "backups"\nREPORTS = ROOT / ".claire_install" / "reports"\n\ndef main() -> int:\n    backup_sets = []\n    if BACKUPS.exists():\n        for path in sorted(BACKUPS.iterdir()):\n            if path.is_dir():\n                backup_sets.append({"name": path.name, "file_count": sum(1 for p in path.rglob("*") if p.is_file())})\n    payload = {\n        "validation": "rollback_validation",\n        "version": "v16.29",\n        "created_at": datetime.now().isoformat(),\n        "status": "success",\n        "backup_set_count": len(backup_sets),\n        "backup_sets": backup_sets[-50:],\n        "install_report_count": len(list(REPORTS.glob("*.json"))) if REPORTS.exists() else 0,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "rollback_validation.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nRollback validation written: {out_path}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/CORE_RUNTIME_LOCK.md': '# Claire Core Runtime Lock\n\nv16.29 defines the protected launch spine.\n', 'tests/regression/test_core_runtime_lock.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_core_runtime_lock_passes():\n    assert subprocess.run([sys.executable, "tools/core_runtime_lock.py"], cwd=ROOT).returncode == 0\n\ndef test_lifecycle_enforcement_check_passes():\n    assert subprocess.run([sys.executable, "tools/lifecycle_enforcement_check.py"], cwd=ROOT).returncode == 0\n\ndef test_rollback_validation_runs():\n    assert subprocess.run([sys.executable, "tools/rollback_validation.py"], cwd=ROOT).returncode == 0\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("core_runtime_lock", [sys.executable, "tools/core_runtime_lock.py"]),
        run_command("lifecycle_enforcement_check", [sys.executable, "tools/lifecycle_enforcement_check.py"]),
        run_command("rollback_validation", [sys.executable, "tools/rollback_validation.py"]),
        run_command("core_runtime_lock_tests", [sys.executable, "-m", "pytest", "tests/regression/test_core_runtime_lock.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Core Runtime Lock",
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
