#!/usr/bin/env python3
"""
Claire v16.45 Runtime + Intelligence Unified Control Layer Installer
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

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


def run_command(name: str, cmd: list[str]) -> Dict[str, Any]:
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


FILES = {
    "tools/master_control_layer_builder.py": """#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

RUNTIME_FILES = [
    "runtime_state.json",
    "unified_runtime_dashboard.json",
    "runtime_control_center.json",
    "runtime_intelligence.json",
    "runtime_recovery_state.json",
    "route_activity_monitor.json",
    "install_governance_dashboard.json",
]

INTELLIGENCE_FILES = [
    "lifecycle_quality_score.json",
    "trend_thesis_intelligence.json",
    "portfolio_breakthrough_routing.json",
]

def load(path: Path):
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        return {"status": "error", "path": str(path), "error": repr(exc)}

def main() -> int:
    runtime_dir = ROOT / "data" / "runtime"
    intelligence_dir = ROOT / "data" / "intelligence"

    runtime = {name: load(runtime_dir / name) for name in RUNTIME_FILES}
    intelligence = {name: load(intelligence_dir / name) for name in INTELLIGENCE_FILES}

    payload = {
        "layer": "master_control_state",
        "version": "v16.45",
        "created_at": datetime.now().isoformat(),
        "runtime": runtime,
        "intelligence": intelligence,
        "status": "available",
        "recommendations": [
            "continue protecting runtime spine",
            "keep install governance mandatory",
            "connect intelligence outputs to lifecycle runtime gradually",
            "avoid direct uncontrolled feature expansion",
            "preserve portfolio-first routing policy",
        ],
    }

    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "master_control_state.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "layer": payload["layer"],
        "status": payload["status"],
    }, indent=2))

    print(f"\nMaster control state written: {out}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
""",

    "src/claire/control/master_control_state.py": """from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def load_master_control_state(root: str | Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root else Path.cwd()

    path = base / "data" / "runtime" / "master_control_state.json"

    if not path.exists():
        return {
            "status": "not_available",
            "message": "Run python tools/master_control_layer_builder.py first.",
        }

    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
""",

    "docs/runtime/MASTER_CONTROL_LAYER.md": """# Claire Master Control Layer

v16.45 unifies:
- runtime governance
- runtime operationalization
- runtime self-maintenance
- intelligence scoring
- route intelligence
- recovery state
- runtime health

into a single master operating state.

Output:
data/runtime/master_control_state.json
""",

    "tests/regression/test_master_control_layer.py": """import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_master_control_layer_builder_runs():
    result = subprocess.run(
        [sys.executable, "tools/master_control_layer_builder.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0

    assert (
        ROOT / "data" / "runtime" / "master_control_state.json"
    ).exists()


def test_master_control_loader_imports():
    from claire.control.master_control_state import (
        load_master_control_state,
    )

    payload = load_master_control_state(ROOT)

    assert (
        "runtime" in payload
        or payload.get("status") == "not_available"
    )
""",
}


VERSION = "v16.45_runtime_intelligence_unified_control_layer"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []

    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command(
            "master_control_layer_builder",
            [sys.executable, "tools/master_control_layer_builder.py"],
        ),
        run_command(
            "master_control_layer_tests",
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/regression/test_master_control_layer.py",
                "-q",
            ],
        ),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Runtime + Intelligence Unified Control Layer",
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
