from __future__ import annotations

"""
Governed Source Registry for Claire Syntalion.

This module is a fail-closed, non-live source governance layer. It classifies source
records, builds cockpit-safe cards, and exposes governed action descriptors without
performing web execution, package installation, body reads, autonomous crawling, or
runtime mutation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

VERSION = "v19.89.8-S576-S582"

BLOCKED_CAPABILITIES: dict[str, bool] = {
    "live_web_execution_enabled": False,
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

TRUST_TIERS: dict[str, dict[str, Any]] = {
    "tier_0_blocked": {
        "rank": 0,
        "label": "Blocked / denied",
        "default_status": "denied",
        "runtime_truth_allowed": False,
        "body_read_allowed": False,
        "requires_operator_review": True,
        "description": "Explicitly denied or unsafe sources. Metadata and body reads remain blocked.",
    },
    "tier_1_authoritative": {
        "rank": 1,
        "label": "Authoritative primary",
        "default_status": "allowlisted_metadata_only",
        "runtime_truth_allowed": False,
        "body_read_allowed": False,
        "requires_operator_review": True,
        "description": "Primary official, regulatory, standards, court, or vendor documentation sources.",
    },
    "tier_2_reputable": {
        "rank": 2,
        "label": "Reputable secondary",
        "default_status": "review_required",
        "runtime_truth_allowed": False,
        "body_read_allowed": False,
        "requires_operator_review": True,
        "description": "Established secondary sources that can support evidence baskets after review.",
    },
    "tier_3_contextual": {
        "rank": 3,
        "label": "Contextual / community",
        "default_status": "quarantine_by_default",
        "runtime_truth_allowed": False,
        "body_read_allowed": False,
        "requires_operator_review": True,
        "description": "Useful context only. Must not drive runtime truth without stronger corroboration.",
    },
    "tier_4_unknown": {
        "rank": 4,
        "label": "Unknown / unclassified",
        "default_status": "quarantine_by_default",
        "runtime_truth_allowed": False,
        "body_read_allowed": False,
        "requires_operator_review": True,
        "description": "Unknown sources remain quarantined until explicitly classified by an operator.",
    },
}

DEFAULT_POLICY: dict[str, Any] = {
    "allowlist_metadata_only": [
        "sec.gov",
        "federalregister.gov",
        "congress.gov",
        "govinfo.gov",
        "nist.gov",
        "csrc.nist.gov",
        "uspto.gov",
        "openai.com",
        "docs.github.com",
        "developer.mozilla.org",
        "python.org",
        "fastapi.tiangolo.com",
        "pydantic.dev",
    ],
    "denylist": [
        "malware.example",
        "phishing.example",
        "untrusted-download.example",
    ],
    "quarantine_patterns": [
        "unknown",
        "forum",
        "paste",
        "download",
        "binary",
        "archive",
        "mirror",
        "shortener",
    ],
    "allowed_uses_by_tier": {
        "tier_1_authoritative": ["metadata", "source-card", "evidence-candidate"],
        "tier_2_reputable": ["metadata", "source-card", "corroboration-candidate"],
        "tier_3_contextual": ["source-card", "context-only"],
        "tier_4_unknown": ["source-card", "quarantine-review"],
        "tier_0_blocked": ["blocked-audit-record"],
    },
    "blocked_uses_all_tiers": [
        "body-read",
        "autonomous-crawl",
        "runtime-truth-mutation",
        "automatic-update",
        "package-download",
        "package-install",
        "command-execution",
    ],
}

DEFAULT_SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "official_sec_edgar",
        "label": "SEC EDGAR",
        "domain": "sec.gov",
        "source_type": "regulatory",
        "tier": "tier_1_authoritative",
        "status": "allowlisted_metadata_only",
        "notes": "Regulatory filings source candidate. Metadata-only until a governed operator-approved fetch exists.",
    },
    {
        "source_id": "official_federal_register",
        "label": "Federal Register",
        "domain": "federalregister.gov",
        "source_type": "government",
        "tier": "tier_1_authoritative",
        "status": "allowlisted_metadata_only",
        "notes": "Federal rulemaking source candidate. Metadata-only and review gated.",
    },
    {
        "source_id": "official_nist",
        "label": "NIST",
        "domain": "nist.gov",
        "source_type": "standards",
        "tier": "tier_1_authoritative",
        "status": "allowlisted_metadata_only",
        "notes": "Standards and security documentation source candidate.",
    },
    {
        "source_id": "vendor_openai_docs",
        "label": "OpenAI Documentation",
        "domain": "openai.com",
        "source_type": "vendor_docs",
        "tier": "tier_1_authoritative",
        "status": "allowlisted_metadata_only",
        "notes": "Vendor documentation source candidate. Runtime truth mutation remains blocked.",
    },
    {
        "source_id": "technical_python_docs",
        "label": "Python Documentation",
        "domain": "python.org",
        "source_type": "technical_docs",
        "tier": "tier_1_authoritative",
        "status": "allowlisted_metadata_only",
        "notes": "Technical reference candidate for implementation evidence.",
    },
    {
        "source_id": "technical_fastapi_docs",
        "label": "FastAPI Documentation",
        "domain": "fastapi.tiangolo.com",
        "source_type": "technical_docs",
        "tier": "tier_1_authoritative",
        "status": "allowlisted_metadata_only",
        "notes": "Backend framework documentation candidate.",
    },
    {
        "source_id": "search_provider_google_metadata",
        "label": "Google Provider Metadata",
        "domain": "google.com",
        "source_type": "search_provider_metadata",
        "tier": "tier_2_reputable",
        "status": "review_required",
        "notes": "Provider metadata surface only. Query execution remains separately gated.",
    },
    {
        "source_id": "unknown_web_candidate",
        "label": "Unknown Web Candidate",
        "domain": "unknown.example",
        "source_type": "unknown",
        "tier": "tier_4_unknown",
        "status": "quarantine_by_default",
        "notes": "Sentinel showing how unclassified sources are quarantined.",
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_domain(value: str) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return "unknown"
    if "://" in raw:
        parsed = urlparse(raw)
        host = parsed.netloc or parsed.path
    else:
        host = raw.split("/")[0]
    host = host.split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host or "unknown"


def source_id_from_domain(domain: str) -> str:
    cleaned = normalize_domain(domain).replace(".", "_").replace("-", "_")
    return f"source_{cleaned}" if cleaned else "source_unknown"


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    label: str
    domain: str
    source_type: str
    tier: str = "tier_4_unknown"
    status: str = "quarantine_by_default"
    notes: str = ""
    allowlisted: bool = False
    denylisted: bool = False
    quarantined: bool = True
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        tier_info = TRUST_TIERS.get(self.tier, TRUST_TIERS["tier_4_unknown"])
        allowed_uses = DEFAULT_POLICY["allowed_uses_by_tier"].get(self.tier, ["source-card", "quarantine-review"])
        blocked_uses = list(DEFAULT_POLICY["blocked_uses_all_tiers"])
        return {
            "source_id": self.source_id,
            "label": self.label,
            "domain": normalize_domain(self.domain),
            "source_type": self.source_type,
            "tier": self.tier,
            "tier_label": tier_info["label"],
            "tier_rank": tier_info["rank"],
            "status": self.status,
            "notes": self.notes,
            "allowlisted": self.allowlisted,
            "denylisted": self.denylisted,
            "quarantined": self.quarantined,
            "reasons": list(self.reasons),
            "allowed_uses": list(allowed_uses),
            "blocked_uses": blocked_uses,
            "runtime_truth_allowed": False,
            "body_read_allowed": False,
            "requires_operator_review": True,
        }


def classify_source(candidate: dict[str, Any]) -> SourceRecord:
    domain = normalize_domain(str(candidate.get("domain") or candidate.get("url") or candidate.get("source") or "unknown"))
    source_id = str(candidate.get("source_id") or source_id_from_domain(domain))
    label = str(candidate.get("label") or domain)
    source_type = str(candidate.get("source_type") or "unknown")
    requested_tier = str(candidate.get("tier") or "tier_4_unknown")

    denylisted = domain in DEFAULT_POLICY["denylist"]
    allowlisted = domain in DEFAULT_POLICY["allowlist_metadata_only"]
    quarantine_hit = any(pattern in domain or pattern in source_type.lower() for pattern in DEFAULT_POLICY["quarantine_patterns"])

    reasons: list[str] = []
    if denylisted:
        tier = "tier_0_blocked"
        status = "denied"
        quarantined = True
        reasons.append("domain appears in denylist")
    elif allowlisted:
        tier = requested_tier if requested_tier in TRUST_TIERS and requested_tier != "tier_0_blocked" else "tier_1_authoritative"
        status = "allowlisted_metadata_only"
        quarantined = False
        reasons.append("domain appears in metadata-only allowlist")
    elif quarantine_hit or requested_tier == "tier_4_unknown":
        tier = requested_tier if requested_tier in TRUST_TIERS else "tier_4_unknown"
        status = "quarantine_by_default"
        quarantined = True
        reasons.append("source requires quarantine review before use")
    else:
        tier = requested_tier if requested_tier in TRUST_TIERS else "tier_4_unknown"
        status = str(candidate.get("status") or TRUST_TIERS[tier]["default_status"])
        quarantined = status.startswith("quarantine") or status == "review_required"
        reasons.append("source requires operator review before promotion")

    return SourceRecord(
        source_id=source_id,
        label=label,
        domain=domain,
        source_type=source_type,
        tier=tier,
        status=status,
        notes=str(candidate.get("notes") or ""),
        allowlisted=allowlisted,
        denylisted=denylisted,
        quarantined=quarantined,
        reasons=tuple(reasons),
    )


def build_source_cards(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for source in sources:
        record = classify_source(source).to_dict()
        cards.append(
            {
                "card_id": f"source-card::{record['source_id']}",
                "title": record["label"],
                "subtitle": record["domain"],
                "status": record["status"],
                "trust_tier": record["tier"],
                "trust_tier_label": record["tier_label"],
                "source_type": record["source_type"],
                "badges": [
                    record["tier_label"],
                    "metadata only" if record["allowlisted"] else "review gated",
                    "quarantined" if record["quarantined"] else "allowlisted",
                ],
                "body": record["notes"] or "Governed source candidate. Execution remains blocked until a later explicit gate.",
                "policy": {
                    "allowed_uses": record["allowed_uses"],
                    "blocked_uses": record["blocked_uses"],
                    "operator_review_required": record["requires_operator_review"],
                    "runtime_truth_allowed": False,
                    "body_read_allowed": False,
                },
                "source": record,
            }
        )
    return cards


def build_governed_source_actions(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = [classify_source(source).to_dict() for source in sources]
    review_count = sum(1 for record in records if record["requires_operator_review"])
    quarantined_count = sum(1 for record in records if record["quarantined"])
    allowlisted_count = sum(1 for record in records if record["allowlisted"])
    return [
        {
            "action_id": "source_registry.review_candidates",
            "label": "Review source candidates",
            "status": "operator_review_required",
            "count": review_count,
            "enabled": False,
            "execution_blocked": True,
            "reason": "Creates a review task only; source promotion and execution remain blocked.",
            "blocked_capabilities": list(DEFAULT_POLICY["blocked_uses_all_tiers"]),
        },
        {
            "action_id": "source_registry.inspect_quarantine",
            "label": "Inspect quarantined sources",
            "status": "available_for_review",
            "count": quarantined_count,
            "enabled": False,
            "execution_blocked": True,
            "reason": "Quarantine inspection is visual/review-only in this phase.",
            "blocked_capabilities": list(DEFAULT_POLICY["blocked_uses_all_tiers"]),
        },
        {
            "action_id": "source_registry.export_policy_snapshot",
            "label": "Export source policy snapshot",
            "status": "descriptor_ready",
            "count": allowlisted_count,
            "enabled": False,
            "execution_blocked": True,
            "reason": "Descriptor prepared for cockpit wiring; file export is not enabled by this build.",
            "blocked_capabilities": ["automatic-update", "runtime-truth-mutation", "command-execution"],
        },
    ]


def build_source_evidence_cards(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for source in sources:
        record = classify_source(source).to_dict()
        cards.append(
            {
                "evidence_card_id": f"source-evidence::{record['source_id']}",
                "source_id": record["source_id"],
                "title": f"Source evidence policy: {record['label']}",
                "domain": record["domain"],
                "status": "metadata_only" if record["allowlisted"] else "review_or_quarantine_required",
                "body_read_allowed": False,
                "network_request_performed": False,
                "evidence_use": "candidate_source_record_only",
                "lineage": {
                    "created_by": VERSION,
                    "live_fetch": False,
                    "runtime_mutation": False,
                    "operator_promotion_required": True,
                },
                "review_notes": record["reasons"],
            }
        )
    return cards


def build_registry_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    allowlisted = sum(1 for record in records if record["allowlisted"])
    denied = sum(1 for record in records if record["denylisted"])
    quarantined = sum(1 for record in records if record["quarantined"])
    review_required = sum(1 for record in records if record["requires_operator_review"])
    return {
        "total_sources": len(records),
        "allowlisted_metadata_only": allowlisted,
        "denied": denied,
        "quarantined": quarantined,
        "review_required": review_required,
        "live_web_execution_enabled": False,
        "body_read_allowed": False,
        "automatic_updates_enabled": False,
        "runtime_mutation_enabled": False,
        "readiness": "source_registry_ready_governed_blocked",
    }


def build_governed_source_registry_payload(extra_sources: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    source_inputs = [*DEFAULT_SOURCES, *(extra_sources or [])]
    records = [classify_source(source).to_dict() for source in source_inputs]
    cards = build_source_cards(source_inputs)
    actions = build_governed_source_actions(source_inputs)
    evidence_cards = build_source_evidence_cards(source_inputs)
    return {
        "version": VERSION,
        "generated_at": now_iso(),
        "authority": "backend_source_governance_contract",
        "mode": "governed_metadata_only",
        "readiness": "source_registry_ready_governed_blocked",
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "trust_tiers": TRUST_TIERS,
        "policy": DEFAULT_POLICY,
        "summary": build_registry_summary(records),
        "sources": records,
        "source_cards": cards,
        "governed_actions": actions,
        "evidence_cards": evidence_cards,
        "cockpit_panels": {
            "governed_web": {
                "title": "Governed Source Registry",
                "status": "ready_metadata_only",
                "cards": cards,
            },
            "actions": {
                "title": "Governed Source Actions",
                "status": "actions_registered_blocked",
                "actions": actions,
            },
            "evidence_review": {
                "title": "Source Evidence Review",
                "status": "source_evidence_cards_ready",
                "cards": evidence_cards,
            },
        },
        "stop_gate": {
            "build": "S582",
            "status": "forward_motion_proof_ready",
            "next_phase": "S583-S589 Search Plan + Query Governance",
            "may_continue": True,
            "blocks_preserved": True,
        },
    }


def get_source_registry_payload() -> dict[str, Any]:
    return build_governed_source_registry_payload()


def get_source_cards_payload() -> dict[str, Any]:
    payload = build_governed_source_registry_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "source_cards": payload["source_cards"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


def get_source_actions_payload() -> dict[str, Any]:
    payload = build_governed_source_registry_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "governed_actions": payload["governed_actions"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


def get_source_policy_payload() -> dict[str, Any]:
    payload = build_governed_source_registry_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "trust_tiers": payload["trust_tiers"],
        "policy": payload["policy"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }

