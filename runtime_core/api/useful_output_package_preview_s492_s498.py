from __future__ import annotations

"""
Claire Useful Output Package Preview — S492-S498

This module converts Claire's governed answer, evidence, knowledge, domain-route,
and innovation-escalation outputs into first-generation useful package previews.

It builds on:
- S450-S456 Claire Intelligence Answer Contract
- S457-S463 Claire Command Response Cards
- S464-S470 Evidence-Backed Answer Model
- S471-S477 Claire Knowledge Base Registry
- S478-S484 Market / Research / Engineering Answer Routes
- S485-S491 Innovation Potential Detection and Route Escalation

Purpose:
- create preview package shapes for actual useful outputs
- support market, research, engineering/design, portfolio, breakthrough,
  acquisition, governed update, and recursive learning previews
- preserve evidence, assumptions, verification needs, route candidates,
  and governance guardrails
- keep previews review-only until an approved runtime route executes them

No network requests, live crawling, browser execution, response-body reads,
runtime mutation, automatic updates, or autonomous execution are performed here.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S492-S498"
PHASE = "S492-S498"
JS_ASSET = "frontend/cockpit/shell/assets/claire_useful_output_package_preview.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_useful_output_package_preview.css"


BLOCKED_AUTHORITY: Dict[str, bool] = {
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_allowed": False,
    "runtime_truth_write_allowed": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "autonomous_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "package_execution_enabled": False,
    "package_export_performed": False,
}


PACKAGE_TYPES: Dict[str, Dict[str, Any]] = {
    "market_brief": {
        "label": "Market Intelligence Brief",
        "route_sources": ["market_intelligence_route", "portfolio_creation_or_optimization"],
        "required_sections": [
            "market_read",
            "trend_signal",
            "demand_logic",
            "competitive_pressure",
            "timing_window",
            "portfolio_implication",
            "verification_needed",
        ],
        "review_gate": "operator_review_market_brief",
    },
    "research_brief": {
        "label": "Research Evidence Brief",
        "route_sources": ["research_intelligence_route"],
        "required_sections": [
            "evidence_summary",
            "source_quality",
            "supported_claims",
            "assumptions",
            "unknowns",
            "verification_plan",
        ],
        "review_gate": "operator_review_research_brief",
    },
    "engineering_feasibility_preview": {
        "label": "Engineering Feasibility Preview",
        "route_sources": ["engineering_intelligence_route", "auto_invention_solution_generation_to_design_portal"],
        "required_sections": [
            "buildability_read",
            "architecture_implications",
            "dependencies",
            "constraints",
            "feasibility_questions",
            "design_route_potential",
            "verification_needed",
        ],
        "review_gate": "operator_review_engineering_preview",
    },
    "portfolio_action_preview": {
        "label": "Portfolio Action Preview",
        "route_sources": ["portfolio_creation_or_optimization"],
        "required_sections": [
            "thesis",
            "signal_basis",
            "exposure_logic",
            "risk_notes",
            "watchlist_or_action",
            "verification_needed",
        ],
        "review_gate": "operator_review_portfolio_preview",
    },
    "breakthrough_candidate_preview": {
        "label": "Breakthrough Candidate Preview",
        "route_sources": ["breakthrough_identification_and_classification"],
        "required_sections": [
            "structural_gap",
            "non_obvious_advancement",
            "route_candidate",
            "evidence_basis",
            "buildability_or_market_notes",
            "verification_needed",
        ],
        "review_gate": "operator_review_breakthrough_candidate",
    },
    "acquisition_package_preview": {
        "label": "Acquisition Package Preview",
        "route_sources": ["acquirer_identification_to_final_package"],
        "required_sections": [
            "strategic_fit",
            "value_capture",
            "buyer_logic",
            "package_readiness",
            "risks",
            "verification_needed",
        ],
        "review_gate": "operator_review_acquisition_preview",
    },
    "governed_update_preview": {
        "label": "Governed Update Package Preview",
        "route_sources": ["online_update_readiness_to_staged_validation"],
        "required_sections": [
            "update_goal",
            "zero_trust_checks",
            "validation_plan",
            "rollback_plan",
            "approval_gate",
            "blocked_authority",
        ],
        "review_gate": "operator_review_update_preview",
    },
    "recursive_learning_preview": {
        "label": "Recursive Learning Preview",
        "route_sources": ["lifecycle_memory_and_recursive_self_ingestion"],
        "required_sections": [
            "run_memory_input",
            "trace_reuse",
            "pattern_learning",
            "future_run_improvement",
            "replay_plan",
            "verification_needed",
        ],
        "review_gate": "operator_review_recursive_learning_preview",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = 0.0
    return max(low, min(high, number))


def _safe_base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": VERSION,
        "phase": PHASE,
        "stage_version": stage_version,
        "status": status,
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "created_at": _now(),
    }
    payload.update(BLOCKED_AUTHORITY)
    payload.update(extra)
    return payload


def _load_domain_routes_module():
    from runtime_core.api import domain_answer_routes_s478_s484 as domain_routes

    return domain_routes


def _load_innovation_module():
    from runtime_core.api import innovation_route_escalation_s485_s491 as innovation

    return innovation


def _choose_package_type(question: str | None, detection: Dict[str, Any], domain_output: Dict[str, Any]) -> str:
    normalized = _normalize(question)
    selected_candidate = detection.get("selected_candidate") or {}
    candidate_key = selected_candidate.get("candidate_key", "")
    route_id = selected_candidate.get("route_id", "")
    selected_domain_route = domain_output.get("route_selection", {}).get("selected_domain_route", "")

    if candidate_key == "update_governance" or "update" in normalized or "rollback" in normalized:
        return "governed_update_preview"
    if candidate_key == "recursive_learning" or "recursive" in normalized or "self-ingestion" in normalized:
        return "recursive_learning_preview"
    if candidate_key == "acquisition_package" or "acquirer" in normalized or "acquisition" in normalized:
        return "acquisition_package_preview"
    if candidate_key == "portfolio_optimization" or "portfolio" in normalized or "allocation" in normalized:
        return "portfolio_action_preview"
    if candidate_key == "breakthrough_escalation" or "breakthrough" in normalized or "non-obvious" in normalized:
        return "breakthrough_candidate_preview"
    if candidate_key == "engineering_design" or selected_domain_route == "engineering" or "buildable" in normalized:
        return "engineering_feasibility_preview"
    if selected_domain_route == "research" or "research" in normalized or "evidence" in normalized:
        return "research_brief"
    if selected_domain_route == "market" or "market" in normalized or "trend" in normalized:
        return "market_brief"

    for key, spec in PACKAGE_TYPES.items():
        if route_id in spec["route_sources"]:
            return key
    return "market_brief"


def build_s492_output_package_schema() -> Dict[str, Any]:
    return _safe_base(
        "S492",
        "output_package_schema_ready",
        package_fields=[
            "package_id",
            "package_type",
            "label",
            "question",
            "summary",
            "sections",
            "evidence_summary",
            "route_candidate",
            "assumptions",
            "verification_needed",
            "readiness_score",
            "review_status",
            "export_manifest",
            "governance",
        ],
        package_types=PACKAGE_TYPES,
        review_only=True,
    )


def build_s493_package_type_contracts() -> Dict[str, Any]:
    return _safe_base(
        "S493",
        "package_type_contracts_ready",
        package_types=PACKAGE_TYPES,
        supported_previews=sorted(PACKAGE_TYPES.keys()),
        rules=[
            "Preview packages are not final packages.",
            "Preview packages preserve evidence, assumptions, and verification needs.",
            "Preview packages require operator review before export or runtime action.",
            "Preview packages cannot mutate runtime truth or execute route transitions.",
        ],
    )


def _section_value(package_type: str, section: str, domain_output: Dict[str, Any], detection: Dict[str, Any]) -> Any:
    route_sections = domain_output.get("route_sections", {})
    evidence_answer = domain_output.get("evidence_answer", {})
    route_candidate = detection.get("selected_candidate")

    aliases = {
        "market_read": "direct_market_read",
        "trend_signal": "trend_signal_read",
        "competitive_pressure": "competitive_pressure",
        "timing_window": "timing_window",
        "portfolio_implication": "portfolio_implication",
        "evidence_summary": "evidence_summary",
        "source_quality": "source_quality",
        "supported_claims": "claim_support",
        "buildability_read": "buildability_read",
        "architecture_implications": "architecture_implications",
        "dependencies": "dependencies",
        "constraints": "constraints",
        "feasibility_questions": "feasibility_questions",
        "design_route_potential": "design_route_potential",
    }

    if section in aliases and aliases[section] in route_sections:
        return route_sections[aliases[section]]

    if section == "demand_logic":
        return route_sections.get("demand_logic", "Demand logic requires signal validation and market evidence review.")
    if section == "assumptions":
        return evidence_answer.get("assumptions", [])
    if section in {"unknowns", "verification_plan", "verification_needed"}:
        return evidence_answer.get("verification_needed", []) or route_sections.get("verification_needs", [])
    if section == "thesis":
        return "Preview thesis generated from domain route, evidence basket, and innovation signal context."
    if section == "signal_basis":
        return detection.get("category_scores", {})
    if section == "exposure_logic":
        return "Exposure logic is preview-only until portfolio runtime validates risk, evidence, and operator constraints."
    if section == "risk_notes":
        return [
            "Evidence confidence may be incomplete.",
            "No brokerage/account integration is active in this preview.",
            "No financial action is executed.",
        ]
    if section == "watchlist_or_action":
        return "Review candidate route and evidence before converting into portfolio action."
    if section == "structural_gap":
        return detection.get("category_scores", {}).get("market_gap", {})
    if section == "non_obvious_advancement":
        return detection.get("category_scores", {}).get("breakthrough", {})
    if section == "route_candidate":
        return route_candidate
    if section == "evidence_basis":
        return evidence_answer.get("evidence_basket", {}).get("support_summary", {})
    if section == "buildability_or_market_notes":
        return route_sections
    if section == "strategic_fit":
        return "Acquisition fit preview requires buyer logic, value capture, moat, and package readiness review."
    if section == "value_capture":
        return "Value capture is preview-only until strategy and acquirer evidence are validated."
    if section == "buyer_logic":
        return "Buyer logic requires acquirer identification and strategic fit evidence."
    if section == "package_readiness":
        return "Preview is not final package-ready until verification and operator review pass."
    if section == "risks":
        return ["Strategic fit unverified.", "Acquirer evidence not validated.", "No final package generated."]
    if section == "update_goal":
        return "Governed update preview is for staged inspection and validation only."
    if section == "zero_trust_checks":
        return ["hash_or_signature_check_required", "source_trust_check_required", "protected_path_check_required"]
    if section == "validation_plan":
        return ["static_scan", "dependency_check", "targeted_tests", "rollback_validation", "operator_review"]
    if section == "rollback_plan":
        return "Rollback must be proven before active update application."
    if section == "approval_gate":
        return "Operator approval required. Automatic update application remains blocked."
    if section == "blocked_authority":
        return dict(BLOCKED_AUTHORITY)
    if section == "run_memory_input":
        return "Completed run outputs may become future inputs after lifecycle memory owner is active."
    if section == "trace_reuse":
        return "Evidence trace and route decisions can be replayed without mutating runtime truth."
    if section == "pattern_learning":
        return "Pattern learning remains governed and review-only in this preview."
    if section == "future_run_improvement":
        return "Future runs may improve through approved recursive memory loops."
    if section == "replay_plan":
        return "Replay requires traceability, evidence IDs, and lifecycle memory contracts."

    return "Preview content pending stronger evidence or a specialized downstream route."


def _build_sections(package_type: str, domain_output: Dict[str, Any], detection: Dict[str, Any]) -> Dict[str, Any]:
    spec = PACKAGE_TYPES[package_type]
    return {
        section: _section_value(package_type, section, domain_output, detection)
        for section in spec["required_sections"]
    }


def _readiness_score(domain_output: Dict[str, Any], detection: Dict[str, Any]) -> float:
    evidence_answer = domain_output.get("evidence_answer", {})
    confidence = _clamp(evidence_answer.get("confidence", domain_output.get("confidence", 0.0)))
    innovation_score = _clamp(detection.get("innovation_score", 0.0))
    has_candidate = 1.0 if detection.get("selected_candidate") else 0.45
    support = evidence_answer.get("confidence_basis", {}).get("support_level", "insufficient")
    support_bonus = {"strong": 0.14, "usable": 0.10, "limited": 0.04, "insufficient": 0.0}.get(str(support), 0.0)
    return round(_clamp((confidence * 0.45) + (innovation_score * 0.35) + (has_candidate * 0.10) + support_bonus), 3)


def _review_status(score: float, verification_needed: List[Any]) -> str:
    if score >= 0.76 and not verification_needed:
        return "review_ready"
    if score >= 0.58:
        return "operator_review_required"
    if score >= 0.38:
        return "needs_more_evidence"
    return "insufficient_for_preview"


def build_useful_output_package_preview(
    question: str | None,
    preferred_package_type: str | None = None,
    preferred_domain: str | None = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a review-only useful output preview package."""
    domain_routes = _load_domain_routes_module()
    innovation = _load_innovation_module()

    domain_output = domain_routes.build_domain_answer_route(
        question,
        preferred_domain=preferred_domain,
        context=context or {},
    )
    detection = innovation.detect_innovation_potential(
        question,
        context=context or {},
        preferred_domain=preferred_domain,
    )

    requested_type = _normalize(preferred_package_type)
    package_type = requested_type if requested_type in PACKAGE_TYPES else _choose_package_type(question, detection, domain_output)
    spec = PACKAGE_TYPES[package_type]
    sections = _build_sections(package_type, domain_output, detection)
    evidence_answer = domain_output.get("evidence_answer", {})
    verification_needed = list(evidence_answer.get("verification_needed", []))
    score = _readiness_score(domain_output, detection)
    review_status = _review_status(score, verification_needed)

    selected_candidate = detection.get("selected_candidate")
    package = {
        "package_id": f"useful_package_preview_{abs(hash((question, package_type, score))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "package_type": package_type,
        "label": spec["label"],
        "question": str(question or ""),
        "summary": (
            f"{spec['label']} generated as a governed review-only preview from Claire's "
            f"{domain_output.get('route_selection', {}).get('label', 'domain route')}."
        ),
        "sections": sections,
        "evidence_summary": evidence_answer.get("evidence_basket", {}).get("support_summary", {}),
        "knowledge_result_count": len(domain_output.get("knowledge_results", {}).get("results", [])),
        "route_candidate": selected_candidate,
        "assumptions": evidence_answer.get("assumptions", []),
        "verification_needed": verification_needed,
        "readiness_score": score,
        "review_status": review_status,
        "export_manifest": build_export_manifest_stub(package_type, spec, review_status),
        "safe_next_operator_actions": [
            "review_package_preview",
            "inspect_evidence_summary",
            "resolve_verification_needs",
            "approve_export_only_after_review",
        ],
        "governance": {
            "review_only": True,
            "execution_allowed": False,
            "export_allowed_without_review": False,
            "review_gate": spec["review_gate"],
            **BLOCKED_AUTHORITY,
        },
    }
    package.update(BLOCKED_AUTHORITY)
    return package


