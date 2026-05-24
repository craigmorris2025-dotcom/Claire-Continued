"""Updater health and readiness checks for Claire."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

from runtime_core.updater.rollback_manager import RollbackManager


class UpdaterHealth:
    """Summarize updater readiness, sources, rollback state, and validation path."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def status(self) -> Dict[str, Any]:
        source_path = self.project_root / "data" / "update_sources" / "allowed_sources.json"
        backup_dir = self.project_root / "data" / "backups"
        downloads_dir = self.project_root / "data" / "update_downloads"
        logs_dir = self.project_root / "data" / "update_logs"
        allowed_sources = self._load_sources(source_path)
        backups = RollbackManager(self.project_root).list_backups(limit=5)
        checks = {
            "allowed_sources_file": source_path.exists(),
            "backup_dir": backup_dir.exists(),
            "downloads_dir": downloads_dir.exists(),
            "logs_dir": logs_dir.exists(),
            "rollback_backups_valid": all(item.get("valid") for item in backups.get("backups", [])),
        }
        return {
            "status": "success" if all(checks.values()) else "partial",
            "updater": "web_download_updater_bootstrap",
            "readiness": "self_update_ready" if all(checks.values()) else "needs_attention",
            "checks": checks,
            "allowed_sources": allowed_sources,
            "recent_rollbacks": backups,
            "recommended_command": "python tools\\claire_update_from_url.py --url <approved_package_url> --dry-run",
        }

    def _load_sources(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {"status": "missing", "sources": []}
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            payload.setdefault("status", "success")
            return payload
        except Exception as exc:
            return {"status": "failed", "error": str(exc), "sources": []}


__all__ = ["UpdaterHealth"]
