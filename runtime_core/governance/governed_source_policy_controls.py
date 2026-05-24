from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

PHASE = "S632-S638"
PHASE_LABEL = "Source Policy Cockpit Controls"

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

SOURCE_POLICY_CONTROLS: List[Dict[str, Any]] = [
    {
        "control_id": "allowlist-policy",
        "label": "Allowlist policy",
        "control_type": "source_access_policy",
        "state": "visible_enforced_for_planning",
        "operator_visible": True,
        "allows_execution": False,
        "description": "Defines approved source families for planning without granting network execution authority.",
        "rules": ["approved families can be planned", "execution still requires later gate", "metadata only until explicitly changed"],
    },
    {
        "control_id": "denylist-policy",
        "label": "Denylist policy",
        "control_type": "source_access_policy",
        "state": "visible_enforced",
        "operator_visible": True,
        "allows_execution": False,
        "description": "Displays source families that must not be searched or promoted.",
        "rules": ["denied families cannot be queried", "denied families cannot become runtime truth", "blocked reason must be visible"],
    },
    {
        "control_id": "quarantine-policy",
        "label": "Quarantine policy",
        "control_type": "evidence_policy",
        "state": "visible_enforced",
        "operator_visible": True,
        "allows_execution": False,
        "description": "Requires all external evidence to land in quarantine before review or promotion.",
        "rules": ["quarantine first", "review required", "promotion is not automatic"],
    },
    {
        "control_id": "trust-tier-policy",
        "label": "Trust tier policy",
        "control_type": "trust_policy",
        "state": "visible_enforced_for_planning",
        "operator_visible": True,
        "allows_execution": False,
        "description": "Maps source families to trust tiers for search planning and evidence review.",
        "rules": ["T1 authoritative", "T2 verified domain", "T3 provider metadata", "T4 unverified open web", "D denied"],
    },
    {
        "control_id": "body-read-policy",
        "label": "Body read policy",
        "control_type": "execution_policy",
        "state": "blocked",
        "operator_visible": True,
        "allows_execution": False,
        "description": "Keeps response body reads disabled through this phase.",
        "rules": ["metadata planning only", "no page body extraction", "no crawler behavior"],
    },
    {
        "control_id": "update-mutation-policy",
        "label": "Update and mutation policy",
        "control_type": "runtime_policy",
        "state": "blocked",
        "operator_visible": True,
        "allows_execution": False,
        "description": "Prevents automatic updates, package install, command execution, and runtime mutation.",
        "rules": ["no automatic update", "no package download", "no package install", "no command execution", "no runtime mutation"],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_blocked_execution_flags() -> Dict[str, Any]:
    return deepcopy(BLOCKED_EXECUTION_FLAGS)


def get_source_policy_controls() -> Dict[str, Any]:
    controls = deepcopy(SOURCE_POLICY_CONTROLS)
    return {
        "phase": PHASE,
        "label": PHASE_LABEL,
        "status": "source_policy_controls_ready",
        "generated_at": _utc_now(),
        "summary": {
            "control_count": len(controls),
            "operator_visible_count": sum(1 for control in controls if control.get("operator_visible")),
            "execution_enabling_control_count": sum(1 for control in controls if control.get("allows_execution")),
            "blocked_control_count": sum(1 for control in controls if control.get("state") == "blocked"),
            "cockpit_visible": True,
        },
        "controls": controls,
        "blocked_execution": get_blocked_execution_flags(),
        "authority_state": {
            "policy_controls_visible": True,
            "policy_controls_can_unlock_authority": False,
            "network_authority": "blocked",
            "body_read_authority": "blocked",
            "runtime_mutation_authority": "blocked",
            "automatic_update_authority": "blocked",
        },
        "next_gate": "S639-S645 quarantine evidence store and review queue UX",
    }


def build_source_policy_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for control in SOURCE_POLICY_CONTROLS:
        cards.append(
            {
                "card_id": f"source-policy-{control['control_id']}",
                "card_type": "source_policy_control",
                "title": control["label"],
                "status": control["state"],
                "control_type": control["control_type"],
                "summary": control["description"],
                "rules": list(control.get("rules", [])),
                "operator_visible": bool(control.get("operator_visible")),
                "execution_enabled": False,
                "allows_execution": False,
                "network_request_performed": False,
                "cockpit_surface": "Governed Web" if control["control_type"] != "runtime_policy" else "System",
            }
        )
    return cards


def build_source_policy_actions() -> List[Dict[str, Any]]:
    return [
        {
            "action_id": "inspect-source-policy-controls",
            "label": "Inspect source policy controls",
            "surface": "Actions",
            "status": "available_for_review",
            "executable": False,
            "requires_operator_approval": False,
            "blocked_reason": "Review-only action descriptor; policy controls do not unlock execution.",
            "target_endpoint": "/api/sources/policy/controls",
        },
        {
            "action_id": "review-allowlist-denylist-quarantine",
            "label": "Review allowlist, denylist, and quarantine policy",
            "surface": "Governed Web",
            "status": "available_for_review",
            "executable": False,
            "requires_operator_approval": True,
            "blocked_reason": "Manual review can prepare policy decisions only; no network request is performed.",
            "target_endpoint": "/api/sources/policy/cards",
        },
        {
            "action_id": "verify-policy-blocks",
            "label": "Verify source policy execution blocks",
            "surface": "System",
            "status": "ready",
            "executable": False,
            "requires_operator_approval": False,
            "blocked_reason": "Proof action only; confirms blocked flags remain fail-closed.",
            "target_endpoint": "/api/sources/policy/status",
        },
    ]


def get_source_policy() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "policy_status": "fail_closed_controls_visible",
        "rules": [
            "Allowlist, denylist, quarantine, and trust-tier controls are visible to the cockpit.",
            "Controls may shape future search plans but cannot execute searches in this phase.",
            "No live network request may be performed in this phase.",
            "No response body may be read in this phase.",
            "No source evidence may become runtime truth automatically.",
            "No update, mutation, package, or command authority is enabled.",
        ],
        "blocked_execution": get_blocked_execution_flags(),
    }


def get_source_policy_status() -> Dict[str, Any]:
    controls = get_source_policy_controls()
    return {
        "phase": PHASE,
        "status": "ready",
        "readiness": "source_policy_cockpit_controls_visible",
        "cards_ready": len(build_source_policy_cards()),
        "actions_ready": len(build_source_policy_actions()),
        "control_count": controls["summary"]["control_count"],
        "execution_enabled": False,
        "blocked_execution": get_blocked_execution_flags(),
    }


def get_source_policy_payload() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "status": "ready",
        "controls": get_source_policy_controls(),
        "cards": build_source_policy_cards(),
        "actions": build_source_policy_actions(),
        "policy": get_source_policy(),
        "stop_gate": get_source_policy_stop_gate(),
    }


def get_source_policy_stop_gate() -> Dict[str, Any]:
    return {
        "phase": "S638",
        "gate": "source_policy_cockpit_controls_stop_gate",
        "forward_motion_allowed": True,
        "authority_unlock_allowed": False,
        "evidence": [
            "allowlist policy is cockpit-visible",
            "denylist policy is cockpit-visible",
            "quarantine policy is cockpit-visible",
            "trust-tier policy is cockpit-visible",
            "body-read and update/mutation policies remain blocked",
            "all live/search/network/body/update/mutation/package/command authorities remain blocked",
        ],
        "blocked_execution": get_blocked_execution_flags(),
    }
