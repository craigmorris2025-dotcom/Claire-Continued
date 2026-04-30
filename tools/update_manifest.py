#!/usr/bin/env python
"""
Claire Update Manifest Helper

Inspect an update zip and print a simple manifest.

Usage:

    python tools/update_manifest.py .\some_claire_update.zip
    python tools/update_manifest.py .\some_claire_update.zip --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_for_zip(zip_path: Path) -> Dict[str, Any]:
    if not zip_path.exists():
        raise SystemExit(f"Zip not found: {zip_path}")

    files: List[Dict[str, Any]] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        bad = z.testzip()
        if bad is not None:
            raise SystemExit(f"Zip integrity failed for: {bad}")

        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            if not name or name.endswith("/") or name.startswith("__MACOSX/"):
                continue
            data = z.read(info.filename)
            files.append({
                "path": name,
                "size": len(data),
                "sha256": sha256_bytes(data),
            })

    return {
        "zip_path": str(zip_path),
        "zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        "file_count": len(files),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a Claire update zip manifest")
    parser.add_argument("zip_path")
    parser.add_argument("--json", action="store_true", help="Print full JSON manifest")
    args = parser.parse_args()

    manifest = manifest_for_zip(Path(args.zip_path).resolve())

    if args.json:
        print(json.dumps(manifest, indent=2))
        return 0

    print("Claire Update Manifest")
    print("======================")
    print(f"Zip:        {manifest['zip_path']}")
    print(f"Zip SHA256: {manifest['zip_sha256']}")
    print(f"Files:      {manifest['file_count']}")
    print("")
    for item in manifest["files"]:
        print(f"- {item['path']} ({item['size']} bytes) {item['sha256'][:12]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
