"""Governed provider/source readiness for Claire Syntalion S597-S603.

This module models where Claire may later search and what each provider is allowed
to do today. It is intentionally read-only and fail-closed: it performs no network
calls, reads no response bodies, executes no commands, installs no packages, and
mutates no runtime truth.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

S597_S603_VERSION = "v19.89.8-S597-S603"

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
        "allowed_uses": ["contract validation", "runtime status", "operator proof"],
        "default_review": "accepted as internal status only",
    },
    "tier_1_official": {
        "label": "Official / primary source",
        "allowed_uses": ["source discovery", "metadata proposal", "operator review"],
        "default_review": "manual promotion required",
    },
    "tier_2_reputable": {
        "label": "Reputable secondary source",
        "allowed_uses": ["corroboration", "comparison", "evidence basket support"],
        "default_review": "manual promotion required with corroboration",
    },
    "tier_3_open_web": {
        "label": "Open web / unverified source",
        "allowed_uses": ["candidate discovery only", "quarantine"],
        "default_review": "quarantine until reviewed",
    },
    "tier_4_blocked": {
        "label": "Blocked / denied source",
        "allowed_uses": [],
        "default_review": "do not use",
    },
}

@dataclass(frozen=True)
class ProviderReadiness:
    provider_id: str
    label: str
    provider_type: str
    trust_tier: str
    default_scope: str
    readiness: str
    configured: bool
    execution_allowed: bool
    body_read_allowed: bool
    network_allowed: bool
    evidence_policy: str
    allowed_operations: List[str] = field(default_factory=list)
    blocked_operations: List[str] = field(default_factory=list)
    required_operator_gate: str = "manual_review"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["blocked_reason"] = build_blocked_reason(data)
        data["trust_tier_label"] = TRUST_TIERS.get(self.trust_tier, {}).get("label", self.trust_tier)
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_blocked_reason(provider: Mapping[str, Any]) -> str:
    if provider.get("execution_allowed") is False:
        return "provider execution is governed and currently blocked"
    if provider.get("network_allowed") is False:
        return "network requests are blocked"
    if provider.get("body_read_allowed") is False:
        return "body reads are blocked"
    return "ready for governed operator review"


def default_provider_registry() -> List[ProviderReadiness]:
    return [
        ProviderReadiness(
            provider_id="google_search",
            label="Google Search Provider",
            provider_type="search_provider",
            trust_tier="tier_2_reputable",
            default_scope="web_search_metadata",
            readiness="configured_blocked",
            configured=True,
            execution_allowed=False,
            body_read_allowed=False,
            network_allowed=False,
            evidence_policy="metadata-only when operator gate is later opened; no body reads",
            allowed_operations=["readiness display", "operator preflight", "search plan preview"],
            blocked_operations=["live search execution", "result body read", "autonomous crawling"],
            required_operator_gate="provider_probe_gate",
            notes=["Used only for cockpit readiness and planned provider path at this phase."],
        ),
        ProviderReadiness(
            provider_id="official_vendor_docs",
            label="Official Vendor Documentation Sources",
            provider_type="source_family",
            trust_tier="tier_1_official",
            default_scope="official_docs_metadata",
            readiness="policy_ready_blocked",
            configured=True,
            execution_allowed=False,
            body_read_allowed=False,
            network_allowed=False,
            evidence_policy="official sources preferred for software/platform update facts after manual approval",
            allowed_operations=["source card", "trust tier classification", "review proposal"],
            blocked_operations=["uncontrolled fetch", "body ingestion", "automatic update"],
            required_operator_gate="source_review_gate",
            notes=["Primary candidate tier for future update/source verification."],
        ),
        ProviderReadiness(
            provider_id="market_financial_sources",
            label="Market / Financial Data Sources",
            provider_type="source_family",
            trust_tier="tier_1_official",
            default_scope="market_metadata_and_reference",
            readiness="policy_ready_blocked",
            configured=False,
            execution_allowed=False,
            body_read_allowed=False,
            network_allowed=False,
            evidence_policy="future portfolio routes require source-specific provenance and timestamps",
            allowed_operations=["source readiness card", "gap identification"],
            blocked_operations=["account integration", "brokerage action", "live market scrape"],
            required_operator_gate="financial_source_gate",
            notes=["No brokerage/account authority is enabled."],
        ),
        ProviderReadiness(
            provider_id="open_web_discovery",
            label="Open Web Discovery Sources",
            provider_type="source_family",
            trust_tier="tier_3_open_web",
            default_scope="candidate_discovery_only",
            readiness="quarantined_blocked",
            configured=True,
            execution_allowed=False,
            body_read_allowed=False,
            network_allowed=False,
            evidence_policy="candidate discovery only; quarantine before review",
            allowed_operations=["risk display", "quarantine policy explanation"],
            blocked_operations=["runtime truth promotion", "autonomous crawl", "untrusted body read"],
            required_operator_gate="quarantine_review_gate",
            notes=["Open web content cannot become runtime truth without manual review and corroboration."],
        ),
        ProviderReadiness(
            provider_id="blocked_untrusted_sources",
            label="Denied / Unsafe Source Patterns",
            provider_type="denylist_family",
            trust_tier="tier_4_blocked",
            default_scope="denylist",
            readiness="blocked",
            configured=True,
            execution_allowed=False,
            body_read_allowed=False,
            network_allowed=False,
            evidence_policy="do not use",
            allowed_operations=["denylist explanation"],
            blocked_operations=["all evidence operations", "all update operations", "all runtime operations"],
            required_operator_gate="not_allowed",
            notes=["Used to make deny policy visible rather than implicit."],
        ),
    ]


def provider_registry() -> Dict[str, Any]:
    providers = [provider.to_dict() for provider in default_provider_registry()]
    return {
        "version": S597_S603_VERSION,
        "generated_at": utc_now(),
        "phase": "S597-S603 governed provider/source readiness",
        "summary": {
            "provider_count": len(providers),
            "configured_count": sum(1 for p in providers if p["configured"]),
            "execution_allowed_count": sum(1 for p in providers if p["execution_allowed"]),
            "network_allowed_count": sum(1 for p in providers if p["network_allowed"]),
            "body_read_allowed_count": sum(1 for p in providers if p["body_read_allowed"]),
            "readiness": "provider_readiness_visible_execution_blocked",
        },
        "providers": providers,
        "blocked_flags": dict(BLOCKED_FLAGS),
        "trust_tiers": TRUST_TIERS,
    }


def provider_cards() -> Dict[str, Any]:
    cards: List[Dict[str, Any]] = []
    for provider in provider_registry()["providers"]:
        cards.append({
            "card_id": f"provider_card::{provider['provider_id']}",
            "title": provider["label"],
            "provider_id": provider["provider_id"],
            "provider_type": provider["provider_type"],
            "trust_tier": provider["trust_tier"],
            "trust_tier_label": provider["trust_tier_label"],
            "status": provider["readiness"],
            "configured": provider["configured"],
            "execution_allowed": provider["execution_allowed"],
            "network_allowed": provider["network_allowed"],
            "body_read_allowed": provider["body_read_allowed"],
            "primary_policy": provider["evidence_policy"],
            "blocked_reason": provider["blocked_reason"],
            "allowed_operations": provider["allowed_operations"],
            "blocked_operations": provider["blocked_operations"],
            "operator_gate": provider["required_operator_gate"],
            "ui_region": "Governed Web / Sources",
        })
    return {
        "version": S597_S603_VERSION,
        "generated_at": utc_now(),
        "card_count": len(cards),
        "cards": cards,
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def provider_actions() -> Dict[str, Any]:
    """Return visible actions. These are descriptors only; they are not executable."""
    actions = [
        {
            "action_id": "review_provider_readiness",
            "label": "Review provider readiness",
            "action_type": "review_descriptor",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "actions are visible for operator review but execution remains blocked",
            "target_endpoint": "/api/search/providers/readiness",
            "would_require": ["manual operator gate", "source policy review", "provider execution gate"],
        },
        {
            "action_id": "classify_source_for_search_plan",
            "label": "Classify source for search plan",
            "action_type": "classification_descriptor",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "classification is display-only in this phase",
            "target_endpoint": "/api/search/providers/cards",
            "would_require": ["source registry", "trust tier", "allowlist or quarantine policy"],
        },
        {
            "action_id": "prepare_provider_probe_request",
            "label": "Prepare provider probe request",
            "action_type": "preflight_descriptor",
            "enabled": False,
            "blocked": True,
            "blocked_reason": "provider probe execution remains blocked by current runway instruction",
            "target_endpoint": "/api/search/providers/status",
            "would_require": ["explicit future gate", "no body reads", "rate limit policy"],
        },
    ]
    return {
        "version": S597_S603_VERSION,
        "generated_at": utc_now(),
        "action_count": len(actions),
        "actions": actions,
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def provider_policy() -> Dict[str, Any]:
    return {
        "version": S597_S603_VERSION,
        "generated_at": utc_now(),
        "policy_name": "governed_provider_readiness_policy",
        "rules": [
            "Provider/source readiness may be displayed in cockpit.",
            "Provider execution remains disabled.",
            "Network request authority remains disabled.",
            "Body reads remain disabled.",
            "Open web sources remain quarantined unless manually promoted in a later governed phase.",
            "Automatic updates, runtime mutation, command execution, package download, and package install remain disabled.",
        ],
        "trust_tiers": TRUST_TIERS,
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def provider_status() -> Dict[str, Any]:
    registry = provider_registry()
    return {
        "version": S597_S603_VERSION,
        "generated_at": utc_now(),
        "status": "governed_provider_readiness_visible",
        "readiness": registry["summary"]["readiness"],
        "provider_count": registry["summary"]["provider_count"],
        "execution_allowed": False,
        "network_allowed": False,
        "body_read_allowed": False,
        "automatic_updates_enabled": False,
        "runtime_mutation_enabled": False,
        "blocked_flags": dict(BLOCKED_FLAGS),
    }


def provider_payload() -> Dict[str, Any]:
    return {
        "version": S597_S603_VERSION,
        "generated_at": utc_now(),
        "registry": provider_registry(),
        "cards": provider_cards(),
        "actions": provider_actions(),
        "policy": provider_policy(),
        "status": provider_status(),
    }


def build_stop_gate() -> Dict[str, Any]:
    payload = provider_payload()
    flags = payload["status"]["blocked_flags"]
    return {
        "version": S597_S603_VERSION,
        "stop_gate": "S603",
        "passed": all(value is False for value in flags.values()),
        "forward_motion": "allowed_to_next_governed_source_search_phase_only",
        "next_recommended_phase": "S604-S610 governed source gap matrix and search scope planner",
        "must_remain_blocked": sorted(flags.keys()),
    }
