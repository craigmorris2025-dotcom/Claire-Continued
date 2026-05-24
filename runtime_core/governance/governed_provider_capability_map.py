from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

PHASE = "S625-S631"
PHASE_LABEL = "Governed Provider Capability Map + Probe Readiness Hardening"

BLOCKED_EXECUTION_FLAGS: Dict[str, Any] = {
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

PROVIDER_CAPABILITIES: List[Dict[str, Any]] = [
    {
        "provider_id": "official_documentation",
        "label": "Official documentation sources",
        "source_family": "official_docs",
        "trust_tier": "T1_authoritative",
        "readiness": "policy_defined",
        "configuration_state": "registry_ready_provider_not_executing",
        "allowed_capabilities": [
            "source_card_display",
            "search_scope_planning",
            "metadata_only_probe_candidate",
            "quarantine_routing_plan",
        ],
        "blocked_capabilities": [
            "live_network_request",
            "body_read",
            "autonomous_crawl",
            "runtime_truth_mutation",
            "automatic_update",
        ],
        "cockpit_surface": "Governed Web",
        "notes": "Highest trust family, but still cannot execute until the metadata-only gate is explicitly opened.",
    },
    {
        "provider_id": "market_and_financial_sources",
        "label": "Market and financial sources",
        "source_family": "market_financial",
        "trust_tier": "T2_verified_domain",
        "readiness": "policy_defined",
        "configuration_state": "registry_ready_provider_not_executing",
        "allowed_capabilities": [
            "source_card_display",
            "search_scope_planning",
            "metadata_only_probe_candidate",
            "quarantine_routing_plan",
        ],
        "blocked_capabilities": [
            "live_network_request",
            "body_read",
            "autonomous_crawl",
            "runtime_truth_mutation",
            "automatic_update",
        ],
        "cockpit_surface": "Governed Web",
        "notes": "Useful for portfolio and market routes after manual metadata probe gates exist.",
    },
    {
        "provider_id": "approved_search_provider",
        "label": "Approved search provider boundary",
        "source_family": "search_provider",
        "trust_tier": "T3_provider_metadata",
        "readiness": "adapter_boundary_required",
        "configuration_state": "capability_mapped_provider_not_executing",
        "allowed_capabilities": [
            "provider_capability_display",
            "manual_metadata_probe_planning",
            "quarantine_routing_plan",
        ],
        "blocked_capabilities": [
            "provider_execution",
            "body_read",
            "autonomous_crawl",
            "runtime_truth_mutation",
            "automatic_update",
        ],
        "cockpit_surface": "Actions",
        "notes": "Provider capabilities are visible, but provider calls remain blocked until a later controlled probe gate.",
    },
    {
        "provider_id": "open_web_general",
        "label": "Open web general sources",
        "source_family": "open_web",
        "trust_tier": "T4_unverified_open_web",
        "readiness": "quarantine_only",
        "configuration_state": "visible_not_trusted_for_runtime_truth",
        "allowed_capabilities": [
            "source_card_display",
            "search_scope_planning",
            "quarantine_required_flagging",
        ],
        "blocked_capabilities": [
            "provider_execution",
            "body_read",
            "autonomous_crawl",
            "runtime_truth_mutation",
            "automatic_update",
        ],
        "cockpit_surface": "Evidence & Review",
        "notes": "Open-web results must be quarantined and reviewed before they can influence any runtime answer or lifecycle route.",
    },
    {
        "provider_id": "denied_source_families",
        "label": "Denied source families",
        "source_family": "denied",
        "trust_tier": "D_denied",
        "readiness": "denylist_enforced",
        "configuration_state": "blocked_by_policy",
        "allowed_capabilities": ["policy_visibility", "blocked_reason_display"],
        "blocked_capabilities": [
            "provider_execution",
            "network_request",
            "body_read",
            "autonomous_crawl",
            "runtime_truth_mutation",
            "automatic_update",
        ],
        "cockpit_surface": "System",
        "notes": "Denied families are shown for operator proof only and cannot be searched.",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_execution_flags() -> Dict[str, Any]:
    return deepcopy(BLOCKED_EXECUTION_FLAGS)


def get_provider_capability_map() -> Dict[str, Any]:
    providers = deepcopy(PROVIDER_CAPABILITIES)
    return {
        "phase": PHASE,
        "label": PHASE_LABEL,
        "status": "provider_capability_map_ready",
        "generated_at": _utc_now(),
        "summary": {
            "provider_family_count": len(providers),
            "configured_for_execution_count": 0,
            "metadata_probe_candidate_count": sum(
                1 for provider in providers if "metadata_only_probe_candidate" in provider.get("allowed_capabilities", [])
            ),
            "denied_family_count": sum(1 for provider in providers if provider.get("trust_tier") == "D_denied"),
            "cockpit_visible": True,
        },
        "providers": providers,
        "blocked_execution": get_blocked_execution_flags(),
        "authority_state": {
            "provider_execution_authority": "blocked",
            "network_authority": "blocked",
            "body_read_authority": "blocked",
            "runtime_mutation_authority": "blocked",
            "automatic_update_authority": "blocked",
        },
        "next_gate": "S639-S645 quarantine evidence store after S632-S638 source policy cockpit controls",
    }


def build_provider_capability_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for provider in PROVIDER_CAPABILITIES:
        blocked = provider.get("blocked_capabilities", [])
        cards.append(
            {
                "card_id": f"provider-capability-{provider['provider_id']}",
                "card_type": "provider_capability",
                "title": provider["label"],
                "status": provider["readiness"],
                "source_family": provider["source_family"],
                "trust_tier": provider["trust_tier"],
                "cockpit_surface": provider["cockpit_surface"],
                "summary": provider["notes"],
                "allowed_capabilities": list(provider.get("allowed_capabilities", [])),
                "blocked_capabilities": list(blocked),
                "execution_enabled": False,
                "network_request_performed": False,
                "requires_operator_review": True,
            }
        )
    return cards


def build_provider_capability_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "inspect-provider-capability-map",
            "label": "Inspect provider capability map",
            "surface": "Actions",
            "status": "available_for_review",
            "executable": False,
            "requires_operator_approval": False,
            "blocked_reason": "Review-only action descriptor; no provider execution authority is granted.",
            "target_endpoint": "/api/search/providers/capability-map",
        },
        {
            "action_id": "review-metadata-probe-candidates",
            "label": "Review metadata probe candidates",
            "surface": "Actions",
            "status": "planned_not_enabled",
            "executable": False,
            "requires_operator_approval": True,
            "blocked_reason": "Manual metadata probe gate is scheduled later; provider calls are still blocked.",
            "target_endpoint": "/api/search/providers/capability/cards",
        },
        {
            "action_id": "verify-provider-blocks",
            "label": "Verify provider execution blocks",
            "surface": "System",
            "status": "ready",
            "executable": False,
            "requires_operator_approval": False,
            "blocked_reason": "Proof action only; confirms flags remain fail-closed.",
            "target_endpoint": "/api/search/providers/capability/status",
        },
    ]


def get_provider_capability_policy() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "policy_status": "fail_closed",
        "rules": [
            "Provider capabilities may be displayed in cockpit cards.",
            "Provider configuration state may be inspected without exposing secrets.",
            "No provider may execute a live request in this phase.",
            "No response body may be read in this phase.",
            "No search result may become runtime truth without quarantine and review.",
            "No automatic update, package download, install, command execution, or runtime mutation is allowed.",
        ],
        "blocked_execution": get_blocked_execution_flags(),
    }


