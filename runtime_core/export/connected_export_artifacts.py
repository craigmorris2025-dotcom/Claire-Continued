"""
Connected / hybrid export artifacts.

v5.51:
- Writes provenance sidecars for connected and hybrid dashboard runs.
- Keeps deterministic export-package generation intact while making connected
  context reviewable in the export folder.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import hashlib
import json


class ConnectedExportArtifactWriter:
    """Write connected/hybrid provenance artifacts into an existing export folder."""

    def write(
        self,
        output_dir: str | Path,
        payload: Dict[str, Any] | None = None,
        normalized_signals: List[Dict[str, Any]] | None = None,
        run_result: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        payload = payload or {}
        normalized_signals = normalized_signals or []
        run_result = run_result or {}
        folder = Path(output_dir)
        if not folder.exists() or not folder.is_dir():
            return {
                "status": "skipped",
                "reason": "export output folder not available",
                "output_dir": str(output_dir),
            }

        connected_enrichment = payload.get("connected_enrichment") or {}
        hybrid_fusion = payload.get("hybrid_fusion") or {}
        should_write = bool(connected_enrichment or hybrid_fusion or normalized_signals)
        if not should_write:
            return {
                "status": "skipped",
                "reason": "no connected or hybrid context was attached to this run",
                "output_dir": str(folder),
            }

        artifacts = {
            "source_manifest.json": self.source_manifest(payload, normalized_signals),
            "normalized_signals.json": {
                "status": "success",
                "generated_at": self._now(),
                "signal_count": len(normalized_signals),
                "signals": normalized_signals,
            },
            "connected_context.json": self.connected_context(payload, run_result),
            "hybrid_fusion_summary.md": self.hybrid_markdown(payload),
            "governance_connected_summary.md": self.governance_markdown(payload),
        }

        written = []
        for filename, content in artifacts.items():
            path = folder / filename
            text = self._serialize(content, markdown=filename.endswith(".md"))
            path.write_text(text, encoding="utf-8")
            written.append(self._file_record(path))

        self._augment_manifest(folder, written)
        return {
            "status": "success",
            "output_dir": str(folder),
            "written_file_count": len(written),
            "written_files": written,
        }

    def source_manifest(self, payload: Dict[str, Any], normalized_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        sources = []
        for signal in normalized_signals:
            source_url = signal.get("source_url") or (signal.get("metadata") or {}).get("raw_signal", {}).get("source_url")
            sources.append({
                "signal_id": signal.get("signal_id"),
                "raw_signal_id": signal.get("raw_signal_id"),
                "source_url": source_url,
                "source_category": signal.get("source_category"),
                "market_universe": signal.get("market_universe"),
                "industry_domain": signal.get("industry_domain"),
                "governance_status": signal.get("governance_status"),
                "signal_type": signal.get("signal_type"),
                "opportunity_relevance": signal.get("opportunity_relevance"),
                "signal_strength": signal.get("signal_strength"),
                "safe_to_enrich": signal.get("safe_to_enrich"),
            })
        return {
            "status": "success",
            "generated_at": self._now(),
            "artifact_type": "connected_source_manifest",
            "execution_mode": payload.get("execution_mode"),
            "market_universe": payload.get("market_universe"),
            "industry_domain": payload.get("industry_domain"),
            "source_count": len(sources),
            "sources": sources,
        }

    def connected_context(self, payload: Dict[str, Any], run_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "generated_at": self._now(),
            "artifact_type": "connected_context",
            "workflow": payload.get("workflow"),
            "execution_mode": payload.get("execution_mode"),
            "market_universe": payload.get("market_universe"),
            "industry_domain": payload.get("industry_domain"),
            "buyer_segment": payload.get("buyer_segment"),
            "objective": payload.get("objective"),
            "connected_enrichment": payload.get("connected_enrichment") or {},
            "hybrid_fusion": payload.get("hybrid_fusion") or {},
            "run_result": {
                "decision_classification": run_result.get("decision_classification"),
                "breakthrough_classification": run_result.get("breakthrough_classification"),
                "scores": run_result.get("scores"),
            },
        }

    def hybrid_markdown(self, payload: Dict[str, Any]) -> str:
        fusion = payload.get("hybrid_fusion") or {}
        enrichment = payload.get("connected_enrichment") or {}
        lines = [
            "# Hybrid Fusion Summary",
            "",
            f"**Generated:** {self._now()}",
            f"**Execution mode:** {payload.get('execution_mode')}",
            f"**Fusion status:** {fusion.get('status', 'not_available')}",
            f"**Hybrid readiness:** {fusion.get('hybrid_readiness', 'not_available')}",
            f"**Recommended mode:** {fusion.get('recommended_mode', 'not_available')}",
            f"**Hybrid score:** {fusion.get('hybrid_score', 'not_available')}",
            f"**Deterministic score:** {fusion.get('deterministic_score', 'not_available')}",
            f"**Connected score:** {fusion.get('connected_score', 'not_available')}",
            "",
            "## Fusion Thesis",
            "",
            fusion.get("fusion_summary") or "No hybrid fusion summary was attached.",
            "",
            "## Connected Enrichment",
            "",
            enrichment.get("connected_thesis") or "No connected enrichment thesis was attached.",
            "",
            "## Recommended Actions",
            "",
        ]
        for action in fusion.get("recommended_actions", []) or []:
            lines.append(f"- **{action.get('priority', 'medium')}**: {action.get('action')} — {action.get('purpose')}")
        return "\n".join(lines)

    def governance_markdown(self, payload: Dict[str, Any]) -> str:
        enrichment = payload.get("connected_enrichment") or {}
        fusion = payload.get("hybrid_fusion") or {}
        return "\n".join([
            "# Governance / Connected Summary",
            "",
            f"**Generated:** {self._now()}",
            f"**Execution mode:** {payload.get('execution_mode')}",
            f"**Market universe:** {payload.get('market_universe')}",
            f"**Industry / domain:** {payload.get('industry_domain')}",
            f"**Connected safe to enrich:** {enrichment.get('safe_to_enrich', False)}",
            f"**Fusion governance state:** {fusion.get('governance_state', 'not_available')}",
            "",
            "Connected and hybrid context is treated as public-market evidence only. Deterministic reasoning remains separate and governed.",
        ])

    def _augment_manifest(self, folder: Path, written: List[Dict[str, Any]]) -> None:
        manifest_path = folder / "export_writer_manifest.json"
        if not manifest_path.exists():
            return
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return
        files = manifest.get("files") or []
        existing = {item.get("filename") for item in files if isinstance(item, dict)}
        for item in written:
            if item.get("filename") not in existing:
                files.append(item)
        manifest["files"] = files
        manifest["connected_hybrid_artifacts"] = {
            "status": "available",
            "generated_at": self._now(),
            "file_count": len(written),
            "files": [item.get("filename") for item in written],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")

    def _serialize(self, content: Any, markdown: bool = False) -> str:
        if markdown:
            return str(content or "")
        return json.dumps(content, indent=2, sort_keys=True, default=str)

    def _file_record(self, path: Path) -> Dict[str, Any]:
        return {
            "filename": path.name,
            "path": str(path),
            "relative_path": str(path.as_posix()),
            "format": "markdown" if path.suffix == ".md" else "json" if path.suffix == ".json" else "text",
            "size_bytes": path.stat().st_size,
            "sha256": self._sha256_file(path),
        }

    def _sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


__all__ = ["ConnectedExportArtifactWriter"]
