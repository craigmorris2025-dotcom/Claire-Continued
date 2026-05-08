#!/usr/bin/env python3
"""
Claire v16.27 Runtime Cleanroom Installer

Purpose:
- Fix UTF-8 BOM pollution introduced by earlier placeholder creation.
- Quarantine generated placeholder tests that only raise NotImplementedError.
- Add runtime-only compile/test tools.
- Add pytest_runtime.ini so the active core can be tested without polluted placeholder tests.
- Preserve /docs and active runtime imports.

This installer is additive + backup-safe.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


VERSION = "v16.27_runtime_cleanroom"
ROOT = Path.cwd()
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = ROOT / ".claire_install" / "reports"
BACKUP_DIR = ROOT / ".claire_install" / "backups" / f"{VERSION}_{TIMESTAMP}"

BOM_FIX_FILES = [
    "src/claire/autonomous/governance/__init__.py",
    "src/claire/design/proof/__init__.py",
    "src/claire/design/renderers/__init__.py",
    "src/claire/production/uptime_monitor.py",
    "src/claire/recursive/longitudinal/__init__.py",
    "src/claire/research/live/__init__.py",
    "src/claire/technology/__init__.py",
    "src/claire/validation/benchmarks/__init__.py",
]

PLACEHOLDER_TESTS = [
    "tests/test_acquisition_stages.py",
    "tests/test_analysis_stages.py",
    "tests/test_breakthrough_stages.py",
    "tests/test_feasibility_stages.py",
    "tests/test_memory_system.py",
    "tests/test_portfolio_stages.py",
    "tests/test_validation_system.py",
]

FILES = {'tools/runtime_compile_check.py': '#!/usr/bin/env python3\n"""\nRuntime Compile Check\n\nFast syntax check for active runtime source.\n"""\n\nfrom __future__ import annotations\n\nimport ast\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\n\nROOT = Path.cwd()\nSRC = ROOT / "src"\n\n\ndef main() -> int:\n    failures = []\n\n    for path in SRC.rglob("*.py"):\n        try:\n            text = path.read_text(encoding="utf-8-sig", errors="strict")\n            ast.parse(text, filename=str(path))\n        except SyntaxError as exc:\n            failures.append({\n                "path": str(path.relative_to(ROOT)),\n                "line": exc.lineno,\n                "error": exc.msg,\n            })\n        except Exception as exc:\n            failures.append({\n                "path": str(path.relative_to(ROOT)),\n                "line": None,\n                "error": repr(exc),\n            })\n\n    payload = {\n        "check": "runtime_compile_check",\n        "created_at": datetime.now().isoformat(),\n        "status": "success" if not failures else "failed",\n        "failure_count": len(failures),\n        "failures": failures[:100],\n    }\n\n    out_dir = ROOT / ".claire_install" / "reports"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f"runtime_compile_check_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps(payload, indent=2))\n    print(f"\\nReport written: {out_path}")\n    return 0 if payload["status"] == "success" else 1\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/runtime_test_scope.py': '#!/usr/bin/env python3\n"""\nRuntime Test Scope\n\nLists tests considered active runtime tests versus quarantined placeholder tests.\n"""\n\nfrom __future__ import annotations\n\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\n\nROOT = Path.cwd()\nTESTS = ROOT / "tests"\n\n\ndef main() -> int:\n    active = []\n    quarantined = []\n\n    if TESTS.exists():\n        for path in TESTS.rglob("test_*.py"):\n            rel = str(path.relative_to(ROOT))\n            if "placeholder_disabled" in rel:\n                quarantined.append(rel)\n            else:\n                active.append(rel)\n\n    payload = {\n        "tool": "runtime_test_scope",\n        "created_at": datetime.now().isoformat(),\n        "active_test_count": len(active),\n        "quarantined_placeholder_test_count": len(quarantined),\n        "active_tests": active,\n        "quarantined_placeholder_tests": quarantined,\n    }\n\n    out_dir = ROOT / ".claire_install" / "reports"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f"runtime_test_scope_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps(payload, indent=2))\n    print(f"\\nReport written: {out_path}")\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'pytest_runtime.ini': '[pytest]\ntestpaths =\n    tests/regression\n    tests/consistency\npythonpath =\n    .\n    src\naddopts = -q\nnorecursedirs =\n    tests/placeholder_disabled\n    archive\n    exports\n    .claire_install\n    .venv\n', 'docs/install_governance/RUNTIME_CLEANROOM.md': '# Claire Runtime Cleanroom\n\nv16.27 establishes a clean runtime testing surface.\n\n## What this means\n\nThe full repository can still contain generated exports, docs, historical proof packs, and archived scaffolds.\n\nThe active runtime surface must remain:\n\n- importable\n- syntax clean\n- launchable\n- testable without generated placeholder tests\n\n## Placeholder test policy\n\nGenerated tests that only contain `raise NotImplementedError("Import target class")` are not valid active tests.\n\nThey belong in:\n\n`tests/placeholder_disabled/`\n\nThey can be restored later only after they are connected to real target classes.\n\n## Runtime test command\n\nUse:\n\n`pytest -c pytest_runtime.ini`\n\ninstead of full `pytest tests` during stabilization.\n\n## Runtime compile command\n\nUse:\n\n`python tools/runtime_compile_check.py`\n', 'tests/regression/test_runtime_cleanroom.py': 'from pathlib import Path\n\n\nROOT = Path(__file__).resolve().parents[2]\n\n\ndef test_placeholder_tests_are_quarantined():\n    offenders = []\n    for path in (ROOT / "tests").rglob("test_*.py"):\n        if "placeholder_disabled" in str(path):\n            continue\n        text = path.read_text(encoding="utf-8", errors="ignore")\n        if \'raise NotImplementedError("Import target class")\' in text:\n            offenders.append(str(path.relative_to(ROOT)))\n\n    assert offenders == []\n\n\ndef test_pytest_runtime_ini_exists():\n    assert (ROOT / "pytest_runtime.ini").exists()\n\n\ndef test_runtime_compile_tool_exists():\n    assert (ROOT / "tools" / "runtime_compile_check.py").exists()\n'}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def backup(path: Path) -> str | None:
    if not path.exists():
        return None
    backup_path = BACKUP_DIR / rel(path)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)
    return rel(backup_path)


def write_file(path: Path, content: str) -> Dict:
    action = {
        "action": "write_file",
        "path": rel(path),
        "existed_before": path.exists(),
        "backup_path": backup(path),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return action


def fix_bom(path: Path) -> Dict:
    action = {
        "action": "fix_bom",
        "path": rel(path),
        "exists": path.exists(),
        "backup_path": None,
        "changed": False,
    }
    if not path.exists():
        return action

    action["backup_path"] = backup(path)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        path.write_bytes(raw[3:])
        action["changed"] = True
    else:
        try:
            text = path.read_text(encoding="utf-8-sig")
            path.write_text(text, encoding="utf-8")
            action["changed"] = True
        except Exception as exc:
            action["error"] = repr(exc)
    return action


def quarantine_placeholder_test(path: Path) -> Dict:
    target = ROOT / "tests" / "placeholder_disabled" / path.name
    action = {
        "action": "quarantine_placeholder_test",
        "source": rel(path),
        "target": rel(target),
        "source_exists": path.exists(),
        "moved": False,
    }
    if not path.exists():
        return action

    text = path.read_text(encoding="utf-8", errors="ignore")
    if 'raise NotImplementedError("Import target class")' not in text and "raise NotImplementedError('Import target class')" not in text:
        action["reason"] = "not_placeholder_pattern"
        return action

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup(target)
        target.unlink()
    shutil.move(str(path), str(target))
    action["moved"] = True
    return action


def run_command(name: str, cmd: List[str]) -> Dict:
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-5000:],
        "stderr_tail": completed.stderr[-5000:],
    }


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    actions = []

    for file_path, content in FILES.items():
        actions.append(write_file(ROOT / file_path, content))

    for file_path in BOM_FIX_FILES:
        actions.append(fix_bom(ROOT / file_path))

    for file_path in PLACEHOLDER_TESTS:
        actions.append(quarantine_placeholder_test(ROOT / file_path))

    validations = [
        run_command("active_runtime_check", [sys.executable, "tools/active_runtime_check.py"]),
        run_command("runtime_compile_check", [sys.executable, "tools/runtime_compile_check.py"]),
        run_command("forward_install_guard", [sys.executable, "tools/forward_install_guard.py"]),
        run_command("runtime_cleanroom_tests", [sys.executable, "-m", "pytest", "tests/regression/test_runtime_cleanroom.py", "-q"]),
        run_command("runtime_pytest_scope", [sys.executable, "-m", "pytest", "-c", "pytest_runtime.ini"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    report = {
        "installer": VERSION,
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "installed_with_warnings",
        "root": str(ROOT),
        "actions": actions,
        "validations": validations,
        "failed_validation_count": len(failed),
        "next_commands": [
            "python tools/active_runtime_check.py",
            "python tools/runtime_compile_check.py",
            "python tools/forward_install_guard.py",
            "pytest tests/regression/test_runtime_cleanroom.py -q",
            "pytest -c pytest_runtime.ini",
            "python main.py",
        ],
    }

    report_path = REPORT_DIR / f"{VERSION}_{TIMESTAMP}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nInstall report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
