from __future__ import annotations

"""
Claire Evidence-Backed Answer Model — S464-S470

This module builds on:
- S450-S456 Claire Intelligence Answer Contract
- S457-S463 Claire Command Classification and Response Cards

Purpose:
- define evidence source objects
- score evidence quality deterministically
- build evidence baskets for Claire answers
- separate supported facts, assumptions, inferences, and verification needs
- produce an evidence-backed answer model without performing live web activity
- preserve governance: backend truth, presentation-only cockpit, no runtime mutation

No network requests, live crawling, browser execution, response-body reads,
runtime mutation, automatic updates, or autonomous execution are performed here.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S464-S470"
PHASE = "S464-S470"
JS_ASSET = "frontend/cockpit/shell/assets/claire_evidence_backed_answers.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_evidence_backed_answers.css"


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
}


SOURCE_TYPE_WEIGHTS: Dict[str, float] = {
    "governance_contract": 0.95,
    "runtime_payload": 0.92,
    "lifecycle_contract": 0.90,
    "uploaded_master_document": 0.88,
    "uploaded_architecture_document": 0.86,
    "uploaded_pipeline_document": 0.84,
    "technology_database_document": 0.82,
    "operator_context": 0.74,
    "quarantined_web_evidence": 0.62,
    "general_context": 0.50,
}


SUPPORTED_CLAIM_STATUSES = [
    "supported",
    "partially_supported",
    "inference",
    "assumption",
    "needs_verification",
    "unsupported",
]


@dataclass(frozen=True)
class EvidenceSource:
    source_id: str
    title: str
    source_type: str
    summary: str
    relevance: float
    specificity: float
    trust: float
    recency: float
    supports: List[str]
    limitations: List[str]


@dataclass(frozen=True)
class EvidenceClaim:
    claim_id: str
    text: str
    status: str
    support_level: float
    evidence_ids: List[str]
    assumptions: List[str]
    verification_needed: List[str]


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


def _load_answer_contract_module():
    from runtime_core.api import intelligence_answer_contract_s450_s456 as answer_contract

    return answer_contract


def _load_response_card_module():
    from runtime_core.api import command_response_cards_s457_s463 as response_cards

    return response_cards


def make_evidence_source(
    source_id: str,
    title: str,
    source_type: str,
    summary: str,
    relevance: float = 0.75,
    specificity: float = 0.70,
    trust: Optional[float] = None,
    recency: float = 0.65,
    supports: Optional[Sequence[str]] = None,
    limitations: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    source_weight = SOURCE_TYPE_WEIGHTS.get(source_type, SOURCE_TYPE_WEIGHTS["general_context"])
    source = EvidenceSource(
        source_id=str(source_id),
        title=str(title),
        source_type=str(source_type),
        summary=str(summary),
        relevance=_clamp(relevance),
        specificity=_clamp(specificity),
        trust=_clamp(source_weight if trust is None else trust),
        recency=_clamp(recency),
        supports=list(supports or []),
        limitations=list(limitations or []),
    )
    return asdict(source)


def score_evidence_source(source: Dict[str, Any]) -> Dict[str, Any]:
    """Score an evidence source without external lookup."""
    source_type = str(source.get("source_type", "general_context"))
    type_weight = SOURCE_TYPE_WEIGHTS.get(source_type, SOURCE_TYPE_WEIGHTS["general_context"])
    relevance = _clamp(source.get("relevance", 0.0))
    specificity = _clamp(source.get("specificity", 0.0))
    trust = _clamp(source.get("trust", type_weight))
    recency = _clamp(source.get("recency", 0.0))
    supports = source.get("supports") if isinstance(source.get("supports"), list) else []
    limitations = source.get("limitations") if isinstance(source.get("limitations"), list) else []

    support_bonus = min(0.08, 0.02 * len(supports))
    limitation_penalty = min(0.12, 0.03 * len(limitations))

    score = (
        relevance * 0.32
        + specificity * 0.24
        + trust * 0.28
        + recency * 0.10
        + type_weight * 0.06
        + support_bonus
        - limitation_penalty
    )
    score = round(_clamp(score), 3)

    if score >= 0.80:
        grade = "strong"
    elif score >= 0.65:
        grade = "usable"
    elif score >= 0.45:
        grade = "weak"
    else:
        grade = "insufficient"

    return {
        "source_id": source.get("source_id", ""),
        "source_type": source_type,
        "score": score,
        "grade": grade,
        "components": {
            "relevance": relevance,
            "specificity": specificity,
            "trust": trust,
            "recency": recency,
            "type_weight": type_weight,
            "support_bonus": round(support_bonus, 3),
            "limitation_penalty": round(limitation_penalty, 3),
        },
    }


def build_default_claire_evidence_sources() -> List[Dict[str, Any]]:
    """Canonical baseline evidence sources derived from Claire's uploaded architecture set."""
    return [
        make_evidence_source(
            "claire_master_build_plan",
            "Claire Master System Build Plan",
            "uploaded_master_document",
            "Defines Claire as a governed recursive lifecycle system with a 30-stage canonical pipeline.",
            relevance=0.95,
            specificity=0.92,
            recency=0.82,
            supports=["platform_identity", "30_stage_lifecycle", "route_aware_runtime"],
        ),
        make_evidence_source(
            "claire_governance_safety",
            "Claire Governance and Safety Documentation",
            "governance_contract",
            "Defines mode isolation, redline detection, oversight, intervention, and compliance boundaries.",
            relevance=0.94,
            specificity=0.90,
            recency=0.80,
            supports=["blocked_authority", "fail_closed_governance", "mode_safety"],
        ),
        make_evidence_source(
            "claire_hybrid_mode",
            "Claire Hybrid Mode Architecture",
            "uploaded_architecture_document",
            "Defines deterministic and connected intelligence fusion as Claire's maximum capability state.",
            relevance=0.88,
            specificity=0.84,
            recency=0.78,
            supports=["hybrid_mode", "cross_validation", "strategic_intelligence"],
        ),
        make_evidence_source(
            "claire_core_pipeline",
            "Core Pipeline Architecture",
            "uploaded_pipeline_document",
            "Defines signal governance to trend discovery, thesis, portfolio optimization, escalation, and recursive self-ingestion.",
            relevance=0.92,
            specificity=0.86,
            recency=0.84,
            supports=["signal_governance", "portfolio_path", "breakthrough_escalation", "recursive_self_ingestion"],
        ),
        make_evidence_source(
            "claire_technology_database",
            "Technology Database and Search Dictionary",
            "technology_database_document",
            "Defines technology categories, maturity, dependencies, compatibility, complexity, and recommendation fields.",
            relevance=0.78,
            specificity=0.82,
            recency=0.72,
            supports=["technology_intelligence", "engineering_answering", "buildability_context"],
        ),
    ]


