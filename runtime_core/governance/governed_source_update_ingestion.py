from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

BLOCKED_CAPABILITIES: Dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "body_read_performed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

DEFAULT_DRAFTS: List[Dict[str, Any]] = [
    {"draft_id": "source-ingestion-draft-official-docs-001", "title": "Official documentation source ingestion draft", "source_family": "official_docs", "trust_tier": "tier_1_official", "ingestion_route": "knowledge_base_candidate", "evidence_state": "metadata_only_or_reviewed_evidence_required"},
    {"draft_id": "source-ingestion-draft-update-signal-002", "title": "Update-source ingestion draft", "source_family": "release_notes_or_vendor_advisory", "trust_tier": "tier_1_official", "ingestion_route": "governed_update_candidate", "evidence_state": "reviewed_evidence_required_before_sandbox"},
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def normalize_ingestion_drafts(drafts: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    raw = list(drafts) if drafts is not None else deepcopy(DEFAULT_DRAFTS)
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(raw):
        source_family = str(item.get("source_family") or "unknown_or_user_supplied")
        trust_tier = str(item.get("trust_tier") or "tier_4_unknown")
        high_risk = trust_tier.startswith("tier_4") or source_family in {"open_web_unknown", "denied_source_family"}
        normalized.append({
            "draft_id": str(item.get("draft_id") or f"source-ingestion-draft-{index + 1:03d}"),
            "title": str(item.get("title") or "Source ingestion draft"),
            "source_family": source_family,
            "trust_tier": trust_tier,
            "ingestion_route": str(item.get("ingestion_route") or "manual_review_candidate"),
            "evidence_state": str(item.get("evidence_state") or "review_required"),
            "validation_state": "quarantine_validation_required" if high_risk else "validation_packet_ready",
            "operator_review_required": True,
            "ingestion_allowed": False,
            "automatic_update_allowed": False,
            "runtime_truth_mutation_allowed": False,
            "package_install_allowed": False,
            "network_request_performed": False,
            "created_at": str(item.get("created_at") or _now_iso()),
        })
    return normalized


def build_source_ingestion_payload(drafts: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    normalized = normalize_ingestion_drafts(drafts)
    return {
        "stage_range": "S856-S883",
        "name": "Governed Source/Update Ingestion Drafts",
        "terminal_state": "source_update_ingestion_drafts_ready_execution_blocked",
        "authority": "draft_and_review_queue_only_no_ingestion_execution",
        "summary": {"ingestion_drafts": len(normalized), "operator_review_required": len(normalized), "ingestions_allowed": 0, "automatic_updates_allowed": 0, "runtime_truth_mutations": 0, "package_installs": 0, "network_requests": 0},
        "blocked_capabilities": get_blocked_capabilities(),
        "drafts": normalized,
        "validation_rules": {"lineage_required": True, "source_trust_required": True, "quarantine_before_promotion": True, "operator_approval_before_any_ingestion": True, "no_package_download": True, "no_package_install": True, "no_runtime_mutation": True},
    }


def build_source_lineage_payload(drafts: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    normalized = normalize_ingestion_drafts(drafts)
    lineage = [{"lineage_id": f"lineage-{item['draft_id']}", "draft_id": item["draft_id"], "source_family": item["source_family"], "trust_tier": item["trust_tier"], "evidence_state": item["evidence_state"], "lineage_state": "lineage_packet_ready_for_review", "runtime_truth_mutation_allowed": False, "ingestion_allowed": False} for item in normalized]
    return {"stage_range": "S863-S869", "name": "Ingestion Validation + Lineage", "terminal_state": "ingestion_lineage_ready_review_required", "summary": {"lineage_packets": len(lineage), "mutations_allowed": 0, "ingestions_allowed": 0}, "blocked_capabilities": get_blocked_capabilities(), "lineage": lineage}


def build_update_proposal_payload(drafts: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    proposals = []
    for item in normalize_ingestion_drafts(drafts):
        proposals.append({"proposal_id": f"update-proposal-{item['draft_id']}", "draft_id": item["draft_id"], "title": item["title"], "proposal_type": "source_or_update_ingestion_review", "state": "proposal_ready_for_operator_review_execution_blocked", "sandbox_required": True, "rollback_packet_required": True, "operator_approval_required": True, "automatic_update_allowed": False, "package_download_allowed": False, "package_install_allowed": False, "runtime_truth_mutation_allowed": False})
    return {"stage_range": "S870-S876", "name": "Update/Source Change Proposal Model", "terminal_state": "update_source_change_proposals_ready_execution_blocked", "summary": {"proposals": len(proposals), "automatic_updates_allowed": 0, "package_installs": 0, "runtime_mutations": 0}, "blocked_capabilities": get_blocked_capabilities(), "proposals": proposals}


def build_operator_ingestion_actions() -> List[Dict[str, Any]]:
    return [
        {"action_id": "review_source_ingestion_draft", "label": "Review source ingestion draft", "description": "Review a proposed source/update ingestion packet; no ingestion executes.", "execution_enabled": False, "ingestion_allowed": False, "requires_operator_approval": True},
        {"action_id": "reject_source_ingestion_draft", "label": "Reject source ingestion draft", "description": "Non-executable rejection action descriptor.", "execution_enabled": False, "ingestion_allowed": False, "requires_operator_approval": True},
        {"action_id": "prepare_sandbox_validation_packet", "label": "Prepare sandbox validation packet", "description": "Prepares a future validation packet descriptor only; no package download/install occurs.", "execution_enabled": False, "package_download_allowed": False, "package_install_allowed": False, "requires_operator_approval": True},
    ]


def build_source_ingestion_cards(drafts: Optional[Iterable[Mapping[str, Any]]] = None) -> List[Dict[str, Any]]:
    return [{"card_id": f"source-ingestion-{item['draft_id']}", "title": item["title"], "subtitle": f"{item['source_family']} / {item['ingestion_route']}", "state": item["validation_state"], "summary": "Source/update ingestion is prepared for operator review only; no automatic update or runtime mutation can run.", "badges": ["ingestion-draft", "review-required", "mutation-blocked", "updates-blocked"], "actions": ["review_source_ingestion_draft", "reject_source_ingestion_draft", "prepare_sandbox_validation_packet"], "execution_enabled": False} for item in build_source_ingestion_payload(drafts)["drafts"]]
