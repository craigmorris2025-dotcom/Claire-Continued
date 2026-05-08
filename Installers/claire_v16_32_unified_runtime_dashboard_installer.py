#!/usr/bin/env python3
"""
Claire v16.32_unified_runtime_dashboard Installer
Unified Runtime Dashboard
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


VERSION = "v16.32_unified_runtime_dashboard"
FILES = {'src/claire/dashboard/unified_runtime_dashboard.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef _load(path: Path):\n    if not path.exists():\n        return None\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n\ndef build_unified_runtime_dashboard(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    runtime = base / "data" / "runtime"\n    return {\n        "dashboard": "unified_runtime_dashboard",\n        "status": "available",\n        "runtime_state": _load(runtime / "runtime_state.json"),\n        "live_runtime_dashboard_state": _load(runtime / "live_runtime_dashboard_state.json"),\n        "runtime_manifest": _load(runtime / "runtime_manifest.json"),\n        "active_module_registry": _load(runtime / "active_module_registry.json"),\n        "core_runtime_lock": _load(runtime / "core_runtime_lock.json"),\n        "rollback_validation": _load(runtime / "rollback_validation.json"),\n    }\n', 'tools/unified_runtime_dashboard_builder.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json, subprocess, sys\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\ndef main() -> int:\n    subprocess.run([sys.executable, "tools/runtime_state_engine.py"], cwd=ROOT)\n    subprocess.run([sys.executable, "tools/live_runtime_dashboard_state.py"], cwd=ROOT)\n    from claire.dashboard.unified_runtime_dashboard import build_unified_runtime_dashboard\n    payload = build_unified_runtime_dashboard(ROOT)\n    payload["version"] = "v16.32"\n    payload["created_at"] = datetime.now().isoformat()\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "unified_runtime_dashboard.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps({"dashboard": payload["dashboard"], "status": payload["status"], "created_at": payload["created_at"]}, indent=2))\n    print(f"\\nUnified runtime dashboard written: {out}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/UNIFIED_RUNTIME_DASHBOARD.md': '# Claire Unified Runtime Dashboard\n\nv16.32 creates a unified JSON dashboard for runtime state, manifests, active modules, locks, and rollback state.\n', 'tests/regression/test_unified_runtime_dashboard.py': 'import subprocess, sys, json\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_unified_runtime_dashboard_builder_runs():\n    result = subprocess.run([sys.executable, "tools/unified_runtime_dashboard_builder.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    data = json.loads((ROOT / "data" / "runtime" / "unified_runtime_dashboard.json").read_text(encoding="utf-8"))\n    assert data["dashboard"] == "unified_runtime_dashboard"\n\ndef test_unified_runtime_dashboard_imports():\n    from claire.dashboard.unified_runtime_dashboard import build_unified_runtime_dashboard\n    payload = build_unified_runtime_dashboard(ROOT)\n    assert payload["status"] == "available"\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("unified_runtime_dashboard_builder", [sys.executable, "tools/unified_runtime_dashboard_builder.py"]),
        run_command("unified_runtime_dashboard_tests", [sys.executable, "-m", "pytest", "tests/regression/test_unified_runtime_dashboard.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Unified Runtime Dashboard",
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
