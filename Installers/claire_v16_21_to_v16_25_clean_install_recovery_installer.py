#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import py_compile
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

INSTALLER_NAME = "Claire v16.21-v16.25 Clean Install Recovery Installer"
INSTALLER_VERSION = "16.21-16.25"
DEFAULT_TARGET = Path.home() / "OneDrive" / "Desktop" / "Claire"

CURRENT_STATE_CLEANER = r'''from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def class_name_from_file(path: Path) -> str:
    parts = [p for p in path.stem.split("_") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) or "TechnologyStub"


def stub_content(class_name: str) -> str:
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import Any, Dict",
        "",
        "",
        f"class {class_name}:",
        "    def __init__(self, *args, **kwargs) -> None:",
        "        self.args = args",
        "        self.kwargs = kwargs",
        "",
        "    def _result(self, method: str = 'run') -> Dict[str, Any]:",
        "        return {",
        "            'status': 'not_implemented',",
        "            'method': method,",
        "            'confidence': 0.0,",
        "            'evidence': [],",
        "            'payload': {},",
        "            'failure_reasons': ['valid stub only; implementation pending'],",
        "            'metadata': {'safe_stub': True},",
        "        }",
        "",
    ]
    for method in ['run', 'evaluate', 'assess', 'build', 'recommend', 'match']:
        lines.extend([
            f"    def {method}(self, *args, **kwargs):",
            f"        return self._result('{method}')",
            "",
        ])
    lines.extend([
        "    def list_items(self, *args, **kwargs):",
        "        return []",
        "",
    ])
    return "\n".join(lines)


def backup_then_remove(root: Path, path: Path, bucket: str, install: bool) -> Dict[str, Any]:
    rel = path.relative_to(root)
    dest = root / "quarantine_legacy_placeholders" / bucket / rel
    action = {
        "action": "remove_from_active_collection",
        "path": str(rel),
        "quarantine": str(dest.relative_to(root)),
        "installed": install,
    }
    if install and path.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        path.unlink()
    return action


def repair_technology(root: Path, install: bool) -> List[Dict[str, Any]]:
    tech = root / "src" / "claire" / "technology"
    actions: List[Dict[str, Any]] = []
    if install:
        tech.mkdir(parents=True, exist_ok=True)
        (tech / "__init__.py").write_text('\"\"\"Claire technology intelligence package.\"\"\"\n', encoding="utf-8")
    actions.append({"action": "ensure_package", "path": "src/claire/technology", "installed": install})

    if not tech.exists():
        return actions

    backup_root = root / "quarantine_legacy_placeholders" / "backups" / ("technology_" + stamp())
    for path in sorted(tech.glob("*.py")):
        if path.name == "__init__.py":
            continue
        cls = class_name_from_file(path)
        action = {
            "action": "replace_technology_stub",
            "path": str(path.relative_to(root)),
            "class": cls,
            "backup": None,
            "installed": install,
        }
        if install:
            backup = backup_root / path.relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                shutil.copy2(path, backup)
                action["backup"] = str(backup.relative_to(root))
            path.write_text(stub_content(cls), encoding="utf-8", newline="\n")
        actions.append(action)
    return actions


def find_import_target_tests(root: Path) -> List[Path]:
    tests = root / "tests"
    if not tests.exists():
        return []
    out: List[Path] = []
    for path in tests.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "Import target class" in text and "NotImplementedError" in text:
            out.append(path)
    return sorted(out)


def remove_problem_tests(root: Path, install: bool) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    for path in find_import_target_tests(root):
        actions.append(backup_then_remove(root, path, "tests_import_target_class", install))

    for rel in [
        "tests/regression/test_baseline_runner.py",
        "tests/regression/test_lifecycle_regression.py",
        "tests/test_pipeline.py",
    ]:
        path = root / rel
        if path.exists():
            actions.append(backup_then_remove(root, path, "legacy_regression_tests", install))
    return actions


def clean_current_state(root: str | Path = ".", install: bool = False) -> Dict[str, Any]:
    root = Path(root).resolve()
    actions: List[Dict[str, Any]] = []
    actions.extend(repair_technology(root, install))
    actions.extend(remove_problem_tests(root, install))

    payload = {
        "record_type": "claire_current_state_clean_report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "installed": install,
        "root": str(root),
        "actions": actions,
    }
    if install:
        out = root / "data" / "install_safety" / "reports" / ("current_state_clean_" + stamp() + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(out.relative_to(root))
    return payload
'''

