from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

VERSION = "v19.89.8-S929-S956"
PHASE = "S929-S956"
TITLE = "Cockpit Operation Controls + Command Bar Action Surface"

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
class OperationButton:
    key: str
    label: str
    group: str
    stage_range: str
    cockpit_tab: str
    intent: str
    preview_endpoint: str
    target_payload_endpoint: str
    action_state: str
    blocked_reason: str
    requires_operator_review: bool = True
    execution_enabled: bool = False
    external_network_allowed: bool = False
    body_read_allowed: bool = False
    runtime_mutation_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["safe_button"] = True
        data["button_mode"] = "preview_only"
        data["click_behavior"] = "local_backend_preview_no_external_execution"
        return data

OPERATIONS: List[OperationButton] = [
    OperationButton("readiness_audit", "Run readiness audit", "Readiness", "S681-S687", "Governed Web", "Show readiness checks before metadata search activation.", "/api/cockpit/operations/preview/readiness_audit", "/api/search/readiness/audit", "available_preview_only", "Audit is local status only; no provider execution is enabled."),
    OperationButton("provider_configuration", "Inspect providers", "Providers", "S688-S694", "Governed Web", "Inspect configured/missing/blocked provider state without using a provider.", "/api/cockpit/operations/preview/provider_configuration", "/api/search/providers/configuration/payload", "available_preview_only", "Provider inspection is local configuration visibility only."),
    OperationButton("query_compile", "Compile search plan", "Search planning", "S618-S624", "Governed Web", "Compile a governed query plan with source scope, trust tier, and risk constraints.", "/api/cockpit/operations/preview/query_compile", "/api/search/governed/query/sample", "available_preview_only", "Compiling a plan does not execute search or contact external providers."),
    OperationButton("metadata_probe_preflight", "Preview metadata search", "Metadata search", "S702-S708", "Governed Web", "Preview the manual metadata-search probe gate before any real provider request.", "/api/cockpit/operations/preview/metadata_probe_preflight", "/api/search/metadata/probe/manual/preflight", "blocked_execution_preview_ready", "Search provider execution and external network requests remain blocked."),
    OperationButton("metadata_contract", "View metadata contract", "Metadata search", "S646-S652", "Governed Web", "Show the metadata-only result contract that search output must satisfy.", "/api/cockpit/operations/preview/metadata_contract", "/api/search/metadata/contract", "available_preview_only", "Contract view is local and does not perform search."),
    OperationButton("quarantine_review", "Open quarantine review", "Evidence review", "S709-S715", "Evidence & Review", "Show quarantined result-review status before anything becomes runtime truth.", "/api/cockpit/operations/preview/quarantine_review", "/api/search/results/quarantine/cards", "available_preview_only", "Quarantine review is visible only; automatic promotion remains blocked."),
    OperationButton("evidence_normalize", "Build evidence cards", "Evidence review", "S716-S722", "Evidence & Review", "Normalize metadata/search results into cockpit evidence cards.", "/api/cockpit/operations/preview/evidence_normalize", "/api/search/results/normalize/payload", "available_preview_only", "Evidence card normalization uses quarantined payloads only."),
    OperationButton("source_confidence", "Score source confidence", "Evidence review", "S723-S729", "Evidence & Review", "Preview source confidence and citation-candidate scoring.", "/api/cockpit/operations/preview/source_confidence", "/api/search/source-confidence/payload", "available_preview_only", "Confidence scoring is review support only and does not mutate runtime truth."),
    OperationButton("operator_review_actions", "Show review actions", "Operator actions", "S730-S736", "Actions", "Show operator review/reject/promote-draft action descriptors.", "/api/cockpit/operations/preview/operator_review_actions", "/api/search/operator-review/actions", "available_preview_only", "Actions are descriptors; executable approval flow is not enabled here."),
    OperationButton("body_read_request_packet", "Build body-read request", "Body read planning", "S765-S771", "Actions", "Create a manual body-read request packet for an approved result.", "/api/cockpit/operations/preview/body_read_request_packet", "/api/web/body-read/request-packet", "blocked_execution_preview_ready", "Body reads remain blocked; this only previews the request packet."),
    OperationButton("body_read_preflight", "Run body-read preflight", "Body read planning", "S772-S834", "Actions", "Show body-read authorization, extraction scope, sanitizer, and manual gate state.", "/api/cockpit/operations/preview/body_read_preflight", "/api/cockpit/body-read-gate/payload", "blocked_execution_preview_ready", "Body-read execution is not enabled; preflight is local status only."),
    OperationButton("source_ingestion_draft", "Draft source ingestion", "Source ingestion", "S856-S883", "Actions", "Preview reviewed source ingestion draft, lineage, validation, and operator queue.", "/api/cockpit/operations/preview/source_ingestion_draft", "/api/cockpit/source-ingestion/payload", "available_preview_only", "Ingestion is draft/review only; runtime truth mutation remains blocked."),
    OperationButton("runtime_truth_promotion_preview", "Preview truth promotion", "Runtime truth", "S884-S890", "Actions", "Preview how reviewed evidence would be promoted if a later gate allowed it.", "/api/cockpit/operations/preview/runtime_truth_promotion_preview", "/api/web/runtime-truth/promotion-preview", "blocked_execution_preview_ready", "Runtime truth mutation is explicitly blocked."),
    OperationButton("s900_stop_gate", "Verify S900 gate", "Stop gates", "S891-S900", "System", "Show the S900 web/source ingestion stop gate proof.", "/api/cockpit/operations/preview/s900_stop_gate", "/api/internet/s900-stop-gate", "available_preview_only", "Stop gate is local proof only."),
    OperationButton("s956_control_gate", "Verify operation controls", "Stop gates", "S929-S956", "System", "Show that operation controls exist while dangerous execution stays blocked.", "/api/cockpit/operations/preview/s956_control_gate", "/api/cockpit/operations/stop-gate", "available_preview_only", "This is the current cockpit operation-control stop gate."),
]

