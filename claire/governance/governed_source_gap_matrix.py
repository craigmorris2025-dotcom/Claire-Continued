"""Governed source gap matrix and search scope planner for Claire Syntalion S604-S610.

This module is a read-only planning/visibility layer. It identifies what source families
Claire can reason about, what is missing before trusted search/update use, which cockpit
cards should be shown, and which governed actions should appear for operator review.
It performs no network calls, reads no response bodies, executes no commands, mutates no
runtime truth, and installs/downloads no packages.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

S604_S610_VERSION = "v19.89.8-S604-S610"

BLOCKED_FLAGS: Dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

TRUST_TIERS: Dict[str, Dict[str, Any]] = {
    "tier_0_system": {
        "label": "System-owned canonical truth",
        "default_status": "available_internal_only",
        "promotion_rule": "already internal status; not external evidence",
    },
    "tier_1_official": {
        "label": "Official / primary source",
        "default_status": "preferred_for_future_verified_search",
        "promotion_rule": "manual promotion after operator review",
    },
    "tier_2_reputable": {
        "label": "Reputable secondary source",
        "default_status": "corroboration_only",
        "promotion_rule": "manual promotion with corroboration",
    },
    "tier_3_open_web": {
        "label": "Open web / unverified",
        "default_status": "quarantine_first",
        "promotion_rule": "cannot promote without review and corroboration",
    },
    "tier_4_blocked": {
        "label": "Denied / unsafe source pattern",
        "default_status": "blocked",
        "promotion_rule": "never promote",
    },
}

@dataclass(frozen=True)
class SourceGap:
    source_family_id: str
    label: str
    trust_tier: str
    route_relevance: List[str]
    current_state: str
    missing_before_use: List[str]
    allowed_now: List[str]
    blocked_now: List[str]
    evidence_required: List[str]
    cockpit_region: str = "Governed Web / Source Gaps"
    priority: str = "medium"
    owner: str = "operator_review"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["trust_tier_label"] = TRUST_TIERS.get(self.trust_tier, {}).get("label", self.trust_tier)
        data["gap_count"] = len(self.missing_before_use)
        data["blocked_reason"] = build_blocked_reason(data)
        return data


@dataclass(frozen=True)
class SearchScopePlan:
    plan_id: str
    query_intent: str
    user_visible_label: str
    preferred_source_families: List[str]
    fallback_source_families: List[str]
    denied_source_families: List[str]
    evidence_path: List[str]
    required_trust_tiers: List[str]
    blocked_capabilities: List[str]
    allowed_now: List[str] = field(default_factory=list)
    status: str = "plan_only_blocked"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["execution_allowed"] = False
        data["network_allowed"] = False
        data["body_read_allowed"] = False
        data["runtime_mutation_allowed"] = False
        data["blocked_flags"] = dict(BLOCKED_FLAGS)
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_blocked_reason(source_gap: Mapping[str, Any]) -> str:
    if source_gap.get("trust_tier") == "tier_4_blocked":
        return "source family is denied by policy"
    if BLOCKED_FLAGS["live_web_execution_enabled"] is False:
        return "live web/search execution remains blocked; source is visible for planning only"
    return "manual review required before source use"


def _base_source_gaps() -> List[SourceGap]:
    return [
        SourceGap(
            source_family_id="system_runtime_truth",
            label="Claire Runtime Truth / Existing Backend Contracts",
            trust_tier="tier_0_system",
            route_relevance=["system", "dashboard", "runtime", "proof"],
            current_state="available_internal_only",
            missing_before_use=["none for internal status display", "external evidence still requires separate source review"],
            allowed_now=["status display", "contract proof", "operator cockpit visibility"],
            blocked_now=["external fact substitution", "runtime mutation", "automatic update execution"],
            evidence_required=["active endpoint", "timestamp", "contract owner"],
            priority="high",
        ),
        SourceGap(
            source_family_id="official_software_docs",
            label="Official Software / Platform Documentation",
            trust_tier="tier_1_official",
            route_relevance=["updates", "packages", "runtime compatibility", "technology intelligence"],
            current_state="policy_defined_execution_blocked",
            missing_before_use=["approved domain allowlist", "operator-selected scope", "metadata-only probe approval", "source timestamp capture"],
            allowed_now=["source card", "gap card", "search scope preview", "review action descriptor"],
            blocked_now=["live fetch", "body read", "automatic package update", "runtime mutation"],
            evidence_required=["official domain", "version/date", "retrieval method", "manual promotion decision"],
            priority="high",
        ),
        SourceGap(
            source_family_id="official_market_sources",
            label="Official Market / Financial Reference Sources",
            trust_tier="tier_1_official",
            route_relevance=["portfolio", "market signals", "trend discovery"],
            current_state="identified_not_connected",
            missing_before_use=["approved source list", "financial data policy", "timestamp policy", "no brokerage action guarantee"],
            allowed_now=["gap display", "scope planning", "route relevance mapping"],
            blocked_now=["brokerage connection", "account action", "live market scrape", "investment execution"],
            evidence_required=["source authority", "data timestamp", "licensing/usage status", "manual review"],
            priority="high",
        ),
        SourceGap(
            source_family_id="reputable_secondary_sources",
            label="Reputable Secondary / Corroboration Sources",
            trust_tier="tier_2_reputable",
            route_relevance=["corroboration", "news context", "competitive analysis"],
            current_state="corroboration_policy_defined_execution_blocked",
            missing_before_use=["source reputation rule", "cross-source confirmation rule", "citation capture"],
            allowed_now=["corroboration plan", "trust gap display"],
            blocked_now=["single-source promotion", "body ingestion", "truth mutation"],
            evidence_required=["publisher/source", "date", "corroborating official source when available"],
            priority="medium",
        ),
        SourceGap(
            source_family_id="open_web_discovery",
            label="Open Web Discovery Candidates",
            trust_tier="tier_3_open_web",
            route_relevance=["early discovery", "weak signals", "candidate leads"],
            current_state="quarantine_policy_defined_execution_blocked",
            missing_before_use=["quarantine review queue", "source risk labeling", "manual promotion rule", "body-read gate"],
            allowed_now=["candidate-scope planning", "risk display", "quarantine route preview"],
            blocked_now=["autonomous crawl", "untrusted body read", "runtime truth promotion"],
            evidence_required=["source URL/domain", "why candidate matters", "risk label", "corroboration requirement"],
            priority="medium",
        ),
        SourceGap(
            source_family_id="denied_source_patterns",
            label="Denied / Unsafe Source Patterns",
            trust_tier="tier_4_blocked",
            route_relevance=["safety", "source governance"],
            current_state="blocked",
            missing_before_use=["not eligible for use"],
            allowed_now=["denylist display", "blocked reason display"],
            blocked_now=["search", "fetch", "crawl", "promotion", "package install"],
            evidence_required=["denylist match reason"],
            priority="critical",
        ),
    ]


def source_gap_matrix() -> Dict[str, Any]:
    gaps = [gap.to_dict() for gap in _base_source_gaps()]
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda item: (priority_order.get(item.get("priority", "medium"), 9), item.get("source_family_id", "")))
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "matrix_id": "governed_source_gap_matrix::s604_s610",
        "status": "source_gap_matrix_ready_blocked",
        "source_family_count": len(gaps),
        "blocked_flags": dict(BLOCKED_FLAGS),
        "trust_tiers": dict(TRUST_TIERS),
        "source_gaps": gaps,
        "summary": {
            "critical_gaps": [gap["source_family_id"] for gap in gaps if gap["priority"] == "critical"],
            "high_priority_gaps": [gap["source_family_id"] for gap in gaps if gap["priority"] == "high"],
            "visible_in_cockpit": True,
            "execution_allowed": False,
            "network_allowed": False,
            "body_read_allowed": False,
        },
    }


def search_scope_plans() -> Dict[str, Any]:
    plans = [
        SearchScopePlan(
            plan_id="scope_plan::software_update_check",
            query_intent="software_update_check",
            user_visible_label="Check software/package update information",
            preferred_source_families=["official_software_docs"],
            fallback_source_families=["reputable_secondary_sources"],
            denied_source_families=["open_web_discovery", "denied_source_patterns"],
            evidence_path=["source card", "metadata proposal", "manual review", "promotion decision packet"],
            required_trust_tiers=["tier_1_official"],
            blocked_capabilities=["live fetch", "body read", "automatic update", "package install"],
            allowed_now=["plan preview", "source gap display", "operator review action descriptor"],
        ),
        SearchScopePlan(
            plan_id="scope_plan::market_signal_discovery",
            query_intent="market_signal_discovery",
            user_visible_label="Discover market/portfolio signals from governed sources",
            preferred_source_families=["official_market_sources", "reputable_secondary_sources"],
            fallback_source_families=["open_web_discovery"],
            denied_source_families=["denied_source_patterns"],
            evidence_path=["source scope", "timestamped evidence", "trust score", "manual review", "route-specific output"],
            required_trust_tiers=["tier_1_official", "tier_2_reputable"],
            blocked_capabilities=["brokerage action", "live market scrape", "autonomous crawl", "runtime mutation"],
            allowed_now=["scope plan", "gap card", "evidence requirement display"],
        ),
        SearchScopePlan(
            plan_id="scope_plan::open_discovery_candidate",
            query_intent="open_discovery_candidate",
            user_visible_label="Explore open-web discovery candidates safely",
            preferred_source_families=["reputable_secondary_sources"],
            fallback_source_families=["open_web_discovery"],
            denied_source_families=["denied_source_patterns"],
            evidence_path=["candidate only", "quarantine", "risk label", "corroboration", "manual promotion"],
            required_trust_tiers=["tier_2_reputable", "tier_3_open_web"],
            blocked_capabilities=["body read", "autonomous crawling", "truth promotion without review"],
            allowed_now=["candidate plan", "quarantine preview", "review action descriptor"],
        ),
        SearchScopePlan(
            plan_id="scope_plan::system_self_audit",
            query_intent="system_self_audit",
            user_visible_label="Review Claire internal runtime/source readiness",
            preferred_source_families=["system_runtime_truth"],
            fallback_source_families=[],
            denied_source_families=["denied_source_patterns"],
            evidence_path=["backend status", "contract proof", "cockpit card", "operator report"],
            required_trust_tiers=["tier_0_system"],
            blocked_capabilities=["runtime mutation", "automatic repair", "command execution"],
            allowed_now=["internal status display", "proof report", "dashboard card"],
        ),
    ]
    rendered = [plan.to_dict() for plan in plans]
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "status": "search_scope_plans_ready_blocked",
        "plan_count": len(rendered),
        "plans": rendered,
        "blocked_flags": dict(BLOCKED_FLAGS),
        "policy": {
            "execution_allowed": False,
            "network_allowed": False,
            "body_read_allowed": False,
            "planning_only": True,
        },
    }


def source_gap_cards() -> Dict[str, Any]:
    matrix = source_gap_matrix()
    cards: List[Dict[str, Any]] = []
    for gap in matrix["source_gaps"]:
        cards.append({
            "card_id": f"source_gap_card::{gap['source_family_id']}",
            "title": gap["label"],
            "subtitle": gap["trust_tier_label"],
            "status": gap["current_state"],
            "priority": gap["priority"],
            "ui_region": gap["cockpit_region"],
            "route_relevance": gap["route_relevance"],
            "missing_before_use": gap["missing_before_use"],
            "allowed_now": gap["allowed_now"],
            "blocked_now": gap["blocked_now"],
            "evidence_required": gap["evidence_required"],
            "blocked_reason": gap["blocked_reason"],
            "execution_allowed": False,
            "network_allowed": False,
            "body_read_allowed": False,
        })
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "card_count": len(cards),
        "cards": cards,
        "presentation_mode": "cockpit_cards_not_raw_json",
    }


def search_scope_cards() -> Dict[str, Any]:
    plan_payload = search_scope_plans()
    cards: List[Dict[str, Any]] = []
    for plan in plan_payload["plans"]:
        cards.append({
            "card_id": f"search_scope_card::{plan['query_intent']}",
            "title": plan["user_visible_label"],
            "status": plan["status"],
            "ui_region": "Governed Web / Search Scope",
            "preferred_source_families": plan["preferred_source_families"],
            "fallback_source_families": plan["fallback_source_families"],
            "denied_source_families": plan["denied_source_families"],
            "evidence_path": plan["evidence_path"],
            "blocked_capabilities": plan["blocked_capabilities"],
            "allowed_now": plan["allowed_now"],
            "execution_allowed": False,
            "network_allowed": False,
            "body_read_allowed": False,
        })
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "card_count": len(cards),
        "cards": cards,
        "presentation_mode": "cockpit_cards_not_raw_json",
    }


def source_gap_actions() -> Dict[str, Any]:
    actions = [
        {
            "action_id": "source_gap.review_allowlist_requirements",
            "label": "Review allowlist requirements",
            "target_region": "Actions / Governed Web",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "operator review action only; source use remains blocked",
            "would_require": ["approved source owner", "trust tier", "manual decision"],
            "does_not_perform": ["network request", "body read", "source promotion"],
        },
        {
            "action_id": "source_gap.prepare_metadata_probe_scope",
            "label": "Prepare metadata probe scope",
            "target_region": "Actions / Search Scope",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "metadata probing is not enabled in this phase",
            "would_require": ["operator gate", "source scope", "rate policy", "audit log"],
            "does_not_perform": ["provider execution", "fetch", "crawl"],
        },
        {
            "action_id": "source_gap.open_quarantine_review_plan",
            "label": "Open quarantine review plan",
            "target_region": "Evidence & Review",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "quarantine queue is visible but no external evidence is ingested here",
            "would_require": ["candidate source", "risk label", "manual review"],
            "does_not_perform": ["truth mutation", "automatic promotion", "body ingestion"],
        },
        {
            "action_id": "source_gap.generate_stop_gate_proof",
            "label": "Generate S610 stop-gate proof",
            "target_region": "System",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "proof is exposed by read-only endpoint, not by executable UI action",
            "would_require": ["read stop-gate endpoint"],
            "does_not_perform": ["command execution", "mutation"],
        },
    ]
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "action_count": len(actions),
        "actions": actions,
        "all_actions_non_executable": all(not action["enabled"] and action["blocked"] for action in actions),
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def source_gap_policy() -> Dict[str, Any]:
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "policy_id": "governed_source_gap_policy::s604_s610",
        "rules": [
            "Source gap cards may be displayed without enabling network or provider execution.",
            "Search scope plans are planning artifacts only and cannot execute searches.",
            "Official sources are preferred for future update/package facts but still require manual approval.",
            "Open web candidates remain quarantined and cannot become runtime truth without review.",
            "Body reads remain disabled.",
            "Automatic updates, runtime mutation, package download/install, autonomous crawling, and command execution remain disabled.",
        ],
        "blocked_flags": dict(BLOCKED_FLAGS),
        "trust_tiers": dict(TRUST_TIERS),
    }


def source_gap_status() -> Dict[str, Any]:
    matrix = source_gap_matrix()
    plans = search_scope_plans()
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "status": "governed_source_gap_matrix_ready",
        "readiness": "source_search_planning_visible_execution_blocked",
        "source_family_count": matrix["source_family_count"],
        "search_scope_plan_count": plans["plan_count"],
        "source_gap_cards_ready": True,
        "search_scope_cards_ready": True,
        "actions_visible": True,
        "actions_executable": False,
        "execution_allowed": False,
        "network_allowed": False,
        "body_read_allowed": False,
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def governed_source_gap_payload() -> Dict[str, Any]:
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "status": source_gap_status(),
        "matrix": source_gap_matrix(),
        "search_scope_plans": search_scope_plans(),
        "source_gap_cards": source_gap_cards(),
        "search_scope_cards": search_scope_cards(),
        "actions": source_gap_actions(),
        "policy": source_gap_policy(),
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def build_stop_gate() -> Dict[str, Any]:
    blocked_ok = all(value is False for value in BLOCKED_FLAGS.values())
    payload = governed_source_gap_payload()
    return {
        "version": S604_S610_VERSION,
        "generated_at": utc_now(),
        "stop_gate": "S610",
        "passed": blocked_ok
        and payload["status"]["source_gap_cards_ready"] is True
        and payload["status"]["actions_visible"] is True
        and payload["status"]["actions_executable"] is False,
        "proof": {
            "source_gap_matrix_ready": payload["matrix"]["source_family_count"] >= 5,
            "search_scope_plans_ready": payload["search_scope_plans"]["plan_count"] >= 4,
            "cards_ready": payload["source_gap_cards"]["card_count"] >= 5,
            "actions_non_executable": payload["actions"]["all_actions_non_executable"],
        },
        "must_remain_blocked": list(BLOCKED_FLAGS.keys()),
        "blocked_flags": dict(BLOCKED_FLAGS),
        "next_recommended_phase": "S611-S617 governed metadata probe authorization surfaces",
    }
