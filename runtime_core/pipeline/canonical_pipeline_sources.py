from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "claire.canonical_pipeline_sources.v1"
PIPELINE_ROOT_CANDIDATES = [
    Path("C:/Users/craig/OneDrive/Desktop/pipelines"),
    Path("C:/Users/craig/OneDrive/Desktop/Docs Main/pipelines"),
    Path("C:/Users/craig/OneDrive/Desktop"),
]
OPERATOR_MANUAL_CANDIDATES = [
    Path("C:/Users/craig/OneDrive/Desktop/Master docs/Claire Syntalion \u2014 Operator Instruction Manual.pdf"),
    Path("C:/Users/craig/OneDrive/Desktop/pipelines/Claire Syntalion \u2014 Operator Instruction Manual.pdf"),
    Path("C:/Users/craig/OneDrive/Desktop/Docs Main/pipelines/Claire Syntalion \u2014 Operator Instruction Manual.pdf"),
    Path("C:/Users/craig/OneDrive/Desktop/Docs Main/Master docs/Claire Syntalion \u2014 Operator Instruction Manual.pdf"),
    Path("C:/Users/craig/OneDrive/Desktop/Master docs/Claire Syntalion — Operator Instruction Manual.pdf"),
    Path("C:/Users/craig/OneDrive/Desktop/Docs Main/pipelines/Claire Syntalion — Operator Instruction Manual.pdf"),
    Path("C:/Users/craig/OneDrive/Desktop/Docs Main/Master docs/Claire Syntalion — Operator Instruction Manual.pdf"),
]
MASTER_DOC_ROOT_CANDIDATES = [
    Path("C:/Users/craig/OneDrive/Desktop/Master docs"),
    Path("C:/Users/craig/OneDrive/Desktop/Docs Main/Master docs"),
]


