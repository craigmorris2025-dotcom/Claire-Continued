#!/usr/bin/env python3
"""
Claire Safe Version Installer / Preflight Auditor
================================================

This is NOT a normal installer. It is a safety wrapper for Claire's
self-extracting version installers.

Mission:
  Preserve end-to-end Claire functionality after every version install.

Active Claire authority:
  ACTIVE RUNTIME:  src/claire/
  ACTIVE FRONTEND: src/frontend/
  LEGACY ONLY:     backend/
  FORBIDDEN:       src/backend/

Core policy:
  - Dry-run first.
  - Never execute the original installer.
  - Decode the embedded ZIP only.
  - Build exact source -> destination mapping.
  - Block backend/ and src/backend/.
  - Never overwrite existing files automatically.
  - Install NEW_SAFE files only with --approve-install.
  - Stage changed existing files for review.
  - Detect ambiguity and stop.
  - Detect backend imports and stop.
  - Track successful prior paths in .claire_install/install_registry.json.
  - Run py_compile on newly installed Python files.

First command:
  python tools/safe_install_claire_version.py --installer claire_v5_91_0_installer.py --project-root . --dry-run

Install safe new files only:
  python tools/safe_install_claire_version.py --installer claire_v5_91_0_installer.py --project-root . --approve-install
"""

from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import json
import os
import py_compile
import re
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ACTIVE_RUNTIME_PREFIXES = ("src/claire/", "src/frontend/")
ALLOWED_SUPPORT_PREFIXES = ("tests/", "docs/", "data/", "tools/", "scripts/", "config/")
ALLOWED_ROOT_FILES = {"version.json", "README.md", "CHANGELOG.md", "pyproject.toml", "requirements.txt", "pytest.ini"}
BLOCKED_PREFIXES = ("backend/", "src/backend/", ".venv/", ".git/", "__pycache__/")
SCAN_EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".claire_install", "logs"}
COMMON_AMBIGUOUS_FILENAMES_TO_IGNORE = {"__init__.py", "README.md", ".gitkeep", "index.json"}


@dataclass
class FilePlan:
    source_in_archive: str
    source_relative: str
    destination: str
    status: str
    reason: str
    sha256_new: str
    sha256_existing: Optional[str] = None
    existing_matches: Optional[List[str]] = None
    import_flags: Optional[List[str]] = None


@dataclass
class InstallReport:
    version: str
    installer: str
    project_root: str
    generated_at: str
    mode: str
    summary: Dict[str, int]
    files: List[FilePlan]


