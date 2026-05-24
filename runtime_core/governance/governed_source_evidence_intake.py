from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List


PHASE = "S611-S617"
SYSTEM = "Claire Syntalion"
GATE_NAME = "governed_source_evidence_intake_gate"


BLOCKED_AUTHORITY: Dict[str, Any] = {
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


SOURCE_FAMILY_POLICY: List[Dict[str, Any]] = [
    {
        "source_family": "official_docs",
        "trust_tier": "tier_1_primary",
        "default_state": "allowed_for_planning",
        "intake_permission": "metadata_descriptor_only",
        "body_read_permission": "blocked",
        "examples": ["official product documentation", "vendor API documentation", "release notes"],
        "allowed_use": ["source planning", "metadata card preparation", "operator review"],
    },
    {
        "source_family": "regulatory_or_standards",
        "trust_tier": "tier_1_primary",
        "default_state": "allowed_for_planning",
        "intake_permission": "metadata_descriptor_only",
        "body_read_permission": "blocked",
        "examples": ["regulators", "standards bodies", "government publications"],
        "allowed_use": ["policy-aware source planning", "compliance evidence planning"],
    },
    {
        "source_family": "market_data",
        "trust_tier": "tier_2_structured",
        "default_state": "allowed_for_planning",
        "intake_permission": "metadata_descriptor_only",
        "body_read_permission": "blocked",
        "examples": ["market-data providers", "exchange pages", "financial data pages"],
        "allowed_use": ["market signal planning", "portfolio route source planning"],
    },
    {
        "source_family": "news_signal",
        "trust_tier": "tier_3_context",
        "default_state": "quarantine_by_default",
        "intake_permission": "metadata_descriptor_only",
        "body_read_permission": "blocked",
        "examples": ["news articles", "press coverage", "industry coverage"],
        "allowed_use": ["context signal planning", "quarantined evidence review"],
    },
    {
        "source_family": "open_web",
        "trust_tier": "tier_4_untrusted_until_reviewed",
        "default_state": "quarantine_by_default",
        "intake_permission": "metadata_descriptor_only",
        "body_read_permission": "blocked",
        "examples": ["general web pages", "blogs", "public websites"],
        "allowed_use": ["low-trust context only after review"],
    },
    {
        "source_family": "denied_or_unsafe",
        "trust_tier": "denied",
        "default_state": "denied",
        "intake_permission": "blocked",
        "body_read_permission": "blocked",
        "examples": ["malware", "credential dumps", "piracy", "private data leaks"],
        "allowed_use": [],
    },
]


@dataclass(frozen=True)
class SourceEvidenceCandidate:
    candidate_id: str
    source_family: str
    trust_tier: str
    intake_state: str
    title: str
    evidence_goal: str
    planned_metadata_fields: List[str]
    blocked_operations: List[str]
    review_requirement: str
    promotion_state: str

    def to_card(self) -> Dict[str, Any]:
        data = asdict(self)
        data["card_type"] = "source_evidence_intake"
        data["display_state"] = "review_required"
        data["safe_to_render"] = True
        data["runtime_truth"] = False
        data["body_text"] = None
        data["network_performed"] = False
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocked_authority() -> Dict[str, Any]:
    return deepcopy(BLOCKED_AUTHORITY)


def source_family_policy() -> List[Dict[str, Any]]:
    return deepcopy(SOURCE_FAMILY_POLICY)


def _policy_for_family(source_family: str) -> Dict[str, Any]:
    normalized = (source_family or "").strip().lower()
    for item in SOURCE_FAMILY_POLICY:
        if item["source_family"] == normalized:
            return deepcopy(item)
    return deepcopy(next(item for item in SOURCE_FAMILY_POLICY if item["source_family"] == "open_web"))


def build_source_evidence_candidates(query: str = "", route_context: str = "web_source_search") -> List[SourceEvidenceCandidate]:
    query_text = (query or "").strip()
    topic = query_text if query_text else "governed source/search readiness"
    candidates: List[SourceEvidenceCandidate] = []

    for idx, family in enumerate(["official_docs", "regulatory_or_standards", "market_data", "news_signal", "open_web"], start=1):
        policy = _policy_for_family(family)
        default_state = policy["default_state"]
        intake_state = "planned_review_only" if default_state != "denied" else "blocked"

        if family in {"news_signal", "open_web"}:
            intake_state = "quarantined_planning_only"

        candidates.append(
            SourceEvidenceCandidate(
                candidate_id=f"s611_source_candidate_{idx:02d}",
                source_family=family,
                trust_tier=policy["trust_tier"],
                intake_state=intake_state,
                title=f"{family.replace('_', ' ').title()} evidence candidate",
                evidence_goal=f"Prepare metadata-only review path for: {topic}",
                planned_metadata_fields=[
                    "source_family",
                    "trust_tier",
                    "title_or_descriptor",
                    "publisher_or_owner",
                    "retrieval_status",
                    "operator_review_state",
                    "promotion_eligibility",
                ],
                blocked_operations=[
                    "network_request",
                    "body_read",
                    "autonomous_crawl",
                    "runtime_truth_mutation",
                    "automatic_update",
                ],
                review_requirement="operator_review_required_before_promotion",
                promotion_state="not_promotable_without_review",
            )
        )

    return candidates


def build_source_evidence_cards(query: str = "", route_context: str = "web_source_search") -> List[Dict[str, Any]]:
    return [candidate.to_card() for candidate in build_source_evidence_candidates(query, route_context)]


def build_source_review_queue(query: str = "", route_context: str = "web_source_search") -> Dict[str, Any]:
    cards = build_source_evidence_cards(query, route_context)
    return {
        "queue_name": "governed_source_evidence_intake_review",
        "queue_state": "prepared_empty_runtime_truth",
        "review_total": len(cards),
        "pending_review_total": len(cards),
        "approved_total": 0,
        "rejected_total": 0,
        "promoted_to_runtime_truth_total": 0,
        "cards": cards,
        "notes": [
            "Cards are planning/review descriptors only.",
            "No source body has been read.",
            "No network request has been performed.",
            "No evidence is promoted to runtime truth by this gate.",
        ],
    }


def build_source_intake_actions(query: str = "", route_context: str = "web_source_search") -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "s611_prepare_source_review",
            "label": "Prepare source review cards",
            "tab": "Evidence & Review",
            "state": "available_non_executing",
            "execution_authority": "blocked",
            "description": "Build metadata-only source evidence cards for operator review.",
            "requires_operator": True,
            "performs_network": False,
            "mutates_runtime": False,
        },
        {
            "action_id": "s613_mark_source_family_policy",
            "label": "Review source-family policy",
            "tab": "Governed Web",
            "state": "available_non_executing",
            "execution_authority": "blocked",
            "description": "Inspect trust tier, quarantine, allowlist, and denylist posture.",
            "requires_operator": True,
            "performs_network": False,
            "mutates_runtime": False,
        },
        {
            "action_id": "s616_hold_for_query_compiler",
            "label": "Hold for governed query compiler",
            "tab": "Actions",
            "state": "blocked_until_query_plan_review",
            "execution_authority": "blocked",
            "description": "Do not execute search. Wait for the search scope compiler and operator review.",
            "requires_operator": True,
            "performs_network": False,
            "mutates_runtime": False,
        },
    ]


