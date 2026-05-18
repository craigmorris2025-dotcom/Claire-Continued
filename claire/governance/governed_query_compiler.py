from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

from claire.governance.governed_source_evidence_intake import (
    BLOCKED_AUTHORITY,
    source_family_policy,
)


PHASE = "S618-S624"
SYSTEM = "Claire Syntalion"
GATE_NAME = "governed_query_builder_and_search_scope_compiler"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocked_authority() -> Dict[str, Any]:
    return deepcopy(BLOCKED_AUTHORITY)


def _normalize_query(query: str) -> str:
    return " ".join((query or "").strip().split())


def detect_query_intent(query: str, route_context: str = "web_source_search") -> Dict[str, Any]:
    q = _normalize_query(query).lower()
    route = (route_context or "web_source_search").strip().lower()

    keyword_map = {
        "software_update": ["update", "version", "release", "changelog", "patch", "package"],
        "official_documentation": ["docs", "documentation", "api", "sdk", "manual", "install"],
        "market_signal": ["market", "stock", "portfolio", "earnings", "price", "trend"],
        "regulatory": ["regulation", "compliance", "law", "sec", "fda", "standard", "policy"],
        "breakthrough_scan": ["breakthrough", "invention", "patent", "novel", "discovery"],
        "source_health": ["source", "provider", "allowlist", "denylist", "trust", "search"],
    }

    matched: List[str] = []
    for intent, words in keyword_map.items():
        if any(word in q for word in words):
            matched.append(intent)

    if not matched:
        if "portfolio" in route:
            matched.append("market_signal")
        elif "design" in route:
            matched.append("official_documentation")
        else:
            matched.append("general_research")

    risk_flags: List[str] = []
    if any(term in q for term in ["buy", "sell", "trade", "brokerage", "portfolio"]):
        risk_flags.append("financial_decision_support_requires_review")
    if any(term in q for term in ["legal", "law", "regulation", "compliance"]):
        risk_flags.append("legal_or_regulatory_context_requires_primary_sources")
    if any(term in q for term in ["install", "execute", "command", "run", "package"]):
        risk_flags.append("execution_or_install_language_detected_but_blocked")
    if any(term in q for term in ["crawl", "scrape", "autonomous", "body read"]):
        risk_flags.append("web_body_or_crawling_language_detected_but_blocked")

    return {
        "primary_intent": matched[0],
        "matched_intents": matched,
        "risk_flags": risk_flags,
        "route_context": route,
        "query_empty": not bool(q),
    }


def build_source_scope(query: str, route_context: str = "web_source_search") -> List[Dict[str, Any]]:
    intent = detect_query_intent(query, route_context)
    primary = intent["primary_intent"]

    order_by_intent = {
        "software_update": ["official_docs", "regulatory_or_standards", "open_web"],
        "official_documentation": ["official_docs", "regulatory_or_standards", "open_web"],
        "market_signal": ["market_data", "official_docs", "news_signal", "open_web"],
        "regulatory": ["regulatory_or_standards", "official_docs", "news_signal"],
        "breakthrough_scan": ["official_docs", "market_data", "news_signal", "open_web"],
        "source_health": ["official_docs", "regulatory_or_standards", "open_web"],
        "general_research": ["official_docs", "regulatory_or_standards", "news_signal", "open_web"],
    }

    policy_by_family = {item["source_family"]: item for item in source_family_policy()}
    source_order = order_by_intent.get(primary, order_by_intent["general_research"])
    scope: List[Dict[str, Any]] = []

    for idx, family in enumerate(source_order, start=1):
        policy = policy_by_family.get(family, policy_by_family["open_web"])
        quarantine = policy["default_state"] in {"quarantine_by_default", "denied"} or family == "open_web"
        scope.append(
            {
                "rank": idx,
                "source_family": family,
                "trust_tier": policy["trust_tier"],
                "scope_state": "planned_only",
                "quarantine_required": quarantine,
                "body_read_allowed": False,
                "network_execution_allowed": False,
                "promotion_requirement": "operator_review_required",
                "why_selected": f"Selected for {primary} query planning.",
            }
        )

    return scope


def compile_query_terms(query: str) -> List[Dict[str, Any]]:
    q = _normalize_query(query)
    if not q:
        return [
            {
                "compiled_query_id": "s618_sample_query_01",
                "query_text": "governed source registry readiness",
                "query_role": "sample_placeholder",
                "execution_state": "not_executed",
            }
        ]

    return [
        {
            "compiled_query_id": "s618_exact_query_01",
            "query_text": f'"{q}"',
            "query_role": "exact_user_intent",
            "execution_state": "not_executed",
        },
        {
            "compiled_query_id": "s619_primary_source_query_01",
            "query_text": f"{q} official documentation source",
            "query_role": "primary_source_bias",
            "execution_state": "not_executed",
        },
        {
            "compiled_query_id": "s620_policy_context_query_01",
            "query_text": f"{q} standards policy release notes",
            "query_role": "policy_and_change_context",
            "execution_state": "not_executed",
        },
    ]