PIPELINE_SOURCE_ROLES: dict[str, dict[str, Any]] = {
    "Lifecycle Spine.txt": {
        "role": "canonical_lifecycle_order",
        "stage_scope": "1-30",
        "conditions_owned": ["stage_contracts", "evidence", "replay", "lifecycle_memory", "recursive_self_ingestion"],
        "scoring_owned": ["stage_confidence", "stage_quality", "reuse_potential", "learning_value"],
    },
    "Core Pipeline Architecture.txt": {
        "role": "core_runtime_architecture",
        "stage_scope": "signal_to_recursive_memory",
        "conditions_owned": ["signal_governance", "trend_discovery", "thesis_formation", "portfolio_normal_path", "breakthrough_gate"],
        "scoring_owned": ["trend_strength", "route_readiness", "recursive_improvement"],
    },
    "Branching Master Pipeline.txt": {
        "role": "route_branching_master",
        "stage_scope": "1-30",
        "conditions_owned": ["portfolio_path", "breakthrough_design_path", "acquisition_path", "final_package_path"],
        "scoring_owned": ["route_selection", "path_justification", "branch_thresholds"],
    },
    "Branch Logic.txt": {
        "role": "branch_condition_rules",
        "stage_scope": "10-15",
        "conditions_owned": ["portfolio_vs_breakthrough", "advancement_path_selection"],
        "scoring_owned": ["branch_decision_confidence"],
    },
    "portfolio and optimization.txt": {
        "role": "portfolio_optimization_path",
        "stage_scope": "1-10,23,26,27",
        "conditions_owned": ["portfolio_action", "risk_exposure_notes", "action_recommendations"],
        "scoring_owned": ["portfolio_score", "risk_adjusted_opportunity", "portfolio_fit"],
    },
    "trends 2 portfolio.txt": {
        "role": "trend_to_portfolio_path",
        "stage_scope": "1-10,23,26,27",
        "conditions_owned": ["trend_to_portfolio", "market_positioning", "competitor_analysis"],
        "scoring_owned": ["trend_strength", "portfolio_readiness"],
    },
    "trend to breakthrough.txt": {
        "role": "trend_to_breakthrough_path",
        "stage_scope": "1-22",
        "conditions_owned": ["gap_detection", "gap_qualification", "discovery_generation", "breakthrough_identification", "design_portal_output"],
        "scoring_owned": ["breakthrough_score", "buildability_score", "viability_score", "manufacturability_score", "feasibility_score"],
    },
    "breakthrough escalation.txt": {
        "role": "breakthrough_escalation_gate",
        "stage_scope": "11-22",
        "conditions_owned": ["non_obvious_advancement", "escalation_threshold", "design_or_solution_requirement"],
        "scoring_owned": ["breakthrough_threshold", "novelty", "strategic_advancement"],
    },
    "Breakthrough categories.txt": {
        "role": "breakthrough_classification_taxonomy",
        "stage_scope": "14-15",
        "conditions_owned": ["primary_breakthrough_type", "secondary_breakthrough_types", "non_technology_breakthroughs_allowed"],
        "scoring_owned": ["classification_confidence", "route_specific_breakthrough_value"],
    },
    "Full Breakthrough-to-Acquisition Package Pipeline.txt": {
        "role": "full_breakthrough_to_acquisition_package",
        "stage_scope": "1-30",
        "conditions_owned": ["design_portal", "market_positioning", "moat", "business_model", "portfolio_creation", "acquirer_fit", "final_package"],
        "scoring_owned": ["acquisition_score", "package_readiness", "deal_readiness"],
    },
    "trend 3 acquisition.txt": {
        "role": "trend_to_acquisition_path",
        "stage_scope": "1-10,23-30",
        "conditions_owned": ["market_positioning", "portfolio_creation", "acquirer_identification", "acquisition_fit"],
        "scoring_owned": ["acquirer_fit_score", "strategic_timing", "buyer_gap_score"],
    },
    "discovery first.txt": {
        "role": "discovery_first_path",
        "stage_scope": "1-13",
        "conditions_owned": ["signal_to_gap", "gap_to_discovery", "discovery_candidate"],
        "scoring_owned": ["discovery_score", "opportunity_score"],
    },
    "Existing System Ingestion  Replacement Pipeline.txt": {
        "role": "existing_system_ingestion_replacement",
        "stage_scope": "system_ingestion_to_replacement",
        "conditions_owned": ["system_decomposition", "weakness_detection", "replacement_candidate_generation"],
        "scoring_owned": ["replacement_value", "system_gap_score"],
    },
    "Governance  Fail-Safe Pipeline.txt": {
        "role": "governance_fail_safe",
        "stage_scope": "all",
        "conditions_owned": ["operator_review", "no_auto_promotion", "runtime_truth_firewall", "failure_and_insufficient_data"],
        "scoring_owned": ["governance_readiness", "evidence_sufficiency"],
    },
    "Recursive Learning Pipeline.txt": {
        "role": "recursive_learning",
        "stage_scope": "memory",
        "conditions_owned": ["approved_outputs_only", "failed_assumption_learning", "cross_run_comparison"],
        "scoring_owned": ["reuse_potential", "learning_value"],
    },
    "Final Endgame Pipeline.txt": {
        "role": "endgame_system_transformation",
        "stage_scope": "v10_target",
        "conditions_owned": ["ingest_systems", "decompose_weaknesses", "generate_superior_systems", "package_and_acquire"],
        "scoring_owned": ["endgame_readiness", "system_transformation_value"],
    },
    "Minimal Completed-State Pipeline.txt": {
        "role": "minimum_completed_state",
        "stage_scope": "proof",
        "conditions_owned": ["minimum_viable_run", "reviewable_output", "evidence_chain"],
        "scoring_owned": ["completion_score"],
    },
    "pipeline.txt": {
        "role": "general_pipeline_reference",
        "stage_scope": "all",
        "conditions_owned": ["pipeline_continuity"],
        "scoring_owned": ["pipeline_consistency"],
    },
    "Claire Enterprise Online Update Governance System.txt": {
        "role": "online_update_governance",
        "stage_scope": "update_governance",
        "conditions_owned": ["approved_provider", "signature_verification", "rollback", "manual_approval"],
        "scoring_owned": ["update_safety", "provider_trust"],
    },
    "(7)Claire-Complete-Systems-Flow .html": {
        "role": "complete_system_flow_visual",
        "stage_scope": "all",
        "conditions_owned": ["system_flow_visual_reference"],
        "scoring_owned": ["flow_completeness"],
    },
}


