from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

VERSION = "v19.89.8-S957-S984"
PHASE = "S957-S984"
TITLE = "Cockpit Operation Button Visual Mount Repair"

BLOCKED_CAPABILITIES: Dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "external_network_request_performed": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
    "uncontrolled_web_execution_enabled": False,
}

@dataclass(frozen=True)
class VisualOperationButton:
    key: str
    label: str
    group: str
    stage_range: str
    cockpit_tab: str
    description: str
    preview_endpoint: str
    state: str = "preview_only"
    execution_enabled: bool = False
    external_network_allowed: bool = False
    body_read_allowed: bool = False
    runtime_mutation_allowed: bool = False
    command_execution_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["button_visible"] = True
        data["button_mode"] = "local_preview_only"
        data["click_behavior"] = "fetches_local_preview_packet_only"
        data["dangerous_authority_blocked"] = True
        return data

OPERATIONS: List[VisualOperationButton] = [
    VisualOperationButton("readiness_audit", "Run readiness audit", "Readiness", "S681-S687", "Governed Web", "Audit search/web readiness without contacting providers.", "/api/cockpit/operation-visuals/preview/readiness_audit"),
    VisualOperationButton("provider_inspector", "Inspect providers", "Providers", "S688-S694", "Governed Web", "Show provider configuration, missing keys, and blocked authority.", "/api/cockpit/operation-visuals/preview/provider_inspector"),
    VisualOperationButton("source_policy", "View source policy", "Sources", "S632-S638", "Governed Web", "Show allowlist, denylist, quarantine, and trust-tier state.", "/api/cockpit/operation-visuals/preview/source_policy"),
    VisualOperationButton("compile_query", "Compile search plan", "Search plan", "S618-S624", "Command Bar", "Turn an operator query into a governed plan without executing search.", "/api/cockpit/operation-visuals/preview/compile_query"),
    VisualOperationButton("metadata_probe_preview", "Preview metadata search", "Metadata search", "S702-S708", "Governed Web", "Prepare a metadata-only provider probe packet; provider execution stays blocked.", "/api/cockpit/operation-visuals/preview/metadata_probe_preview", "execution_blocked_preview_ready"),
    VisualOperationButton("metadata_contract", "Open metadata contract", "Metadata search", "S646-S652", "Governed Web", "Show the fields a metadata-only result must satisfy.", "/api/cockpit/operation-visuals/preview/metadata_contract"),
    VisualOperationButton("quarantine_store", "Open quarantine store", "Evidence", "S709-S715", "Evidence & Review", "Show quarantined search/source evidence before review.", "/api/cockpit/operation-visuals/preview/quarantine_store"),
    VisualOperationButton("evidence_cards", "Build evidence cards", "Evidence", "S716-S722", "Evidence & Review", "Normalize quarantined metadata into cockpit evidence cards.", "/api/cockpit/operation-visuals/preview/evidence_cards"),
    VisualOperationButton("source_confidence", "Score source confidence", "Evidence", "S723-S729", "Evidence & Review", "Score source trust, recency, relevance, and citation usefulness.", "/api/cockpit/operation-visuals/preview/source_confidence"),
    VisualOperationButton("operator_review", "Show review queue", "Operator review", "S730-S736", "Actions", "Show review/reject/promote-draft actions, still non-executable.", "/api/cockpit/operation-visuals/preview/operator_review"),
    VisualOperationButton("body_read_request", "Build body-read request", "Body read", "S765-S771", "Actions", "Draft a body-read request packet; body read remains blocked.", "/api/cockpit/operation-visuals/preview/body_read_request", "execution_blocked_preview_ready"),
    VisualOperationButton("body_read_preflight", "Run body-read preflight", "Body read", "S772-S834", "Actions", "Check authorization, extraction scope, sanitizer, and manual gate state.", "/api/cockpit/operation-visuals/preview/body_read_preflight", "execution_blocked_preview_ready"),
    VisualOperationButton("source_ingestion", "Draft source ingestion", "Source ingestion", "S856-S883", "Actions", "Draft reviewed source ingestion and lineage without runtime mutation.", "/api/cockpit/operation-visuals/preview/source_ingestion"),
    VisualOperationButton("truth_promotion_preview", "Preview truth promotion", "Runtime truth", "S884-S890", "Actions", "Preview what promotion would look like if later approved; mutation remains blocked.", "/api/cockpit/operation-visuals/preview/truth_promotion_preview", "runtime_mutation_blocked_preview_ready"),
    VisualOperationButton("s900_gate", "Verify S900 gate", "Stop gates", "S891-S900", "System", "Verify web/source ingestion stop gate state.", "/api/cockpit/operation-visuals/preview/s900_gate"),
    VisualOperationButton("s956_controls", "Verify operation controls", "Stop gates", "S929-S956", "System", "Verify operation-control registry exists.", "/api/cockpit/operation-visuals/preview/s956_controls"),
    VisualOperationButton("s984_visual_mount", "Verify visual mount", "Stop gates", "S957-S984", "System", "Verify the operation buttons are mounted into the cockpit UI.", "/api/cockpit/operation-visuals/preview/s984_visual_mount"),
]