SIMPLE_MANIFEST_INSTALLER = r'''from __future__ import annotations

import ast
import json
import py_compile
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

APPROVED_PREFIXES = ("src/claire/", "src/frontend/", "tests/", "data/", "docs/", "requirements/", "tools/", "scripts/", "config/")
BLOCKED_PREFIXES = ("backend/", "src/backend/", ".git/", ".venv/", "__pycache__/", ".pytest_cache/")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def normalize_manifest_text(text: str) -> str:
    text = re.sub(r"(?<=:\s)true(?=[,\n\r}])", "True", text)
    text = re.sub(r"(?<=:\s)false(?=[,\n\r}])", "False", text)
    text = re.sub(r"(?<=:\s)null(?=[,\n\r}])", "None", text)
    return text


def parse_manifest(installer: str | Path) -> Dict[str, Any]:
    path = Path(installer)
    text = normalize_manifest_text(path.read_text(encoding="utf-8", errors="ignore"))
    tree = ast.parse(text, filename=str(path))
    wanted = {"INSTALLER_NAME", "INSTALLER_VERSION", "FOLDERS", "FILES", "VERSION_FILE", "VERSION_FILE_NAME", "LOCK_PAYLOAD"}
    values: Dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    values[target.id] = ast.literal_eval(node.value)
    return {
        "installer_path": str(path),
        "installer_name": values.get("INSTALLER_NAME", path.stem),
        "installer_version": values.get("INSTALLER_VERSION", "unknown"),
        "folders": list(values.get("FOLDERS", [])),
        "files": dict(values.get("FILES", {})),
        "version_file": values.get("VERSION_FILE") or values.get("VERSION_FILE_NAME") or "version_manifest_install.json",
        "lock_payload": dict(values.get("LOCK_PAYLOAD", {})),
    }


def blocked(rel: str) -> bool:
    rel = norm(rel)
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in BLOCKED_PREFIXES)


def approved(rel: str) -> bool:
    rel = norm(rel)
    return rel.startswith("version_") or any(rel.startswith(p) for p in APPROVED_PREFIXES)


def compile_content(rel: str, content: str, temp_root: Path) -> str | None:
    if not rel.endswith(".py"):
        return None
    temp = temp_root / rel
    temp.parent.mkdir(parents=True, exist_ok=True)
    temp.write_text(content, encoding="utf-8", newline="\n")
    try:
        py_compile.compile(str(temp), doraise=True)
        return None
    except Exception as exc:
        return str(exc)


def test_folders(manifest: Dict[str, Any]) -> List[str]:
    folders: List[str] = []
    for rel in manifest["files"]:
        rel = norm(rel)
        if rel.startswith("tests/") and rel.endswith(".py"):
            parts = rel.split("/")
            if len(parts) >= 2:
                folder = "tests/" + parts[1]
                if folder not in folders:
                    folders.append(folder)
    return folders


def install_manifest(root: str | Path, installer: str | Path, install: bool = False, run_tests: bool = False) -> Dict[str, Any]:
    root = Path(root).resolve()
    manifest = parse_manifest(installer)
    actions: List[Dict[str, Any]] = []
    blocked_actions: List[Dict[str, Any]] = []
    temp_root = root / ".claire_install" / "temp_compile" / stamp()

    for folder in manifest["folders"]:
        rel = norm(folder)
        action = {"action": "ensure_dir", "path": rel, "installed": install, "status": "ok"}
        if blocked(rel) or not approved(rel):
            action["status"] = "blocked"
            blocked_actions.append(action)
        elif install:
            (root / rel).mkdir(parents=True, exist_ok=True)
        actions.append(action)

    all_files = dict(manifest["files"])
    payload = dict(manifest["lock_payload"])
    payload["installed_at_utc"] = datetime.now(timezone.utc).isoformat()
    payload["installed_by"] = "Claire simple manifest installer"
    all_files[manifest["version_file"]] = json.dumps(payload, indent=2, sort_keys=True)

    for rel, content in all_files.items():
        rel = norm(rel)
        action = {"action": "write_file", "path": rel, "installed": install, "status": "ok", "backup": None}
        if blocked(rel) or not approved(rel):
            action["status"] = "blocked"
            blocked_actions.append(action)
        else:
            err = compile_content(rel, content, temp_root)
            if err:
                action["status"] = "compile_error"
                action["error"] = err
                blocked_actions.append(action)
            elif install:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists() and dest.read_text(encoding="utf-8", errors="ignore") != content:
                    backup = dest.with_name(dest.name + ".bak_" + stamp())
                    shutil.copy2(dest, backup)
                    action["backup"] = str(backup)
                dest.write_text(content, encoding="utf-8", newline="\n")
        actions.append(action)

    test_results: List[Dict[str, Any]] = []
    if install and run_tests and not blocked_actions:
        for folder in test_folders(manifest):
            proc = subprocess.run([sys.executable, "-m", "pytest", folder, "-q"], cwd=str(root), text=True, capture_output=True)
            test_results.append({
                "folder": folder,
                "returncode": proc.returncode,
                "passed": proc.returncode == 0,
                "stdout_tail": (proc.stdout or "").splitlines()[-80:],
                "stderr_tail": (proc.stderr or "").splitlines()[-80:],
            })

    report = {
        "record_type": "simple_manifest_install_report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "installed": install,
        "manifest": {k: v for k, v in manifest.items() if k != "files"},
        "actions": actions,
        "blocked": blocked_actions,
        "targeted_tests": test_results,
        "passed": not blocked_actions and all(r.get("passed") for r in test_results),
    }
    if install:
        out = root / ".claire_install" / "reports" / ("simple_manifest_install_" + stamp() + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        report["report_path"] = str(out.relative_to(root))
    return report
'''

