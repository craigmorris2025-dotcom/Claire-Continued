"""Acquisition-grade export sidecars for Claire runs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import hashlib
import json


class AcquisitionExportArtifactWriter:
    """Write buyer/acquirer-facing diligence artifacts beside standard exports."""

    def write(self, output_dir: str | Path, run_result: Dict[str, Any] | None = None, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        folder = Path(output_dir)
        run_result = run_result or {}
        payload = payload or {}
        if not folder.exists() or not folder.is_dir():
            return {"status": "skipped", "reason": "export output folder not available", "output_dir": str(output_dir)}

        context = self._context(run_result, payload)
        artifacts = {
            "acquisition_readiness_summary.md": self._readiness_markdown(context),
            "acquirer_discovery_summary.md": self._acquirer_markdown(context),
            "value_capture_summary.md": self._value_capture_markdown(context),
            "diligence_checklist.json": self._diligence_checklist(context),
        }

        written = []
        for filename, content in artifacts.items():
            path = folder / filename
            text = content if filename.endswith(".md") else json.dumps(content, indent=2, sort_keys=True, default=str)
            path.write_text(text, encoding="utf-8")
            written.append(self._file_record(path))

        self._augment_manifest(folder, written, context)
        return {
            "status": "success",
            "output_dir": str(folder),
            "written_file_count": len(written),
            "written_files": written,
            "acquisition_readiness": context["acquisition_readiness"],
        }

    def preview(self, run_result: Dict[str, Any] | None = None, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = self._context(run_result or {}, payload or {})
        return {
            "status": "success",
            "artifact_type": "acquisition_export_preview",
            "acquisition_readiness": context["acquisition_readiness"],
            "top_acquirers": context["top_acquirers"],
            "diligence_sections": [item["section"] for item in self._diligence_checklist(context)["checklist"]],
        }

    def _context(self, data: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        scores = data.get("scores") or {}
        strategic = data.get("strategic_positioning") or {}
        productization = data.get("productization_path") or {}
        business = data.get("business_model") or {}
        deal = data.get("deal_exit_modeling") or {}
        market_gap = data.get("market_gap") or {}
        acquirers = data.get("acquirer_matches") or []
        if not acquirers and isinstance(deal.get("acquirer_fit"), dict):
            acquirers = deal.get("acquirer_fit", {}).get("likely_acquirers") or []

        portfolio_score = float(scores.get("portfolio_score") or 0.0)
        export_score = float(scores.get("export_package_score") or 0.0)
        readiness_score = round(min(0.98, (portfolio_score * 0.52) + (export_score * 0.22) + (0.14 if acquirers else 0.0) + 0.10), 3)
        readiness = "acquisition_grade" if readiness_score >= 0.78 else "diligence_ready" if readiness_score >= 0.62 else "internal_review"

        return {
            "generated_at": self._now(),
            "execution_mode": payload.get("execution_mode") or data.get("mode"),
            "title": data.get("category_name") or market_gap.get("needed_solution") or payload.get("signal") or "Claire opportunity",
            "sector": market_gap.get("sector") or data.get("sector"),
            "decision": data.get("decision_classification"),
            "breakthrough": data.get("breakthrough_classification"),
            "portfolio_score": portfolio_score,
            "export_score": export_score,
            "acquisition_readiness": {"level": readiness, "score": readiness_score},
            "market_gap": market_gap.get("market_gap"),
            "needed_solution": market_gap.get("needed_solution"),
            "value_capture": business.get("value_capture") or {},
            "revenue_model": business.get("revenue_model") or {},
            "strategic_positioning": strategic.get("positioning_classification") or {},
            "category_positioning": strategic.get("category_positioning") or {},
            "productization": productization.get("productization_classification") or {},
            "deal_exit": deal,
            "top_acquirers": self._top_acquirers(acquirers),
        }

    def _readiness_markdown(self, context: Dict[str, Any]) -> str:
        return "\n".join([
            "# Acquisition Readiness Summary",
            "",
            f"**Generated:** {context['generated_at']}",
            f"**Readiness:** {context['acquisition_readiness']['level']} ({context['acquisition_readiness']['score']})",
            f"**Decision:** {context.get('decision')}",
            f"**Breakthrough:** {context.get('breakthrough')}",
            f"**Sector:** {context.get('sector')}",
            "",
            "## Opportunity",
            "",
            f"- Market gap: {context.get('market_gap')}",
            f"- Needed solution: {context.get('needed_solution')}",
            f"- Productization state: {context.get('productization', {}).get('state')}",
            f"- Strategic posture: {context.get('strategic_positioning', {}).get('narrative_posture')}",
            "",
            "## Diligence Posture",
            "",
            "Claire has assembled the core evidence chain for buyer review: lifecycle output, portfolio binder, productization path, strategic positioning, acquirer discovery, and deal/exit modeling.",
        ])

    def _acquirer_markdown(self, context: Dict[str, Any]) -> str:
        lines = ["# Acquirer Discovery Summary", "", f"**Generated:** {context['generated_at']}", ""]
        acquirers = context.get("top_acquirers") or []
        if not acquirers:
            lines.append("No acquirer matches were attached to this run.")
            return "\n".join(lines)
        for idx, item in enumerate(acquirers, 1):
            lines.append(f"{idx}. **{item.get('name')}**")
            if item.get("rationale"):
                lines.append(f"   - Rationale: {item.get('rationale')}")
            if item.get("fit_score") is not None:
                lines.append(f"   - Fit score: {item.get('fit_score')}")
        return "\n".join(lines)

    def _value_capture_markdown(self, context: Dict[str, Any]) -> str:
        value = context.get("value_capture") or {}
        revenue = context.get("revenue_model") or {}
        category = context.get("category_positioning") or {}
        return "\n".join([
            "# Value Capture Summary",
            "",
            f"**Generated:** {context['generated_at']}",
            f"**Revenue model:** {revenue.get('primary_model')}",
            f"**Value capture strength:** {value.get('strength')}",
            f"**Category:** {category.get('category_name')}",
            "",
            "## Buyer Value Logic",
            "",
            str(value.get("logic") or value.get("summary") or "Value-capture detail is available in the business model artifact."),
        ])

    def _diligence_checklist(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "generated_at": context["generated_at"],
            "artifact_type": "acquisition_diligence_checklist",
            "acquisition_readiness": context["acquisition_readiness"],
            "checklist": [
                {"section": "market_gap", "status": "available" if context.get("market_gap") else "needs_review"},
                {"section": "needed_solution", "status": "available" if context.get("needed_solution") else "needs_review"},
                {"section": "productization_path", "status": "available" if context.get("productization") else "needs_review"},
                {"section": "strategic_positioning", "status": "available" if context.get("strategic_positioning") else "needs_review"},
                {"section": "value_capture", "status": "available" if context.get("value_capture") else "needs_review"},
                {"section": "acquirer_discovery", "status": "available" if context.get("top_acquirers") else "needs_review"},
                {"section": "deal_exit_modeling", "status": "available" if context.get("deal_exit") else "needs_review"},
            ],
        }

    def _top_acquirers(self, acquirers: Any) -> List[Dict[str, Any]]:
        items = acquirers if isinstance(acquirers, list) else []
        out = []
        for item in items[:8]:
            if isinstance(item, str):
                out.append({"name": item})
            elif isinstance(item, dict):
                out.append({
                    "name": item.get("name") or item.get("acquirer") or item.get("company"),
                    "rationale": item.get("rationale") or item.get("reason") or item.get("strategic_rationale"),
                    "fit_score": item.get("fit_score") or item.get("score"),
                })
        return [item for item in out if item.get("name")]

    def _augment_manifest(self, folder: Path, written: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
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
        manifest["acquisition_artifacts"] = {
            "status": "available",
            "generated_at": self._now(),
            "readiness": context["acquisition_readiness"],
            "file_count": len(written),
            "files": [item.get("filename") for item in written],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")

    def _file_record(self, path: Path) -> Dict[str, Any]:
        return {
            "filename": path.name,
            "path": str(path),
            "relative_path": str(path.as_posix()),
            "format": "markdown" if path.suffix == ".md" else "json",
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


__all__ = ["AcquisitionExportArtifactWriter"]
