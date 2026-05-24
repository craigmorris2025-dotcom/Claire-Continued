"""
Export Writer — filesystem persistence for Claire export packages.

v5.33:
- Writes export_package.documents to an exports/<run_folder>/ directory.
- Produces a writer manifest with filenames, paths, sizes, and hashes.
- Keeps the export package engine responsible for content generation while this
  writer handles safe deterministic persistence.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re

from runtime_core.runtime.run_history import RunHistory


class ExportWriter:
    """Persist Claire export-package documents to disk."""

    def write(
        self,
        export_package: Dict[str, Any],
        output_root: str = "exports",
        run_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        export_package = export_package or {}
        context = context or {}

        if export_package.get("status") != "success":
            return {
                "status": "skipped",
                "reason": "export_package was not successful",
                "export_package_status": export_package.get("status"),
            }

        documents = export_package.get("documents") or {}
        if not isinstance(documents, dict) or not documents:
            return {
                "status": "skipped",
                "reason": "export_package.documents was empty",
            }

        package_profile = export_package.get("package_profile") or {}
        folder_name = self._folder_name(run_id, package_profile)
        output_dir = Path(output_root) / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        written_files: List[Dict[str, Any]] = []
        for filename, content in documents.items():
            safe_name = self._safe_filename(filename)
            target = output_dir / safe_name

            if isinstance(content, (dict, list)):
                text = json.dumps(content, indent=2, sort_keys=True, default=str)
            else:
                text = str(content or "")

            target.write_text(text, encoding="utf-8")
            written_files.append({
                "filename": safe_name,
                "path": str(target),
                "relative_path": str(target.as_posix()),
                "format": "json" if safe_name.endswith(".json") else "markdown" if safe_name.endswith(".md") else "text",
                "size_bytes": target.stat().st_size,
                "sha256": self._sha256_file(target),
            })

        writer_manifest = self._writer_manifest(
            export_package=export_package,
            package_profile=package_profile,
            output_dir=output_dir,
            written_files=written_files,
            context=context,
        )

        manifest_path = output_dir / "export_writer_manifest.json"
        manifest_path.write_text(json.dumps(writer_manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")

        written_files.append({
            "filename": "export_writer_manifest.json",
            "path": str(manifest_path),
            "relative_path": str(manifest_path.as_posix()),
            "format": "json",
            "size_bytes": manifest_path.stat().st_size,
            "sha256": self._sha256_file(manifest_path),
        })

        index_path = output_dir / "README.md"
        index_text = self._index_markdown(package_profile, written_files)
        index_path.write_text(index_text, encoding="utf-8")

        written_files.append({
            "filename": "README.md",
            "path": str(index_path),
            "relative_path": str(index_path.as_posix()),
            "format": "markdown",
            "size_bytes": index_path.stat().st_size,
            "sha256": self._sha256_file(index_path),
        })

        history_record = self._register_history(
            export_writer_result={
                "status": "success",
                "output_dir": str(output_dir),
                "folder_name": folder_name,
                "document_count": len(documents),
                "written_file_count": len(written_files),
                "written_files": written_files,
                "manifest_path": str(manifest_path),
                "index_path": str(index_path),
            },
            export_package=export_package,
            context=context,
        )

        return {
            "status": "success",
            "output_dir": str(output_dir),
            "folder_name": folder_name,
            "document_count": len(documents),
            "written_file_count": len(written_files),
            "written_files": written_files,
            "manifest_path": str(manifest_path),
            "index_path": str(index_path),
            "history_record": history_record,
            "export_writer_score": {
                "level": "written",
                "score": 0.96 if len(written_files) >= len(documents) else 0.70,
                "documents_written": len(documents),
                "files_written": len(written_files),
            },
            "recommended_next_actions": [
                {
                    "action": "review generated export folder",
                    "purpose": "inspect shareable markdown and JSON artifacts before sending externally",
                    "priority": "high",
                },
                {
                    "action": "commit or archive export artifacts selectively",
                    "purpose": "preserve useful outputs without accidentally committing sensitive run data",
                    "priority": "medium",
                },
            ],
            "export_writer_thesis": (
                f"Export writer persisted {len(documents)} export document(s) to {output_dir}."
            ),
            "confidence": 0.92,
        }


    def _register_history(
        self,
        export_writer_result: Dict[str, Any],
        export_package: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            return RunHistory().register_export(
                export_writer_result=export_writer_result,
                export_package=export_package,
                context=context,
            )
        except Exception as exc:
            return {
                "status": "history_failed",
                "error": str(exc),
            }

    def _writer_manifest(
        self,
        export_package: Dict[str, Any],
        package_profile: Dict[str, Any],
        output_dir: Path,
        written_files: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_dir": str(output_dir),
            "package_profile": package_profile,
            "export_package_score": export_package.get("export_package_score"),
            "quality_checks": export_package.get("quality_checks"),
            "sharing_guidance": export_package.get("sharing_guidance"),
            "files": written_files,
            "context": {
                "decision_classification": context.get("decision_classification"),
                "breakthrough_classification": context.get("breakthrough_classification"),
                "domain": context.get("domain"),
                "sector": package_profile.get("sector"),
                "category_name": package_profile.get("category_name"),
            },
        }

    def _index_markdown(self, package_profile: Dict[str, Any], written_files: List[Dict[str, Any]]) -> str:
        lines = [
            "# Claire Export Folder",
            "",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Domain:** {package_profile.get('domain')}",
            f"**Sector:** {package_profile.get('sector')}",
            f"**Category:** {package_profile.get('category_name')}",
            f"**Decision:** {package_profile.get('decision_classification')}",
            "",
            "## Files",
            "",
        ]

        for item in written_files:
            lines.append(f"- `{item.get('filename')}` — {item.get('size_bytes')} bytes")

        lines.extend([
            "",
            "## Suggested review order",
            "",
            "1. `run_summary.md`",
            "2. `portfolio_binder.md`",
            "3. `strategic_positioning.md`",
            "4. `productization_path.md`",
            "5. `technical_feasibility.md`",
            "6. `deal_exit_model.md`",
            "7. `opportunity_discovery.md`",
            "8. `full_pipeline_output.json`",
            "",
        ])

        return "\n".join(lines)

    def _folder_name(self, run_id: Optional[str], package_profile: Dict[str, Any]) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        sector = self._slug(package_profile.get("sector") or "general")
        category = self._slug(package_profile.get("category_name") or "")
        run = self._slug(run_id or "")

        parts = ["claire_run", timestamp]
        if sector:
            parts.append(sector)
        if category and category != sector:
            parts.append(category)
        if run and run != "unknown":
            parts.append(run)

        return "_".join([p for p in parts if p])[:180]

    def _safe_filename(self, filename: str) -> str:
        filename = str(filename or "artifact.txt").replace("\\", "/").split("/")[-1]
        filename = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
        return filename or "artifact.txt"

    def _slug(self, value: Any) -> str:
        text = str(value or "").lower().strip()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        return text.strip("_")

    def _sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
