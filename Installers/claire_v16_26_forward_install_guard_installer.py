#!/usr/bin/env python3
"""
Claire v16.26 Forward Install Guard Installer

Purpose:
- Add forward-install governance without changing Claire runtime behavior.
- Create tools that inventory the current system, check protected runtime imports,
  detect active placeholder tests, detect nested repo pollution, and validate compile health.
- Add docs and a regression test for the guard.

This installer is additive and backup-safe.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


VERSION = "v16.26_forward_install_guard"
ROOT = Path.cwd()
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = ROOT / ".claire_install" / "reports"
BACKUP_DIR = ROOT / ".claire_install" / "backups" / f"{VERSION}_{TIMESTAMP}"

FILES = {'tools/forward_install_guard.py': '#!/usr/bin/env python3\n"""\nForward Install Guard\n\nChecks that future Claire installers do not break the active runtime.\nThis tool is intentionally read-only.\n"""\n\nfrom __future__ import annotations\n\nimport ast\nimport json\nimport os\nimport subprocess\nimport sys\nfrom datetime import datetime\nfrom pathlib import Path\nfrom typing import Dict\n\n\nROOT = Path.cwd()\n\nPROTECTED_PATHS = [\n    "main.py",\n    "src/claire/app.py",\n    "src/claire/api",\n    "src/claire/orchestrator",\n    "src/claire/lifecycle",\n    "src/claire/engines",\n    "src/claire/output",\n    "src/claire/dashboard",\n    "src/claire/technology/technology_intelligence.py",\n]\n\nPROTECTED_IMPORTS = [\n    "claire.app",\n    "claire.api.routes_pipeline",\n    "claire.orchestrator.pipeline_v4",\n    "claire.technology.technology_intelligence",\n]\n\n\ndef _result(name: str, status: str, **extra):\n    payload = {"name": name, "status": status}\n    payload.update(extra)\n    return payload\n\n\ndef check_protected_paths() -> Dict:\n    missing = []\n    for rel in PROTECTED_PATHS:\n        if not (ROOT / rel).exists():\n            missing.append(rel)\n    return _result(\n        "protected_paths",\n        "success" if not missing else "failed",\n        missing=missing,\n        checked_count=len(PROTECTED_PATHS),\n    )\n\n\ndef check_nested_repo_pollution() -> Dict:\n    nested = []\n    for path in [\n        ROOT / "src" / "claire" / ".git",\n        ROOT / "src" / "claire" / "Claire" / ".git",\n        ROOT / "src" / "claire" / "Claire",\n    ]:\n        if path.exists():\n            nested.append(str(path.relative_to(ROOT)))\n    return _result(\n        "nested_repo_pollution",\n        "success" if not nested else "failed",\n        nested=nested,\n    )\n\n\ndef check_placeholder_tests() -> Dict:\n    offenders = []\n    tests_dir = ROOT / "tests"\n    if tests_dir.exists():\n        for path in tests_dir.rglob("test_*.py"):\n            try:\n                text = path.read_text(encoding="utf-8", errors="ignore")\n            except Exception:\n                continue\n            if \'raise NotImplementedError("Import target class")\' in text or "raise NotImplementedError(\'Import target class\')" in text:\n                offenders.append(str(path.relative_to(ROOT)))\n\n    return _result(\n        "active_placeholder_tests",\n        "success" if not offenders else "failed",\n        offenders=offenders,\n        offender_count=len(offenders),\n    )\n\n\ndef check_syntax_fast() -> Dict:\n    src = ROOT / "src"\n    failures = []\n    if src.exists():\n        for path in src.rglob("*.py"):\n            try:\n                ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))\n            except SyntaxError as exc:\n                failures.append({\n                    "path": str(path.relative_to(ROOT)),\n                    "line": exc.lineno,\n                    "error": exc.msg,\n                })\n            except Exception as exc:\n                failures.append({\n                    "path": str(path.relative_to(ROOT)),\n                    "line": None,\n                    "error": f"read_or_parse_error: {exc}",\n                })\n\n    return _result(\n        "syntax_fast",\n        "success" if not failures else "failed",\n        failure_count=len(failures),\n        failures=failures[:50],\n    )\n\n\ndef check_protected_imports() -> Dict:\n    code = "\\n".join([f"import {module}" for module in PROTECTED_IMPORTS])\n    completed = subprocess.run(\n        [sys.executable, "-c", code],\n        cwd=ROOT,\n        text=True,\n        capture_output=True,\n    )\n    return _result(\n        "protected_imports",\n        "success" if completed.returncode == 0 else "failed",\n        returncode=completed.returncode,\n        stdout=completed.stdout[-2000:],\n        stderr=completed.stderr[-4000:],\n        imports=PROTECTED_IMPORTS,\n    )\n\n\ndef run_guard() -> Dict:\n    checks = [\n        check_protected_paths(),\n        check_nested_repo_pollution(),\n        check_placeholder_tests(),\n        check_syntax_fast(),\n        check_protected_imports(),\n    ]\n\n    failed = [c for c in checks if c["status"] != "success"]\n\n    return {\n        "guard": "forward_install_guard",\n        "version": "v16.26",\n        "created_at": datetime.now().isoformat(),\n        "status": "success" if not failed else "failed",\n        "check_count": len(checks),\n        "failed_count": len(failed),\n        "checks": checks,\n    }\n\n\ndef main() -> int:\n    payload = run_guard()\n    out_dir = ROOT / ".claire_install" / "reports"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f"forward_install_guard_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nReport written: {out_path}")\n    return 0 if payload["status"] == "success" else 1\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/current_state_inventory.py': '#!/usr/bin/env python3\n"""\nCurrent State Inventory\n\nProduces a compact inventory of Claire\'s current tree without changing files.\n"""\n\nfrom __future__ import annotations\n\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\n\nROOT = Path.cwd()\n\n\ndef count_files(path: Path) -> int:\n    if not path.exists():\n        return 0\n    return sum(1 for p in path.rglob("*") if p.is_file())\n\n\ndef main() -> int:\n    top = []\n    for child in ROOT.iterdir():\n        if child.is_dir():\n            top.append({\n                "folder": child.name,\n                "files": count_files(child),\n            })\n\n    top.sort(key=lambda item: item["files"], reverse=True)\n\n    payload = {\n        "inventory": "current_state_inventory",\n        "created_at": datetime.now().isoformat(),\n        "root": str(ROOT),\n        "total_files": count_files(ROOT),\n        "top_folders_by_file_count": top,\n        "key_paths": {\n            "main.py": (ROOT / "main.py").exists(),\n            "src/claire": (ROOT / "src" / "claire").exists(),\n            "src/frontend": (ROOT / "src" / "frontend").exists(),\n            "tests": (ROOT / "tests").exists(),\n            "archive": (ROOT / "archive").exists(),\n            ".claire_install": (ROOT / ".claire_install").exists(),\n        },\n    }\n\n    out_dir = ROOT / ".claire_install" / "reports"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f"current_state_inventory_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps(payload, indent=2))\n    print(f"\\nReport written: {out_path}")\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/active_runtime_check.py': '#!/usr/bin/env python3\n"""\nActive Runtime Check\n\nChecks the minimum import path needed for Claire to launch.\nThis does not start the server.\n"""\n\nfrom __future__ import annotations\n\nimport importlib\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\n\nROOT = Path.cwd()\n\nIMPORTS = [\n    "claire.app",\n    "claire.api.routes_pipeline",\n    "claire.orchestrator.pipeline_v4",\n    "claire.technology.technology_intelligence",\n]\n\n\ndef main() -> int:\n    results = []\n    for module in IMPORTS:\n        try:\n            importlib.import_module(module)\n            results.append({"module": module, "status": "success"})\n        except Exception as exc:\n            results.append({"module": module, "status": "failed", "error": repr(exc)})\n\n    failed = [r for r in results if r["status"] != "success"]\n\n    payload = {\n        "check": "active_runtime_check",\n        "created_at": datetime.now().isoformat(),\n        "status": "success" if not failed else "failed",\n        "failed_count": len(failed),\n        "imports": results,\n    }\n\n    out_dir = ROOT / ".claire_install" / "reports"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f"active_runtime_check_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps(payload, indent=2))\n    print(f"\\nReport written: {out_path}")\n    return 0 if payload["status"] == "success" else 1\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/install_governance/FORWARD_INSTALL_RULE.md': '# Claire Forward Install Rule\n\nClaire is allowed to move forward, but future installers must be manifest-gated.\n\n## Required installer behavior\n\nEvery installer must:\n\n1. Declare every file it creates or replaces.\n2. Back up every replaced file before writing.\n3. Avoid active runtime pollution from demo, placeholder, generated, or proof-only files.\n4. Write an install manifest under `.claire_install/reports/`.\n5. Preserve `/docs` launch path.\n6. Preserve protected runtime imports.\n7. Avoid adding placeholder tests to active pytest.\n8. Keep incomplete scaffolds disabled until implemented.\n9. Never place nested repos under `src/claire`.\n\n## Protected runtime paths\n\n- `main.py`\n- `src/claire/app.py`\n- `src/claire/api/`\n- `src/claire/orchestrator/`\n- `src/claire/lifecycle/`\n- `src/claire/engines/`\n- `src/claire/output/`\n- `src/claire/dashboard/`\n- `src/claire/technology/technology_intelligence.py`\n\n## Current policy\n\nForward movement is allowed only through controlled installers.\nBlind additive installs are not allowed.\n', 'tests/regression/test_forward_install_guard.py': 'from tools.forward_install_guard import run_guard\n\n\ndef test_forward_install_guard_runs():\n    payload = run_guard()\n    assert "status" in payload\n    assert payload["check_count"] >= 5\n\n\ndef test_forward_install_guard_has_required_checks():\n    payload = run_guard()\n    names = {check["name"] for check in payload["checks"]}\n    assert "protected_paths" in names\n    assert "nested_repo_pollution" in names\n    assert "active_placeholder_tests" in names\n    assert "syntax_fast" in names\n    assert "protected_imports" in names\n'}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def write_file(path: Path, content: str) -> Dict:
    action = {
        "path": rel(path),
        "existed_before": path.exists(),
        "backup_path": None,
    }

    if path.exists():
        backup_path = BACKUP_DIR / rel(path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        action["backup_path"] = rel(backup_path)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
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
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    actions = []
    for file_path, content in FILES.items():
        actions.append(write_file(ROOT / file_path, content))

    validations = [
        run_command("active_runtime_check", [sys.executable, "tools/active_runtime_check.py"]),
        run_command("forward_install_guard", [sys.executable, "tools/forward_install_guard.py"]),
        run_command("current_state_inventory", [sys.executable, "tools/current_state_inventory.py"]),
    ]

    failed_validations = [v for v in validations if v["returncode"] != 0]

    report = {
        "installer": VERSION,
        "created_at": datetime.now().isoformat(),
        "status": "installed_with_warnings" if failed_validations else "success",
        "root": str(ROOT),
        "files_written": actions,
        "validations": validations,
        "failed_validation_count": len(failed_validations),
        "note": "Warnings are expected while cleanup is in progress. This installer adds guard tooling and does not modify runtime behavior.",
        "next_commands": [
            "python tools/current_state_inventory.py",
            "python tools/active_runtime_check.py",
            "python tools/forward_install_guard.py",
            "pytest tests/regression/test_forward_install_guard.py -q",
        ],
    }

    report_path = REPORT_DIR / f"{VERSION}_{TIMESTAMP}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nInstall report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
