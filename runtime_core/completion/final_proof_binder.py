"""
Assembles the final proof binder for v10 completion
===================================================
ACS2-Claire / Syntalion - 10.3.9-10.4.4

Module: src.claire.completion.final_proof_binder

Spec: Class FinalProofBinder. Methods: assemble_binder(scorecard, closure, maturity, market, production) -> ProofBinder, attach_evidence(binder, evidence) -> ProofBinder, validate_binder(binder) -> BinderValidation, generate_executive_summary(binder) -> str, export_binder(binder, format) -> Path, sign_binder(binder, authority) -> SignedBinder. Writes to data/completion/final_binders/. ProofBinder is the canonical completion artifact. Formats: JSON, PDF-ready Markdown, HTML.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

from runtime_core.proof.verified_output_proof import (
    build_verified_output_proof_binder,
    persist_verified_output_proof_binder,
)

logger = logging.getLogger(__name__)


class FinalProofBinder:
    """
    Assembles the final proof binder for v10 completion
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def assemble_binder(self, *args, **kwargs):
        """Assemble the verified output proof binder.

        Supports the historical loose signature while accepting the current
        proof-phase inputs as keyword arguments:
        run_spine, portfolio_payload, and project_root.
        """
        run_spine = kwargs.get("run_spine")
        portfolio_payload = kwargs.get("portfolio_payload")
        project_root = kwargs.get("project_root")
        if run_spine is None and args and isinstance(args[0], dict):
            run_spine = args[0]
        if portfolio_payload is None and len(args) > 1 and isinstance(args[1], dict):
            portfolio_payload = args[1]
        if not isinstance(run_spine, dict):
            raise ValueError("FinalProofBinder.assemble_binder requires a run_spine dictionary")
        return build_verified_output_proof_binder(run_spine, portfolio_payload, project_root)

    def attach_evidence(self, binder: dict[str, Any], evidence: Any) -> dict[str, Any]:
        binder = dict(binder)
        attached = list(binder.get("attached_evidence", [])) if isinstance(binder.get("attached_evidence"), list) else []
        attached.append(evidence)
        binder["attached_evidence"] = attached
        binder["evidence_attached_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return binder

    def validate_binder(self, binder: dict[str, Any]) -> dict[str, Any]:
        checks = {
            "binder_schema_present": binder.get("schema_version") == "claire.verified_output_proof_binder.v1",
            "lifecycle_section_present": isinstance(binder.get("lifecycle_generation"), dict),
            "portfolio_section_present": isinstance(binder.get("portfolio_route_proof"), dict),
            "technology_section_present": isinstance(binder.get("technology_route_proof"), dict),
            "completion_percent_present": isinstance(binder.get("completion_percent"), (int, float)),
        }
        return {
            "schema_version": "claire.final_proof_binder_validation.v1",
            "status": "valid" if all(checks.values()) else "invalid",
            "checks": checks,
        }

    def generate_executive_summary(self, binder: dict[str, Any]) -> str:
        portfolio = binder.get("portfolio_route_proof", {}) if isinstance(binder.get("portfolio_route_proof"), dict) else {}
        technology = binder.get("technology_route_proof", {}) if isinstance(binder.get("technology_route_proof"), dict) else {}
        return (
            f"Claire verified output proof status: {binder.get('status')} "
            f"({binder.get('completion_percent')}%). Portfolio proof is {portfolio.get('status')}; "
            f"technology/design proof is {technology.get('status')}."
        )

    def export_binder(self, binder: dict[str, Any], format: str = "json", project_root: Path | str | None = None) -> Path:
        if format not in {"json", "markdown", "md"}:
            raise ValueError("FinalProofBinder.export_binder supports json and markdown")
        root = Path(project_root) if project_root is not None else Path.cwd()
        run_id = str(binder.get("run_id") or "unknown_run")
        out_dir = root / "data" / "completion" / "final_binders" / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        if format == "json":
            path = out_dir / "verified_output_proof_binder.json"
            path.write_text(json.dumps(binder, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
            return path
        path = out_dir / "verified_output_proof_binder.md"
        path.write_text(self.generate_executive_summary(binder) + "\n", encoding="utf-8")
        return path

    def sign_binder(self, binder: dict[str, Any], authority: str) -> dict[str, Any]:
        signed = dict(binder)
        signed["signature"] = {
            "authority": authority,
            "signed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "runtime_truth_write": "blocked",
            "operator_review_required": True,
        }
        return signed

    def assemble_and_persist(
        self,
        run_spine: dict[str, Any],
        portfolio_payload: dict[str, Any] | None = None,
        project_root: Path | str | None = None,
    ) -> dict[str, Any]:
        return persist_verified_output_proof_binder(run_spine, portfolio_payload, project_root)