def _grouped_buttons() -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for operation in OPERATIONS:
        grouped.setdefault(operation.group, []).append(operation.to_dict())
    return grouped

def build_operation_buttons() -> List[Dict[str, Any]]:
    return [operation.to_dict() for operation in OPERATIONS]

def build_operation_actions() -> List[Dict[str, Any]]:
    return [
        {
            "key": f"action_{operation.key}",
            "title": operation.label,
            "source": "cockpit_operation_controls",
            "stage_range": operation.stage_range,
            "cockpit_tab": operation.cockpit_tab,
            "action_type": "operator_button_preview",
            "state": operation.action_state,
            "preview_endpoint": operation.preview_endpoint,
            "target_payload_endpoint": operation.target_payload_endpoint,
            "executable_now": False,
            "execution_enabled": False,
            "requires_operator_review": operation.requires_operator_review,
            "reason": operation.blocked_reason,
        }
        for operation in OPERATIONS
    ]

def build_operation_cards() -> List[Dict[str, Any]]:
    return [
        {
            "id": group.lower().replace(" ", "_").replace("/", "_"),
            "title": group,
            "kind": "operation_group",
            "summary": f"{len(operations)} cockpit operation controls available as preview-only buttons.",
            "button_count": len(operations),
            "operations": operations,
            "execution_enabled": False,
            "external_network_allowed": False,
            "status": "buttons_visible_execution_blocked",
        }
        for group, operations in _grouped_buttons().items()
    ]

