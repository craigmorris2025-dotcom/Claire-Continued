#!/usr/bin/env python3
"""
Claire Safe Version Installer Wrapper
====================================

Purpose:
  Safely install ONE Claire version installer at a time without letting the
  self-extracting installer write directly into the active project.

Use this instead of running the version installer directly.

Example dry run:
  python safe_install_claire_version.py ^
    --installer "C:\path\to\claire_v5_91_0_installer.py" ^
    --project-root "C:\path\to\Claire"

Example approved install:
  python safe_install_claire_version.py ^
    --installer "C:\path\to\claire_v5_91_0_installer.py" ^
    --project-root "C:\path\to\Claire" ^
    --approve-install

Example approved install with replacement permission:
  python safe_install_claire_version.py ^
    --installer "C:\path\to\claire_v5_91_0_installer.py" ^
    --project-root "C:\path\to\Claire" ^
    --approve-install ^
    --approve-replace

Rules enforced:
  - Dry-run by default.
  - Extracts installer into staging first.
  - Verifies Claire project root.
  - Shows exact source -> destination mapping.
  - Blocks overwrites unless --approve-replace is provided.
  - Backs up replaced files.
  - Compiles installed Python files.
  - Runs pytest for newly installed test files when possible.
  - Rolls back on validation failure.
  - Updates version only when requested and validation succeeds.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional


REQUIRED_ROOT_FILES = [
    "main.py",
    "pyproject.toml",
    "requirements.txt",
    "pytest.ini",
    "version.json",
]

REQUIRED_ROOT_DIRS = [
    "src",
    "src/claire",
    "src/frontend",
    "tests",
]

FORBIDDEN_DESTINATION_PARTS = {
    "src/backend",      # Claire uses root backend/ plus src/claire/, not src/backend/
    "claire_v5_",
    "claire_v6_",
    "claire_v7_",
    "claire_v8_",
    "claire_v9_",
    "claire_v10_",
}

IGNORED_STAGING_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


@dataclass
class PlannedFile:
    source: str
    destination: str
    relative_path: str
    action: str
    exists: bool
    will_write: bool


@dataclass
class InstallRecord:
    version: str
    installer: str
    project_root: str
    timestamp_utc: str
    dry_run: bool
    approve_install: bool
    approve_replace: bool
    staging_dir: str
    backup_dir: str
    planned_files: List[PlannedFile]
    validation_passed: Optional[bool] = None
    error: Optional[str] = None


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def utc_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_rel_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def infer_version_from_name(installer: Path) -> str:
    text = installer.name
    match = re.search(r"v(\d+)_(\d+)_(\d+)", text)
    if match:
        return ".".join(match.groups())

    match = re.search(r"v(\d+)\.(\d+)\.(\d+)", text)
    if match:
        return ".".join(match.groups())

    return "unknown"


def version_folder_name(version: str) -> str:
    if version == "unknown":
        return f"unknown_{utc_stamp()}"
    return "v" + version.replace(".", "_")


def verify_project_root(project_root: Path) -> None:
    missing = []

    for rel in REQUIRED_ROOT_FILES:
        if not (project_root / rel).is_file():
            missing.append(rel)

    for rel in REQUIRED_ROOT_DIRS:
        if not (project_root / rel).is_dir():
            missing.append(rel)

    if missing:
        raise RuntimeError(
            "Project root verification failed. Missing required Claire markers:\n"
            + "\n".join(f"  - {item}" for item in missing)
            + "\n\nRefusing to install. Point --project-root at the real Claire project root."
        )

    if (project_root / "src" / "backend").exists():
        raise RuntimeError(
            "Forbidden path exists: src/backend\n"
            "Claire's current tree uses root backend/ and src/claire/. Refusing to proceed."
        )


def run_subprocess(cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def extract_to_staging(installer: Path, staging_root: Path) -> None:
    staging_root.mkdir(parents=True, exist_ok=True)

    # Current Claire version installers accept:
    #   python installer.py [project_root] --extract-only
    result = run_subprocess(
        [sys.executable, str(installer), str(staging_root), "--extract-only"],
        cwd=staging_root,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Installer extraction failed.\n\n"
            f"Command output:\n{result.stdout}"
        )


def find_files_dir(staging_root: Path) -> Path:
    candidates = []
    for root, dirs, files in os.walk(staging_root):
        root_path = Path(root)
        if root_path.name == "files":
            candidates.append(root_path)

    if not candidates:
        raise RuntimeError(
            "Could not find a 'files' directory after extraction.\n"
            "This wrapper expects each version package to contain a files/ folder."
        )

    # Prefer the shortest path to avoid selecting nested accidental files folders.
    candidates.sort(key=lambda p: len(p.parts))
    return candidates[0]


def destination_is_forbidden(rel: Path) -> bool:
    rel_norm = normalize_rel_path(rel).lower()

    for forbidden in FORBIDDEN_DESTINATION_PARTS:
        if forbidden in rel_norm:
            return True

    # Avoid copying installer package folders into active project.
    first = rel.parts[0].lower() if rel.parts else ""
    if first.startswith("claire_v"):
        return True

    return False


def collect_plan(files_dir: Path, project_root: Path, approve_replace: bool, approve_install: bool) -> List[PlannedFile]:
    planned: List[PlannedFile] = []

    for root, dirs, files in os.walk(files_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_STAGING_DIR_NAMES]
        for fname in files:
            src = Path(root) / fname
            rel = src.relative_to(files_dir)

            if destination_is_forbidden(rel):
                action = "FORBIDDEN_PATH"
                dst = project_root / rel
                planned.append(
                    PlannedFile(
                        source=str(src),
                        destination=str(dst),
                        relative_path=normalize_rel_path(rel),
                        action=action,
                        exists=dst.exists(),
                        will_write=False,
                    )
                )
                continue

            dst = project_root / rel
            exists = dst.exists()

            if exists and approve_replace:
                action = "REPLACE_APPROVED"
                will_write = approve_install
            elif exists:
                action = "BLOCK_OVERWRITE"
                will_write = False
            else:
                action = "CREATE"
                will_write = approve_install

            planned.append(
                PlannedFile(
                    source=str(src),
                    destination=str(dst),
                    relative_path=normalize_rel_path(rel),
                    action=action,
                    exists=exists,
                    will_write=will_write,
                )
            )

    return planned


def print_plan(plan: List[PlannedFile]) -> None:
    print("\nINSTALL PLAN")
    print("=" * 90)

    counts = {}
    for item in plan:
        counts[item.action] = counts.get(item.action, 0) + 1

    for key in sorted(counts):
        print(f"{key:20s}: {counts[key]}")

    print("=" * 90)

    for item in plan:
        print(f"\n[{item.action}] {item.relative_path}")
        print(f"  source:      {item.source}")
        print(f"  destination: {item.destination}")
        print(f"  exists:      {item.exists}")
        print(f"  will_write:  {item.will_write}")

    print("\n" + "=" * 90)


def backup_file(dst: Path, backup_root: Path, rel: str) -> None:
    backup_path = backup_root / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dst, backup_path)


def apply_plan(plan: List[PlannedFile], backup_root: Path, approve_replace: bool) -> dict:
    created = []
    replaced = []
    skipped = []
    blocked = []
    forbidden = []

    for item in plan:
        src = Path(item.source)
        dst = Path(item.destination)

        if item.action == "FORBIDDEN_PATH":
            forbidden.append(item.relative_path)
            continue

        if item.action == "BLOCK_OVERWRITE":
            blocked.append(item.relative_path)
            continue

        if not item.will_write:
            skipped.append(item.relative_path)
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            if not approve_replace:
                blocked.append(item.relative_path)
                continue
            backup_file(dst, backup_root, item.relative_path)
            shutil.copy2(src, dst)
            replaced.append(item.relative_path)
        else:
            shutil.copy2(src, dst)
            created.append(item.relative_path)

    return {
        "created": created,
        "replaced": replaced,
        "skipped": skipped,
        "blocked": blocked,
        "forbidden": forbidden,
    }


def rollback(project_root: Path, backup_root: Path, applied: dict) -> None:
    print("\nROLLBACK STARTED")
    print("=" * 80)

    # Remove files created by this install.
    for rel in applied.get("created", []):
        path = project_root / rel
        if path.exists():
            path.unlink()
            print(f"removed created file: {rel}")

    # Restore replaced files.
    for rel in applied.get("replaced", []):
        backup_path = backup_root / rel
        dst = project_root / rel
        if backup_path.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, dst)
            print(f"restored replaced file: {rel}")

    print("=" * 80)
    print("ROLLBACK COMPLETE\n")


def py_compile_files(files: Iterable[str], project_root: Path) -> None:
    py_files = [str(project_root / rel) for rel in files if rel.endswith(".py") and (project_root / rel).exists()]
    if not py_files:
        return

    result = run_subprocess([sys.executable, "-m", "py_compile", *py_files], cwd=project_root)
    if result.returncode != 0:
        raise RuntimeError("Python compile validation failed:\n" + result.stdout)


def pytest_files(files: Iterable[str], project_root: Path) -> None:
    test_files = [str(project_root / rel) for rel in files if rel.startswith("tests/") and rel.endswith(".py") and (project_root / rel).exists()]
    if not test_files:
        return

    result = run_subprocess([sys.executable, "-m", "pytest", *test_files, "-q"], cwd=project_root)
    if result.returncode != 0:
        raise RuntimeError("Pytest validation failed:\n" + result.stdout)


def update_version_json(project_root: Path, version: str) -> None:
    version_file = project_root / "version.json"
    data = {}

    if version_file.exists():
        try:
            data = json.loads(version_file.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    data["version"] = version
    data["last_verified_install_utc"] = utc_iso()
    data["installer"] = "safe_install_claire_version.py"

    version_file.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def write_audit(record: InstallRecord, project_root: Path) -> Path:
    audit_dir = project_root / "logs" / "installer_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    version_safe = version_folder_name(record.version)
    path = audit_dir / f"{record.timestamp_utc}_{version_safe}.json"

    data = asdict(record)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely install one Claire version installer.")
    parser.add_argument("--installer", required=True, help="Path to claire_vX_X_X_installer.py")
    parser.add_argument("--project-root", required=True, help="Path to active Claire project root")
    parser.add_argument("--version", default=None, help="Version override, e.g. 5.91.0")
    parser.add_argument("--approve-install", action="store_true", help="Actually write files. Without this, dry-run only.")
    parser.add_argument("--approve-replace", action="store_true", help="Allow replacement of existing files, with backup.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest validation for installed tests.")
    parser.add_argument("--update-version", action="store_true", help="Update version.json only after validation succeeds.")
    parser.add_argument("--keep-staging", action="store_true", help="Keep staging files after run.")
    args = parser.parse_args()

    installer = Path(args.installer).resolve()
    project_root = Path(args.project_root).resolve()
    version = args.version or infer_version_from_name(installer)
    stamp = utc_stamp()

    if not installer.is_file():
        print(f"ERROR: installer not found: {installer}", file=sys.stderr)
        return 2

    dry_run = not args.approve_install
    staging_root = project_root / ".claire_installer_staging" / version_folder_name(version) / stamp
    backup_root = project_root / ".claire_installer_backups" / version_folder_name(version) / stamp

    record = InstallRecord(
        version=version,
        installer=str(installer),
        project_root=str(project_root),
        timestamp_utc=stamp,
        dry_run=dry_run,
        approve_install=args.approve_install,
        approve_replace=args.approve_replace,
        staging_dir=str(staging_root),
        backup_dir=str(backup_root),
        planned_files=[],
    )

    applied = {
        "created": [],
        "replaced": [],
        "skipped": [],
        "blocked": [],
        "forbidden": [],
    }

    try:
        print("\nCLAIRE SAFE VERSION INSTALLER")
        print("=" * 90)
        print(f"version:      {version}")
        print(f"installer:    {installer}")
        print(f"project root: {project_root}")
        print(f"mode:         {'APPROVED INSTALL' if args.approve_install else 'DRY RUN ONLY'}")
        print("=" * 90)

        verify_project_root(project_root)
        extract_to_staging(installer, staging_root)

        files_dir = find_files_dir(staging_root)
        plan = collect_plan(
            files_dir=files_dir,
            project_root=project_root,
            approve_replace=args.approve_replace,
            approve_install=args.approve_install,
        )
        record.planned_files = plan

        print_plan(plan)

        if any(item.action == "FORBIDDEN_PATH" for item in plan):
            raise RuntimeError("Forbidden destination path detected. Refusing install.")

        if any(item.action == "BLOCK_OVERWRITE" for item in plan):
            print("\nOverwrite-blocked files exist.")
            print("This is safe. Nothing will replace them unless --approve-replace is provided.")

        if dry_run:
            record.validation_passed = None
            audit_path = write_audit(record, project_root)
            print(f"\nDRY RUN COMPLETE. No files written.")
            print(f"Audit written to: {audit_path}")
            return 0

        backup_root.mkdir(parents=True, exist_ok=True)
        applied = apply_plan(plan, backup_root, args.approve_replace)

        if applied["forbidden"]:
            raise RuntimeError("Forbidden files encountered during apply.")

        if applied["blocked"]:
            print("\nBlocked files were not overwritten:")
            for rel in applied["blocked"]:
                print(f"  - {rel}")

        written_files = applied["created"] + applied["replaced"]

        print("\nVALIDATION")
        print("=" * 90)
        py_compile_files(written_files, project_root)
        print("✓ Python compile validation passed")

        if not args.skip_tests:
            pytest_files(written_files, project_root)
            print("✓ Pytest validation passed or no tests were installed")
        else:
            print("⚠ Pytest validation skipped by request")

        if args.update_version and version != "unknown":
            update_version_json(project_root, version)
            print(f"✓ version.json updated to {version}")

        record.validation_passed = True
        audit_path = write_audit(record, project_root)

        print("\nINSTALL COMPLETE")
        print("=" * 90)
        print(f"created:  {len(applied['created'])}")
        print(f"replaced: {len(applied['replaced'])}")
        print(f"blocked:  {len(applied['blocked'])}")
        print(f"audit:    {audit_path}")
        print("=" * 90)
        return 0

    except Exception as exc:
        record.validation_passed = False
        record.error = str(exc)

        if args.approve_install:
            try:
                rollback(project_root, backup_root, applied)
            except Exception:
                print("Rollback encountered an error:")
                traceback.print_exc()

        try:
            audit_path = write_audit(record, project_root)
            print(f"\nFailed audit written to: {audit_path}")
        except Exception:
            pass

        print("\nINSTALL FAILED")
        print("=" * 90)
        print(str(exc))
        print("=" * 90)
        return 1

    finally:
        if not args.keep_staging:
            # Keep staging on failure for inspection, remove only on success/dry run.
            if record.validation_passed is not False and staging_root.exists():
                shutil.rmtree(staging_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