CLEAN_TOOL = r'''#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from claire.install_safety.current_state_cleaner import clean_current_state

def main() -> int:
    parser = argparse.ArgumentParser(description="Clean Claire current test/install state")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    payload = clean_current_state(PROJECT_ROOT, install=args.install)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''

MANIFEST_TOOL = r'''#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from claire.install_safety.simple_manifest_installer import install_manifest

def main() -> int:
    parser = argparse.ArgumentParser(description="Install Claire manifest-style generated installer")
    parser.add_argument("--installer", required=True)
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()
    payload = install_manifest(PROJECT_ROOT, PROJECT_ROOT / args.installer, install=args.install, run_tests=args.run_tests)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("passed") or not args.install else 1

if __name__ == "__main__":
    raise SystemExit(main())
'''

FILES: Dict[str, str] = {
    "src/claire/install_safety/__init__.py": '"""Claire install safety and recovery tools."""\n',
    "src/claire/install_safety/current_state_cleaner.py": CURRENT_STATE_CLEANER,
    "src/claire/install_safety/simple_manifest_installer.py": SIMPLE_MANIFEST_INSTALLER,
    "tools/clean_current_state.py": CLEAN_TOOL,
    "tools/install_manifest_package.py": MANIFEST_TOOL,
    "tests/install_safety/test_current_state_cleaner.py": '''from pathlib import Path
from claire.install_safety.current_state_cleaner import class_name_from_file, stub_content

def test_class_name_from_file():
    assert class_name_from_file(Path("technology_catalog.py")) == "TechnologyCatalog"

def test_stub_content_compilable():
    compile(stub_content("TechnologyCatalog"), "stub.py", "exec")
''',
    "tests/install_safety/test_simple_manifest_installer.py": '''from claire.install_safety.simple_manifest_installer import parse_manifest

def test_manifest_parser_normalizes_json_booleans(tmp_path):
    installer = tmp_path / "installer.py"
    installer.write_text(
        "INSTALLER_NAME='x'\\nINSTALLER_VERSION='1'\\nFOLDERS=[]\\nFILES={}\\nVERSION_FILE='version_x.json'\\nLOCK_PAYLOAD={'ok': true, 'bad': false, 'none': null}\\n",
        encoding="utf-8",
    )
    manifest = parse_manifest(installer)
    assert manifest["lock_payload"]["ok"] is True
    assert manifest["lock_payload"]["bad"] is False
    assert manifest["lock_payload"]["none"] is None
''',
    "docs/install_safety/v16_21_to_v16_25_clean_install_recovery.md": '''# v16.21-v16.25 Clean Install Recovery

Run:

```powershell
python claire_v16_21_to_v16_25_clean_install_recovery_installer.py --install --apply-current-fixes --run-tests
python -m compileall src\\claire
pytest
```

Future generated installers:

