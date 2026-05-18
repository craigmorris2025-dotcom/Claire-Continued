from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

from claire.governance.governed_manual_body_read_execution_envelope import build_execution_envelope_actions, build_execution_envelope_cards, build_execution_envelope_payload
from claire.governance.governed_sanitized_extraction_preview import build_sanitized_extraction_cards, build_sanitized_extraction_preview_payload
from claire.governance.governed_source_update_ingestion import build_operator_ingestion_actions, build_source_ingestion_cards, build_source_ingestion_payload, build_source_lineage_payload, build_update_proposal_payload

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


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def build_runtime_truth_promotion_preview() -> Dict[str, Any]:
    ingestion = build_source_ingestion_payload()
    proposals = build_update_proposal_payload()
    previews = [{"preview_id": f"promotion-preview-{draft['draft_id']}", "draft_id": draft["draft_id"], "title": draft["title"], "target_surface": draft["ingestion_route"], "state": "promotion_preview_only_runtime_mutation_blocked", "promotion_allowed": False, "runtime_truth_mutation_allowed": False, "automatic_update_allowed": False, "operator_approval_required": True} for draft in ingestion["drafts"]]
    return {"stage_range": "S884-S890", "name": "Runtime Truth Promotion Preview", "terminal_state": "runtime_truth_promotion_preview_ready_mutation_blocked", "authority": "preview_only_no_runtime_truth_mutation", "summary": {"promotion_previews": len(previews), "source_change_proposals": len(proposals["proposals"]), "promotions_allowed": 0, "runtime_truth_mutations": 0, "automatic_updates_allowed": 0, "package_installs": 0}, "blocked_capabilities": get_blocked_capabilities(), "promotion_previews": previews, "rules": {"promotion_requires_operator_approval": True, "promotion_requires_reviewed_evidence": True, "promotion_requires_lineage": True, "promotion_requires_rollback_packet": True, "runtime_truth_mutation_enabled": False}}


def build_cockpit_source_ingestion_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    cards.extend(build_execution_envelope_cards())
    cards.extend(build_sanitized_extraction_cards())
    cards.extend(build_source_ingestion_cards())
    cards.append({"card_id": "runtime-truth-promotion-preview-summary", "title": "Runtime truth promotion preview", "subtitle": "reviewed evidence -> future runtime truth route", "state": "preview_ready_mutation_blocked", "summary": "Promotion path is visible for review, but runtime truth mutation and automatic updates remain blocked.", "badges": ["promotion-preview", "mutation-blocked", "updates-blocked"], "actions": ["review_promotion_preview", "reject_promotion_preview"], "execution_enabled": False})
    cards.append({"card_id": "s900-stop-gate-summary", "title": "S900 source/update ingestion stop gate", "subtitle": "body-read to ingestion runway complete", "state": "ready_for_next_phase_with_execution_blocked", "summary": "The cockpit can now show the planned body-read, extraction, source ingestion, lineage, proposal and promotion path.", "badges": ["S900", "stop-gate", "ready-next-phase", "execution-blocked"], "actions": ["review_s900_gate", "prepare_next_unlock_plan"], "execution_enabled": False})
    return cards


def build_cockpit_source_ingestion_actions() -> List[Dict[str, Any]]:
    actions = []
    actions.extend(build_execution_envelope_actions())
    actions.extend(build_operator_ingestion_actions())
    actions.extend([
        {"action_id": "review_runtime_truth_promotion_preview", "label": "Review runtime truth promotion preview", "description": "Review-only action descriptor; no mutation can execute.", "execution_enabled": False, "runtime_truth_mutation_allowed": False, "requires_operator_approval": True},
        {"action_id": "review_s900_source_ingestion_stop_gate", "label": "Review S900 source/update ingestion stop gate", "description": "Confirms the runway is ready for a later explicit unlock plan.", "execution_enabled": False, "requires_operator_approval": True},
    ])
    return actions


def build_s900_stop_gate() -> Dict[str, Any]:
    return {"gate_id": "S900_BODY_READ_TO_SOURCE_UPDATE_INGESTION_STOP", "stage_range": "S835-S900", "ready_for_next_phase": True, "next_phase_recommendation": "explicit operator-controlled execution unlock plan only; do not enable autonomous crawling or automatic updates", "completed_surfaces": ["manual_body_read_execution_envelope", "sanitized_extraction_preview", "source_update_ingestion_drafts", "source_lineage_validation", "update_source_change_proposals", "operator_ingestion_actions", "runtime_truth_promotion_preview", "cockpit_source_ingestion_cards"], "still_blocked": get_blocked_capabilities(), "proof": {"network_request_performed": False, "body_read_performed": False, "automatic_update_allowed": False, "runtime_truth_mutation_allowed": False, "package_install_performed": False, "executable_actions": 0}}


def build_cockpit_source_ingestion_payload() -> Dict[str, Any]:
    envelope = build_execution_envelope_payload()
    extraction = build_sanitized_extraction_preview_payload()
    ingestion = build_source_ingestion_payload()
    lineage = build_source_lineage_payload()
    proposals = build_update_proposal_payload()
    promotion = build_runtime_truth_promotion_preview()
    cards = build_cockpit_source_ingestion_cards()
    actions = build_cockpit_source_ingestion_actions()
    return {"stage_range": "S835-S900", "name": "Governed Body-Read to Source/Update Ingestion Completion", "terminal_state": "s900_source_update_ingestion_ready_execution_blocked", "authority": "cockpit_review_and_preview_only_no_execution", "summary": {"execution_envelopes": envelope["summary"]["envelopes"], "extraction_previews": extraction["summary"]["previews"], "source_ingestion_drafts": ingestion["summary"]["ingestion_drafts"], "lineage_packets": lineage["summary"]["lineage_packets"], "change_proposals": proposals["summary"]["proposals"], "promotion_previews": promotion["summary"]["promotion_previews"], "cards": len(cards), "actions": len(actions), "executable_actions": 0, "network_requests": 0, "body_reads_performed": 0, "automatic_updates_allowed": 0, "runtime_truth_mutations": 0, "package_installs": 0}, "blocked_capabilities": get_blocked_capabilities(), "sections": {"manual_body_read_execution_envelope": envelope, "sanitized_extraction_preview": extraction, "source_update_ingestion": ingestion, "source_lineage": lineage, "update_source_change_proposals": proposals, "runtime_truth_promotion_preview": promotion}, "cards": cards, "actions": actions, "command_bar_search_state": {"visible_status": "source_ingestion_and_body_read_readiness_visible", "can_search_open_web": False, "can_return_live_results": False, "can_display_review_cards": True, "next_unlock_dependency": "operator-controlled metadata/body-read execution gate must be explicitly enabled later"}, "stop_gate": build_s900_stop_gate(), "generated_at": _now_iso()}
