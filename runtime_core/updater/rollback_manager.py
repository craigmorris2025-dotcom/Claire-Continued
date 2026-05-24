"""
Claire rollback manager.

v5.48 bootstrap:
- Creates zip backups before update install.
- Restores backed up files and removes files created by an update.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import json
import zipfile


class RollbackManager:
    """Backup and rollback update changes."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.backup_dir = project_root / "data" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, files: List[Dict[str, Any]], update_name: str) -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"claire_web_update_backup_{stamp}_{self._safe_name(update_name)}.zip"
        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "update_name": update_name,
            "files": [],
        }
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in files:
                rel = item["target"]
                target = self.project_root / rel
                entry = {"target": rel, "existed_before_update": target.exists(), "backup_member": None}
                if target.exists() and target.is_file():
                    member = "files/" + rel.replace("\\", "/")
                    archive.write(target, member)
                    entry["backup_member"] = member
                manifest["files"].append(entry)
            archive.writestr("rollback_manifest.json", json.dumps(manifest, indent=2))
        return backup_path

    def restore(self, backup_path: Path) -> Dict[str, Any]:
        restored: List[str] = []
        removed: List[str] = []
        with zipfile.ZipFile(backup_path, "r") as archive:
            manifest = json.loads(archive.read("rollback_manifest.json").decode("utf-8"))
            for item in manifest.get("files", []):
                target = self.project_root / item["target"]
                if item.get("existed_before_update"):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(item["backup_member"]))
                    restored.append(item["target"])
                elif target.exists() and target.is_file():
                    target.unlink()
                    removed.append(item["target"])
        return {"status": "success", "backup_path": str(backup_path), "restored": restored, "removed": removed}

    def list_backups(self, limit: int = 20) -> Dict[str, Any]:
        backups = []
        for path in sorted(self.backup_dir.glob("claire_web_update_backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            backups.append({
                "filename": path.name,
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                "valid": self.validate_backup(path).get("valid", False),
            })
        return {"status": "success", "backup_count": len(backups), "backups": backups}

    def validate_backup(self, backup_path: Path) -> Dict[str, Any]:
        try:
            with zipfile.ZipFile(backup_path, "r") as archive:
                bad_member = archive.testzip()
                if bad_member:
                    return {"status": "failed", "valid": False, "backup_path": str(backup_path), "error": f"bad member: {bad_member}"}
                if "rollback_manifest.json" not in archive.namelist():
                    return {"status": "failed", "valid": False, "backup_path": str(backup_path), "error": "missing rollback_manifest.json"}
                manifest = json.loads(archive.read("rollback_manifest.json").decode("utf-8"))
            return {
                "status": "success",
                "valid": True,
                "backup_path": str(backup_path),
                "update_name": manifest.get("update_name"),
                "file_count": len(manifest.get("files", [])),
                "created_at": manifest.get("created_at"),
            }
        except Exception as exc:
            return {"status": "failed", "valid": False, "backup_path": str(backup_path), "error": str(exc)}

    def _safe_name(self, name: str) -> str:
        return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in (name or "update"))[:80]


__all__ = ["RollbackManager"]
