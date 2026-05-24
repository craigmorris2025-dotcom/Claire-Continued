from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List


LOCKS: Dict[str, bool] = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_write_blocked": True,
    "runtime_mutation_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "continuous_crawling_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
}

ACTION_REGISTRY: List[Dict[str, Any]] = [
    {
        "action_id": "review_evidence",
        "label": "Review Evidence",
        "category": "review",
        "risk": "low",
        "enabled": True,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": False,
        "blocked_reason": None,
    },
    {
        "action_id": "inspect_lineage",
        "label": "Inspect Lineage",
        "category": "evidence",
        "risk": "low",
        "enabled": True,
        "requires_manual_approval": False,
        "requires_quarantine": True,
        "unsafe_authority": False,
        "blocked_reason": None,
    },
    {
        "action_id": "export_reviewed_package",
        "label": "Export Reviewed Package",
        "category": "export",
        "risk": "medium",
        "enabled": True,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": False,
        "blocked_reason": None,
    },
    {
        "action_id": "start_bounded_web_job",
        "label": "Start Bounded Web Job",
        "category": "web_job",
        "risk": "medium",
        "enabled": True,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": False,
        "blocked_reason": None,
        "limits": {"continuous": False, "max_job_scope": "bounded", "operator_trigger_required": True},
    },
    {
        "action_id": "approve_candidate_promotion",
        "label": "Approve Candidate Promotion",
        "category": "promotion",
        "risk": "high",
        "enabled": True,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": False,
        "blocked_reason": None,
    },
    {
        "action_id": "request_mutation_proposal",
        "label": "Request Mutation Proposal",
        "category": "proposal",
        "risk": "high",
        "enabled": True,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": False,
        "blocked_reason": None,
        "proposal_only": True,
    },
    {
        "action_id": "execute_runtime_mutation",
        "label": "Execute Runtime Mutation",
        "category": "mutation",
        "risk": "blocked",
        "enabled": False,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": True,
        "blocked_reason": "runtime_mutation_blocked",
    },
    {
        "action_id": "enable_automatic_updates",
        "label": "Enable Automatic Updates",
        "category": "updates",
        "risk": "blocked",
        "enabled": False,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": True,
        "blocked_reason": "automatic_updates_blocked",
    },
    {
        "action_id": "start_continuous_crawl",
        "label": "Start Continuous Crawl",
        "category": "web_job",
        "risk": "blocked",
        "enabled": False,
        "requires_manual_approval": True,
        "requires_quarantine": True,
        "unsafe_authority": True,
        "blocked_reason": "continuous_crawling_blocked",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_cockpit_action_registry() -> Dict[str, Any]:
    actions = deepcopy(ACTION_REGISTRY)
    unsafe_enabled = [a["action_id"] for a in actions if a.get("unsafe_authority") and a.get("enabled")]
    return {
        "version": "v19.89.8-S185-S190",
        "stage_range": "S185-S190",
        "generated_at": _utc_now(),
        "governance_locks": deepcopy(LOCKS),
        "actions": actions,
        "summary": {
            "total_actions": len(actions),
            "enabled_actions": sum(1 for a in actions if a.get("enabled")),
            "blocked_actions": sum(1 for a in actions if not a.get("enabled")),
            "unsafe_enabled": unsafe_enabled,
            "safe": len(unsafe_enabled) == 0,
        },
    }


def _warning_for_action(action: Dict[str, Any]) -> str | None:
    if not action.get("enabled"):
        return f"Blocked by governance lock: {action.get('blocked_reason')}"
    if action.get("requires_manual_approval"):
        return "Manual review/approval required before promotion or export."
    return None


def get_visual_action_surface_contract() -> Dict[str, Any]:
    registry = get_cockpit_action_registry()
    controls: List[Dict[str, Any]] = []
    for action in registry["actions"]:
        state = "enabled" if action["enabled"] else "blocked"
        controls.append(
            {
                "action_id": action["action_id"],
                "label": action["label"],
                "category": action["category"],
                "visual_state": state,
                "button_enabled": bool(action["enabled"]),
                "requires_manual_approval": bool(action.get("requires_manual_approval")),
                "requires_quarantine": bool(action.get("requires_quarantine")),
                "blocked_reason": action.get("blocked_reason"),
                "warning": _warning_for_action(action),
            }
        )
    return {
        "stage": "S185",
        "contract_type": "visual_action_surface",
        "backend_owned": True,
        "cockpit_presentation_only": True,
        "controls": controls,
    }


def get_monitoring_backend_state() -> Dict[str, Any]:
    registry = get_cockpit_action_registry()
    return {
        "stage": "S186",
        "contract_type": "monitoring_backend_core",
        "backend_owned": True,
        "health": {
            "backend": "available",
            "canonical_payload": "available",
            "governance": "locked",
            "cockpit": "presentation_only",
        },
        "queues": {
            "review_queue": {"state": "ready", "count": 0},
            "export_queue": {"state": "ready", "count": 0},
            "web_jobs": {"state": "bounded_only", "active": 0, "continuous_allowed": False},
            "mutation_proposals": {"state": "proposal_only", "count": 0, "execution_allowed": False},
        },
        "locks": deepcopy(LOCKS),
        "action_summary": registry["summary"],
    }


def get_operator_notifications() -> Dict[str, Any]:
    monitoring = get_monitoring_backend_state()
    notifications = [
        {
            "notification_id": "governance-locks-active",
            "severity": "info",
            "title": "Governance locks active",
            "message": "Runtime mutation, automatic updates, autonomous execution, and continuous crawling remain blocked.",
            "requires_operator_action": False,
        },
        {
            "notification_id": "manual-promotion-required",
            "severity": "info",
            "title": "Manual promotion required",
            "message": "Evidence and candidates must remain quarantined until an operator approves promotion.",
            "requires_operator_action": False,
        },
    ]
    if monitoring["action_summary"]["unsafe_enabled"]:
        notifications.append(
            {
                "notification_id": "unsafe-authority-enabled",
                "severity": "critical",
                "title": "Unsafe authority enabled",
                "message": "At least one unsafe authority action is enabled. Forward motion must stop.",
                "requires_operator_action": True,
            }
        )
    return {
        "stage": "S187",
        "contract_type": "operator_notification_pipeline",
        "backend_owned": True,
        "notifications": notifications,
    }


def get_cockpit_panel_wiring_contract() -> Dict[str, Any]:
    return {
        "stage": "S188",
        "contract_type": "cockpit_panel_wiring",
        "backend_owned": True,
        "panels": [
            {"panel_id": "command_bar", "source": "visual_action_surface", "required": True},
            {"panel_id": "runtime_status", "source": "monitoring_backend_core", "required": True},
            {"panel_id": "governance_locks", "source": "monitoring_backend_core", "required": True},
            {"panel_id": "web_jobs", "source": "monitoring_backend_core", "required": True},
            {"panel_id": "review_queue", "source": "review_approval_contract", "required": True},
            {"panel_id": "export_queue", "source": "monitoring_backend_core", "required": True},
            {"panel_id": "operator_notifications", "source": "operator_notification_pipeline", "required": True},
            {"panel_id": "diagnostics_drawer", "source": "all_contracts", "required": True, "default_visible": False},
        ],
        "layout_rule": "consolidated_single_cockpit_with_diagnostics_hidden_by_default",
        "frontend_authority": "presentation_only",
    }


def get_review_approval_contract() -> Dict[str, Any]:
    return {
        "stage": "S189",
        "contract_type": "review_approval_interaction",
        "backend_owned": True,
        "manual_approval_mandatory": True,
        "quarantine_mandatory": True,
        "allowed_decisions": ["approve_for_reviewed_export", "reject", "request_more_evidence", "hold_in_quarantine"],
        "blocked_decisions": [
            "write_runtime_truth_directly",
            "execute_runtime_mutation",
            "enable_automatic_updates",
            "start_continuous_crawl",
            "autonomous_execute",
        ],
        "audit_fields": [
            "review_id",
            "operator_id",
            "decision",
            "timestamp",
            "evidence_ids",
            "reason",
            "target_contract",
        ],
    }


def get_operational_cockpit_plateau() -> Dict[str, Any]:
    contracts = {
        "visual_actions": get_visual_action_surface_contract(),
        "monitoring": get_monitoring_backend_state(),
        "notifications": get_operator_notifications(),
        "panel_wiring": get_cockpit_panel_wiring_contract(),
        "review_approval": get_review_approval_contract(),
    }
    unsafe_enabled = contracts["monitoring"]["action_summary"]["unsafe_enabled"]
    required_panels = [p for p in contracts["panel_wiring"]["panels"] if p.get("required")]
    return {
        "stage": "S190",
        "contract_type": "operational_cockpit_plateau",
        "version": "v19.89.8-S185-S190",
        "plateau_reached": len(unsafe_enabled) == 0 and len(required_panels) >= 8,
        "safe_forward_motion": len(unsafe_enabled) == 0,
        "contracts": contracts,
        "countdown": {
            "to_first_governed_internet_connected_operational_platform": "12-22 builds",
            "to_practical_web_connected_daily_use_platform": "29-49 builds",
            "to_modern_enterprise_cockpit_dashboard_completion": "39-64 builds",
        },
    }