def build_s494_preview_builder_contract() -> Dict[str, Any]:
    sample = build_useful_output_package_preview(
        "Can Claire turn this market gap and buildable breakthrough into a useful preview package?"
    )
    return _safe_base(
        "S494",
        "useful_output_preview_builder_ready",
        builder="build_useful_output_package_preview",
        sample_preview={
            "package_type": sample["package_type"],
            "readiness_score": sample["readiness_score"],
            "review_status": sample["review_status"],
            "section_count": len(sample["sections"]),
        },
    )


def build_s495_review_gate_contract() -> Dict[str, Any]:
    return _safe_base(
        "S495",
        "review_gate_contract_ready",
        review_statuses=[
            "review_ready",
            "operator_review_required",
            "needs_more_evidence",
            "insufficient_for_preview",
        ],
        review_rules=[
            "Every preview must be reviewed before export.",
            "No preview can execute runtime actions.",
            "Verification needs must be shown to the operator.",
            "Governed update previews require rollback and approval gates before any future application.",
            "Portfolio previews cannot execute financial actions.",
        ],
    )


def build_export_manifest_stub(package_type: str, spec: Optional[Dict[str, Any]] = None, review_status: str = "operator_review_required") -> Dict[str, Any]:
    active_spec = spec or PACKAGE_TYPES.get(package_type, PACKAGE_TYPES["market_brief"])
    return {
        "export_id": f"export_manifest_{package_type}",
        "package_type": package_type,
        "label": active_spec["label"],
        "review_status": review_status,
        "export_ready": False,
        "export_performed": False,
        "allowed_future_formats": ["json", "markdown", "operator_report"],
        "requires_operator_review": True,
        "blocked_until": [
            active_spec["review_gate"],
            "verification_needs_resolved_or_disclosed",
            "governance_check_passed",
        ],
    }