def get_provider_capability_status() -> Dict[str, Any]:
    capability_map = get_provider_capability_map()
    return {
        "phase": PHASE,
        "status": "ready",
        "readiness": "provider_capability_map_visible",
        "cards_ready": len(build_provider_capability_cards()),
        "actions_ready": len(build_provider_capability_actions()),
        "provider_family_count": capability_map["summary"]["provider_family_count"],
        "execution_enabled": False,
        "blocked_execution": get_blocked_execution_flags(),
    }


def get_provider_capability_payload() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "status": "ready",
        "capability_map": get_provider_capability_map(),
        "cards": build_provider_capability_cards(),
        "actions": build_provider_capability_actions(),
        "policy": get_provider_capability_policy(),
        "stop_gate": get_provider_capability_stop_gate(),
    }


def get_provider_capability_stop_gate() -> Dict[str, Any]:
    return {
        "phase": "S631",
        "gate": "provider_capability_map_stop_gate",
        "forward_motion_allowed": True,
        "authority_unlock_allowed": False,
        "evidence": [
            "provider capability registry exists",
            "provider cards are cockpit-ready",
            "governed action descriptors exist",
            "all live/search/network/body/update/mutation/package/command authorities remain blocked",
        ],
        "blocked_execution": get_blocked_execution_flags(),
    }
