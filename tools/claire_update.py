#!/usr/bin/env python
r"""
Claire Manifest-Driven Local Updater

Supports two update formats:

1. Path-preserving zip
   Zip member path is installed directly into the same project-relative path.

   Example zip member:
       src/claire/engines/export_package_engine.py

   Installs to:
       <project_root>/src/claire/engines/export_package_engine.py

2. Manifest-driven zip
   Zip contains one of:
       claire_update_manifest.json
       update_manifest.json
       manifest.json

   Manifest routes each source file to a target system folder.

   Example:
       {
         "update_name": "export_writer_package",
         "version": "v5.32",
         "files": [
           {
             "source": "files/export_writer.py",
             "target": "@export/export_writer.py",
             "type": "python",
             "action": "replace"
           },
           {
             "source": "files/pipeline_v4.py",
             "target": "@orchestrator/pipeline_v4.py",
             "type": "python",
             "action": "replace"
           }
         ],
         "post_install": {
           "run_compile_check": true,
           "run_regression_tests": true
         }
       }

Target aliases:
    @engine/name.py          -> src/claire/engines/name.py
    @engines/name.py         -> src/claire/engines/name.py
    @orchestrator/name.py    -> src/claire/orchestrator/name.py
    @domain/name.py          -> src/claire/domain/name.py
    @portfolio/name.py       -> src/claire/portfolio/name.py
    @export/name.py          -> src/claire/export/name.py
    @backend/path            -> backend/path
    @frontend/path           -> frontend/path
    @tests/path              -> tests/path
    @tools/path              -> tools/path
    @data/path               -> data/path
    @root/path               -> path

Common usage:
    python tools/claire_update.py .\next_update.zip --run-tests

Dry run:
    python tools/claire_update.py .\next_update.zip --dry-run

Restore:
    python tools/claire_update.py --list-backups
    python tools/claire_update.py --restore .\data\backups\claire_backup_YYYYMMDD_HHMMSS.zip
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import py_compile
import subprocess
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_MARKERS = ["main.py", "src/claire"]
MANIFEST_NAMES = ["claire_update_manifest.json", "update_manifest.json", "manifest.json"]

TARGET_ALIASES = {
    "@engine": "src/claire/engines",
    "@engines": "src/claire/engines",
    "@orchestrator": "src/claire/orchestrator",
    "@domain": "src/claire/domain",
    "@portfolio": "src/claire/portfolio",
    "@export": "src/claire/export",
    "@backend": "backend",
    "@frontend": "frontend",
    "@tests": "tests",
    "@tools": "tools",
    "@data": "data",
    "@root": "",
}


@dataclass
class UpdateFile:
    source: str
    target: str
    size: int
    sha256: str
    exists: bool
    action: str
    file_type: str
    required: bool = True


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
    for candidate in [start] + list(start.parents):
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


def normalize_zip_path(path: str) -> str:
    normalized = (path or "").replace("\\", "/").strip()
    if not normalized:
        raise ValueError("Empty path is not allowed.")
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized or normalized == "..":
        raise ValueError(f"Unsafe path rejected: {path}")
    return normalized


def should_skip_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return not normalized or normalized.endswith("/") or normalized.startswith("__MACOSX/")


def resolve_target(target: str) -> str:
    target = normalize_zip_path(target)
    if target.startswith("@"):
        head, _, tail = target.partition("/")
        if head not in TARGET_ALIASES:
            raise ValueError(f"Unknown target alias {head!r} in target {target!r}")
        base = TARGET_ALIASES[head]
        resolved = f"{base}/{tail}" if base and tail else (base or tail)
        return normalize_zip_path(resolved)
    return target


def detect_file_type(path: str, explicit: Optional[str] = None) -> str:
    if explicit:
        return str(explicit).lower()
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix in {".json"}:
        return "json"
    if suffix in {".md", ".txt"}:
        return "text"
    if suffix in {".yml", ".yaml"}:
        return "yaml"
    return "file"


def load_manifest(z: zipfile.ZipFile) -> Optional[Dict[str, Any]]:
    names = {name.replace("\\", "/"): name for name in z.namelist()}
    for manifest_name in MANIFEST_NAMES:
        if manifest_name in names:
            raw = z.read(names[manifest_name]).decode("utf-8")
            manifest = json.loads(raw)
            manifest["_manifest_member"] = manifest_name
            return manifest
    return None


def validate_manifest(manifest: Dict[str, Any]) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be a JSON object.")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Manifest must contain a non-empty files list.")
    for idx, entry in enumerate(files):
        if not isinstance(entry, dict):
            raise ValueError(f"Manifest files[{idx}] must be an object.")
        action = entry.get("action", "replace")
        if action not in {"replace", "create", "create_if_missing", "delete"}:
            raise ValueError(f"Unsupported action for files[{idx}]: {action!r}")
        if action != "delete" and not entry.get("source"):
            raise ValueError(f"Manifest files[{idx}] missing source.")
        if not entry.get("target"):
            raise ValueError(f"Manifest files[{idx}] missing target.")


def inspect_manifest_update(zip_path: Path, root: Path, z: zipfile.ZipFile, manifest: Dict[str, Any]) -> List[UpdateFile]:
    validate_manifest(manifest)
    zip_names = {name.replace("\\", "/"): name for name in z.namelist()}
    updates: List[UpdateFile] = []

    for entry in manifest["files"]:
        action = entry.get("action", "replace")
        required = bool(entry.get("required", True))
        source = normalize_zip_path(entry.get("source", f"__delete__/{entry['target']}")) if action != "delete" else ""
        target = resolve_target(entry["target"])
        target_path = root / target
        file_type = detect_file_type(target, entry.get("type"))

        if action == "delete":
            data = b""
            source_label = ""
        else:
            if source not in zip_names:
                if required:
                    raise ValueError(f"Manifest source not found in zip: {source}")
                data = b""
            else:
                data = z.read(zip_names[source])
            source_label = source

        exists = target_path.exists()
        effective_action = action
        if action == "replace" and not exists:
            effective_action = "create"
        elif action == "create" and exists:
            effective_action = "replace"
        elif action == "create_if_missing" and exists:
            effective_action = "skip_existing"

        updates.append(
            UpdateFile(
                source=source_label,
                target=target,
                size=len(data),
                sha256=_sha256_bytes(data) if data else "",
                exists=exists,
                action=effective_action,
                file_type=file_type,
                required=required,
            )
        )

    return updates


def inspect_path_preserving_update(zip_path: Path, root: Path, z: zipfile.ZipFile) -> List[UpdateFile]:
    updates: List[UpdateFile] = []

    for info in z.infolist():
        if should_skip_zip_member(info.filename):
            continue

        rel = normalize_zip_path(info.filename)
        if rel in MANIFEST_NAMES:
            continue

        data = z.read(info.filename)
        target_path = root / rel
        updates.append(
            UpdateFile(
                source=rel,
                target=rel,
                size=len(data),
                sha256=_sha256_bytes(data),
                exists=target_path.exists(),
                action="replace" if target_path.exists() else "create",
                file_type=detect_file_type(rel),
                required=True,
            )
        )

    return updates


def inspect_update_zip(zip_path: Path, root: Path) -> Dict[str, Any]:
    if not zip_path.exists():
        raise SystemExit(f"Update zip not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as z:
        bad = z.testzip()
        if bad is not None:
            raise SystemExit(f"Zip integrity check failed for member: {bad}")

        manifest = load_manifest(z)
        if manifest:
            mode = "manifest"
            updates = inspect_manifest_update(zip_path, root, z, manifest)
        else:
            mode = "path_preserving"
            updates = inspect_path_preserving_update(zip_path, root, z)

    if not updates:
        raise SystemExit("The update zip contains no installable files.")

    return {
        "mode": mode,
        "manifest": manifest,
        "updates": updates,
    }


def print_plan(zip_path: Path, root: Path, inspection: Dict[str, Any]) -> None:
    updates: List[UpdateFile] = inspection["updates"]
    manifest = inspection.get("manifest") or {}

    print("")
    print("Claire Manifest-Driven Updater")
    print("==============================")
    print(f"Project root: {root}")
    print(f"Update zip:   {zip_path}")
    print(f"Mode:         {inspection['mode']}")
    if manifest:
        print(f"Update name:  {manifest.get('update_name', 'unknown')}")
        print(f"Version:      {manifest.get('version', 'unknown')}")
        print(f"Manifest:     {manifest.get('_manifest_member', 'unknown')}")
    print(f"Files:        {len(updates)}")
    print("")
    print("Install plan:")
    for item in updates:
        marker = {
            "replace": "R",
            "create": "C",
            "skip_existing": "S",
            "delete": "D",
        }.get(item.action, "?")
        source = f"{item.source} -> " if item.source and item.source != item.target else ""
        print(f"  [{marker}] {source}{item.target} ({item.size} bytes, {item.file_type})")
    print("")
    print("Legend: [R] replace, [C] create, [S] skip existing, [D] delete")
    print("")


def create_backup(zip_path: Path, root: Path, dirs: Dict[str, Path], inspection: Dict[str, Any]) -> Path:
    stamp = _now_stamp()
    backup_path = dirs["backups"] / f"claire_backup_{stamp}.zip"
    updates: List[UpdateFile] = inspection["updates"]

    manifest = {
        "created_at": _dt.datetime.now().isoformat(),
        "project_root": str(root),
        "update_zip": str(zip_path),
        "update_zip_sha256": _sha256_file(zip_path),
        "update_mode": inspection.get("mode"),
        "update_manifest": inspection.get("manifest"),
        "files": [],
    }

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as z:
        for item in updates:
            target = root / item.target
            entry = {
                "target": item.target,
                "source": item.source,
                "action": item.action,
                "existed_before_update": target.exists(),
                "backup_member": None,
                "sha256_before": None,
            }

            if target.exists() and target.is_file():
                backup_member = f"files/{item.target}"
                z.write(target, backup_member)
                entry["backup_member"] = backup_member
                entry["sha256_before"] = _sha256_file(target)

            manifest["files"].append(entry)

        z.writestr("backup_manifest.json", json.dumps(manifest, indent=2))

    return backup_path


def install_update(zip_path: Path, root: Path, inspection: Dict[str, Any]) -> None:
    updates: List[UpdateFile] = inspection["updates"]

    with zipfile.ZipFile(zip_path, "r") as z:
        zip_names = {name.replace("\\", "/"): name for name in z.namelist()}

        for item in updates:
            target = root / item.target

            if item.action == "skip_existing":
                print(f"Skipped existing: {item.target}")
                continue

            if item.action == "delete":
                if target.exists() and target.is_file():
                    target.unlink()
                    print(f"Deleted: {item.target}")
                elif target.exists() and target.is_dir():
                    raise SystemExit(f"Refusing to delete directory target: {item.target}")
                continue

            if item.source not in zip_names:
                if item.required:
                    raise SystemExit(f"Required source missing during install: {item.source}")
                print(f"Skipped missing optional source: {item.source}")
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(zip_names[item.source]))
            print(f"Installed: {item.target}")


def verify_install(root: Path, inspection: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for item in inspection["updates"]:
        target = root / item.target

        if item.action == "delete":
            ok = not target.exists()
            results.append({"target": item.target, "ok": ok, "check": "deleted", "error": None if ok else "target still exists"})
            continue

        if item.action == "skip_existing":
            results.append({"target": item.target, "ok": True, "check": "skipped", "error": None})
            continue

        if not target.exists():
            results.append({"target": item.target, "ok": False, "check": "exists", "error": "target missing after install"})
            continue

        actual_hash = _sha256_file(target)
        ok = bool(item.sha256) and actual_hash == item.sha256
        results.append({
            "target": item.target,
            "ok": ok,
            "check": "sha256",
            "expected": item.sha256,
            "actual": actual_hash,
            "error": None if ok else "sha256 mismatch",
        })

    failures = [r for r in results if not r["ok"]]
    if failures:
        print("")
        print("Install verification failures:")
        for failure in failures:
            print(f"  - {failure['target']}: {failure['error']}")
        raise SystemExit("Update installed but verification failed. Use backup restore if needed.")

    return results


def validate_json_files(root: Path, updates: List[UpdateFile]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for item in updates:
        if item.file_type != "json" or item.action in {"delete", "skip_existing"}:
            continue
        target = root / item.target
        try:
            json.loads(target.read_text(encoding="utf-8"))
            results.append({"target": item.target, "ok": True, "error": None})
        except Exception as exc:
            results.append({"target": item.target, "ok": False, "error": str(exc)})

    failures = [r for r in results if not r["ok"]]
    if failures:
        print("")
        print("JSON validation failures:")
        for failure in failures:
            print(f"  - {failure['target']}: {failure['error']}")
        raise SystemExit("Update installed but JSON validation failed.")

    return results


def compile_changed_python(root: Path, updates: List[UpdateFile]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for item in updates:
        if item.file_type != "python" or item.action in {"delete", "skip_existing"}:
            continue

        target = root / item.target
        try:
            py_compile.compile(str(target), doraise=True)
            results.append({"target": item.target, "ok": True, "error": None})
        except Exception as exc:
            results.append({"target": item.target, "ok": False, "error": str(exc)})

    failures = [r for r in results if not r["ok"]]
    if failures:
        print("")
        print("Python compile failures:")
        for failure in failures:
            print(f"  - {failure['target']}: {failure['error']}")
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
    return {"command": command, "returncode": proc.returncode, "output": proc.stdout}


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


def manifest_requested_test_mode(inspection: Dict[str, Any]) -> Optional[str]:
    manifest = inspection.get("manifest") or {}
    post_install = manifest.get("post_install") or {}
    if not isinstance(post_install, dict):
        return None
    if post_install.get("run_regression_tests"):
        return "auto"
    if post_install.get("run_pytest"):
        return "pytest"
    if post_install.get("run_smoke_test"):
        return "smoke"
    return None


def write_update_log(
    root: Path,
    dirs: Dict[str, Path],
    zip_path: Path,
    backup_path: Optional[Path],
    inspection: Dict[str, Any],
    compile_results: List[Dict[str, Any]],
    json_results: List[Dict[str, Any]],
    verify_results: List[Dict[str, Any]],
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
        "update_mode": inspection.get("mode"),
        "update_manifest": inspection.get("manifest"),
        "backup_path": str(backup_path) if backup_path else None,
        "files": [asdict(item) for item in inspection["updates"]],
        "compile_results": compile_results,
        "json_results": json_results,
        "verify_results": verify_results,
        "test_result": test_result,
    }
    log_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
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
            rel = entry.get("target") or entry.get("path")
            target = root / rel
            if entry.get("existed_before_update"):
                member = entry.get("backup_member")
                if not member:
                    raise SystemExit(f"Backup manifest error for {rel}: missing backup_member")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(member))
                print(f"Restored: {rel}")
            else:
                if target.exists() and target.is_file():
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
    parser = argparse.ArgumentParser(description="Claire manifest-driven local updater")
    parser.add_argument("zip_path", nargs="?", help="Path to Claire update zip")
    parser.add_argument("--root", help="Claire project root. Defaults to auto-detect from current folder.")
    parser.add_argument("--dry-run", action="store_true", help="Show update plan without modifying files.")
    parser.add_argument("--yes", "-y", action="store_true", help="Apply without interactive confirmation.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a backup before installing.")
    parser.add_argument("--run-tests", action="store_true", help="Run regression tests after install. Same as --test-mode auto.")
    parser.add_argument("--respect-manifest-tests", action="store_true", help="Run tests requested by manifest post_install.")
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
    inspection = inspect_update_zip(zip_path, root)
    updates: List[UpdateFile] = inspection["updates"]
    print_plan(zip_path, root, inspection)

    if args.dry_run:
        log_path = write_update_log(root, dirs, zip_path, None, inspection, [], [], [], {"ran": False}, dry_run=True)
        print(f"Dry run complete. Log written to: {log_path}")
        return 0

    confirm_or_exit(args)

    backup_path: Optional[Path] = None
    if not args.no_backup:
        backup_path = create_backup(zip_path, root, dirs, inspection)
        print(f"Backup created: {backup_path}")
    else:
        print("Backup skipped by --no-backup")

    install_update(zip_path, root, inspection)
    print("Update files installed.")

    verify_results = verify_install(root, inspection)
    print("Install verification passed.")

    compile_results = compile_changed_python(root, updates)
    print("Python compile checks passed.")

    json_results = validate_json_files(root, updates)
    print("JSON validation checks passed.")

    test_mode = "auto" if args.run_tests else args.test_mode
    if args.respect_manifest_tests and test_mode == "none":
        test_mode = manifest_requested_test_mode(inspection) or "none"

    test_result = run_tests(root, test_mode)

    log_path = write_update_log(
        root=root,
        dirs=dirs,
        zip_path=zip_path,
        backup_path=backup_path,
        inspection=inspection,
        compile_results=compile_results,
        json_results=json_results,
        verify_results=verify_results,
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
