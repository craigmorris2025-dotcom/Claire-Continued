from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request


router = APIRouter(tags=["Claire Intelligence Answers"])

VERSION = "v19.89.8-intelligence-answer-entrypoint"

BLOCKED_AUTHORITY: dict[str, Any] = {
    "network_request_performed": False,
    "provider_execution_performed": False,
    "body_read_performed": False,
    "body_read_allowed": False,
    "runtime_truth_write": "blocked",
    "runtime_truth_mutation": False,
    "runtime_mutation_enabled": False,
    "automatic_update_performed": False,
    "automatic_updates_enabled": False,
    "autonomous_execution_enabled": False,
    "live_web_execution_enabled": False,
}


QUESTION_TYPE_TERMS: dict[str, set[str]] = {
    "casual": {"hello", "hi", "thanks", "thank", "what", "who", "why", "how"},
    "research": {"research", "evidence", "source", "paper", "study", "verify", "citation", "document"},
    "engineering": {"engineering", "build", "buildable", "feasible", "prototype", "component", "deploy", "manufacture"},
    "architecture": {"architecture", "system", "api", "route", "stage", "pipeline", "integration", "wiring"},
    "strategic": {"strategy", "strategic", "market", "competitor", "moat", "acquirer", "acquisition", "buyer", "m&a"},
    "portfolio": {"portfolio", "thesis", "exposure", "weighting", "rebalance", "position", "watchlist"},
    "investment": {"investment", "invest", "valuation", "returns", "risk", "upside", "capital", "allocation"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())[:1000]


def query_terms(query: str) -> set[str]:
    text = "".join(ch.lower() if ch.isalnum() else " " for ch in query)
    return {part for part in text.split() if len(part) > 1}


def infer_question_type(query: str, classification: dict[str, Any]) -> dict[str, Any]:
    terms = query_terms(query)
    scored: list[tuple[str, int]] = []
    for question_type, hints in QUESTION_TYPE_TERMS.items():
        scored.append((question_type, len(terms.intersection(hints))))
    scored.sort(key=lambda item: item[1], reverse=True)

    domain = str(classification.get("domain") or "general")
    domain_map = {
        "market": "strategic",
        "acquisition": "strategic",
        "portfolio": "portfolio",
        "engineering": "engineering",
        "research": "research",
        "governance": "architecture",
        "breakthrough": "strategic",
    }
    selected = domain_map.get(domain)
    if not selected or (scored and scored[0][1] > 0 and scored[0][0] != "casual"):
        selected = scored[0][0] if scored and scored[0][1] > 0 else selected or "casual"

    return {
        "question_type": selected,
        "matched_terms": sorted(terms.intersection(QUESTION_TYPE_TERMS.get(selected, set()))),
        "supported_types": sorted(QUESTION_TYPE_TERMS),
    }


def preferred_domain_for_question(question_type: str, classification: dict[str, Any]) -> str | None:
    domain = str(classification.get("domain") or "")
    if question_type in {"engineering", "architecture"}:
        return "engineering"
    if question_type in {"research"}:
        return "research"
    if question_type in {"strategic", "portfolio", "investment"}:
        return "market"
    if domain in {"market", "research", "engineering"}:
        return domain
    return None


def collect_citations(answer: dict[str, Any], domain_output: dict[str, Any] | None) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    basket = answer.get("evidence_basket", {}) if isinstance(answer.get("evidence_basket"), dict) else {}
    for item in basket.get("scored_sources", []) if isinstance(basket.get("scored_sources"), list) else []:
        source = item.get("source", {}) if isinstance(item, dict) else {}
        score = item.get("score", {}) if isinstance(item, dict) else {}
        if not isinstance(source, dict):
            continue
        citations.append(
            {
                "citation_id": source.get("source_id"),
                "title": source.get("title"),
                "source_type": source.get("source_type"),
                "grade": score.get("grade") if isinstance(score, dict) else None,
                "score": score.get("score") if isinstance(score, dict) else None,
                "summary": source.get("summary"),
            }
        )

    knowledge = {}
    if isinstance(domain_output, dict):
        knowledge = domain_output.get("knowledge_results", {}) if isinstance(domain_output.get("knowledge_results"), dict) else {}
    for item in knowledge.get("results", []) if isinstance(knowledge.get("results"), list) else []:
        if not isinstance(item, dict):
            continue
        citations.append(
            {
                "citation_id": item.get("document_id") or item.get("id") or item.get("title"),
                "title": item.get("title"),
                "source_type": "local_knowledge_registry",
                "grade": "local_context",
                "score": item.get("score"),
                "summary": item.get("summary") or item.get("snippet"),
            }
        )

    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for citation in citations:
        key = str(citation.get("citation_id") or citation.get("title") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(citation)
    return deduped[:8]


def build_intelligence_routed_answer(query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    from runtime_core.api import evidence_backed_answer_model_s464_s470 as evidence_model
    from runtime_core.api import intelligence_answer_contract_s450_s456 as answer_contract
    from runtime_core.api import innovation_route_escalation_s485_s491 as escalation
    from runtime_core.api import domain_answer_routes_s478_s484 as domain_routes

    normalized = normalize_query(query)
    classification = answer_contract.classify_claire_question(normalized)
    question_type = infer_question_type(normalized, classification)
    preferred_domain = preferred_domain_for_question(question_type["question_type"], classification)
    evidence_answer = evidence_model.build_evidence_backed_answer(normalized, context=context or {})

    domain_output: dict[str, Any] | None = None
    if normalized and preferred_domain:
        domain_output = domain_routes.build_domain_answer_route(
            normalized,
            preferred_domain=preferred_domain,
            context=context or {},
        )

    route_review = escalation.detect_innovation_potential(
        normalized,
        context=context or {},
        preferred_domain=preferred_domain,
    ) if normalized else None

    citations = collect_citations(evidence_answer, domain_output)
    evidence_requirement = evidence_answer.get("evidence_requirement") or classification.get("evidence_requirement")
    confidence = float(evidence_answer.get("confidence", classification.get("confidence", 0.0)) or 0.0)

    if not normalized:
        direct_answer = "Claire is waiting for a question."
    else:
        direct_answer = evidence_answer.get("direct_answer", "")

    payload = {
        "schema_version": VERSION,
        "status": "answer_ready" if normalized else "blocked_empty_query",
        "generated_at": utc_now(),
        "query": normalized,
        "question_type": question_type,
        "classification": classification,
        "answer_mode": "intelligence_routed_evidence_backed",
        "direct_answer": direct_answer,
        "confidence": round(max(0.0, min(1.0, confidence)), 2),
        "evidence_requirement": evidence_requirement,
        "citations": citations,
        "citation_count": len(citations),
        "assumptions": evidence_answer.get("assumptions", []),
        "verification_needed": evidence_answer.get("verification_needed", []),
        "route_hint": evidence_answer.get("route_hint") or classification.get("default_route"),
        "domain_route": domain_output.get("route_selection") if isinstance(domain_output, dict) else None,
        "route_sections": domain_output.get("route_sections") if isinstance(domain_output, dict) else {},
        "route_review": route_review,
        "answer_quality_state": evidence_answer.get("answer_quality_state"),
        "governance": {
            "backend_owns_truth": True,
            "answer_is_read_only": True,
            "live_search_required_for_fresh_claims": evidence_requirement in {"high", "moderate_to_high"},
            "live_search_must_use_governed_provider_route": True,
            **BLOCKED_AUTHORITY,
        },
    }
    payload.update(BLOCKED_AUTHORITY)
    return payload


@router.post("/api/ask-claire")
async def post_ask_claire(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    body = body if isinstance(body, dict) else {}
    query = body.get("query") or body.get("question") or body.get("text") or ""
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    return build_intelligence_routed_answer(str(query), context=context)


__all__ = [
    "VERSION",
    "BLOCKED_AUTHORITY",
    "infer_question_type",
    "build_intelligence_routed_answer",
    "router",
]