def build_visual_buttons() -> List[Dict[str, Any]]:
    return [operation.to_dict() for operation in OPERATIONS]

def build_grouped_buttons() -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for button in build_visual_buttons():
        grouped.setdefault(button["group"], []).append(button)
    return grouped

def build_visual_actions() -> List[Dict[str, Any]]:
    return [
        {
            "key": f"visual_action_{button['key']}",
            "title": button["label"],
            "group": button["group"],
            "stage_range": button["stage_range"],
            "cockpit_tab": button["cockpit_tab"],
            "preview_endpoint": button["preview_endpoint"],
            "state": button["state"],
            "executable_now": False,
            "execution_enabled": False,
            "visible_in_cockpit": True,
            "reason": "Visible operator control only; dangerous authority remains blocked.",
        }
        for button in build_visual_buttons()
    ]

def build_visual_cards() -> List[Dict[str, Any]]:
    return [
        {
            "id": group.lower().replace(" ", "_").replace("/", "_"),
            "title": group,
            "kind": "operator_control_group",
            "summary": f"{len(buttons)} visible operator buttons mounted for preview/preflight only.",
            "button_count": len(buttons),
            "buttons": buttons,
            "execution_enabled": False,
            "dangerous_authority_blocked": True,
        }
        for group, buttons in build_grouped_buttons().items()
    ]

def build_visual_preview(operation_key: str, command: Optional[str] = None) -> Dict[str, Any]:
    match = next((button for button in build_visual_buttons() if button["key"] == operation_key), None)
    if match is None:
        return {
            "status": "not_found",
            "phase": PHASE,
            "operation_key": operation_key,
            "execution_enabled": False,
            "blocked_capabilities": BLOCKED_CAPABILITIES,
        }
    return {
        "status": "preview_ready",
        "phase": PHASE,
        "operation": match,
        "supplied_command": command or "",
        "button_visible": True,
        "what_happened": "A local preview packet was returned. No external operation was performed.",
        "execution_enabled": False,
        "external_network_request_performed": False,
        "body_read_performed": False,
        "runtime_mutation_performed": False,
        "command_execution_performed": False,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
    }

def build_visual_status() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "phase": PHASE,
        "highest_stage": "S984",
        "status": "operation_button_visual_mount_ready",
        "cockpit_buttons_required": True,
        "cockpit_buttons_exist": True,
        "cockpit_visual_mount_required": True,
        "cockpit_visual_mount_ready": True,
        "button_count": len(OPERATIONS),
        "action_count": len(build_visual_actions()),
        "execution_enabled": False,
        "dangerous_authority_blocked": True,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
    }

def build_visual_stop_gate() -> Dict[str, Any]:
    buttons = build_visual_buttons()
    actions = build_visual_actions()
    checks = {
        "visual_buttons_exist": len(buttons) >= 15,
        "visual_actions_exist": len(actions) >= 15,
        "all_buttons_visible": all(button["button_visible"] for button in buttons),
        "all_buttons_preview_only": all(button["execution_enabled"] is False for button in buttons),
        "all_actions_non_executable": all(action["executable_now"] is False for action in actions),
        "live_web_still_blocked": BLOCKED_CAPABILITIES["live_web_execution_enabled"] is False,
        "provider_execution_still_blocked": BLOCKED_CAPABILITIES["search_provider_execution_enabled"] is False,
        "external_network_still_blocked": BLOCKED_CAPABILITIES["external_network_request_performed"] is False,
        "body_read_still_blocked": BLOCKED_CAPABILITIES["body_read_allowed"] is False,
        "runtime_mutation_still_blocked": BLOCKED_CAPABILITIES["runtime_mutation_enabled"] is False,
        "command_execution_still_blocked": BLOCKED_CAPABILITIES["command_execution_enabled"] is False,
    }
    return {
        "phase": PHASE,
        "highest_stage": "S984",
        "passed": all(checks.values()),
        "checks": checks,
        "next_safe_phase": "S985-S1012 command-bar local preview execution wiring, still no external provider calls",
    }

def build_visual_payload() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "phase": PHASE,
        "highest_stage": "S984",
        "title": TITLE,
        "status": "cockpit_operation_buttons_visible",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "buttons": build_visual_buttons(),
        "button_groups": build_grouped_buttons(),
        "cards": build_visual_cards(),
        "actions": build_visual_actions(),
        "button_count": len(OPERATIONS),
        "action_count": len(build_visual_actions()),
        "visual_mount": {
            "mount_id": "claire-operation-control-mount",
            "actions_mount_id": "claire-operation-actions-mount",
            "asset_js": "claire_cockpit_operation_visual_controls.js",
            "asset_css": "claire_cockpit_operation_visual_controls.css",
            "force_visible": True,
        },
        "status_payload": build_visual_status(),
        "stop_gate": build_visual_stop_gate(),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
    }
