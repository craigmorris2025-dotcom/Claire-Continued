from __future__ import annotations

"""
Claire Dashboard Update-Control Cockpit Wiring — S562-S568

This module wires the governed update-control runway into cockpit-ready backend
truth packets. It does not add update authority.

It builds on:
- S506-S512 Governed Update Inspector
- S513-S519 Staged Update Sandbox Contract
- S520-S526 Controlled Validation Plan
- S527-S533 Update Evidence Review Queue
- S534-S540 Validation Result Intake
- S541-S547 Promotion Decision Packet
- S548-S554 Rollback Recovery Gate
- S555-S561 Operator Staged Update Handoff

Purpose:
- register the update-control cockpit panels
- aggregate readiness from the update runway modules
- define presentation-only action-button contracts
- expose blocked-authority status for the cockpit
- build a review-only cockpit payload section
- prove no apply/install/update/mutation authority is enabled

No update is applied, no package is installed, no package is downloaded, no
command is executed, no backup is created, no restore is performed, no promotion
occurs, no persistent cockpit store is written, and no runtime truth is mutated.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


VERSION = "v19.89.8-S562-S568"
PHASE = "S562-S568"
JS_ASSET = "frontend/cockpit/shell/assets/claire_update_control_cockpit_wiring.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_update_control_cockpit_wiring.css"


BLOCKED_AUTHORITY: Dict[str, bool] = {
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_allowed": False,
    "runtime_truth_write_allowed": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "autonomous_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "package_execution_enabled": False,
    "package_export_performed": False,
    "sandbox_file_write_performed": False,
    "sandbox_created": False,
    "test_execution_performed": False,
    "validation_execution_performed": False,
    "promotion_performed": False,
    "promotion_allowed_now": False,
    "update_apply_allowed": False,
    "backup_created": False,
    "restore_performed": False,
    "rollback_execution_performed": False,
    "recovery_execution_performed": False,
    "handoff_execution_performed": False,
    "application_handoff_performed": False,
    "cockpit_action_execution_performed": False,
    "cockpit_persistent_write_performed": False,
}


UPDATE_CONTROL_RUNWAY: List[Dict[str, str]] = [
    {
        "stage_range": "S506-S512",
        "module": "claire.api.claire_governed_update_inspector_s506_s512",
        "label": "Governed update inspector",
        "owner": "metadata_inspection",
    },
    {
        "stage_range": "S513-S519",
        "module": "claire.api.claire_staged_update_sandbox_contract_s513_s519",
        "label": "Staged update sandbox contract",
        "owner": "sandbox_contract",
    },
    {
        "stage_range": "S520-S526",
        "module": "claire.api.claire_controlled_update_validation_plan_s520_s526",
        "label": "Controlled validation plan",
        "owner": "validation_plan",
    },
    {
        "stage_range": "S527-S533",
        "module": "claire.api.claire_update_evidence_review_queue_s527_s533",
        "label": "Update evidence review queue",
        "owner": "review_queue",
    },
    {
        "stage_range": "S534-S540",
        "module": "claire.api.claire_validation_result_intake_s534_s540",
        "label": "Validation result intake",
        "owner": "result_intake",
    },
    {
        "stage_range": "S541-S547",
        "module": "claire.api.claire_update_promotion_decision_packet_s541_s547",
        "label": "Promotion decision packet",
        "owner": "promotion_packet",
    },
    {
        "stage_range": "S548-S554",
        "module": "claire.api.claire_rollback_recovery_gate_s548_s554",
        "label": "Rollback recovery gate",
        "owner": "rollback_gate",
    },
    {
        "stage_range": "S555-S561",
        "module": "claire.api.claire_operator_staged_update_handoff_s555_s561",
        "label": "Operator staged update handoff",
        "owner": "handoff",
    },
]


COCKPIT_PANEL_ORDER = [
    "update_runway_overview",
    "governed_update_inspector",
    "staged_update_sandbox",
    "controlled_validation_plan",
    "update_evidence_review_queue",
    "validation_result_intake",
    "promotion_decision_packet",
    "rollback_recovery_gate",
    "operator_staged_update_handoff",
    "blocked_authority_matrix",
]


ACTION_BUTTONS = [
    "view_update_runway",
    "open_review_queue",
    "inspect_validation_results",
    "review_promotion_packet",
    "review_rollback_gate",
    "review_handoff_packet",
    "export_review_snapshot_disabled",
    "apply_update_disabled",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": VERSION,
        "phase": PHASE,
        "stage_version": stage_version,
        "status": status,
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "created_at": _now(),
    }
    payload.update(BLOCKED_AUTHORITY)
    payload.update(extra)
    return payload


def _stable_id(prefix: str, *parts: Any) -> str:
    joined = "|".join(str(part) for part in parts)
    return f"{prefix}_{abs(hash(joined)) % 10_000_000:07d}"


def _import_module(module_name: str):
    return __import__(module_name, fromlist=["*"])


def _call_if_available(module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Tuple[bool, Dict[str, Any]]:
    try:
        module = _import_module(module_name)
        fn = getattr(module, function_name)
        result = fn(*args, **kwargs)
        if isinstance(result, dict):
            return True, result
        return False, {"error": "function_returned_non_dict", "function": function_name}
    except Exception as exc:
        return False, {"error": repr(exc), "function": function_name, "module": module_name}


def build_s562_update_control_panel_registry() -> Dict[str, Any]:
    panels = [
        {
            "panel_id": "update_runway_overview",
            "label": "Update Runway Overview",
            "source_stage": "S562-S568",
            "purpose": "Show the full governed update-control chain.",
            "authority": "presentation_only",
            "enabled": True,
        },
        {
            "panel_id": "governed_update_inspector",
            "label": "Governed Update Inspector",
            "source_stage": "S506-S512",
            "purpose": "Show metadata-only update candidate inspection.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "staged_update_sandbox",
            "label": "Staged Update Sandbox",
            "source_stage": "S513-S519",
            "purpose": "Show sandbox contract status without creating sandbox files.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "controlled_validation_plan",
            "label": "Controlled Validation Plan",
            "source_stage": "S520-S526",
            "purpose": "Show planned validation commands without executing them.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "update_evidence_review_queue",
            "label": "Update Evidence Review Queue",
            "source_stage": "S527-S533",
            "purpose": "Show evidence bundles and review packets.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "validation_result_intake",
            "label": "Validation Result Intake",
            "source_stage": "S534-S540",
            "purpose": "Show manually supplied validation result intake packets.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "promotion_decision_packet",
            "label": "Promotion Decision Packet",
            "source_stage": "S541-S547",
            "purpose": "Show promotion eligibility and blockers.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "rollback_recovery_gate",
            "label": "Rollback Recovery Gate",
            "source_stage": "S548-S554",
            "purpose": "Show rollback proof and recovery gate blockers.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "operator_staged_update_handoff",
            "label": "Operator Staged Update Handoff",
            "source_stage": "S555-S561",
            "purpose": "Show approval/handoff boundary and final blockers.",
            "authority": "review_only",
            "enabled": True,
        },
        {
            "panel_id": "blocked_authority_matrix",
            "label": "Blocked Authority Matrix",
            "source_stage": "S562-S568",
            "purpose": "Show all disabled update authorities.",
            "authority": "presentation_only",
            "enabled": True,
        },
    ]

    return _safe_base(
        "S562",
        "update_control_panel_registry_ready",
        panel_order=COCKPIT_PANEL_ORDER,
        panels=panels,
        panel_count=len(panels),
        registry_rules=[
            "Panels display backend truth only.",
            "Panel registration does not create routes or apply updates.",
            "Control surfaces remain review-only.",
        ],
    )


def build_update_runway_readiness_summary(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    modules: List[Dict[str, Any]] = []

    for item in UPDATE_CONTROL_RUNWAY:
        ok = False
        detail = "not_checked"
        stop_gate_ready = None

        try:
            module = _import_module(item["module"])
            ok = True
            detail = "import_ok"
            stop_gate_fn = None
            for name in dir(module):
                if name.startswith("build_s") and name.endswith("_stop_gate"):
                    stop_gate_fn = getattr(module, name)
                    break
            if stop_gate_fn is not None:
                try:
                    stop_gate = stop_gate_fn(project_root=root)
                    stop_gate_ready = bool(stop_gate.get("forward_motion_allowed") is True)
                except Exception as exc:
                    stop_gate_ready = False
                    detail = f"stop_gate_error: {exc!r}"
        except Exception as exc:
            detail = repr(exc)

        modules.append(
            {
                "stage_range": item["stage_range"],
                "label": item["label"],
                "owner": item["owner"],
                "module": item["module"],
                "import_ok": ok,
                "stop_gate_ready": stop_gate_ready,
                "detail": detail,
            }
        )

    summary = {
        "runway_summary_id": _stable_id("update_runway_summary", [module["stage_range"] for module in modules]),
        "version": VERSION,
        "created_at": _now(),
        "module_count": len(modules),
        "modules": modules,
        "all_modules_import": all(module["import_ok"] for module in modules),
        "all_checked_stop_gates_ready": all(module["stop_gate_ready"] is not False for module in modules),
        "ready_stage_count": sum(1 for module in modules if module["import_ok"]),
        "authority_state": "blocked_review_only",
    }
    summary.update(BLOCKED_AUTHORITY)
    return summary


def build_s563_update_runway_readiness_contract(project_root: str | Path | None = None) -> Dict[str, Any]:
    summary = build_update_runway_readiness_summary(project_root)
    return _safe_base(
        "S563",
        "update_runway_readiness_contract_ready",
        sample_summary={
            "module_count": summary["module_count"],
            "all_modules_import": summary["all_modules_import"],
            "ready_stage_count": summary["ready_stage_count"],
            "authority_state": summary["authority_state"],
        },
        readiness_rules=[
            "Readiness summary imports and reads contracts only.",
            "Stop gates are checked as backend truth references.",
            "No update action is performed.",
        ],
    )


def build_cockpit_action_button_contracts() -> Dict[str, Any]:
    buttons = []
    for button_id in ACTION_BUTTONS:
        disabled = button_id.endswith("_disabled") or button_id in {"apply_update_disabled", "export_review_snapshot_disabled"}
        buttons.append(
            {
                "button_id": button_id,
                "label": button_id.replace("_", " ").title(),
                "visible": True,
                "enabled": not disabled,
                "execution_allowed": False,
                "execution_performed": False,
                "authority": "presentation_only" if not disabled else "blocked",
                "disabled_reason": "unsafe_authority_not_enabled" if disabled else "review_navigation_only",
            }
        )

    return _safe_base(
        "S564",
        "cockpit_action_button_contracts_ready",
        buttons=buttons,
        button_count=len(buttons),
        action_rules=[
            "Enabled buttons are navigation/review only.",
            "Disabled buttons make blocked authorities visible.",
            "No cockpit button executes updates in this phase.",
        ],
    )


def build_blocked_authority_matrix() -> Dict[str, Any]:
    blocked_items = [
        {
            "authority": key,
            "enabled": value,
            "status": "blocked" if value is False else "unexpected_enabled",
            "display_group": (
                "internet" if key in {"live_web_execution_enabled", "browser_execution_enabled", "network_request_performed", "body_read_allowed"}
                else "update_application" if key in {"package_install_performed", "update_apply_allowed", "package_execution_enabled", "promotion_performed"}
                else "runtime" if "runtime" in key
                else "execution" if "execution" in key or "test" in key
                else "rollback_recovery" if key in {"backup_created", "restore_performed", "rollback_execution_performed", "recovery_execution_performed"}
                else "cockpit"
            ),
        }
        for key, value in sorted(BLOCKED_AUTHORITY.items())
    ]

    matrix = {
        "blocked_authority_matrix_id": _stable_id("blocked_authority_matrix", len(blocked_items)),
        "version": VERSION,
        "created_at": _now(),
        "items": blocked_items,
        "item_count": len(blocked_items),
        "all_blocked": all(item["enabled"] is False for item in blocked_items),
        "unexpected_enabled": [item["authority"] for item in blocked_items if item["enabled"] is not False],
    }
    matrix.update(BLOCKED_AUTHORITY)
    return matrix


def build_s565_blocked_authority_display_contract() -> Dict[str, Any]:
    matrix = build_blocked_authority_matrix()
    return _safe_base(
        "S565",
        "blocked_authority_display_contract_ready",
        sample_matrix={
            "item_count": matrix["item_count"],
            "all_blocked": matrix["all_blocked"],
            "unexpected_enabled": matrix["unexpected_enabled"],
        },
        display_rules=[
            "Cockpit must visibly show disabled update authority.",
            "Blocked does not mean missing; it means intentionally gated.",
            "No authority can be enabled by the cockpit display contract.",
        ],
    )


def build_update_control_cockpit_payload(project_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_s562_update_control_panel_registry()
    readiness = build_update_runway_readiness_summary(project_root)
    buttons = build_cockpit_action_button_contracts()
    matrix = build_blocked_authority_matrix()

    payload = {
        "update_control_cockpit_payload_id": _stable_id("update_control_cockpit_payload", readiness.get("runway_summary_id")),
        "version": VERSION,
        "created_at": _now(),
        "title": "Claire Governed Update Control",
        "subtitle": "Readiness runway through S561; dashboard wiring through S568.",
        "panel_registry": registry,
        "runway_readiness": readiness,
        "action_buttons": buttons,
        "blocked_authority_matrix": matrix,
        "primary_status": "review_only_ready" if readiness["all_modules_import"] and matrix["all_blocked"] else "needs_attention",
        "operator_message": "Update-control cockpit wiring is ready. Apply/install/update authority remains blocked.",
        "cockpit_persistent_write_allowed": False,
        "cockpit_persistent_write_performed": False,
        "cockpit_action_execution_performed": False,
    }
    payload.update(BLOCKED_AUTHORITY)
    return payload


def build_s566_cockpit_payload_contract(project_root: str | Path | None = None) -> Dict[str, Any]:
    payload = build_update_control_cockpit_payload(project_root)
    return _safe_base(
        "S566",
        "update_control_cockpit_payload_contract_ready",
        sample_payload={
            "primary_status": payload["primary_status"],
            "panel_count": payload["panel_registry"]["panel_count"],
            "button_count": payload["action_buttons"]["button_count"],
            "all_authority_blocked": payload["blocked_authority_matrix"]["all_blocked"],
        },
        payload_rules=[
            "Payload is backend truth for the cockpit.",
            "Payload is review-only and non-persistent.",
            "Payload does not register update execution routes.",
        ],
    )


def build_s567_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S567",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "update_control_cockpit_panel",
            "update_runway_overview",
            "update_runway_stage_cards",
            "update_action_button_row",
            "blocked_authority_matrix",
            "stop_point_status_card",
        ],
        visual_authority="presentation_only",
    )


def build_s568_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s562 = build_s562_update_control_panel_registry()
    readiness = build_update_runway_readiness_summary(project_root)
    s563 = build_s563_update_runway_readiness_contract(project_root)
    s564 = build_cockpit_action_button_contracts()
    matrix = build_blocked_authority_matrix()
    s565 = build_s565_blocked_authority_display_contract()
    payload = build_update_control_cockpit_payload(project_root)
    s566 = build_s566_cockpit_payload_contract(project_root)
    s567 = build_s567_cockpit_asset_manifest(project_root)

    apply_button = next((button for button in s564["buttons"] if button["button_id"] == "apply_update_disabled"), {})
    enabled_exec_buttons = [button for button in s564["buttons"] if button.get("execution_allowed") is not False]

    checks = {
        "s562_panel_registry_ready": s562["panel_count"] == len(COCKPIT_PANEL_ORDER),
        "s563_runway_modules_import": readiness["all_modules_import"] is True,
        "s564_actions_do_not_execute": not enabled_exec_buttons and apply_button.get("enabled") is False,
        "s565_authority_matrix_all_blocked": matrix["all_blocked"] is True and not matrix["unexpected_enabled"],
        "s566_payload_ready": payload["primary_status"] == "review_only_ready",
        "s567_assets_exist": s567["assets"]["js_exists"] is True and s567["assets"]["css_exists"] is True,
        "panel_order_complete": s562["panel_order"] == COCKPIT_PANEL_ORDER,
        "buttons_complete": s564["button_count"] == len(ACTION_BUTTONS),
        "payload_no_persistence": payload["cockpit_persistent_write_performed"] is False,
        "payload_no_action_execution": payload["cockpit_action_execution_performed"] is False,
        "no_update_authority": all(payload.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "contracts_ready": all(contract["ready"] is True for contract in [s563, s565, s566]),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S568",
        "claire_update_control_cockpit_wiring_passed" if ok else "claire_update_control_cockpit_wiring_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "panel_registry": s562,
            "runway_readiness": readiness,
            "action_buttons": s564,
            "blocked_authority_matrix": matrix,
            "cockpit_payload": payload,
        },
        forward_motion_allowed=ok,
        next_phase="S569-S575 End-to-end governed update readiness demo",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s568_claire_update_control_cockpit_wiring_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_update_control_cockpit_wiring_s562_s568(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S562-S568",
        "claire_update_control_cockpit_wiring_ready",
        contracts={
            "s562": build_s562_update_control_panel_registry(),
            "s563": build_s563_update_runway_readiness_contract(project_root),
            "s564": build_cockpit_action_button_contracts(),
            "s565": build_s565_blocked_authority_display_contract(),
            "s566": build_s566_cockpit_payload_contract(project_root),
            "s567": build_s567_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s568_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "UPDATE_CONTROL_RUNWAY",
    "COCKPIT_PANEL_ORDER",
    "ACTION_BUTTONS",
    "build_s562_update_control_panel_registry",
    "build_update_runway_readiness_summary",
    "build_s563_update_runway_readiness_contract",
    "build_cockpit_action_button_contracts",
    "build_blocked_authority_matrix",
    "build_s565_blocked_authority_display_contract",
    "build_update_control_cockpit_payload",
    "build_s566_cockpit_payload_contract",
    "build_s567_cockpit_asset_manifest",
    "build_s568_stop_gate",
    "build_claire_update_control_cockpit_wiring_s562_s568",
]
