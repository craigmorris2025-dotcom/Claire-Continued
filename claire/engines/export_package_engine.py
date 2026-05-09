"""
Export Package Engine — shareable artifact generator for Claire.

v5.29:
- Converts a successful pipeline result into a structured export package.
- Produces markdown-ready artifact documents plus a compact JSON export.
- Keeps exports deterministic and in-memory so API/UI/file-writer layers can
  decide where to persist files.
"""

from typing import Any, Dict, List
from datetime import datetime, timezone
import json
import hashlib


class ExportPackageEngine:
    """Builds deterministic exportable artifact packages from Claire pipeline context."""

    def build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = context or {}
        scores = context.get("scores", {}) or {}
        data = context.get("data", {}) or {}

        package_profile = self._package_profile(context, data, scores)
        documents = self._documents(context, data, scores, package_profile)
        manifest = self._manifest(documents)
        quality_checks = self._quality_checks(context, data, scores, documents)
        export_readiness = self._export_readiness(package_profile, quality_checks, manifest)

        return {
            "status": "success",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "export_package_score": export_readiness,
            "package_profile": package_profile,
            "package_manifest": manifest,
            "documents": documents,
            "json_export": self._json_export(context, data, scores, package_profile),
            "quality_checks": quality_checks,
            "sharing_guidance": self._sharing_guidance(context, data, export_readiness),
            "recommended_next_actions": self._recommended_next_actions(export_readiness, quality_checks),
            "export_package_thesis": self._thesis(package_profile, export_readiness, manifest),
            "confidence": self._confidence(export_readiness, quality_checks),
        }

    # =========================
    # Profile / manifest
    # =========================
    def _package_profile(self, context: Dict[str, Any], data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        market_gap = data.get("market_gap", {}) or {}
        signal_extraction = data.get("signal_extraction", {}) or {}
        strategic_positioning = data.get("strategic_positioning", {}) or {}
        productization = data.get("productization_path", {}) or {}
        technical = data.get("technical_feasibility", {}) or {}
        lifecycle_summary = data.get("lifecycle_summary", {}) or {}
        binder = data.get("portfolio_binder", {}) or {}

        sector = (
            market_gap.get("sector")
            or signal_extraction.get("dominant_sector")
            or "general_intelligence"
        )
        category = self._nested_text(strategic_positioning, "category_positioning", "category_name")
        if not category:
            category = str(sector).replace("_", " ")

        return {
            "package_type": "claire_pipeline_export",
            "version": "v5.29",
            "domain": data.get("domain") or context.get("domain") or "general",
            "sector": sector,
            "category_name": category,
            "decision_classification": context.get("decision_classification", "UNKNOWN"),
            "breakthrough_classification": self._nested_text(data.get("breakthrough_synthesis", {}), "breakthrough_classification", "classification"),
            "technical_state": self._nested_text(technical, "feasibility_classification", "state"),
            "productization_state": self._nested_text(productization, "productization_classification", "state"),
            "lifecycle_active_count": lifecycle_summary.get("active_stage_count"),
            "lifecycle_partial_count": lifecycle_summary.get("partial_stage_count"),
            "lifecycle_pending_count": lifecycle_summary.get("pending_stage_count"),
            "binder_status": binder.get("status"),
            "portfolio_score": scores.get("portfolio_score", 0.0),
            "export_audience": self._export_audience(data),
        }

    def _manifest(self, documents: Dict[str, str]) -> List[Dict[str, Any]]:
        manifest = []
        for filename, content in documents.items():
            manifest.append({
                "filename": filename,
                "format": "markdown" if filename.endswith(".md") else "json",
                "title": self._title_from_filename(filename),
                "ready": bool(content and len(content.strip()) > 40),
                "character_count": len(content or ""),
                "sha256_12": hashlib.sha256((content or "").encode("utf-8")).hexdigest()[:12],
            })
        return manifest

    # =========================
    # Documents
    # =========================
    def _documents(
        self,
        context: Dict[str, Any],
        data: Dict[str, Any],
        scores: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> Dict[str, str]:
        return {
            "run_summary.md": self._run_summary(data, scores, profile),
            "portfolio_binder.md": self._portfolio_binder_doc(data, scores, profile),
            "technical_feasibility.md": self._engine_doc(
                "Technical Feasibility",
                data.get("technical_feasibility", {}),
                [
                    "technical_feasibility_score",
                    "feasibility_classification",
                    "architecture_readiness",
                    "implementation_complexity",
                    "integration_readiness",
                    "data_readiness",
                    "validation_burden",
                    "deployment_controls",
                    "technical_risks",
                    "blocker_burndown_plan",
                ],
            ),
            "productization_path.md": self._engine_doc(
                "Productization Path",
                data.get("productization_path", {}),
                [
                    "productization_score",
                    "productization_classification",
                    "pilot_strategy",
                    "packaging_strategy",
                    "productization_roadmap",
                    "evidence_gates",
                    "go_to_market_readiness",
                    "launch_controls",
                    "launch_risks",
                    "product_requirements",
                    "prototype_to_product_path",
                ],
            ),
            "strategic_positioning.md": self._engine_doc(
                "Strategic Positioning",
                data.get("strategic_positioning", {}),
                [
                    "strategic_positioning_score",
                    "positioning_classification",
                    "category_positioning",
                    "buyer_positioning",
                    "acquirer_positioning",
                    "competitive_positioning",
                    "risk_positioning",
                    "proof_stack",
                    "message_hierarchy",
                    "sales_enablement",
                    "strategic_roadmap",
                    "positioning_risks",
                ],
            ),
            "deal_exit_model.md": self._engine_doc(
                "Deal / Exit Modeling",
                data.get("deal_exit_modeling", {}),
                [
                    "exit_readiness",
                    "strategic_fit",
                    "acquirer_fit",
                    "valuation_logic",
                    "deal_risks",
                    "exit_path",
                    "recommended_next_actions",
                ],
            ),
            "opportunity_discovery.md": self._engine_doc(
                "Opportunity Discovery + Breakthrough",
                {
                    "opportunity_discovery": data.get("opportunity_discovery", {}),
                    "breakthrough_synthesis": data.get("breakthrough_synthesis", {}),
                },
                ["opportunity_discovery", "breakthrough_synthesis"],
            ),
            "full_pipeline_output.json": self._pretty_json(self._json_export(context, data, scores, profile)),
        }

    def _run_summary(self, data: Dict[str, Any], scores: Dict[str, Any], profile: Dict[str, Any]) -> str:
        lifecycle_summary = data.get("lifecycle_summary", {}) or {}
        market_gap = data.get("market_gap", {}) or {}
        signal = data.get("signal_extraction", {}) or {}
        knowledge = data.get("knowledge_ingestion", {}) or {}
        breakthrough = data.get("breakthrough_synthesis", {}) or {}
        productization = data.get("productization_path", {}) or {}
        strategic = data.get("strategic_positioning", {}) or {}

        return "\n".join([
            "# Claire Run Summary",
            "",
            f"**Package version:** {profile.get('version')}",
            f"**Domain:** {profile.get('domain')}",
            f"**Sector:** {profile.get('sector')}",
            f"**Category:** {profile.get('category_name')}",
            f"**Decision:** {profile.get('decision_classification')}",
            "",
            "## Lifecycle",
            "",
            f"- Implemented stages: {lifecycle_summary.get('implemented_stage_count')}",
            f"- Active stages: {lifecycle_summary.get('active_stage_count')}",
            f"- Partial stages: {lifecycle_summary.get('partial_stage_count')}",
            f"- Pending stages: {lifecycle_summary.get('pending_stage_count')}",
            "",
            "## Scores",
            "",
            self._score_lines(scores),
            "",
            "## Key Signals",
            "",
            f"- Knowledge quality: {self._nested(knowledge, 'knowledge_quality_score', 'score')} ({self._nested_text(knowledge, 'knowledge_quality_score', 'level')})",
            f"- Signal extraction route: {signal.get('dominant_sector')} with routing confidence {self._nested(signal, 'routing_evidence', 'routing_confidence_score')}",
            f"- Market gap sector: {market_gap.get('sector')}",
            f"- Breakthrough classification: {self._nested_text(breakthrough, 'breakthrough_classification', 'classification')}",
            f"- Productization state: {self._nested_text(productization, 'productization_classification', 'state')}",
            f"- Strategic posture: {self._nested_text(strategic, 'positioning_classification', 'narrative_posture')}",
            "",
            "## Executive Thesis",
            "",
            self._binder_summary(data),
        ])

    def _portfolio_binder_doc(self, data: Dict[str, Any], scores: Dict[str, Any], profile: Dict[str, Any]) -> str:
        binder = data.get("portfolio_binder", {}) or {}
        sections = binder.get("sections", []) if isinstance(binder, dict) else []

        lines = [
            "# Portfolio Binder Export",
            "",
            f"**Status:** {binder.get('status')}",
            f"**Sector:** {profile.get('sector')}",
            f"**Category:** {profile.get('category_name')}",
            "",
            "## Binder Summary",
            "",
            self._binder_summary(data),
            "",
            "## Sections",
            "",
        ]

        for section in sections:
            if not isinstance(section, dict):
                continue
            section_id = section.get("id") or "unknown"
            title = section.get("title") or self._title_from_filename(section_id)
            ready = section.get("ready")
            lines.extend([
                f"### {title}",
                "",
                f"- Section ID: `{section_id}`",
                f"- Ready: `{ready}`",
                "",
            ])
            content = section.get("content")
            if isinstance(content, dict):
                lines.append(self._short_json(content, 1200))
            elif content is not None:
                lines.append(str(content)[:1200])
            lines.append("")

        return "\n".join(lines)

    def _engine_doc(self, title: str, payload: Dict[str, Any], preferred_keys: List[str]) -> str:
        payload = payload or {}
        lines = [
            f"# {title}",
            "",
            f"**Status:** {payload.get('status', 'not_available')}",
            "",
        ]

        if not payload:
            lines.append("No payload available.")
            return "\n".join(lines)

        for key in preferred_keys:
            if key in payload:
                lines.extend([
                    f"## {self._pretty(key)}",
                    "",
                    self._short_json(payload.get(key), 1800),
                    "",
                ])

        remaining = [key for key in payload.keys() if key not in preferred_keys and key not in {"status", "evidence_signals"}]
        if remaining:
            lines.extend(["## Additional Fields", ""])
            for key in remaining[:12]:
                lines.extend([
                    f"### {self._pretty(key)}",
                    "",
                    self._short_json(payload.get(key), 900),
                    "",
                ])

        return "\n".join(lines)

    # =========================
    # JSON export / checks
    # =========================
    def _json_export(
        self,
        context: Dict[str, Any],
        data: Dict[str, Any],
        scores: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "package_profile": profile,
            "scores": scores,
            "domain": data.get("domain"),
            "keywords": data.get("keywords", []),
            "governed_signals": data.get("governed_signals", {}),
            "knowledge_ingestion": data.get("knowledge_ingestion", {}),
            "signal_extraction": data.get("signal_extraction", {}),
            "market_gap": data.get("market_gap", {}),
            "trend_discovery": data.get("trend_discovery", {}),
            "thesis_formation": data.get("thesis_formation", {}),
            "opportunity_discovery": data.get("opportunity_discovery", {}),
            "breakthrough_synthesis": data.get("breakthrough_synthesis", {}),
            "technical_feasibility": data.get("technical_feasibility", {}),
            "productization_path": data.get("productization_path", {}),
            "strategic_positioning": data.get("strategic_positioning", {}),
            "deal_exit_modeling": data.get("deal_exit_modeling", {}),
            "portfolio_binder": data.get("portfolio_binder", {}),
            "portfolio_optimization": data.get("portfolio_optimization", {}),
            "core_output": data.get("core_output", {}),
            "lifecycle_summary": data.get("lifecycle_summary", {}),
            "lifecycle_stages": data.get("lifecycle_stages", []),
            "acquirer_matches": context.get("acquirer_matches", []),
        }

    def _quality_checks(
        self,
        context: Dict[str, Any],
        data: Dict[str, Any],
        scores: Dict[str, Any],
        documents: Dict[str, str],
    ) -> Dict[str, Any]:
        lifecycle_summary = data.get("lifecycle_summary", {}) or {}
        binder = data.get("portfolio_binder", {}) or {}

        required_docs = [
            "run_summary.md",
            "portfolio_binder.md",
            "technical_feasibility.md",
            "productization_path.md",
            "strategic_positioning.md",
            "deal_exit_model.md",
            "full_pipeline_output.json",
        ]

        missing_docs = [name for name in required_docs if not documents.get(name)]
        weak_docs = [name for name, content in documents.items() if len((content or "").strip()) < 80]
        checks = {
            "lifecycle_complete": lifecycle_summary.get("implemented_stage_count") == 21
            and lifecycle_summary.get("active_stage_count") == 21
            and lifecycle_summary.get("partial_stage_count") == 0
            and lifecycle_summary.get("pending_stage_count") == 0,
            "binder_success": binder.get("status") == "success",
            "required_documents_present": not missing_docs,
            "documents_have_content": not weak_docs,
            "has_scores": bool(scores),
            "has_acquirer_matches": bool(context.get("acquirer_matches", [])),
            "missing_documents": missing_docs,
            "weak_documents": weak_docs,
        }
        checks["passed_count"] = len([value for key, value in checks.items() if isinstance(value, bool) and value])
        checks["failed_count"] = len([value for key, value in checks.items() if isinstance(value, bool) and not value])
        return checks

    def _export_readiness(
        self,
        profile: Dict[str, Any],
        quality_checks: Dict[str, Any],
        manifest: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        ready_docs = len([item for item in manifest if item.get("ready")])
        total_docs = max(1, len(manifest))

        score = self._bounded(
            0.12
            + (0.24 if quality_checks.get("lifecycle_complete") else 0.0)
            + (0.18 if quality_checks.get("binder_success") else 0.0)
            + (0.14 if quality_checks.get("required_documents_present") else 0.0)
            + (0.12 if quality_checks.get("documents_have_content") else 0.0)
            + (ready_docs / total_docs) * 0.16
            + min(0.10, float(profile.get("portfolio_score", 0.0) or 0.0) * 0.10)
        )
        level = "export_ready" if score >= 0.78 else "review_ready" if score >= 0.62 else "draft_ready" if score >= 0.46 else "not_ready"

        return {
            "level": level,
            "score": round(score, 4),
            "ready_document_count": ready_docs,
            "total_document_count": total_docs,
            "blocking_issues": self._blocking_issues(quality_checks),
        }

    # =========================
    # Guidance
    # =========================
    def _sharing_guidance(self, context: Dict[str, Any], data: Dict[str, Any], readiness: Dict[str, Any]) -> Dict[str, Any]:
        risk = data.get("risk_regulation", {}) or {}
        strategic = data.get("strategic_positioning", {}) or {}
        productization = data.get("productization_path", {}) or {}

        readiness_modifier = self._nested_text(strategic, "positioning_classification", "readiness_modifier")
        launch_posture = self._nested_text(productization, "productization_classification", "launch_posture")
        blocker_level = self._nested_text(risk, "blocker_assessment", "blocker_level")

        if readiness_modifier == "control_gated_positioning" or blocker_level == "conditional":
            audience_note = "Share as a controlled validation or advisory opportunity, not as unrestricted automation."
            redaction_note = "Review mission, security, privacy, or regulated-use details before external sharing."
        else:
            audience_note = "Share as a strategy, product, or investment-readiness package."
            redaction_note = "Review proprietary assumptions and customer-specific examples before external sharing."

        return {
            "audience_note": audience_note,
            "redaction_note": redaction_note,
            "launch_posture": launch_posture,
            "recommended_order": [
                "run_summary.md",
                "portfolio_binder.md",
                "strategic_positioning.md",
                "productization_path.md",
                "technical_feasibility.md",
                "deal_exit_model.md",
                "full_pipeline_output.json",
            ],
            "external_sharing_level": "controlled" if blocker_level == "conditional" else "standard_review",
        }

    def _recommended_next_actions(self, readiness: Dict[str, Any], quality_checks: Dict[str, Any]) -> List[Dict[str, str]]:
        actions = []
        if readiness.get("level") in {"not_ready", "draft_ready"}:
            actions.append({
                "action": "review export blockers",
                "purpose": "resolve missing documents, lifecycle gaps, or binder issues before sharing",
                "priority": "critical",
            })
        if not quality_checks.get("lifecycle_complete"):
            actions.append({
                "action": "rerun lifecycle regression tests",
                "purpose": "confirm all 21 lifecycle stages are active before package export",
                "priority": "critical",
            })
        if not quality_checks.get("binder_success"):
            actions.append({
                "action": "repair binder output",
                "purpose": "portfolio binder is the primary shareable artifact",
                "priority": "critical",
            })
        actions.append({
            "action": "write package documents to an exports folder",
            "purpose": "persist markdown and JSON artifacts for review or sharing",
            "priority": "medium",
        })
        actions.append({
            "action": "review redaction and sharing guidance",
            "purpose": "avoid leaking sensitive assumptions, source details, or controlled-use content",
            "priority": "high",
        })
        return actions

    def _thesis(self, profile: Dict[str, Any], readiness: Dict[str, Any], manifest: List[Dict[str, Any]]) -> str:
        return (
            f"Claire generated a {readiness.get('level')} export package for "
            f"{profile.get('category_name')} in {profile.get('sector')}. "
            f"The package contains {len(manifest)} artifact document(s), "
            f"{readiness.get('ready_document_count')} of which are ready for review."
        )

    # =========================
    # Utility helpers
    # =========================
    def _export_audience(self, data: Dict[str, Any]) -> List[str]:
        sector = (data.get("market_gap", {}) or {}).get("sector", "")
        if sector == "defense_autonomy":
            return ["internal strategy review", "controlled design partner", "secure program sponsor"]
        if sector == "climate_insurance":
            return ["underwriting leadership", "reinsurance partner", "insurance innovation team"]
        return ["strategy team", "innovation team", "corporate development", "design partner"]

    def _blocking_issues(self, checks: Dict[str, Any]) -> List[str]:
        issues = []
        if not checks.get("lifecycle_complete"):
            issues.append("lifecycle is not fully complete")
        if not checks.get("binder_success"):
            issues.append("portfolio binder did not succeed")
        if not checks.get("required_documents_present"):
            issues.append("required export documents are missing")
        if not checks.get("documents_have_content"):
            issues.append("one or more export documents are too thin")
        return issues or ["no blocking export issues surfaced"]

    def _binder_summary(self, data: Dict[str, Any]) -> str:
        binder = data.get("portfolio_binder", {}) or {}
        executive = ""
        for section in binder.get("sections", []) or []:
            if isinstance(section, dict) and section.get("id") == "executive_thesis":
                content = section.get("content")
                if isinstance(content, dict):
                    executive = content.get("summary", "")
                elif content:
                    executive = str(content)
        return executive or binder.get("executive_summary", "") or "No executive thesis available."

    def _score_lines(self, scores: Dict[str, Any]) -> str:
        keys = [
            "knowledge_quality_score",
            "signal_quality_score",
            "opportunity_score",
            "breakthrough_synthesis_score",
            "technical_feasibility_score",
            "productization_score",
            "strategic_positioning_score",
            "portfolio_score",
        ]
        lines = []
        for key in keys:
            if key in scores:
                lines.append(f"- {self._pretty(key)}: {scores.get(key)}")
        return "\n".join(lines) or "- No scores available."

    def _title_from_filename(self, filename: str) -> str:
        return self._pretty(filename.replace(".md", "").replace(".json", ""))

    def _pretty(self, value: Any) -> str:
        return str(value or "").replace("_", " ").replace("-", " ").title()

    def _pretty_json(self, value: Any) -> str:
        return json.dumps(value, indent=2, sort_keys=True, default=str)

    def _short_json(self, value: Any, limit: int = 1200) -> str:
        text = self._pretty_json(value)
        if len(text) <= limit:
            return "```json\n" + text + "\n```"
        return "```json\n" + text[:limit] + "\n... [truncated]\n```"

    def _nested(self, obj: Dict[str, Any], *path: str) -> Any:
        cur: Any = obj
        for part in path:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    def _nested_text(self, obj: Dict[str, Any], *path: str) -> str:
        value = self._nested(obj, *path)
        return str(value or "")

    def _bounded(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))

    def _confidence(self, readiness: Dict[str, Any], quality_checks: Dict[str, Any]) -> float:
        return round(self._bounded(
            0.20
            + readiness.get("score", 0.0) * 0.30
            + quality_checks.get("passed_count", 0) * 0.04
            - quality_checks.get("failed_count", 0) * 0.05
        ), 4)
