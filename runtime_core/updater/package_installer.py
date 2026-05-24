"""
Claire update package installer.

v5.48 bootstrap:
- Installs verified manifest-driven update packages.
- Backs up changed files, validates hashes, compiles Python files, and returns rollback path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import hashlib
import json
import py_compile
import zipfile

from runtime_core.updater.rollback_manager import RollbackManager
from runtime_core.updater.update_manifest import MANIFEST_NAMES, UpdateManifest, normalize_package_path


class PackageInstaller:
    """Install a verified Claire update package into a project root."""

    TARGET_ALIASES = {
        "@engine": "src/claire/engines",
        "@engines": "src/claire/engines",
        "@feeds": "src/claire/feeds",
        "@updater": "src/claire/updater",
        "@orchestrator": "src/claire/orchestrator",
        "@domain": "src/claire/domain",
        "@portfolio": "src/claire/portfolio",
        "@export": "src/claire/export",
        "@frontend": "src/frontend",
        "@tools": "tools",
        "@data": "data",
        "@root": "",
    }

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.rollback = RollbackManager(project_root)

    def install(self, package_path: Path, dry_run: bool = False, no_backup: bool = False) -> Dict[str, Any]:
        with zipfile.ZipFile(package_path, "r") as archive:
            manifest = self._load_manifest(archive)
            plan = self._plan(manifest)
            if dry_run:
                return {"status": "dry_run", "manifest": manifest.to_dict(), "plan": plan, "installed_files": []}

            backup_path = None if no_backup else self.rollback.create_backup(plan, manifest.update_name)
            installed = self._install_files(archive, manifest)

        verify_results = self._verify_installed(installed)
        compile_results = self._compile_python(installed)
        return {
            "status": "success",
            "manifest": manifest.to_dict(),
            "backup_path": str(backup_path) if backup_path else None,
            "installed_files": installed,
            "verify_results": verify_results,
            "compile_results": compile_results,
        }

    def _load_manifest(self, archive: zipfile.ZipFile) -> UpdateManifest:
        names = {name.replace("\\", "/"): name for name in archive.namelist()}
        for manifest_name in MANIFEST_NAMES:
            if manifest_name in names:
                payload = json.loads(archive.read(names[manifest_name]).decode("utf-8-sig"))
                return UpdateManifest.from_dict(payload)
        raise ValueError("Package is missing claire_update_manifest.json.")

    def _plan(self, manifest: UpdateManifest) -> List[Dict[str, Any]]:
        plan = []
        for item in manifest.files:
            target = self.resolve_target(item.target)
            plan.append({
                "source": item.source,
                "target": target,
                "action": item.action,
                "type": item.file_type,
                "sha256": item.sha256,
                "exists": (self.project_root / target).exists(),
            })
        return plan

    def _install_files(self, archive: zipfile.ZipFile, manifest: UpdateManifest) -> List[Dict[str, Any]]:
        names = {name.replace("\\", "/"): name for name in archive.namelist()}
        installed: List[Dict[str, Any]] = []
        for item in manifest.files:
            target_rel = self.resolve_target(item.target)
            target = self.project_root / target_rel

            if item.action == "delete":
                if target.exists() and target.is_file():
                    target.unlink()
                installed.append({"target": target_rel, "action": "delete", "type": item.file_type, "sha256": ""})
                continue

            source = normalize_package_path(item.source)
            if source not in names:
                if item.required:
                    raise ValueError(f"Required source missing from package: {source}")
                continue
            if item.action == "create_if_missing" and target.exists():
                installed.append({"target": target_rel, "action": "skip_existing", "type": item.file_type, "sha256": ""})
                continue

            data = archive.read(names[source])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            installed.append({
                "target": target_rel,
                "source": source,
                "action": item.action,
                "type": item.file_type,
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        return installed

    def _verify_installed(self, installed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in installed:
            target = self.project_root / item["target"]
            if item["action"] == "delete":
                ok = not target.exists()
                results.append({"target": item["target"], "ok": ok, "check": "deleted"})
                continue
            if item["action"] == "skip_existing":
                results.append({"target": item["target"], "ok": True, "check": "skipped"})
                continue
            actual = self.sha256_file(target)
            ok = actual == item.get("sha256")
            results.append({"target": item["target"], "ok": ok, "check": "sha256", "actual": actual})
            if not ok:
                raise ValueError(f"Installed file failed SHA256 verification: {item['target']}")
        return results

    def _compile_python(self, installed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in installed:
            if item.get("type") != "python" or item.get("action") in {"delete", "skip_existing"}:
                continue
            target = self.project_root / item["target"]
            try:
                py_compile.compile(str(target), doraise=True)
                results.append({"target": item["target"], "ok": True})
            except Exception as exc:
                results.append({"target": item["target"], "ok": False, "error": str(exc)})
                raise
        return results

    def resolve_target(self, target: str) -> str:
        target = normalize_package_path(target)
        if not target.startswith("@"):
            return target
        head, _, tail = target.partition("/")
        if head not in self.TARGET_ALIASES:
            raise ValueError(f"Unknown update target alias: {head}")
        base = self.TARGET_ALIASES[head]
        return normalize_package_path(f"{base}/{tail}" if base and tail else (base or tail))

    def sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()


__all__ = ["PackageInstaller"]
