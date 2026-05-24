"""
Export Browser — local file browser for Claire export artifacts.

v5.34:
- Lists export runs from data/runs/run_history.json or exports/index.json.
- Reads export folders and export files safely.
- Provides data structures that can be used by API routes or an HTML UI.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import mimetypes

from runtime_core.runtime.run_history import RunHistory


class ExportBrowser:
    """Safe browser for exports/claire_run_* artifact folders."""

    def __init__(self, output_root: str = "exports") -> None:
        self.output_root = Path(output_root)
        self.history = RunHistory()

    def list_runs(self, limit: int = 50, rescan_if_empty: bool = True) -> Dict[str, Any]:
        runs = self.history.list_runs(limit=limit)
        if not runs and rescan_if_empty:
            self.history.rescan_exports(str(self.output_root))
            runs = self.history.list_runs(limit=limit)

        return {
            "status": "success",
            "run_count": len(runs),
            "runs": runs,
        }

    def get_run(self, run_id: str) -> Dict[str, Any]:
        run = self.history.get_run(run_id)
        if not run:
            self.history.rescan_exports(str(self.output_root))
            run = self.history.get_run(run_id)

        if not run:
            return {
                "status": "not_found",
                "run_id": run_id,
            }

        return {
            "status": "success",
            "run": run,
        }

    def list_files(self, run_id: str) -> Dict[str, Any]:
        run_payload = self.get_run(run_id)
        if run_payload.get("status") != "success":
            return run_payload

        run = run_payload["run"]
        folder = self._safe_run_folder(run.get("folder_name") or run_id)

        if not folder.exists():
            return {
                "status": "not_found",
                "run_id": run_id,
                "reason": f"export folder does not exist: {folder}",
            }

        files = []
        for path in sorted(folder.iterdir()):
            if not path.is_file():
                continue
            files.append(self._file_record(path))

        return {
            "status": "success",
            "run_id": run_id,
            "folder": str(folder),
            "file_count": len(files),
            "files": files,
        }

    def read_file(self, run_id: str, filename: str, max_chars: Optional[int] = None) -> Dict[str, Any]:
        run_payload = self.get_run(run_id)
        if run_payload.get("status") != "success":
            return run_payload

        folder = self._safe_run_folder(run_payload["run"].get("folder_name") or run_id)
        target = self._safe_file(folder, filename)

        if not target.exists() or not target.is_file():
            return {
                "status": "not_found",
                "run_id": run_id,
                "filename": filename,
            }

        text = target.read_text(encoding="utf-8", errors="replace")
        truncated = False
        if max_chars is not None and max_chars > 0 and len(text) > max_chars:
            text = text[:max_chars]
            truncated = True

        return {
            "status": "success",
            "run_id": run_id,
            "filename": target.name,
            "file": self._file_record(target),
            "content": text,
            "truncated": truncated,
        }

    def summary(self) -> Dict[str, Any]:
        runs_payload = self.list_runs(limit=100)
        runs = runs_payload.get("runs", [])

        sectors: Dict[str, int] = {}
        decisions: Dict[str, int] = {}
        for run in runs:
            sector = run.get("sector") or "unknown"
            decision = run.get("decision_classification") or "unknown"
            sectors[sector] = sectors.get(sector, 0) + 1
            decisions[decision] = decisions.get(decision, 0) + 1

        return {
            "status": "success",
            "run_count": len(runs),
            "sectors": sectors,
            "decisions": decisions,
            "latest_run": runs[0] if runs else None,
        }

    def _safe_run_folder(self, folder_name: str) -> Path:
        folder_name = Path(str(folder_name or "")).name
        if not folder_name.startswith("claire_run_"):
            raise ValueError(f"Invalid Claire export folder name: {folder_name}")
        return self.output_root / folder_name

    def _safe_file(self, folder: Path, filename: str) -> Path:
        safe_name = Path(str(filename or "")).name
        target = (folder / safe_name).resolve()
        folder_resolved = folder.resolve()
        if folder_resolved not in target.parents and target != folder_resolved:
            raise ValueError(f"Unsafe export file path: {filename}")
        return target

    def _file_record(self, path: Path) -> Dict[str, Any]:
        mime, _ = mimetypes.guess_type(str(path))
        return {
            "filename": path.name,
            "path": str(path),
            "format": self._format(path),
            "mime_type": mime or "text/plain",
            "size_bytes": path.stat().st_size,
        }

    def _format(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".md":
            return "markdown"
        if suffix == ".json":
            return "json"
        if suffix in {".txt", ".log"}:
            return "text"
        return suffix.lstrip(".") or "file"
