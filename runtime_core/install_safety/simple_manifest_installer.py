from __future__ import annotations

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