def build_s464_evidence_source_schema() -> Dict[str, Any]:
    return _safe_base(
        "S464",
        "evidence_source_schema_ready",
        source_fields=[
            "source_id",
            "title",
            "source_type",
            "summary",
            "relevance",
            "specificity",
            "trust",
            "recency",
            "supports",
            "limitations",
        ],
        source_types=sorted(SOURCE_TYPE_WEIGHTS.keys()),
        source_type_weights=dict(SOURCE_TYPE_WEIGHTS),
    )


def build_s465_evidence_quality_scoring_contract() -> Dict[str, Any]:
    sample = make_evidence_source(
        "sample_architecture_doc",
        "Sample Architecture Document",
        "uploaded_architecture_document",
        "Sample evidence source for deterministic scoring.",
        relevance=0.8,
        specificity=0.75,
        recency=0.7,
        supports=["sample_claim"],
    )
    return _safe_base(
        "S465",
        "evidence_quality_scoring_contract_ready",
        scoring_formula={
            "relevance": 0.32,
            "specificity": 0.24,
            "trust": 0.28,
            "recency": 0.10,
            "type_weight": 0.06,
            "support_bonus": "up_to_0.08",
            "limitation_penalty": "up_to_0.12",
        },
        sample_source=sample,
        sample_score=score_evidence_source(sample),
    )


