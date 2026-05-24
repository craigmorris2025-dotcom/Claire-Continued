from __future__ import annotations

"""
Governed Search Plan + Query Governance for Claire Syntalion.

This module builds non-live search plans that make Claire's intended search behavior
visible before any web execution is allowed. It does not call networks, read page
bodies, crawl, install packages, mutate runtime truth, or execute commands.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any

VERSION = "v19.89.8-S583-S589"

BLOCKED_CAPABILITIES: dict[str, bool] = {
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

SEARCH_INTENTS: dict[str, dict[str, Any]] = {
    "source_discovery": {
        "label": "Source discovery",
        "description": "Find candidate source families and map them to trust tiers without executing a search.",
        "preferred_tiers": ["tier_1_authoritative", "tier_2_reputable"],
    },
    "update_inspection": {
        "label": "Update inspection",
        "description": "Plan metadata-only checks for versions, release notes, standards, or policy changes.",
        "preferred_tiers": ["tier_1_authoritative"],
    },
    "technical_research": {
        "label": "Technical research",
        "description": "Plan official documentation and implementation evidence review.",
        "preferred_tiers": ["tier_1_authoritative", "tier_2_reputable"],
    },
    "technology_scan": {
        "label": "Technology scan",
        "description": "Plan current-technology, buildability, manufacturability, and invention-pattern evidence review.",
        "preferred_tiers": ["tier_1_authoritative", "tier_2_reputable", "technical_research_review_required"],
    },
    "patent_prior_art": {
        "label": "Patent / prior-art research",
        "description": "Plan patent, standards, novelty, and prior-art metadata review before design or breakthrough claims.",
        "preferred_tiers": ["tier_1_authoritative", "primary_public_record", "technical_research_review_required"],
    },
    "existing_system_ingestion": {
        "label": "Existing-system ingestion",
        "description": "Plan local/uploaded system decomposition plus external source corroboration.",
        "preferred_tiers": ["operator_master_documentation", "operator_pipeline_source", "tier_1_authoritative"],
    },
    "market_research": {
        "label": "Market / portfolio research",
        "description": "Plan financial, market, regulatory, and company source review with strong provenance.",
        "preferred_tiers": ["tier_1_authoritative", "tier_2_reputable"],
    },
    "general_research": {
        "label": "General governed research",
        "description": "Plan a governed evidence search with source mapping and operator review.",
        "preferred_tiers": ["tier_1_authoritative", "tier_2_reputable", "tier_3_contextual"],
    },
}

SENSITIVE_OPERATION_TERMS: tuple[str, ...] = (
    "install",
    "pip install",
    "download",
    "execute",
    "run command",
    "shell",
    "powershell",
    "runtime mutation",
    "mutate",
    "automatic update",
    "auto update",
    "crawl",
    "scrape",
    "body read",
    "read body",
    "package",
    "credential",
    "secret",
)

DEFAULT_QUERY_SAMPLES: list[str] = [
    "Check official FastAPI and Pydantic documentation for compatibility guidance",
    "Find authoritative sources for SEC filing changes and Federal Register updates",
    "Plan source discovery for technology evidence used by AutoDesign",
    "Map trustworthy market and portfolio evidence sources before any live search",
    "Prepare a governed update inspection plan for Claire dependencies",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_query(query: str) -> str:
    return " ".join((query or "").strip().split())


def _tokens(query: str) -> list[str]:
    normalized = normalize_query(query).lower()
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return [token for token in cleaned.split() if token]


def detect_search_intent(query: str, requested_intent: str | None = None) -> str:
    if requested_intent in SEARCH_INTENTS:
        return str(requested_intent)
    text = normalize_query(query).lower()
    if any(term in text for term in ("source", "domain", "allowlist", "trust", "tier", "registry")):
        return "source_discovery"
    if any(term in text for term in ("update", "version", "release", "changelog", "dependency", "package")):
        return "update_inspection"
    if any(term in text for term in ("patent", "prior art", "novelty", "uspto", "wipo", "claim", "standards")):
        return "patent_prior_art"
    if any(term in text for term in ("existing system", "system replacement", "decompose", "workflow map", "uploaded", "upload")):
        return "existing_system_ingestion"
    if any(term in text for term in ("manufacturable", "manufacturability", "buildability", "buildable", "invention", "autonomous invention", "technology database", "tech scanning", "design portal", "blueprint")):
        return "technology_scan"
    if any(term in text for term in ("api", "docs", "framework", "python", "fastapi", "pydantic", "architecture", "code")):
        return "technical_research"
    if any(term in text for term in ("market", "portfolio", "stock", "sec", "filing", "regulatory", "company", "competitor")):
        return "market_research"
    return "general_research"


def classify_query_risk(query: str) -> list[dict[str, Any]]:
    text = normalize_query(query).lower()
    flags: list[dict[str, Any]] = []
    for term in SENSITIVE_OPERATION_TERMS:
        if term in text:
            flags.append(
                {
                    "flag": "sensitive_operation_term",
                    "term": term,
                    "severity": "review_required",
                    "effect": "plan_only_execution_blocked",
                }
            )
    if not normalize_query(query):
        flags.append(
            {
                "flag": "empty_query",
                "term": "",
                "severity": "blocked_until_query_provided",
                "effect": "no_search_plan_execution",
            }
        )
    return flags


def get_source_registry_snapshot() -> dict[str, Any]:
    try:
        from runtime_core.governance.governed_source_registry import get_source_registry_payload

        payload = get_source_registry_payload()
        return {
            "available": True,
            "readiness": payload.get("readiness"),
            "summary": payload.get("summary", {}),
            "source_cards_available": len(payload.get("source_cards", [])),
            "policy_source": "claire.governance.governed_source_registry",
        }
    except Exception:
        return {
            "available": False,
            "readiness": "source_registry_not_loaded_fallback_policy_active",
            "summary": {"total_sources": 0, "review_required": 0, "quarantined": 0},
            "source_cards_available": 0,
            "policy_source": "fallback_non_live_policy",
        }


def build_source_scope(intent: str) -> dict[str, Any]:
    intent_info = SEARCH_INTENTS.get(intent, SEARCH_INTENTS["general_research"])
    registry = get_source_registry_snapshot()
    source_families = {
        "source_discovery": ["governed_source_registry", "source_allowlist", "local_upload_source_packs"],
        "update_inspection": ["official_release_notes", "package_indexes", "security_advisories", "repository_releases"],
        "technical_research": ["official_docs", "standards", "engineering_research", "implementation_examples"],
        "technology_scan": ["local_auto_invention_technology_database", "patents", "standards", "research", "engineering_signals"],
        "patent_prior_art": ["uspto", "wipo", "patent_metadata", "standards", "technical_research"],
        "existing_system_ingestion": ["local_master_docs", "local_pipeline_docs", "uploaded_system_docs", "architecture_docs"],
        "market_research": ["company_filings", "regulatory_records", "market_data", "public_company_sources"],
        "general_research": ["local_source_packs", "authoritative_web_metadata", "review_required_context"],
    }
    return {
        "intent": intent,
        "preferred_trust_tiers": list(intent_info["preferred_tiers"]),
        "preferred_source_families": source_families.get(intent, source_families["general_research"]),
        "local_authority_first": True,
        "source_selection_order": [
            "local uploaded/master source packs",
            "local runtime and technology database results",
            "tier_1_authoritative metadata candidates",
            "tier_2_reputable corroboration candidates",
            "tier_3_contextual review-only candidates",
            "tier_4_unknown quarantine review only",
        ],
        "registry_snapshot": registry,
        "allow_unknown_sources": False,
        "quarantine_unknown_sources": True,
        "operator_review_required": True,
    }


def build_query_expansion(normalized_query: str, intent: str) -> dict[str, Any]:
    base_terms = list(dict.fromkeys(_tokens(normalized_query)[:16]))
    expansions = {
        "technology_scan": ["buildability", "manufacturability", "deployment", "technical feasibility", "patent", "standards"],
        "patent_prior_art": ["patent", "prior art", "claims", "inventor", "assignee", "classification", "novelty"],
        "existing_system_ingestion": ["architecture", "workflow", "replacement", "decomposition", "requirements", "integration"],
        "market_research": ["market", "filings", "competitor", "acquirer", "portfolio", "regulatory"],
        "update_inspection": ["release notes", "changelog", "security advisory", "migration", "compatibility"],
        "technical_research": ["official documentation", "compatibility", "architecture", "implementation", "security"],
    }
    required_lenses = expansions.get(intent, ["evidence", "source", "date", "authority"])
    return {
        "original_terms": base_terms,
        "required_lenses": required_lenses,
        "combined_query_strategy": [
            "search local source packs first",
            "search local runtime and technology database second",
            "query live metadata provider only for missing proof",
            "quarantine results before evidence promotion",
        ],
        "negative_filters": [
            "speculative claims without source date",
            "science-fiction-only claims",
            "uncited generated content",
            "unverifiable body-only claims",
        ],
    }


def build_query_steps(intent: str) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "query.normalize",
            "label": "Normalize query",
            "status": "planned_complete",
            "execution_allowed": False,
            "notes": "Text-only normalization is allowed; no network request is performed.",
        },
        {
            "step_id": "query.intent_classify",
            "label": "Classify query intent",
            "status": "planned_complete",
            "execution_allowed": False,
            "notes": f"Intent selected: {intent}.",
        },
        {
            "step_id": "source.scope_map",
            "label": "Map source scope and trust tiers",
            "status": "planned_complete",
            "execution_allowed": False,
            "notes": "Uses governed source registry policy only; no provider call.",
        },
        {
            "step_id": "provider.metadata_probe_request",
            "label": "Prepare metadata-only provider probe request",
            "status": "planned_blocked_operator_gate_required",
            "execution_allowed": False,
            "notes": "This is only a request descriptor. Provider execution remains disabled.",
        },
        {
            "step_id": "evidence.basket_draft",
            "label": "Prepare evidence basket draft",
            "status": "planned_blocked_until_reviewed_results_exist",
            "execution_allowed": False,
            "notes": "No evidence is promoted, no body is read, and runtime truth is unchanged.",
        },
    ]


@dataclass(frozen=True)
class GovernedSearchPlan:
    plan_id: str
    raw_query: str
    normalized_query: str
    intent: str
    intent_label: str
    query_terms: tuple[str, ...]
    query_expansion: dict[str, Any] = field(default_factory=dict)
    risk_flags: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    source_scope: dict[str, Any] = field(default_factory=dict)
    query_steps: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "raw_query": self.raw_query,
            "normalized_query": self.normalized_query,
            "intent": self.intent,
            "intent_label": self.intent_label,
            "query_terms": list(self.query_terms),
            "query_expansion": self.query_expansion,
            "risk_flags": list(self.risk_flags),
            "source_scope": self.source_scope,
            "query_steps": list(self.query_steps),
            "execution_allowed": False,
            "provider_probe_allowed": False,
            "network_request_performed": False,
            "body_read_allowed": False,
            "runtime_truth_allowed": False,
            "requires_operator_review": True,
            "result_status": "plan_only_not_executed",
        }


def build_search_plan(query: str, requested_intent: str | None = None) -> dict[str, Any]:
    normalized = normalize_query(query)
    intent = detect_search_intent(normalized, requested_intent)
    intent_info = SEARCH_INTENTS[intent]
    query_terms = tuple(_tokens(normalized)[:16])
    seed = f"{VERSION}|{intent}|{normalized}".encode("utf-8")
    plan_id = "search-plan::" + sha1(seed).hexdigest()[:16]
    plan = GovernedSearchPlan(
        plan_id=plan_id,
        raw_query=query,
        normalized_query=normalized,
        intent=intent,
        intent_label=str(intent_info["label"]),
        query_terms=query_terms,
        query_expansion=build_query_expansion(normalized, intent),
        risk_flags=tuple(classify_query_risk(normalized)),
        source_scope=build_source_scope(intent),
        query_steps=tuple(build_query_steps(intent)),
    )
    return plan.to_dict()


def build_default_search_plans() -> list[dict[str, Any]]:
    return [build_search_plan(sample) for sample in DEFAULT_QUERY_SAMPLES]


def build_search_plan_cards(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for plan in plans:
        risk_count = len(plan.get("risk_flags", []))
        source_scope = plan.get("source_scope", {})
        cards.append(
            {
                "card_id": f"search-plan-card::{plan['plan_id']}",
                "title": plan.get("intent_label") or plan.get("intent") or "Governed search plan",
                "subtitle": plan.get("normalized_query") or "query unavailable",
                "status": "plan_only_execution_blocked",
                "badges": [
                    plan.get("intent", "general_research"),
                    "operator review required",
                    "risks " + str(risk_count),
                    "metadata only",
                ],
                "source_scope": source_scope,
                "steps": plan.get("query_steps", []),
                "policy": {
                    "execution_allowed": False,
                    "provider_probe_allowed": False,
                    "network_request_performed": False,
                    "body_read_allowed": False,
                    "runtime_truth_allowed": False,
                },
            }
        )
    return cards


def build_search_governed_actions(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_risks = sum(len(plan.get("risk_flags", [])) for plan in plans)
    return [
        {
            "action_id": "search_plan.review_plans",
            "label": "Review governed search plans",
            "status": "operator_review_required",
            "count": len(plans),
            "enabled": False,
            "execution_blocked": True,
            "reason": "Plans are visible for review; search provider execution remains blocked.",
        },
        {
            "action_id": "search_plan.inspect_query_risk",
            "label": "Inspect query risk flags",
            "status": "risk_review_ready",
            "count": total_risks,
            "enabled": False,
            "execution_blocked": True,
            "reason": "Risk inspection is cockpit-only and cannot execute commands or web calls.",
        },
        {
            "action_id": "search_plan.map_sources_to_query",
            "label": "Map sources to query intent",
            "status": "source_scope_ready",
            "count": len(plans),
            "enabled": False,
            "execution_blocked": True,
            "reason": "Source mapping uses existing registry metadata only; unknown sources remain quarantined.",
        },
        {
            "action_id": "search_plan.request_metadata_probe_gate",
            "label": "Request metadata-only probe gate",
            "status": "blocked_until_later_phase",
            "count": 0,
            "enabled": False,
            "execution_blocked": True,
            "reason": "This phase does not enable provider probes. It only prepares the action descriptor.",
        },
    ]


def build_search_evidence_cards(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for plan in plans:
        cards.append(
            {
                "evidence_card_id": f"search-plan-evidence::{plan['plan_id']}",
                "title": "Search plan evidence stub",
                "query": plan.get("normalized_query"),
                "intent": plan.get("intent"),
                "status": "no_external_evidence_collected",
                "network_request_performed": False,
                "body_read_allowed": False,
                "lineage": {
                    "created_by": VERSION,
                    "live_fetch": False,
                    "provider_execution": False,
                    "runtime_mutation": False,
                    "operator_promotion_required": True,
                },
                "review_notes": [
                    "This card represents a planned evidence path only.",
                    "No external source was contacted by this build.",
                ],
            }
        )
    return cards


def build_search_summary(plans: list[dict[str, Any]]) -> dict[str, Any]:
    intent_counts: dict[str, int] = {}
    risk_total = 0
    for plan in plans:
        intent = str(plan.get("intent") or "general_research")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        risk_total += len(plan.get("risk_flags", []))
    return {
        "total_plans": len(plans),
        "intent_counts": intent_counts,
        "risk_flags": risk_total,
        "provider_execution_allowed": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "automatic_updates_enabled": False,
        "runtime_mutation_enabled": False,
        "readiness": "governed_search_plan_ready_execution_blocked",
    }


def build_governed_search_plan_payload(queries: list[str] | None = None) -> dict[str, Any]:
    query_inputs = queries if queries is not None else list(DEFAULT_QUERY_SAMPLES)
    plans = [build_search_plan(query) for query in query_inputs]
    cards = build_search_plan_cards(plans)
    actions = build_search_governed_actions(plans)
    evidence_cards = build_search_evidence_cards(plans)
    return {
        "version": VERSION,
        "generated_at": now_iso(),
        "authority": "backend_search_governance_contract",
        "mode": "plan_only_non_live",
        "readiness": "governed_search_plan_ready_execution_blocked",
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "search_intents": SEARCH_INTENTS,
        "source_registry_snapshot": get_source_registry_snapshot(),
        "summary": build_search_summary(plans),
        "plans": plans,
        "search_plan_cards": cards,
        "governed_actions": actions,
        "evidence_cards": evidence_cards,
        "cockpit_panels": {
            "governed_web": {
                "title": "Governed Search Plan",
                "status": "plan_only_execution_blocked",
                "cards": cards,
            },
            "actions": {
                "title": "Search Plan Governed Actions",
                "status": "actions_registered_blocked",
                "actions": actions,
            },
            "evidence_review": {
                "title": "Search Plan Evidence Stubs",
                "status": "evidence_path_visible_no_collection",
                "cards": evidence_cards,
            },
        },
        "stop_gate": {
            "build": "S589",
            "status": "forward_motion_proof_ready",
            "next_phase": "S590-S596 Evidence Card Normalization + Review Surface",
            "may_continue": True,
            "blocks_preserved": True,
        },
    }


def get_governed_search_plan_payload() -> dict[str, Any]:
    return build_governed_search_plan_payload()


def get_governed_search_cards_payload() -> dict[str, Any]:
    payload = build_governed_search_plan_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "search_plan_cards": payload["search_plan_cards"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


def get_governed_search_actions_payload() -> dict[str, Any]:
    payload = build_governed_search_plan_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "governed_actions": payload["governed_actions"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


def get_governed_search_policy_payload() -> dict[str, Any]:
    payload = build_governed_search_plan_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "search_intents": payload["search_intents"],
        "source_registry_snapshot": payload["source_registry_snapshot"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }

