"""
Run History — persistent index for Claire export runs.

v5.34:
- Maintains data/runs/run_history.json as the durable run-history ledger.
- Maintains exports/index.json as a browser-friendly export index.
- Registers export_writer outputs after each pipeline run.
- Can rescan existing exports/claire_run_* folders to rebuild indexes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


class RunHistory:
    """Small JSON-backed run-history store for local Claire runs."""

    def __init__(
        self,
        history_path: str = "data/runs/run_history.json",
        export_index_path: str = "exports/index.json",
    ) -> None:
        self.history_path = Path(history_path)
        self.export_index_path = Path(export_index_path)

    def register_export(
        self,
        export_writer_result: Dict[str, Any],
        export_package: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a completed export writer result in both history indexes."""
        export_writer_result = export_writer_result or {}
        export_package = export_package or {}
        context = context or {}

        if export_writer_result.get("status") != "success":
            return {
                "status": "skipped",
                "reason": "export_writer_result was not successful",
                "export_writer_status": export_writer_result.get("status"),
            }

        folder_name = export_writer_result.get("folder_name") or Path(export_writer_result.get("output_dir", "")).name
        output_dir = export_writer_result.get("output_dir") or str(Path("exports") / folder_name)
        package_profile = export_package.get("package_profile", {}) if isinstance(export_package, dict) else {}
        export_score = export_package.get("export_package_score", {}) if isinstance(export_package, dict) else {}

        record = {
            "run_id": folder_name,
            "folder_name": folder_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": output_dir,
            "status": "success",
            "domain": package_profile.get("domain") or context.get("domain"),
            "sector": package_profile.get("sector") or context.get("sector"),
            "category_name": package_profile.get("category_name"),
            "decision_classification": package_profile.get("decision_classification") or context.get("decision_classification"),
            "breakthrough_classification": package_profile.get("breakthrough_classification") or context.get("breakthrough_classification"),
            "portfolio_score": package_profile.get("portfolio_score"),
            "export_package_level": export_score.get("level"),
            "export_package_score": export_score.get("score"),
            "document_count": export_writer_result.get("document_count"),
            "written_file_count": export_writer_result.get("written_file_count"),
            "manifest_path": export_writer_result.get("manifest_path"),
            "index_path": export_writer_result.get("index_path"),
            "files": self._compact_files(export_writer_result.get("written_files", [])),
            "fingerprint": self._fingerprint(folder_name, output_dir, export_writer_result.get("written_files", [])),
        }

        history = self._read_index(self.history_path)
        history = self._upsert(history, record)

        export_index = self._read_index(self.export_index_path)
        export_index = self._upsert(export_index, record)

        self._write_index(self.history_path, history)
        self._write_index(self.export_index_path, export_index)

        return {
            "status": "success",
            "run_id": record["run_id"],
            "folder_name": record["folder_name"],
            "history_path": str(self.history_path),
            "export_index_path": str(self.export_index_path),
            "record": record,
        }

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return known runs, newest first."""
        history = self._read_index(self.history_path)
        runs = history.get("runs", [])
        return sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True)[:limit]

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        for run in self.list_runs(limit=10000):
            if run.get("run_id") == run_id or run.get("folder_name") == run_id:
                return run
        return None

    def rescan_exports(self, output_root: str = "exports") -> Dict[str, Any]:
        """Rebuild run history by scanning export folders on disk."""
        root = Path(output_root)
        records: List[Dict[str, Any]] = []

        if not root.exists():
            return {
                "status": "skipped",
                "reason": f"{output_root} does not exist",
                "run_count": 0,
            }

        for folder in sorted(root.glob("claire_run_*")):
            if not folder.is_dir():
                continue
            manifest_path = folder / "export_writer_manifest.json"
            if not manifest_path.exists():
                continue

            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            package_profile = manifest.get("package_profile", {}) or {}
            files = manifest.get("files", []) or []

            record = {
                "run_id": folder.name,
                "folder_name": folder.name,
                "created_at": manifest.get("generated_at") or datetime.fromtimestamp(folder.stat().st_mtime, timezone.utc).isoformat(),
                "output_dir": str(folder),
                "status": "success",
                "domain": package_profile.get("domain"),
                "sector": package_profile.get("sector"),
                "category_name": package_profile.get("category_name"),
                "decision_classification": package_profile.get("decision_classification"),
                "breakthrough_classification": package_profile.get("breakthrough_classification"),
                "portfolio_score": package_profile.get("portfolio_score"),
                "export_package_level": (manifest.get("export_package_score") or {}).get("level"),
                "export_package_score": (manifest.get("export_package_score") or {}).get("score"),
                "document_count": len([f for f in files if f.get("filename") not in {"README.md", "export_writer_manifest.json"}]),
                "written_file_count": len(files),
                "manifest_path": str(manifest_path),
                "index_path": str(folder / "README.md"),
                "files": self._compact_files(files),
                "fingerprint": self._fingerprint(folder.name, str(folder), files),
            }
            records.append(record)

        payload = {
            "status": "success",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "run_count": len(records),
            "runs": sorted(records, key=lambda item: item.get("created_at", ""), reverse=True),
        }

        self._write_index(self.history_path, payload)
        self._write_index(self.export_index_path, payload)

        return {
            "status": "success",
            "run_count": len(records),
            "history_path": str(self.history_path),
            "export_index_path": str(self.export_index_path),
        }

    def _read_index(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {
                "status": "success",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "run_count": 0,
                "runs": [],
            }

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "status": "recovering",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "run_count": 0,
                "runs": [],
            }

        if "runs" not in payload or not isinstance(payload["runs"], list):
            payload["runs"] = []
        return payload

    def _write_index(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        payload["run_count"] = len(payload.get("runs", []))
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    def _upsert(self, index: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        runs = index.get("runs", [])
        filtered = [
            run for run in runs
            if run.get("run_id") != record.get("run_id")
            and run.get("folder_name") != record.get("folder_name")
        ]
        filtered.insert(0, record)
        index["runs"] = sorted(filtered, key=lambda item: item.get("created_at", ""), reverse=True)
        return index

    def _compact_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compact = []
        for item in files or []:
            if not isinstance(item, dict):
                continue
            compact.append({
                "filename": item.get("filename"),
                "path": item.get("path"),
                "relative_path": item.get("relative_path"),
                "format": item.get("format"),
                "size_bytes": item.get("size_bytes"),
                "sha256": item.get("sha256"),
            })
        return compact

    def _fingerprint(self, folder_name: str, output_dir: str, files: List[Dict[str, Any]]) -> str:
        source = json.dumps({
            "folder_name": folder_name,
            "output_dir": output_dir,
            "files": self._compact_files(files),
        }, sort_keys=True, default=str)
        return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