def build_evidence_basket(
    question: str | None,
    sources: Optional[Sequence[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    answer_contract = _load_answer_contract_module()
    classification = answer_contract.classify_claire_question(question)

    active_sources = list(sources) if sources is not None else build_default_claire_evidence_sources()
    scored_sources = []
    for source in active_sources:
        normalized_source = dict(source)
        if "source_id" not in normalized_source:
            normalized_source["source_id"] = f"source_{len(scored_sources) + 1}"
        scored_sources.append(
            {
                "source": normalized_source,
                "score": score_evidence_source(normalized_source),
            }
        )

    scored_sources.sort(key=lambda item: item["score"]["score"], reverse=True)

    strong = [item for item in scored_sources if item["score"]["grade"] == "strong"]
    usable = [item for item in scored_sources if item["score"]["grade"] in {"strong", "usable"}]
    weak = [item for item in scored_sources if item["score"]["grade"] == "weak"]
    insufficient = [item for item in scored_sources if item["score"]["grade"] == "insufficient"]

    if len(strong) >= 2:
        support_level = "strong"
        confidence = 0.86
    elif len(usable) >= 2:
        support_level = "usable"
        confidence = 0.74
    elif len(usable) == 1:
        support_level = "limited"
        confidence = 0.58
    else:
        support_level = "insufficient"
        confidence = 0.32

    confidence = round(
        _clamp(confidence + min(0.06, len(scored_sources) * 0.01) - min(0.08, len(insufficient) * 0.02)),
        2,
    )

    return _safe_base(
        "S466",
        "evidence_basket_ready",
        question=str(question or ""),
        classification=classification,
        context_keys=sorted((context or {}).keys()),
        source_count=len(scored_sources),
        scored_sources=scored_sources,
        support_summary={
            "strong_count": len(strong),
            "usable_count": len(usable),
            "weak_count": len(weak),
            "insufficient_count": len(insufficient),
            "support_level": support_level,
            "confidence": confidence,
        },
    )


def classify_claim_support(
    claim_text: str,
    evidence_basket: Dict[str, Any],
    required_support: str | None = None,
) -> Dict[str, Any]:
    scored_sources = evidence_basket.get("scored_sources", [])
    support_summary = evidence_basket.get("support_summary", {})
    support_level = support_summary.get("support_level", "insufficient")
    confidence = _clamp(support_summary.get("confidence", 0.0))

    usable_sources = [
        item
        for item in scored_sources
        if item.get("score", {}).get("grade") in {"strong", "usable"}
    ]
    evidence_ids = [
        str(item.get("source", {}).get("source_id", ""))
        for item in usable_sources[:4]
    ]

    required = required_support or evidence_basket.get("classification", {}).get("evidence_requirement", "moderate_to_high")
    if support_level == "strong":
        status = "supported"
    elif support_level == "usable":
        status = "partially_supported" if required in {"high", "contractual"} else "supported"
    elif support_level == "limited":
        status = "inference"
    else:
        status = "needs_verification"

    assumptions: List[str] = []
    verification_needed: List[str] = []

    if status in {"inference", "needs_verification", "partially_supported"}:
        assumptions.append("Available evidence is not enough for an absolute claim.")
    if required in {"high", "contractual"} and status != "supported":
        verification_needed.append("Add stronger evidence or a governed source check before treating this as proven.")
    if not evidence_ids:
        verification_needed.append("No usable evidence sources were found in the current basket.")

    claim = EvidenceClaim(
        claim_id=f"claim_{abs(hash((claim_text, tuple(evidence_ids)))) % 10_000_000:07d}",
        text=str(claim_text),
        status=status,
        support_level=round(confidence, 2),
        evidence_ids=evidence_ids,
        assumptions=assumptions,
        verification_needed=verification_needed,
    )
    return asdict(claim)


def build_s466_evidence_basket_contract() -> Dict[str, Any]:
    basket = build_evidence_basket("Can Claire evaluate this engineering trend for innovation potential?")
    return _safe_base(
        "S466",
        "evidence_basket_contract_ready",
        basket_fields=[
            "question",
            "classification",
            "source_count",
            "scored_sources",
            "support_summary",
        ],
        sample_basket_summary=basket["support_summary"],
    )


def build_s467_claim_support_contract() -> Dict[str, Any]:
    basket = build_evidence_basket("Can Claire explain its governance and safety boundary?")
    claim = classify_claim_support(
        "Claire must keep runtime mutation and automatic updates blocked until governed approval.",
        basket,
        required_support="contractual",
    )
    return _safe_base(
        "S467",
        "claim_support_contract_ready",
        claim_statuses=SUPPORTED_CLAIM_STATUSES,
        claim_fields=[
            "claim_id",
            "text",
            "status",
            "support_level",
            "evidence_ids",
            "assumptions",
            "verification_needed",
        ],
        sample_claim=claim,
    )


def build_evidence_backed_answer(
    question: str | None,
    sources: Optional[Sequence[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    answer_contract = _load_answer_contract_module()
    response_cards = _load_response_card_module()

    base_answer = answer_contract.build_claire_intelligence_answer(question, context=context or {})
    response_card = response_cards.build_claire_response_card(question, context=context or {})
    basket = build_evidence_basket(question, sources=sources, context=context or {})

    claim_text = base_answer.get("direct_answer", "Claire generated an answer contract.")
    claim = classify_claim_support(
        claim_text,
        basket,
        required_support=base_answer.get("evidence_requirement"),
    )

    support_summary = basket["support_summary"]
    confidence = round(
        _clamp((float(base_answer.get("confidence", 0.0)) * 0.45) + (support_summary["confidence"] * 0.55)),
        2,
    )

    answer = {
        "answer_id": base_answer["answer_id"],
        "version": VERSION,
        "created_at": _now(),
        "question": str(question or ""),
        "classification": base_answer["classification"],
        "response_card": {
            "card_id": response_card["card_id"],
            "card_type": response_card["card_type"],
            "title": response_card["title"],
            "chips": response_card["chips"],
        },
        "direct_answer": base_answer["direct_answer"],
        "evidence_basket": basket,
        "claims": [claim],
        "confidence": confidence,
        "confidence_basis": {
            "base_answer_confidence": base_answer.get("confidence", 0.0),
            "evidence_confidence": support_summary["confidence"],
            "support_level": support_summary["support_level"],
        },
        "assumptions": list(base_answer.get("assumptions", [])) + claim["assumptions"],
        "verification_needed": claim["verification_needed"],
        "innovation_potential": bool(base_answer.get("innovation_potential")),
        "route_hint": base_answer.get("route_hint"),
        "evidence_requirement": base_answer.get("evidence_requirement"),
        "answer_quality_state": "evidence_backed" if claim["status"] in {"supported", "partially_supported"} else "verification_needed",
        "governance_state": base_answer.get("governance_state", {}),
    }
    answer.update(BLOCKED_AUTHORITY)
    return answer


def build_s468_evidence_backed_answer_contract() -> Dict[str, Any]:
    answer = build_evidence_backed_answer("Can Claire analyze this market trend and identify an innovation route?")
    return _safe_base(
        "S468",
        "evidence_backed_answer_contract_ready",
        answer_fields=[
            "answer_id",
            "question",
            "classification",
            "response_card",
            "direct_answer",
            "evidence_basket",
            "claims",
            "confidence",
            "confidence_basis",
            "assumptions",
            "verification_needed",
            "innovation_potential",
            "route_hint",
            "evidence_requirement",
            "answer_quality_state",
            "governance_state",
        ],
        sample_answer_summary={
            "answer_quality_state": answer["answer_quality_state"],
            "confidence": answer["confidence"],
            "support_level": answer["confidence_basis"]["support_level"],
        },
    )


def build_s469_traceability_contract() -> Dict[str, Any]:
    return _safe_base(
        "S469",
        "traceability_contract_ready",
        trace_fields=[
            "source_id",
            "source_type",
            "score",
            "grade",
            "claim_id",
            "evidence_ids",
            "verification_needed",
        ],
        trace_rules=[
            "Every strong answer should identify evidence sources.",
            "Unsupported claims must be marked as assumptions, inference, or needs_verification.",
            "Web evidence remains quarantined unless promoted through governed workflow.",
            "No answer may claim live research was performed unless governed live research actually ran.",
        ],
    )


def build_s470_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s464 = build_s464_evidence_source_schema()
    s465 = build_s465_evidence_quality_scoring_contract()
    s466 = build_s466_evidence_basket_contract()
    s467 = build_s467_claim_support_contract()
    s468 = build_s468_evidence_backed_answer_contract()
    s469 = build_s469_traceability_contract()

    answer = build_evidence_backed_answer("Can Claire evaluate this engineering architecture for buildability?")
    weak_source = make_evidence_source(
        "weak_note",
        "Weak Operator Note",
        "general_context",
        "Unverified note.",
        relevance=0.20,
        specificity=0.20,
        trust=0.20,
        recency=0.20,
        limitations=["unverified", "not specific", "no corroboration"],
    )
    weak_answer = build_evidence_backed_answer(
        "Can Claire prove this unsupported claim?",
        sources=[weak_source],
    )

    root = Path(project_root) if project_root is not None else Path.cwd()
    js_exists = (root / JS_ASSET).exists()
    css_exists = (root / CSS_ASSET).exists()

    checks = {
        "s464_schema_ready": "source_id" in s464["source_fields"],
        "s465_scoring_ready": s465["sample_score"]["grade"] in {"strong", "usable", "weak", "insufficient"},
        "s466_basket_ready": s466["sample_basket_summary"]["support_level"] in {"strong", "usable", "limited", "insufficient"},
        "s467_claim_support_ready": s467["sample_claim"]["status"] in SUPPORTED_CLAIM_STATUSES,
        "s468_answer_contract_ready": s468["sample_answer_summary"]["answer_quality_state"] in {"evidence_backed", "verification_needed"},
        "s469_traceability_ready": "verification_needed" in s469["trace_fields"],
        "strong_answer_safe": all(answer.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "weak_answer_marks_verification_needed": weak_answer["answer_quality_state"] == "verification_needed",
        "assets_exist": js_exists and css_exists,
    }

    ok = all(checks.values())
    result = _safe_base(
        "S470",
        "claire_evidence_backed_answer_model_passed" if ok else "claire_evidence_backed_answer_model_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_answer=answer,
        weak_answer=weak_answer,
        forward_motion_allowed=ok,
        next_phase="S471-S477 Claire knowledge base registry from uploaded docs",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s470_claire_evidence_backed_answer_model_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_evidence_backed_answer_model_s464_s470(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S464-S470",
        "claire_evidence_backed_answer_model_ready",
        contracts={
            "s464": build_s464_evidence_source_schema(),
            "s465": build_s465_evidence_quality_scoring_contract(),
            "s466": build_s466_evidence_basket_contract(),
            "s467": build_s467_claim_support_contract(),
            "s468": build_s468_evidence_backed_answer_contract(),
            "s469": build_s469_traceability_contract(),
        },
        stop_gate=build_s470_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "SOURCE_TYPE_WEIGHTS",
    "SUPPORTED_CLAIM_STATUSES",
    "make_evidence_source",
    "score_evidence_source",
    "build_default_claire_evidence_sources",
    "build_evidence_basket",
    "classify_claim_support",
    "build_evidence_backed_answer",
    "build_s464_evidence_source_schema",
    "build_s465_evidence_quality_scoring_contract",
    "build_s466_evidence_basket_contract",
    "build_s467_claim_support_contract",
    "build_s468_evidence_backed_answer_contract",
    "build_s469_traceability_contract",
    "build_s470_stop_gate",
    "build_evidence_backed_answer_model_s464_s470",
]
