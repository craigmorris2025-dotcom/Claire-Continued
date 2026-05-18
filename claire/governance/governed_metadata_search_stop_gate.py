"""First controlled metadata search stop gate for S744-S750.

The stop gate proves the metadata search pathway can be represented end-to-end
without live execution. It does not call providers or perform network requests.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

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

PROOF_STEPS: List[Dict[str, Any]] = [
    {"step_id": "query_compiled", "label": "Query compiled", "state": "represented", "execution_enabled": False},
    {"step_id": "source_policy_applied", "label": "Source policy applied", "state": "represented", "execution_enabled": False},
    {"step_id": "provider_boundary_checked", "label": "Provider boundary checked", "state": "represented", "execution_enabled": False},
    {"step_id": "metadata_contract_validated", "label": "Metadata contract validated", "state": "represented", "execution_enabled": False},
    {"step_id": "quarantine_store_ready", "label": "Quarantine store ready", "state": "represented", "execution_enabled": False},
    {"step_id": "review_cards_ready", "label": "Review cards ready", "state": "represented", "execution_enabled": False},
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_capabilities() -> Dict[str, bool]:
    return deepcopy(BLOCKED_CAPABILITIES)


def build_metadata_search_proof() -> Dict[str, Any]:
    return {
        "stage_range": "S744-S750",
        "name": "First Controlled Metadata Search Stop Gate",
        "terminal_state": "controlled_metadata_search_proof_ready",
        "authority": "manual_metadata_search_proof_only",
        "proof_id": "controlled-metadata-search-proof-s744-s750",
        "created_at": _now_iso(),
        "summary": {
            "proof_steps_total": len(PROOF_STEPS),
            "represented_steps_total": len(PROOF_STEPS),
            "provider_calls": 0,
            "network_requests": 0,
            "body_reads": 0,
            "runtime_truth_mutations": 0,
            "executable_actions": 0,
        },
        "blocked_capabilities": get_blocked_capabilities(),
        "proof_steps": deepcopy(PROOF_STEPS),
        "stop_gate": {
            "gate_id": "S750_CONTROLLED_METADATA_SEARCH_STOP_GATE",
            "passed": True,
            "meaning": "The end-to-end metadata search path is modeled and cockpit-visible, but not yet allowed to execute live provider searches.",
            "allowed_next_phase": "governed_body_read_planning_only",
            "blocked_next_phase": "uncontrolled_open_web_or_body_reads",
        },
    }


def build_metadata_search_cards() -> List[Dict[str, Any]]:
    payload = build_metadata_search_proof()
    cards: List[Dict[str, Any]] = []
    for step in payload["proof_steps"]:
        cards.append(
            {
                "card_id": f"metadata-proof-{step['step_id']}",
                "title": step["label"],
                "state": step["state"],
                "summary": "Controlled metadata search proof step is represented; no live web execution occurred.",
                "badges": ["proof", "metadata-only", "execution-blocked", "body-read-blocked"],
                "execution_enabled": False,
            }
        )
    return cards


def build_metadata_search_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "run_manual_metadata_probe_when_enabled",
            "label": "Run manual metadata probe when governance enables it",
            "description": "Descriptor only in this build; provider execution remains blocked.",
            "execution_enabled": False,
            "provider_execution_enabled": False,
            "requires_operator_approval": True,
        },
        {
            "action_id": "open_metadata_result_review",
            "label": "Open metadata result review",
            "description": "Displays review cards when metadata exists; does not fetch or read pages.",
            "execution_enabled": False,
            "provider_execution_enabled": False,
            "requires_operator_approval": True,
        },
    ]


def build_status() -> Dict[str, Any]:
    return {
        "stage_range": "S744-S750",
        "status": "stop_gate_ready",
        "terminal_state": "controlled_metadata_search_proof_ready",
        "blocked_capabilities": get_blocked_capabilities(),
    }