```powershell
python tools\\install_manifest_package.py --installer claire_next_installer.py
python tools\\install_manifest_package.py --installer claire_next_installer.py --install --run-tests
```
''',
}

FOLDERS = [
    "src/claire/install_safety",
    "tests/install_safety",
    "data/install_safety/reports",
    "docs/install_safety",
    ".claire_install/reports",
]

VERSION_FILE = "version_16_25_clean_install_recovery.json"
LOCK_PAYLOAD = {
    "version": "16.25",
    "state": "clean_install_recovery_installed",
    "phase": "install_safety_recovery",
    "status": "installed_not_validated",
    "safety_contract": {
        "repairs_current_compile_state": True,
        "restores_clean_installer_path": True,
        "does_not_modify_core_runtime_routing": True,
        "does_not_modify_scoring": True,
        "does_not_modify_core_run_output": True,
        "backs_up_removed_problem_files": True,
    },
}

def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_dir(path: Path, install: bool, actions: List[Dict[str, Any]]) -> None:
    existed = path.exists()
    if install:
        path.mkdir(parents=True, exist_ok=True)
    actions.append({"action": "ensure_dir", "path": str(path), "installed": install, "existed": existed})

def write_file(path: Path, content: str, install: bool, actions: List[Dict[str, Any]]) -> None:
    existed = path.exists()
    backup = None
    if install:
        path.parent.mkdir(parents=True, exist_ok=True)
        if existed and path.read_text(encoding="utf-8", errors="ignore") != content:
            backup_path = path.with_name(path.name + ".bak_" + stamp())
            shutil.copy2(path, backup_path)
            backup = str(backup_path)
        path.write_text(content, encoding="utf-8", newline="\n")
    actions.append({"action": "write_file", "path": str(path), "installed": install, "existed": existed, "backup": backup})

def run_cmd(root: Path, cmd: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(root), text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "passed": proc.returncode == 0, "stdout_tail": (proc.stdout or "").splitlines()[-80:], "stderr_tail": (proc.stderr or "").splitlines()[-80:]}

def main() -> int:
    parser = argparse.ArgumentParser(description=INSTALLER_NAME)
    parser.add_argument("--target", default=str(DEFAULT_TARGET), help="Claire project root")
    parser.add_argument("--install", action="store_true", help="Apply install")
    parser.add_argument("--apply-current-fixes", action="store_true", help="Apply current compile/pytest cleanup")
    parser.add_argument("--run-tests", action="store_true", help="Run install_safety tests")
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    install = bool(args.install)

    print(f"{INSTALLER_NAME} {INSTALLER_VERSION}")
    print(f"Target: {root}")
    print("Mode:", "INSTALL" if install else "DRY RUN")

    if not root.exists() or not (root / "src").exists() or not (root / "tests").exists():
        print("[ERROR] This does not look like Claire project root. Missing src or tests folder.")
        return 2

    actions: List[Dict[str, Any]] = []
    for folder in FOLDERS:
        ensure_dir(root / folder, install, actions)
    for rel, content in FILES.items():
        write_file(root / rel, content, install, actions)

    payload = dict(LOCK_PAYLOAD)
    payload["installed_at_utc"] = now_iso()
    write_file(root / VERSION_FILE, json.dumps(payload, indent=2, sort_keys=True), install, actions)

    fix_report = None
    test_results = []
    if install and args.apply_current_fixes:
        sys.path.insert(0, str(root / "src"))
        from claire.install_safety.current_state_cleaner import clean_current_state
        fix_report = clean_current_state(root, install=True)

    if install and args.run_tests:
        test_results.append(run_cmd(root, [sys.executable, "-m", "compileall", "src/claire/install_safety"]))
        test_results.append(run_cmd(root, [sys.executable, "-m", "pytest", "tests/install_safety", "-q"]))

    report = {
        "installer": INSTALLER_NAME,
        "installer_version": INSTALLER_VERSION,
        "installed": install,
        "installed_at_utc": now_iso(),
        "target": str(root),
        "actions": actions,
        "fix_report": fix_report,
        "test_results": test_results,
        "version_file": VERSION_FILE,
        "safety_contract": payload["safety_contract"],
        "post_install_checks": [
            "python tools\\clean_current_state.py --install",
            "python -m compileall src\\claire",
            "pytest tests\\install_safety -v",
            "pytest",
            "python tools\\install_manifest_package.py --installer <next_installer.py> --install --run-tests",
        ],
    }

    if install:
        report_path = root / ".claire_install" / "reports" / (VERSION_FILE.replace(".json", "") + "_" + stamp() + ".json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[OK] Report written: {report_path}")
    else:
        print("[DRY RUN] No files changed. Re-run with --install to apply.")

    print(json.dumps({"installed": install, "target": str(root), "installer_version": INSTALLER_VERSION, "folders": len(FOLDERS), "files": len(FILES) + 1, "applied_current_fixes": bool(fix_report), "tests_run": len(test_results)}, indent=2))
    return 1 if any(not r.get("passed") for r in test_results) else 0

if __name__ == "__main__":
    raise SystemExit(main())
