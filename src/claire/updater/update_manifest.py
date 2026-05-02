"""
Claire web update manifest contracts.

v5.48 bootstrap:
- Reads claire_update_manifest.json from update packages.
- Validates expected file entries, install targets, and optional SHA256 hashes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


MANIFEST_NAMES = ("claire_update_manifest.json", "update_manifest.json", "manifest.json")


@dataclass
class UpdateManifestFile:
    source: str
    target: str
    action: str = "replace"
    file_type: str = "file"
    required: bool = True
    sha256: str = ""

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "UpdateManifestFile":
        return cls(
            source=str(value.get("source") or ""),
            target=str(value.get("target") or ""),
            action=str(value.get("action") or "replace"),
            file_type=str(value.get("type") or value.get("file_type") or "file"),
            required=bool(value.get("required", True)),
            sha256=str(value.get("sha256") or ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "action": self.action,
            "type": self.file_type,
            "required": self.required,
            "sha256": self.sha256,
        }


@dataclass
class UpdateManifest:
    update_name: str
    version: str
    description: str = ""
    files: List[UpdateManifestFile] = field(default_factory=list)
    package_sha256: str = ""
    trusted_source: str = ""
    post_install: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UpdateManifest":
        if not isinstance(payload, dict):
            raise ValueError("Update manifest must be a JSON object.")
        files = [UpdateManifestFile.from_dict(item) for item in payload.get("files", [])]
        manifest = cls(
            update_name=str(payload.get("update_name") or payload.get("name") or ""),
            version=str(payload.get("version") or ""),
            description=str(payload.get("description") or ""),
            files=files,
            package_sha256=str(payload.get("package_sha256") or ""),
            trusted_source=str(payload.get("trusted_source") or ""),
            post_install=payload.get("post_install") or {},
        )
        manifest.validate()
        return manifest

    def validate(self) -> None:
        if not self.update_name:
            raise ValueError("Manifest missing update_name.")
        if not self.version:
            raise ValueError("Manifest missing version.")
        if not self.files:
            raise ValueError("Manifest must include at least one file.")
        for idx, item in enumerate(self.files):
            if item.action not in {"replace", "create", "create_if_missing", "delete"}:
                raise ValueError(f"Unsupported action in files[{idx}]: {item.action}")
            if item.action != "delete" and not item.source:
                raise ValueError(f"Missing source in files[{idx}].")
            if not item.target:
                raise ValueError(f"Missing target in files[{idx}].")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "update_name": self.update_name,
            "version": self.version,
            "description": self.description,
            "package_sha256": self.package_sha256,
            "trusted_source": self.trusted_source,
            "files": [item.to_dict() for item in self.files],
            "post_install": self.post_install,
        }


def normalize_package_path(path: str) -> str:
    path = (path or "").replace("\\", "/").strip()
    if not path or path.startswith("/") or path.startswith("../") or "/../" in path or path == "..":
        raise ValueError(f"Unsafe package path rejected: {path!r}")
    return path


__all__ = ["MANIFEST_NAMES", "UpdateManifest", "UpdateManifestFile", "normalize_package_path"]