def build_s496_export_manifest_contract() -> Dict[str, Any]:
    manifests = {
        package_type: build_export_manifest_stub(package_type, spec)
        for package_type, spec in PACKAGE_TYPES.items()
    }
    return _safe_base(
        "S496",
        "export_manifest_contract_ready",
        manifests=manifests,
        export_rules=[
            "S496 defines export manifest shape only.",
            "No file export is performed by this module.",
            "Final package construction is a later lifecycle route, not this preview.",
        ],
    )


def build_s497_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S497",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "useful_output_preview_panel",
            "package_type_badge",
            "readiness_score_badge",
            "review_status_badge",
            "package_section_cards",
            "verification_needs_list",
            "export_manifest_stub",
        ],
        visual_authority="presentation_only",
    )


def build_s498_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s492 = build_s492_output_package_schema()
    s493 = build_s493_package_type_contracts()
    market = build_useful_output_package_preview(
        "Can Claire build a market trend brief with portfolio implications?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    engineering = build_useful_output_package_preview(
        "Can Claire build an engineering feasibility preview for this system architecture?",
        preferred_package_type="engineering_feasibility_preview",
        preferred_domain="engineering",
    )
    update = build_useful_output_package_preview(
        "Can Claire evaluate an online update package with rollback validation and approval?",
        preferred_package_type="governed_update_preview",
    )
    breakthrough = build_useful_output_package_preview(
        "Can Claire create a breakthrough candidate preview from this non-obvious market gap?",
        preferred_package_type="breakthrough_candidate_preview",
    )
    s494 = build_s494_preview_builder_contract()
    s495 = build_s495_review_gate_contract()
    s496 = build_s496_export_manifest_contract()
    s497 = build_s497_cockpit_asset_manifest(project_root)

    checks = {
        "s492_schema_ready": "package_id" in s492["package_fields"],
        "s493_package_types_ready": all(key in s493["package_types"] for key in ["market_brief", "engineering_feasibility_preview", "governed_update_preview"]),
        "s494_builder_ready": s494["sample_preview"]["section_count"] >= 1,
        "s495_review_gate_ready": "operator_review_required" in s495["review_statuses"],
        "s496_export_manifest_ready": s496["manifests"]["market_brief"]["export_ready"] is False,
        "s497_assets_exist": s497["assets"]["js_exists"] is True and s497["assets"]["css_exists"] is True,
        "market_preview_safe": market["package_type"] == "market_brief" and all(market.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "engineering_preview_safe": engineering["package_type"] == "engineering_feasibility_preview" and "buildability_read" in engineering["sections"],
        "update_preview_blocks_export": update["package_type"] == "governed_update_preview" and update["export_manifest"]["export_ready"] is False,
        "breakthrough_preview_has_route_candidate_field": "route_candidate" in breakthrough,
        "all_previews_review_only": all(
            preview["governance"]["review_only"] is True and preview["governance"]["execution_allowed"] is False
            for preview in [market, engineering, update, breakthrough]
        ),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S498",
        "claire_useful_output_package_preview_passed" if ok else "claire_useful_output_package_preview_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_previews={
            "market": market,
            "engineering": engineering,
            "update": update,
            "breakthrough": breakthrough,
        },
        forward_motion_allowed=ok,
        next_phase="S499-S505 Claire answer memory and replay",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s498_claire_useful_output_package_preview_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_useful_output_package_preview_s492_s498(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S492-S498",
        "claire_useful_output_package_preview_ready",
        contracts={
            "s492": build_s492_output_package_schema(),
            "s493": build_s493_package_type_contracts(),
            "s494": build_s494_preview_builder_contract(),
            "s495": build_s495_review_gate_contract(),
            "s496": build_s496_export_manifest_contract(),
            "s497": build_s497_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s498_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "PACKAGE_TYPES",
    "build_s492_output_package_schema",
    "build_s493_package_type_contracts",
    "build_useful_output_package_preview",
    "build_s494_preview_builder_contract",
    "build_s495_review_gate_contract",
    "build_export_manifest_stub",
    "build_s496_export_manifest_contract",
    "build_s497_cockpit_asset_manifest",
    "build_s498_stop_gate",
    "build_useful_output_package_preview_s492_s498",
]