def build_evidence_path(query: str, route_context: str = "web_source_search") -> List[Dict[str, Any]]:
    scope = build_source_scope(query, route_context)
    return [
        {"step": 1, "name": "compile_query_without_execution", "state": "complete", "performs_network": False},
        {"step": 2, "name": "select_source_scope", "state": "complete", "source_scope_count": len(scope), "performs_network": False},
        {"step": 3, "name": "prepare_metadata_result_contract", "state": "prepared", "body_reads": "blocked", "performs_network": False},
        {"step": 4, "name": "operator_review_before_probe", "state": "required", "runtime_truth_mutation": "blocked", "performs_network": False},
    ]


def build_governed_query_plan(query: str = "", route_context: str = "web_source_search") -> Dict[str, Any]:
    normalized = _normalize_query(query)
    intent = detect_query_intent(normalized, route_context)
    scope = build_source_scope(normalized, route_context)
    compiled_terms = compile_query_terms(normalized)

    return {
        "plan_id": "s618_s624_governed_query_plan",
        "system": SYSTEM,
        "phase": PHASE,
        "gate": GATE_NAME,
        "generated_at": utc_now(),
        "status": "compiled_not_executed",
        "query": {"raw": query or "", "normalized": normalized, "empty": not bool(normalized)},
        "intent": intent,
        "source_scope": scope,
        "compiled_queries": compiled_terms,
        "trust_constraints": {
            "primary_sources_first": True,
            "open_web_quarantined": True,
            "denied_sources_blocked": True,
            "body_reads_blocked": True,
            "runtime_truth_requires_operator_review": True,
        },
        "evidence_path": build_evidence_path(normalized, route_context),
        "authority": blocked_authority(),
        "stop_gate": {
            "gate_id": "S624",
            "state": "pass_ready",
            "forward_motion_allowed": True,
            "allowed_next_phase": "S625-S631 provider capability map and probe readiness hardening",
            "search_execution_allowed": False,
            "blocked_authorities_preserved": True,
        },
    }


def build_query_cards(query: str = "", route_context: str = "web_source_search") -> List[Dict[str, Any]]:
    plan = build_governed_query_plan(query, route_context)
    return [
        {
            "card_id": "s618_query_intent_card",
            "card_type": "governed_query_intent",
            "title": "Query intent",
            "state": "compiled_not_executed",
            "summary": plan["intent"],
            "safe_to_render": True,
            "network_performed": False,
        },
        {
            "card_id": "s619_source_scope_card",
            "card_type": "governed_source_scope",
            "title": "Source scope",
            "state": "planned_only",
            "summary": {
                "source_families": [item["source_family"] for item in plan["source_scope"]],
                "scope_count": len(plan["source_scope"]),
            },
            "items": plan["source_scope"],
            "safe_to_render": True,
            "network_performed": False,
        },
        {
            "card_id": "s620_compiled_query_card",
            "card_type": "compiled_queries",
            "title": "Compiled query terms",
            "state": "not_executed",
            "items": plan["compiled_queries"],
            "safe_to_render": True,
            "network_performed": False,
        },
        {
            "card_id": "s623_evidence_path_card",
            "card_type": "planned_evidence_path",
            "title": "Evidence path",
            "state": "operator_review_required",
            "items": plan["evidence_path"],
            "safe_to_render": True,
            "network_performed": False,
        },
    ]


def build_query_actions(query: str = "", route_context: str = "web_source_search") -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "s618_compile_query_plan",
            "label": "Compile governed query plan",
            "tab": "Governed Web",
            "state": "available_non_executing",
            "execution_authority": "blocked",
            "description": "Compile intent, source scope, trust constraints, and evidence path without running a search.",
            "requires_operator": True,
            "performs_network": False,
            "mutates_runtime": False,
        },
        {
            "action_id": "s621_review_search_scope",
            "label": "Review search scope",
            "tab": "Actions",
            "state": "review_required",
            "execution_authority": "blocked",
            "description": "Review source family order, trust tiers, quarantine requirements, and blocked operations.",
            "requires_operator": True,
            "performs_network": False,
            "mutates_runtime": False,
        },
        {
            "action_id": "s624_stop_gate_provider_capability_map",
            "label": "Advance to provider capability map",
            "tab": "System",
            "state": "forward_motion_ready_after_pytest",
            "execution_authority": "blocked",
            "description": "Next phase maps provider capabilities and readiness while execution remains blocked.",
            "requires_operator": True,
            "performs_network": False,
            "mutates_runtime": False,
        },
    ]


def build_query_compiler_payload(query: str = "", route_context: str = "web_source_search") -> Dict[str, Any]:
    plan = build_governed_query_plan(query, route_context)
    return {
        "system": SYSTEM,
        "phase": PHASE,
        "gate": GATE_NAME,
        "generated_at": utc_now(),
        "status": "query_compiler_ready",
        "plan": plan,
        "cards": build_query_cards(query, route_context),
        "actions": build_query_actions(query, route_context),
        "policy": {
            "execution": "blocked",
            "body_reads": "blocked",
            "network_requests": "not_performed",
            "runtime_truth_mutation": "blocked",
            "operator_review_required": True,
        },
        "authority": blocked_authority(),
    }