def build_button_preview(operation_key: str, supplied_command: Optional[str] = None) -> Dict[str, Any]:
    match = next((operation for operation in OPERATIONS if operation.key == operation_key), None)
    if match is None:
        return {
            "status": "not_found",
            "operation_key": operation_key,
            "message": "No cockpit operation control exists for the supplied key.",
            "execution_enabled": False,
            "blocked_capabilities": BLOCKED_CAPABILITIES,
        }
    return {
        "status": "preview_ready",
        "phase": PHASE,
        "operation": match.to_dict(),
        "supplied_command": supplied_command or "",
        "what_click_does_now": "Returns this local preview packet only.",
        "what_click_does_not_do": [
            "does not execute a web search provider",
            "does not perform an external network request",
            "does not read page bodies",
            "does not crawl",
            "does not mutate runtime truth",
            "does not install packages",
            "does not execute commands",
        ],
        "safe_forward_motion": True,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
    }

def build_command_surface() -> Dict[str, Any]:
    return {
        "status": "command_surface_buttons_ready",
        "mode": "operator_preview_only",
        "placeholder": "Ask Claire or run a governed web operation...",
        "primary_buttons": [
            "readiness_audit",
            "provider_configuration",
            "query_compile",
            "metadata_probe_preflight",
            "quarantine_review",
            "body_read_preflight",
            "source_ingestion_draft",
        ],
        "button_count": len(OPERATIONS),
        "execution_enabled": False,
        "command_execution_enabled": False,
        "search_provider_execution_enabled": False,
        "body_read_allowed": False,
    }

def build_status() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "phase": PHASE,
        "status": "operation_controls_ready",
        "highest_stage": "S956",
        "cockpit_buttons_exist": True,
        "operation_count": len(OPERATIONS),
        "action_count": len(build_operation_actions()),
        "button_groups": sorted(_grouped_buttons().keys()),
        "execution_enabled": False,
        "dangerous_authority_blocked": True,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
    }

def build_stop_gate() -> Dict[str, Any]:
    buttons = build_operation_buttons()
    actions = build_operation_actions()
    checks = {
        "operation_buttons_exist": len(buttons) >= 10,
        "actions_registered": len(actions) >= 10,
        "all_buttons_preview_only": all(button["execution_enabled"] is False for button in buttons),
        "all_actions_non_executable": all(action["executable_now"] is False for action in actions),
        "live_web_still_blocked": BLOCKED_CAPABILITIES["live_web_execution_enabled"] is False,
        "provider_execution_still_blocked": BLOCKED_CAPABILITIES["search_provider_execution_enabled"] is False,
        "external_network_still_blocked": BLOCKED_CAPABILITIES["external_network_request_performed"] is False,
        "body_read_still_blocked": BLOCKED_CAPABILITIES["body_read_allowed"] is False,
        "runtime_mutation_still_blocked": BLOCKED_CAPABILITIES["runtime_mutation_enabled"] is False,
        "package_install_still_blocked": BLOCKED_CAPABILITIES["package_install_performed"] is False,
        "command_execution_still_blocked": BLOCKED_CAPABILITIES["command_execution_enabled"] is False,
    }
    return {
        "phase": PHASE,
        "highest_stage": "S956",
        "passed": all(checks.values()),
        "checks": checks,
        "next_safe_phase": "S957-S984 command button wiring to existing local preflight endpoints, still no external execution",
        "not_ready_for": [
            "unrestricted open web",
            "body reads",
            "autonomous crawling",
            "automatic updates",
            "runtime mutation",
            "package install",
            "command execution",
        ],
    }

def build_operation_payload() -> Dict[str, Any]:
    buttons = build_operation_buttons()
    actions = build_operation_actions()
    return {
        "version": VERSION,
        "phase": PHASE,
        "title": TITLE,
        "status": "operation_controls_ready",
        "highest_stage": "S956",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "cockpit_buttons_exist": True,
        "operation_count": len(buttons),
        "action_count": len(actions),
        "buttons": buttons,
        "button_groups": _grouped_buttons(),
        "cards": build_operation_cards(),
        "actions": actions,
        "command_surface": build_command_surface(),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "stop_gate": build_stop_gate(),
    }
