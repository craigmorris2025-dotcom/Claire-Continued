"""
Claire update package verifier.

v5.48 bootstrap:
- Validates zip integrity, manifest shape, file presence, and optional SHA256 hashes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import hashlib
import json
import zipfile

from runtime_core.updater.update_manifest import MANIFEST_NAMES, UpdateManifest, normalize_package_path


class PackageVerifier:
    """Verify Claire update package structure before install."""

    def verify(self, package_path: Path, expected_sha256: str = "") -> Dict[str, Any]:
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")
        package_hash = self.sha256_file(package_path)
        if expected_sha256 and package_hash.lower() != expected_sha256.lower():
            raise ValueError("Package SHA256 does not match expected hash.")

        with zipfile.ZipFile(package_path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise ValueError(f"Zip integrity check failed for {bad_member}")
            manifest_member = self._find_manifest_member(archive)
            manifest_payload = json.loads(archive.read(manifest_member).decode("utf-8-sig"))
            manifest = UpdateManifest.from_dict(manifest_payload)
            if manifest.package_sha256 and manifest.package_sha256.lower() != package_hash.lower():
                raise ValueError("Manifest package_sha256 does not match downloaded package.")
            self._verify_manifest_files(archive, manifest)

        return {
            "status": "success",
            "package_path": str(package_path),
            "package_sha256": package_hash,
            "manifest_member": manifest_member,
            "manifest": manifest.to_dict(),
            "file_count": len(manifest.files),
        }

    def _find_manifest_member(self, archive: zipfile.ZipFile) -> str:
        names = {name.replace("\\", "/"): name for name in archive.namelist()}
        for manifest_name in MANIFEST_NAMES:
            if manifest_name in names:
                return names[manifest_name]
        raise ValueError("Package is missing claire_update_manifest.json.")

    def _verify_manifest_files(self, archive: zipfile.ZipFile, manifest: UpdateManifest) -> None:
        names = {name.replace("\\", "/"): name for name in archive.namelist()}
        for item in manifest.files:
            normalize_package_path(item.target)
            if item.action == "delete":
                continue
            source = normalize_package_path(item.source)
            if source not in names:
                if item.required:
                    raise ValueError(f"Manifest source missing from package: {source}")
                continue
            if item.sha256:
                actual = hashlib.sha256(archive.read(names[source])).hexdigest()
                if actual.lower() != item.sha256.lower():
                    raise ValueError(f"SHA256 mismatch for package member: {source}")

    def sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()


__all__ = ["PackageVerifier"]
