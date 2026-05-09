#!/usr/bin/env python
r"""
Claire Manifest-Driven Local Updater

Supports two update formats:

1. Path-preserving zip
   Zip member path is installed directly into the same project-relative path.

   Example zip member:
       claire/engines/export_package_engine.py

   Installs to:
       <project_root>/claire/engines/export_package_engine.py

2. Manifest-driven zip
   Zip contains one of:
       claire_update_manifest.json
       update_manifest.json
       manifest.json

   Manifest routes each source file to a target system folder.

Target aliases:
    @engine/name.py          -> claire/engines/name.py
    @engines/name.py         -> claire/engines/name.py
    @orchestrator/name.py    -> claire/orchestrator/name.py
    @domain/name.py          -> claire/domain/name.py
    @portfolio/name.py       -> claire/portfolio/name.py
    @export/name.py          -> claire/export/name.py
    @backend/path            -> backend/path
    @frontend/path           -> frontend/path
    @tests/path              -> tests/path
    @tools/path              -> tools/path
    @data/path               -> data/path
    @root/path               -> path
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

PROJECT_MARKERS = ["main.py", "claire"]

MANIFEST_NAMES = [
    "claire_update_manifest.json",
    "update_manifest.json",
    "manifest.json",
]

TARGET_ALIASES = {
    "@engine": "claire/engines",
    "@engines": "claire/engines",
    "@orchestrator": "claire/orchestrator",
    "@domain": "claire/domain",
    "@portfolio": "claire/portfolio",
    "@export": "claire/export",
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
        "Could not detect Claire project root. "
        "Run from the folder containing main.py and claire, "
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

    if (
        normalized.startswith("/")
        or normalized.startswith("../")
        or "/../" in normalized
        or normalized == ".."
    ):
        raise ValueError(f"Unsafe path rejected: {path}")

    return normalized


def should_skip_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")

    return (
        not normalized
        or normalized.endswith("/")
        or normalized.startswith("__MACOSX/")
    )


def resolve_target(target: str) -> str:
    target = normalize_zip_path(target)

    if target.startswith("@"):
        head, _, tail = target.partition("/")

        if head not in TARGET_ALIASES:
            raise ValueError(
                f"Unknown target alias {head!r} in target {target!r}"
            )

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

    if suffix == ".json":
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


def compile_changed_python(root: Path, updates: List[UpdateFile]):
    results = []

    for item in updates:
        if item.file_type != "python":
            continue

        target = root / item.target

        try:
            py_compile.compile(str(target), doraise=True)
            results.append(
                {
                    "target": item.target,
                    "ok": True,
                    "error": None,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "target": item.target,
                    "ok": False,
                    "error": str(exc),
                }
            )

    failures = [r for r in results if not r["ok"]]

    if failures:
        print("")
        print("Python compile failures:")

        for failure in failures:
            print(f"  - {failure['target']}: {failure['error']}")

        raise SystemExit(
            "Update installed but Python compile checks failed."
        )

    return results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Claire manifest-driven local updater"
    )

    parser.add_argument("zip_path", nargs="?")
    parser.add_argument("--root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", "-y", action="store_true")

    args = parser.parse_args(argv)

    root = (
        find_project_root(Path(args.root))
        if args.root
        else find_project_root()
    )

    ensure_dirs(root)

    print("")
    print("Claire updater runtime root:")
    print(root)
    print("")

    print("Resolved package root:")
    print(root / "claire")
    print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())