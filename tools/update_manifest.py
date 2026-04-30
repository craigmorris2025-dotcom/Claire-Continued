#!/usr/bin/env python
r"""
Claire Update Manifest Helper

Inspect an update zip and print a manifest.

Usage:
    python tools/update_manifest.py .\some_update.zip
    python tools/update_manifest.py .\some_update.zip --json

The helper detects both:
    - path-preserving zips
    - manifest-driven zips with claire_update_manifest.json / update_manifest.json / manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional


MANIFEST_NAMES = ["claire_update_manifest.json", "update_manifest.json", "manifest.json"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(z: zipfile.ZipFile) -> Optional[Dict[str, Any]]:
    names = {name.replace("\\", "/"): name for name in z.namelist()}
    for manifest_name in MANIFEST_NAMES:
        if manifest_name in names:
            raw = z.read(names[manifest_name]).decode("utf-8")
            manifest = json.loads(raw)
            manifest["_manifest_member"] = manifest_name
            return manifest
    return None


def manifest_for_zip(zip_path: Path) -> Dict[str, Any]:
    if not zip_path.exists():
        raise SystemExit(f"Zip not found: {zip_path}")

    files: List[Dict[str, Any]] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        bad = z.testzip()
        if bad is not None:
            raise SystemExit(f"Zip integrity failed for: {bad}")

        detected_manifest = load_manifest(z)

        if detected_manifest:
            mode = "manifest"
            zip_names = {name.replace("\\", "/"): name for name in z.namelist()}
            for entry in detected_manifest.get("files", []):
                source = entry.get("source", "")
                action = entry.get("action", "replace")
                if action == "delete":
                    data = b""
                    source_exists = True
                else:
                    source_exists = source in zip_names
                    data = z.read(zip_names[source]) if source_exists else b""

                files.append({
                    "source": source,
                    "target": entry.get("target", ""),
                    "action": action,
                    "type": entry.get("type", ""),
                    "required": entry.get("required", True),
                    "source_exists": source_exists,
                    "size": len(data),
                    "sha256": sha256_bytes(data) if data else "",
                })
        else:
            mode = "path_preserving"
            for info in z.infolist():
                name = info.filename.replace("\\", "/")
                if not name or name.endswith("/") or name.startswith("__MACOSX/"):
                    continue
                data = z.read(info.filename)
                files.append({
                    "source": name,
                    "target": name,
                    "action": "replace_or_create",
                    "type": Path(name).suffix.lower().lstrip(".") or "file",
                    "required": True,
                    "source_exists": True,
                    "size": len(data),
                    "sha256": sha256_bytes(data),
                })

    return {
        "zip_path": str(zip_path),
        "zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        "mode": mode,
        "manifest": detected_manifest,
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
    print(f"Mode:       {manifest['mode']}")
    print(f"Files:      {manifest['file_count']}")
    if manifest.get("manifest"):
        detected = manifest["manifest"]
        print(f"Name:       {detected.get('update_name', 'unknown')}")
        print(f"Version:    {detected.get('version', 'unknown')}")
        print(f"Manifest:   {detected.get('_manifest_member', 'unknown')}")
    print("")

    for item in manifest["files"]:
        src = f"{item['source']} -> " if item.get("source") and item["source"] != item.get("target") else ""
        status = "" if item.get("source_exists", True) else " [MISSING SOURCE]"
        print(f"- {src}{item.get('target')} ({item['size']} bytes) {item.get('sha256', '')[:12]}{status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
