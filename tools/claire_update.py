#!/usr/bin/env python
"""
Claire Local Updater

Install Claire update zips safely from the project root.

Common usage:

    python tools/claire_update.py .\claire_export_package_engine_update.zip --run-tests

Dry run:

    python tools/claire_update.py .\some_update.zip --dry-run

Restore a backup:

    python tools/claire_update.py --restore .\data\backups\claire_backup_20260430_120000.zip

List backups:

    python tools/claire_update.py --list-backups
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import py_compile
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PROJECT_MARKERS = [
    "main.py",
    "src/claire",
]


@dataclass
class UpdateFile:
    path: str
    size: int
    sha256: str
    exists: bool
    action: str


def _now_stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_project_root(path: Path) -> bool:
    return all((path / marker).exists() for marker in PROJECT_MARKERS)


def find_project_root(start: Optional[Path] = None) -> Path:
    start = (start or Path.cwd()).resolve()
    candidates = [start] + list(start.parents)

    for candidate in candidates:
        if _is_project_root(candidate):
            return candidate

    raise SystemExit(
        "Could not detect Claire project root. Run from the folder containing main.py and src/claire, "
        "or pass --root C:\\path\\to\\Claire."
    )


def ensure_dirs(root: Path) -> Dict[str, Path]:
    dirs = {
        "backups": root / "data" / "backups",
        "logs": root / "data" / "update_logs",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def validate_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    if not normalized or normalized.endswith("/"):
        return False
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        raise ValueError(f"Unsafe zip path rejected: {name}")
    if normalized.startswith("__MACOSX/"):
        return False
    return True


def inspect_update_zip(zip_path: Path, root: Path) -> List[UpdateFile]:
    if not zip_path.exists():
        raise SystemExit(f"Update zip not found: {zip_path}")

    updates: List[UpdateFile] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        bad = z.testzip()
        if bad is not None:
            raise SystemExit(f"Zip integrity check failed for member: {bad}")

        for info in z.infolist():
            if not validate_zip_member(info.filename):
                continue

            rel = info.filename.replace("\\", "/")
            data = z.read(info.filename)
            target = root / rel
            exists = target.exists()

            if exists:
                action = "replace"
            else:
                action = "create"

            updates.append(
                UpdateFile(
                    path=rel,
                    size=len(data),
                    sha256=_sha256_bytes(data),
                    exists=exists,
                    action=action,
                )
            )

    if not updates:
        raise SystemExit("The update zip contains no installable files.")

    return updates


def print_plan(zip_path: Path, root: Path, updates: List[UpdateFile]) -> None:
    print("")
    print("Claire Local Updater")
    print("====================")
    print(f"Project root: {root}")
    print(f"Update zip:   {zip_path}")
    print(f"Files:        {len(updates)}")
    print("")
    print("Install plan:")
    for item in updates:
        marker = "R" if item.action == "replace" else "C"
        print(f"  [{marker}] {item.path} ({item.size} bytes)")
    print("")
    print("Legend: [R] replace existing file, [C] create new file")
    print("")


def create_backup(zip_path: Path, root: Path, dirs: Dict[str, Path], updates: List[UpdateFile]) -> Path:
    stamp = _now_stamp()
    backup_path = dirs["backups"] / f"claire_backup_{stamp}.zip"

    manifest = {
        "created_at": _dt.datetime.now().isoformat(),
        "project_root": str(root),
        "update_zip": str(zip_path),
        "update_zip_sha256": _sha256_file(zip_path),
        "files": [],
    }

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as z:
        for item in updates:
            target = root / item.path
            entry = {
                "path": item.path,
                "existed_before_update": target.exists(),
                "backup_member": None,
                "sha256_before": None,
            }

            if target.exists() and target.is_file():
                backup_member = f"files/{item.path}"
                z.write(target, backup_member)
                entry["backup_member"] = backup_member
                entry["sha256_before"] = _sha256_file(target)

            manifest["files"].append(entry)

        z.writestr("backup_manifest.json", json.dumps(manifest, indent=2))

    return backup_path


def install_update(zip_path: Path, root: Path, updates: List[UpdateFile]) -> None:
    update_paths = {item.path for item in updates}

    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            if not validate_zip_member(info.filename):
                continue

            rel = info.filename.replace("\\", "/")
            if rel not in update_paths:
                continue

            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(info.filename))


def compile_changed_python(root: Path, updates: List[UpdateFile]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for item in updates:
        if not item.path.endswith(".py"):
            continue

        target = root / item.path
        try:
            py_compile.compile(str(target), doraise=True)
            results.append({"path": item.path, "ok": True, "error": None})
        except Exception as exc:
            results.append({"path": item.path, "ok": False, "error": str(exc)})

    failures = [r for r in results if not r["ok"]]
    if failures:
        print("")
        print("Python compile failures:")
        for failure in failures:
            print(f"  - {failure['path']}: {failure['error']}")
        raise SystemExit("Update installed but Python compile checks failed. Use backup restore if needed.")

    return results


def run_command(root: Path, command: List[str]) -> Dict[str, Any]:
    print("")
    print("Running:", " ".join(command))
    proc = subprocess.run(
        command,
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(proc.stdout)
    return {
        "command": command,
        "returncode": proc.returncode,
        "output": proc.stdout,
    }


def run_tests(root: Path, mode: str) -> Dict[str, Any]:
    if mode == "none":
        return {"ran": False, "mode": mode, "result": None}

    pytest_file = root / "tests" / "regression" / "test_lifecycle_regression.py"
    smoke_file = root / "tests" / "regression" / "run_lifecycle_smoke.py"

    env_python = sys.executable

    if mode in {"pytest", "auto"} and pytest_file.exists():
        result = run_command(root, [env_python, "-m", "pytest", str(pytest_file.relative_to(root)), "-q"])
        if result["returncode"] == 0:
            return {"ran": True, "mode": "pytest", "result": result}
        if mode == "pytest":
            raise SystemExit("Pytest regression suite failed.")

        print("Pytest failed or is unavailable; trying smoke test fallback...")

    if mode in {"smoke", "auto"} and smoke_file.exists():
        result = run_command(root, [env_python, str(smoke_file.relative_to(root))])
        if result["returncode"] != 0:
            raise SystemExit("Smoke regression test failed.")
        return {"ran": True, "mode": "smoke", "result": result}

    if mode == "auto":
        print("No regression suite found. Skipping tests.")
        return {"ran": False, "mode": mode, "result": "no regression suite found"}

    raise SystemExit(f"Requested test mode {mode!r}, but matching test file was not found.")


def write_update_log(
    root: Path,
    dirs: Dict[str, Path],
    zip_path: Path,
    backup_path: Optional[Path],
    updates: List[UpdateFile],
    compile_results: List[Dict[str, Any]],
    test_result: Dict[str, Any],
    dry_run: bool,
) -> Path:
    log_path = dirs["logs"] / f"update_{_now_stamp()}.json"

    payload = {
        "created_at": _dt.datetime.now().isoformat(),
        "dry_run": dry_run,
        "project_root": str(root),
        "update_zip": str(zip_path),
        "update_zip_sha256": _sha256_file(zip_path),
        "backup_path": str(backup_path) if backup_path else None,
        "files": [item.__dict__ for item in updates],
        "compile_results": compile_results,
        "test_result": test_result,
    }

    log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return log_path


def list_backups(root: Path) -> None:
    dirs = ensure_dirs(root)
    backups = sorted(dirs["backups"].glob("claire_backup_*.zip"), reverse=True)
    if not backups:
        print("No Claire backups found.")
        return

    print("Claire backups:")
    for backup in backups:
        print(f"  - {backup}")


def restore_backup(root: Path, backup_path: Path) -> None:
    if not backup_path.exists():
        raise SystemExit(f"Backup zip not found: {backup_path}")

    with zipfile.ZipFile(backup_path, "r") as z:
        if "backup_manifest.json" not in z.namelist():
            raise SystemExit("Invalid Claire backup: missing backup_manifest.json")

        manifest = json.loads(z.read("backup_manifest.json").decode("utf-8"))

        for entry in manifest.get("files", []):
            rel = entry["path"]
            target = root / rel

            if entry.get("existed_before_update"):
                member = entry.get("backup_member")
                if not member:
                    raise SystemExit(f"Backup manifest error for {rel}: missing backup_member")

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(member))
                print(f"Restored: {rel}")
            else:
                if target.exists():
                    target.unlink()
                    print(f"Removed created file: {rel}")

    print("")
    print("Restore complete.")


def confirm_or_exit(args: argparse.Namespace) -> None:
    if args.yes or args.dry_run:
        return

    response = input("Apply this update? Type YES to continue: ").strip()
    if response != "YES":
        raise SystemExit("Update cancelled.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Claire local zip updater")
    parser.add_argument("zip_path", nargs="?", help="Path to Claire update zip")
    parser.add_argument("--root", help="Claire project root. Defaults to auto-detect from current folder.")
    parser.add_argument("--dry-run", action="store_true", help="Show update plan without modifying files.")
    parser.add_argument("--yes", "-y", action="store_true", help="Apply without interactive confirmation.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a backup before installing.")
    parser.add_argument("--run-tests", action="store_true", help="Run regression tests after install. Same as --test-mode auto.")
    parser.add_argument("--test-mode", choices=["none", "auto", "pytest", "smoke"], default="none")
    parser.add_argument("--list-backups", action="store_true", help="List available Claire backup zips.")
    parser.add_argument("--restore", help="Restore a Claire backup zip.")
    parser.add_argument("--commit-message", default="", help="Optional commit message to print after update.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = find_project_root(Path(args.root)) if args.root else find_project_root()
    dirs = ensure_dirs(root)

    if args.list_backups:
        list_backups(root)
        return 0

    if args.restore:
        restore_backup(root, Path(args.restore).resolve())
        return 0

    if not args.zip_path:
        parser.error("zip_path is required unless using --restore or --list-backups")

    zip_path = Path(args.zip_path).resolve()
    updates = inspect_update_zip(zip_path, root)
    print_plan(zip_path, root, updates)

    if args.dry_run:
        log_path = write_update_log(root, dirs, zip_path, None, updates, [], {"ran": False}, dry_run=True)
        print(f"Dry run complete. Log written to: {log_path}")
        return 0

    confirm_or_exit(args)

    backup_path: Optional[Path] = None
    if not args.no_backup:
        backup_path = create_backup(zip_path, root, dirs, updates)
        print(f"Backup created: {backup_path}")
    else:
        print("Backup skipped by --no-backup")

    install_update(zip_path, root, updates)
    print("Update files installed.")

    compile_results = compile_changed_python(root, updates)
    print("Python compile checks passed.")

    test_mode = "auto" if args.run_tests else args.test_mode
    test_result = run_tests(root, test_mode)

    log_path = write_update_log(
        root=root,
        dirs=dirs,
        zip_path=zip_path,
        backup_path=backup_path,
        updates=updates,
        compile_results=compile_results,
        test_result=test_result,
        dry_run=False,
    )

    print("")
    print("Claire update complete.")
    print(f"Update log: {log_path}")
    if backup_path:
        print(f"Backup:     {backup_path}")

    if args.commit_message:
        print("")
        print("Recommended commit:")
        print("git add .")
        print(f'git commit -m "{args.commit_message}"')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