MASTER_SOURCE_ROLES: dict[str, dict[str, Any]] = {
    "Claire Syntalion — Operator Instruction Manual.pdf": {
        "role": "operator_governance_manual",
        "conditions_owned": ["explicit_operator_action", "review_queue", "mode_selection", "no_auto_promotion"],
        "scoring_owned": ["operator_readiness", "governance_safety"],
    },
    "Claire_Syntalion_Unified_Platform_Definition_v1.pdf": {
        "role": "unified_platform_definition",
        "conditions_owned": ["platform_identity", "capability_boundaries", "completed_state_definition"],
        "scoring_owned": ["platform_alignment", "capability_completeness"],
    },
    "Syntalion_ACS2 Claire AI - Complete System Documentation.pdf": {
        "role": "complete_system_documentation",
        "conditions_owned": ["subsystem_contracts", "runtime_contracts", "end_to_end_system_behavior"],
        "scoring_owned": ["system_completeness", "contract_coverage"],
    },
    "Syntalion_Claire AI Deterministic.pdf": {
        "role": "deterministic_mode_contract",
        "conditions_owned": ["local_only_execution", "no_network_mode", "repeatable_outputs"],
        "scoring_owned": ["deterministic_reproducibility", "local_evidence_sufficiency"],
    },
    "Syntalion_Claire AI Execution Flow Specification.pdf": {
        "role": "execution_flow_specification",
        "conditions_owned": ["stage_order", "input_output_flow", "runtime_execution_rules"],
        "scoring_owned": ["flow_correctness", "stage_transition_quality"],
    },
    "Syntalion_Claire AI Full Data Model Map.pdf": {
        "role": "full_data_model_map",
        "conditions_owned": ["run_context_schema", "stage_output_schema", "memory_schema", "portfolio_schema"],
        "scoring_owned": ["schema_completeness", "data_lineage_quality"],
    },
    "Syntalion_Claire AI Governance And Safety Documentation.pdf": {
        "role": "governance_and_safety_contract",
        "conditions_owned": ["runtime_truth_firewall", "review_required", "source_governance", "safe_failure"],
        "scoring_owned": ["governance_score", "safety_score", "evidence_sufficiency"],
    },
    "Syntalion_Claire AI Hybrid Mode.pdf": {
        "role": "hybrid_mode_contract",
        "conditions_owned": ["local_plus_connected_evidence", "promotion_required", "metadata_quarantine"],
        "scoring_owned": ["hybrid_confidence", "source_agreement"],
    },
    "Syntalion_Claire AI Mode Switching Architecture.pdf": {
        "role": "mode_switching_architecture",
        "conditions_owned": ["deterministic_to_connected", "connected_to_hybrid", "mode_authority"],
        "scoring_owned": ["mode_readiness", "mode_transition_safety"],
    },
    "Syntalion_Claire AI Repo Structure And Code Skeletons.pdf": {
        "role": "repo_structure_and_code_skeletons",
        "conditions_owned": ["module_ownership", "route_mounting", "code_organization"],
        "scoring_owned": ["implementation_alignment", "module_coverage"],
    },
    "Syntalion_Claire AI Subsystem Dependency Graph.pdf": {
        "role": "subsystem_dependency_graph",
        "conditions_owned": ["dependency_order", "subsystem_inputs_outputs", "blocked_dependency_detection"],
        "scoring_owned": ["dependency_health", "route_wiring_completeness"],
    },
    "Syntalion_Claire Connected Intelligence Mode.pdf": {
        "role": "connected_intelligence_mode_contract",
        "conditions_owned": ["provider_gate", "source_allowlist", "connected_search", "quarantine"],
        "scoring_owned": ["connected_readiness", "provider_trust", "source_quality"],
    },
    "Syntalion_Claire System Book.pdf": {
        "role": "system_book",
        "conditions_owned": ["operator_reference", "system_narrative", "platform_scope"],
        "scoring_owned": ["system_alignment"],
    },
    "Syntalion_The Complete ACS2-Claire AI Platform Revolutionary Autonomous Innovation System.pdf": {
        "role": "acs2_claire_platform_vision",
        "conditions_owned": ["autonomous_innovation_scope", "design_generation_scope", "acquisition_readiness_scope"],
        "scoring_owned": ["innovation_route_alignment", "endgame_readiness"],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "main.py").exists() or (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def pipeline_root() -> Path | None:
    roots = pipeline_roots()
    return roots[0] if roots else None


def pipeline_roots() -> list[Path]:
    return [root for root in PIPELINE_ROOT_CANDIDATES if root.exists()]


def resolve_pipeline_source(filename: str) -> Path:
    for root in pipeline_roots():
        exact = root / filename
        if exact.exists():
            return exact
        numbered = sorted(root.glob(f"*. {filename}"))
        if numbered:
            return numbered[0]
    return (pipeline_root() or Path.cwd()) / filename


def operator_manual_path() -> Path | None:
    for path in OPERATOR_MANUAL_CANDIDATES:
        if path.exists():
            return path
    return None


def master_doc_root() -> Path | None:
    for root in MASTER_DOC_ROOT_CANDIDATES:
        if root.exists():
            return root
    return None


def _sample_text(path: Path, limit: int = 900) -> str:
    if not path.exists() or path.suffix.lower() not in {".txt", ".html", ".md"}:
        return ""
    try:
        return " ".join(path.read_text(encoding="utf-8", errors="replace").split())[:limit]
    except Exception:
        return ""


def build_canonical_pipeline_source_index(root: Path | str | None = None) -> dict[str, Any]:
    base = Path(root or project_root()).resolve()
    source_root = pipeline_root()
    manual = operator_manual_path()
    master_root = master_doc_root()
    sources: list[dict[str, Any]] = []
    missing: list[str] = []
    for filename, contract in PIPELINE_SOURCE_ROLES.items():
        path = resolve_pipeline_source(filename)
        exists = path.exists()
        if not exists:
            missing.append(filename)
        sources.append(
            {
                "filename": filename,
                "path": str(path).replace("\\", "/"),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else 0,
                "role": contract["role"],
                "stage_scope": contract["stage_scope"],
                "conditions_owned": contract["conditions_owned"],
                "scoring_owned": contract["scoring_owned"],
                "sample": _sample_text(path),
            }
        )
    master_sources: list[dict[str, Any]] = []
    missing_master: list[str] = []
    for filename, contract in MASTER_SOURCE_ROLES.items():
        path = manual if contract["role"] == "operator_governance_manual" and manual else master_root / filename if master_root else Path(filename)
        exists = path.exists()
        if not exists:
            missing_master.append(filename)
        master_sources.append(
            {
                "filename": filename,
                "path": str(path).replace("\\", "/"),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else 0,
                "role": contract["role"],
                "stage_scope": "all",
                "conditions_owned": contract["conditions_owned"],
                "scoring_owned": contract["scoring_owned"],
            }
        )
    route_contracts = {
        "portfolio_normal_path": {
            "required_sources": ["portfolio and optimization.txt", "trends 2 portfolio.txt", "Core Pipeline Architecture.txt"],
            "required_stage_outputs": [1, 2, 3, 4, 5, 8, 9, 10, 23, 26, 27],
            "must_produce": ["updated_portfolio_thesis", "risk_exposure_notes", "action_recommendations"],
        },
        "breakthrough_design_path": {
            "required_sources": ["trend to breakthrough.txt", "breakthrough escalation.txt", "Breakthrough categories.txt"],
            "required_stage_outputs": list(range(1, 23)),
            "must_produce": ["gap_detection", "breakthrough_classification", "design_portal_output", "blueprints_specs"],
        },
        "acquisition_package_path": {
            "required_sources": ["Full Breakthrough-to-Acquisition Package Pipeline.txt", "trend 3 acquisition.txt"],
            "required_stage_outputs": list(range(1, 31)),
            "must_produce": ["market_positioning", "business_model", "portfolio_creation", "acquirer_identification", "acquisition_fit", "final_package"],
        },
        "existing_system_replacement_path": {
            "required_sources": [
                "Existing System Ingestion  Replacement Pipeline.txt",
                "Final Endgame Pipeline.txt",
                "Full Breakthrough-to-Acquisition Package Pipeline.txt",
                "Core Pipeline Architecture.txt",
            ],
            "required_stage_outputs": ["existing_system_ingestion", *list(range(1, 31)), "existing_system_decomposition", "superior_system_design"],
            "must_produce": [
                "existing_system_decomposition",
                "gap_detection",
                "solution_generation",
                "design_portal_output",
                "superior_system_design",
                "market_positioning",
                "portfolio_creation",
                "acquirer_identification",
                "acquisition_fit",
                "final_package",
            ],
        },
        "governed_update_path": {
            "required_sources": ["Claire Enterprise Online Update Governance System.txt", "Governance  Fail-Safe Pipeline.txt"],
            "required_stage_outputs": ["provider_trust", "signature_verification", "rollback", "manual_approval"],
            "must_produce": ["proposal_only_update_request", "audit_event", "no_auto_apply"],
        },
    }
    index = {
        "schema_version": SCHEMA_VERSION,
        "status": "ready" if not missing and not missing_master else "missing_sources",
        "generated_at": utc_now(),
        "source_root": str(source_root).replace("\\", "/") if source_root else "",
        "source_roots": [str(path).replace("\\", "/") for path in pipeline_roots()],
        "master_doc_root": str(master_root).replace("\\", "/") if master_root else "",
        "operator_manual": next((item for item in master_sources if item["filename"] == "Claire Syntalion — Operator Instruction Manual.pdf"), {}),
        "source_count": len(sources),
        "master_source_count": len(master_sources),
        "missing": missing + missing_master,
        "sources": sources,
        "master_sources": master_sources,
        "route_contracts": route_contracts,
        "final_package_requirements": [
            "executive_summary",
            "signal_basis",
            "trend_basis",
            "thesis",
            "gap_explanation",
            "discovery_output",
            "breakthrough_classification",
            "advancement_path",
            "invention_or_solution_if_applicable",
            "buildability",
            "viability",
            "manufacturability_deployability",
            "feasibility",
            "design_portal_output_if_applicable",
            "market_positioning",
            "moat_and_differentiation",
            "business_model_and_value_capture",
            "competitor_analysis",
            "portfolio_placement",
            "acquirer_targets",
            "acquisition_rationale",
            "evidence",
            "confidence",
            "risks",
            "next_steps",
        ],
        "operator_rules": {
            "dashboard_is_governance_surface": True,
            "nothing_auto_promotes": True,
            "review_queue_required": True,
            "runtime_truth_write_requires_promotion": True,
            "internal_manual_not_for_external_distribution": True,
        },
    }
    out = base / "data" / "pipeline" / "canonical_pipeline_source_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**index, "index_path": str(out).replace("\\", "/")}