def build_source_evidence_intake_payload(query: str = "", route_context: str = "web_source_search") -> Dict[str, Any]:
    cards = build_source_evidence_cards(query, route_context)
    return {
        "system": SYSTEM,
        "phase": PHASE,
        "gate": GATE_NAME,
        "generated_at": utc_now(),
        "status": "ready_for_operator_review",
        "summary": {
            "headline": "Governed source evidence intake is prepared without live execution.",
            "query": query or "",
            "route_context": route_context,
            "cards_total": len(cards),
            "runtime_truth_mutation": "blocked",
            "body_reads": "blocked",
            "network_requests": "not_performed",
        },
        "authority": blocked_authority(),
        "policy": {
            "source_families": source_family_policy(),
            "default_body_read": "blocked",
            "default_promotion_state": "operator_review_required",
            "default_quarantine_state": "quarantine_by_default_for_non_primary_sources",
        },
        "cards": cards,
        "review_queue": build_source_review_queue(query, route_context),
        "actions": build_source_intake_actions(query, route_context),
        "stop_gate": {
            "gate_id": "S617",
            "state": "pass_ready",
            "forward_motion_allowed": True,
            "allowed_next_phase": "S618-S624 governed query builder and search scope compiler",
            "blocked_authorities_preserved": True,
        },
    }