def normalize_rel(path: Path | str) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text_safely(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def ensure_project_root(root: Path) -> None:
    required = [
        root / "src",
        root / "src" / "claire",
        root / "src" / "frontend",
        root / "tests",
        root / "version.json",
    ]
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    if missing:
        raise SystemExit(
            "PROJECT ROOT VALIDATION FAILED\n"
            "Expected active Claire layout was not found.\n"
            "Missing:\n  - " + "\n  - ".join(missing)
        )


def install_state_paths(root: Path, version: str) -> Dict[str, Path]:
    base = root / ".claire_install"
    staging = base / "staging" / version
    return {
        "base": base,
        "registry": base / "install_registry.json",
        "staging": staging,
        "review": staging / "review_required",
        "reports": base / "reports",
    }


def load_registry(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {"installed_files": {}, "known_families": {}, "versions": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"installed_files": {}, "known_families": {}, "versions": {}}


def save_registry(path: Path, registry: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def load_path_approvals(root: Path) -> Dict[str, dict]:
    path = root / ".claire_install" / "path_approvals.json"
    if not path.exists():
        return {"approved_ambiguities": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"approved_ambiguities": []}


def is_approved_ambiguity(root: Path, source_rel: str, dest_rel: str) -> bool:
    approvals = load_path_approvals(root).get("approved_ambiguities", [])
    source_rel = normalize_rel(source_rel)
    dest_rel = normalize_rel(dest_rel)
    for item in approvals:
        if (
            normalize_rel(item.get("source", "")) == source_rel
            and normalize_rel(item.get("dest", "")) == dest_rel
        ):
            return True
    return False


def extract_version_from_installer_text(text: str, installer_path: Path) -> str:
    m = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', text)
    if m:
        return m.group(1)
    m = re.search(r'Claire v([0-9]+(?:_[0-9]+){1,2}|[0-9]+(?:\.[0-9]+){1,2})', text)
    if m:
        return m.group(1).replace("_", ".")
    m = re.search(r'claire_v([0-9]+)_([0-9]+)_([0-9]+)', installer_path.name)
    if m:
        return ".".join(m.groups())
    return "unknown_version"


def find_embedded_archive_b64(text: str) -> Tuple[str, str]:
    patterns = [
        ("PACKAGE_DATA", r"PACKAGE_DATA\s*=\s*[\"']{3}\\?\n?(.*?)[\"']{3}"),
        ("ARCHIVE_B64", r"ARCHIVE_B64\s*=\s*[\"']{3}\\?\n?(.*?)[\"']{3}"),
    ]
    for var_name, pattern in patterns:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            return var_name, "".join(m.group(1).split())
    raise SystemExit("No embedded PACKAGE_DATA or ARCHIVE_B64 block found in installer.")


def decode_zip_from_installer(installer: Path) -> Tuple[str, zipfile.ZipFile]:
    text = installer.read_text(encoding="utf-8", errors="ignore")
    version = extract_version_from_installer_text(text, installer)
    _, b64 = find_embedded_archive_b64(text)
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        raise SystemExit(f"Failed to decode embedded base64 archive: {e}")
    try:
        from io import BytesIO
        zf = zipfile.ZipFile(BytesIO(data))
    except Exception as e:
        raise SystemExit(f"Decoded archive is not a valid ZIP: {e}")
    return version, zf


def find_files_payload_members(zf: zipfile.ZipFile) -> List[str]:
    payload = []
    for name in zf.namelist():
        if name.endswith("/"):
            continue
        norm = normalize_rel(name)
        if "/files/" in norm:
            after = norm.split("/files/", 1)[1]
            if after:
                payload.append(name)
    return payload


def source_rel_after_files(member_name: str) -> str:
    return normalize_rel(member_name).split("/files/", 1)[1]


def is_blocked_path(rel: str) -> bool:
    rel = normalize_rel(rel)
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in BLOCKED_PREFIXES)


def is_allowed_path(rel: str) -> bool:
    rel = normalize_rel(rel)
    return (
        any(rel.startswith(p) for p in ACTIVE_RUNTIME_PREFIXES)
        or any(rel.startswith(p) for p in ALLOWED_SUPPORT_PREFIXES)
        or rel in ALLOWED_ROOT_FILES
    )


def family_key(rel: str) -> str:
    parts = normalize_rel(rel).split("/")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "claire":
        return "/".join(parts[:3])
    if len(parts) >= 2 and parts[0] == "src" and parts[1] == "frontend":
        return "src/frontend"
    return parts[0] if parts else ""


def destination_for_source_rel(source_rel: str, registry: Dict[str, dict]) -> str:
    source_rel = normalize_rel(source_rel)
    installed_files = registry.get("installed_files", {})
    if source_rel in installed_files:
        prior = installed_files[source_rel].get("installed_to")
        if prior:
            return normalize_rel(prior)
    return source_rel


def scan_existing_by_filename(root: Path) -> Dict[str, List[str]]:
    results: Dict[str, List[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = normalize_rel(Path(dirpath).relative_to(root))
        dirnames[:] = [d for d in dirnames if d not in SCAN_EXCLUDE_DIRS]
        if any(rel_dir == ex or rel_dir.startswith(ex + "/") for ex in SCAN_EXCLUDE_DIRS):
            continue
        for filename in filenames:
            if filename in COMMON_AMBIGUOUS_FILENAMES_TO_IGNORE:
                continue
            rel = normalize_rel((Path(dirpath) / filename).relative_to(root))
            results.setdefault(filename, []).append(rel)
    return results


def detect_import_flags(data: bytes, source_rel: str) -> List[str]:
    flags = []
    if not source_rel.endswith(".py"):
        return flags
    text = read_text_safely(data)
    if re.search(r'^\s*from\s+backend(\.|\s+import)', text, re.MULTILINE):
        flags.append("imports from backend.*")
    if re.search(r'^\s*import\s+backend(\.|\s|$)', text, re.MULTILINE):
        flags.append("imports backend.*")
    if "src.backend" in text:
        flags.append("references src.backend")
    return flags


def classify_file(root: Path, source_rel: str, dest_rel: str, data: bytes, existing_by_filename: Dict[str, List[str]], registry: Dict[str, dict], allow_new_folders: bool) -> FilePlan:
    source_rel = normalize_rel(source_rel)
    dest_rel = normalize_rel(dest_rel)
    dest = root / dest_rel
    new_hash = sha256_bytes(data)

    basename = Path(dest_rel).name
    existing_matches = [p for p in existing_by_filename.get(basename, []) if normalize_rel(p) != dest_rel]
    import_flags = detect_import_flags(data, source_rel)

    if is_blocked_path(dest_rel):
        return FilePlan(source_rel, source_rel, dest_rel, "BLOCKED", "Destination is forbidden/legacy path.", new_hash, existing_matches=existing_matches, import_flags=import_flags)

    if not is_allowed_path(dest_rel):
        return FilePlan(source_rel, source_rel, dest_rel, "NEW_PATH_REVIEW", "Destination is outside known active/support roots; review required.", new_hash, existing_matches=existing_matches, import_flags=import_flags)

    if import_flags:
        return FilePlan(source_rel, source_rel, dest_rel, "IMPORT_MISMATCH", "File references backend/src.backend while active runtime is src/claire.", new_hash, existing_matches=existing_matches, import_flags=import_flags)

    meaningful_matches = []
    for p in existing_matches:
        pn = normalize_rel(p)
        if pn.startswith("backend/"):
            meaningful_matches.append(pn + " [legacy]")
        elif pn.startswith("src/backend/"):
            meaningful_matches.append(pn + " [forbidden]")
        elif pn.startswith("src/claire/") or pn.startswith("src/frontend/"):
            meaningful_matches.append(pn + " [active]")
        elif pn.startswith(("tests/", "docs/", "tools/", "scripts/", "config/")):
            meaningful_matches.append(pn + " [support]")

    if meaningful_matches and not dest.exists():
        if is_approved_ambiguity(root, source_rel, dest_rel):
            return FilePlan(source_rel, source_rel, dest_rel, "NEW_SAFE", "Approved ambiguity; exact source/destination pair is allowed.", new_hash, existing_matches=meaningful_matches, import_flags=import_flags)
        return FilePlan(source_rel, source_rel, dest_rel, "AMBIGUOUS", "Same filename already exists elsewhere; confirm pathway before adding.", new_hash, existing_matches=meaningful_matches, import_flags=import_flags)

    if not dest.parent.exists() and not allow_new_folders:
        fam = family_key(dest_rel)
        known = registry.get("known_families", {}).get(fam)
        if not known:
            return FilePlan(source_rel, source_rel, dest_rel, "NEW_FOLDER_REVIEW", "Destination folder/family does not exist yet; review required.", new_hash, existing_matches=meaningful_matches, import_flags=import_flags)

    if dest.exists():
        old_hash = sha256_file(dest)
        if old_hash == new_hash:
            return FilePlan(source_rel, source_rel, dest_rel, "EXISTS_SAME", "Identical file already exists; skip.", new_hash, sha256_existing=old_hash, existing_matches=meaningful_matches, import_flags=import_flags)
        return FilePlan(source_rel, source_rel, dest_rel, "EXISTS_DIFFERENT", "Existing file differs; stage for review, do not overwrite.", new_hash, sha256_existing=old_hash, existing_matches=meaningful_matches, import_flags=import_flags)

    return FilePlan(source_rel, source_rel, dest_rel, "NEW_SAFE", "New file in approved active/support path.", new_hash, existing_matches=meaningful_matches, import_flags=import_flags)


def summarize(plans: List[FilePlan]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for p in plans:
        counts[p.status] = counts.get(p.status, 0) + 1
    return counts


def print_report(report: InstallReport) -> None:
    print("\n" + "=" * 78)
    print(f"Claire Safe Installer Preflight — v{report.version}")
    print("=" * 78)
    print(f"Installer: {report.installer}")
    print(f"Project:   {report.project_root}")
    print(f"Mode:      {report.mode}")
    print("\nSUMMARY")
    for k in sorted(report.summary):
        print(f"  {k:22} {report.summary[k]}")
    print("\nFILE MAP")
    for p in report.files:
        print(f"\n[{p.status}] {p.reason}")
        print(f"  source: {p.source_in_archive}")
        print(f"  dest:   {p.destination}")
        if p.existing_matches:
            print("  existing/similar:")
            for m in p.existing_matches[:10]:
                print(f"    - {m}")
            if len(p.existing_matches) > 10:
                print(f"    ... {len(p.existing_matches) - 10} more")
        if p.import_flags:
            print("  import flags:")
            for flag in p.import_flags:
                print(f"    - {flag}")


def write_json_report(paths: Dict[str, Path], report: InstallReport) -> Path:
    paths["reports"].mkdir(parents=True, exist_ok=True)
    out = paths["reports"] / f"{report.version}_preflight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return out


def stage_review_file(paths: Dict[str, Path], root: Path, plan: FilePlan, data: bytes) -> None:
    review = paths["review"] / plan.destination
    current = review.with_suffix(review.suffix + ".CURRENT")
    proposed = review.with_suffix(review.suffix + ".PROPOSED")
    diff = review.with_suffix(review.suffix + ".diff.txt")
    current.parent.mkdir(parents=True, exist_ok=True)
    dest = root / plan.destination
    if dest.exists():
        current.write_bytes(dest.read_bytes())
    proposed.write_bytes(data)
    current_text = dest.read_text(encoding="utf-8", errors="ignore").splitlines() if dest.exists() else []
    proposed_text = read_text_safely(data).splitlines()
    diff_text = "\n".join(difflib.unified_diff(current_text, proposed_text, fromfile=f"CURRENT/{plan.destination}", tofile=f"PROPOSED/{plan.destination}", lineterm=""))
    diff.write_text(diff_text, encoding="utf-8")


def compile_python_files(root: Path, installed_paths: Iterable[str]) -> Tuple[bool, List[str]]:
    errors = []
    for rel in installed_paths:
        if not rel.endswith(".py"):
            continue
        try:
            py_compile.compile(str(root / rel), doraise=True)
        except Exception as e:
            errors.append(f"{rel}: {e}")
    return not errors, errors


def update_registry(registry: Dict[str, dict], version: str, installed: List[FilePlan]) -> None:
    registry.setdefault("installed_files", {})
    registry.setdefault("known_families", {})
    registry.setdefault("versions", {})
    now = datetime.now().isoformat(timespec="seconds")
    version_files = []
    for plan in installed:
        registry["installed_files"][plan.source_relative] = {
            "installed_to": plan.destination,
            "version_added": version,
            "last_updated": version,
            "sha256": plan.sha256_new,
            "status": "active",
            "updated_at": now,
        }
        fam = family_key(plan.destination)
        if fam:
            registry["known_families"][fam] = {
                "first_seen_version": registry["known_families"].get(fam, {}).get("first_seen_version", version),
                "last_seen_version": version,
                "status": "active",
            }
        version_files.append(plan.destination)
    registry["versions"][version] = {"installed_at": now, "files_installed": version_files}


def build_plan(root: Path, installer: Path, allow_new_folders: bool) -> Tuple[str, Dict[str, Path], Dict[str, bytes], InstallReport]:
    ensure_project_root(root)
    version, zf = decode_zip_from_installer(installer)
    paths = install_state_paths(root, version)
    registry = load_registry(paths["registry"])
    payload_members = find_files_payload_members(zf)
    if not payload_members:
        raise SystemExit("No per-version files/ payload found. Use this for the 28 per-version installers only.")
    existing_by_filename = scan_existing_by_filename(root)
    payload_data: Dict[str, bytes] = {}
    plans: List[FilePlan] = []
    for member in payload_members:
        source_rel = source_rel_after_files(member)
        dest_rel = destination_for_source_rel(source_rel, registry)
        data = zf.read(member)
        payload_data[source_rel] = data
        plan = classify_file(root, source_rel, dest_rel, data, existing_by_filename, registry, allow_new_folders)
        plan.source_in_archive = member
        plans.append(plan)
    report = InstallReport(version=version, installer=str(installer), project_root=str(root), generated_at=datetime.now().isoformat(timespec="seconds"), mode="dry-run", summary=summarize(plans), files=plans)
    return version, paths, payload_data, report


def install_safe_new_files(root: Path, version: str, paths: Dict[str, Path], payload_data: Dict[str, bytes], report: InstallReport) -> None:
    blocking = [p for p in report.files if p.status in {"BLOCKED", "AMBIGUOUS", "IMPORT_MISMATCH"}]
    if blocking:
        raise SystemExit("INSTALL BLOCKED. Resolve BLOCKED / AMBIGUOUS / IMPORT_MISMATCH files before installing.")
    review_required = [p for p in report.files if p.status in {"EXISTS_DIFFERENT", "NEW_FOLDER_REVIEW", "NEW_PATH_REVIEW"}]
    new_safe = [p for p in report.files if p.status == "NEW_SAFE"]
    paths["staging"].mkdir(parents=True, exist_ok=True)
    paths["review"].mkdir(parents=True, exist_ok=True)
    for plan in review_required:
        stage_review_file(paths, root, plan, payload_data[plan.source_relative])
    installed: List[FilePlan] = []
    created_paths: List[Path] = []
    try:
        for plan in new_safe:
            dest = root / plan.destination
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(payload_data[plan.source_relative])
            installed.append(plan)
            created_paths.append(dest)
        ok, errors = compile_python_files(root, [p.destination for p in installed])
        if not ok:
            for p in created_paths:
                try:
                    p.unlink()
                except Exception:
                    pass
            raise SystemExit("PY_COMPILE FAILED. New files were removed.\n" + "\n".join(errors))
        registry = load_registry(paths["registry"])
        update_registry(registry, version, installed)
        save_registry(paths["registry"], registry)
        print(f"\nInstalled NEW_SAFE files: {len(installed)}")
        print(f"Review-required files staged: {len(review_required)}")
        if review_required:
            print(f"Review folder: {paths['review']}")
    except Exception:
        for p in created_paths:
            try:
                p.unlink()
            except Exception:
                pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire safe installer / preflight auditor")
    parser.add_argument("--installer", required=True, help="Path to claire_vX_Y_Z_installer.py or .txt")
    parser.add_argument("--project-root", default=".", help="Claire project root")
    parser.add_argument("--dry-run", action="store_true", help="Preflight only. Default behavior.")
    parser.add_argument("--approve-install", action="store_true", help="Install only NEW_SAFE files. Existing different files are staged for review.")
    parser.add_argument("--allow-new-folders", action="store_true", help="Allow new approved-family folders without NEW_FOLDER_REVIEW.")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    installer = Path(args.installer).resolve()
    if not installer.exists():
        raise SystemExit(f"Installer not found: {installer}")

    version, paths, payload_data, report = build_plan(root, installer, args.allow_new_folders)
    report.mode = "approve-install-new-safe-only" if args.approve_install else "dry-run"
    print_report(report)
    report_path = write_json_report(paths, report)
    print(f"\nReport written: {report_path}")

    if args.approve_install:
        install_safe_new_files(root, version, paths, payload_data, report)
    else:
        print("\nDry run only. No files were installed.")


if __name__ == "__main__":
    main()
