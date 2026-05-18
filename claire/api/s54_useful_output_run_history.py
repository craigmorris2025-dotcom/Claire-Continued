from __future__ import annotations

from typing import Any
from claire.api.s53_cockpit_useful_output_browser import build_s53r1_r8_plateau_report

S54_VERSION = "v19.89.8-S54R1-R8"

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "response_mode": "read_only_artifact",
    }

def build_useful_output_persistence_contract() -> dict[str, Any]:
    s53 = build_s53r1_r8_plateau_report()
    export_items = s53["export_registry"]["exports"]
    records = []
    for item in export_items:
        records.append({
            "record_id": f"history-{item['route_id']}",
            "route_id": item["route_id"],
            "export_id": item["export_id"],
            "record_state": "available_for_operator_review",
            "storage_mode": "contract_only_no_runtime_write",
            "requires_manual_review": True,
            "runtime_truth_write_allowed": False,
            "auto_persist_enabled": False,
            "auto_promotion_enabled": False,
            "allowed_formats": list(item["allowed_formats"]),
            **_authority(),
        })
    return {
        "version": S54_VERSION,
        "phase": "S54R1-R3",
        "status": "useful_output_persistence_contract_ready",
        "source_s53_status": s53["status"],
        "record_count": len(records),
        "records": records,
        "persistence_state": "review_record_contract_ready",
        **_authority(),
        "next_phase": "S54R4-R6 run history integration contract",
    }

def build_run_history_integration_contract() -> dict[str, Any]:
    persistence = build_useful_output_persistence_contract()
    run_history_items = []
    for record in persistence["records"]:
        run_history_items.append({
            "history_id": f"run-history-{record['route_id']}",
            "record_id": record["record_id"],
            "route_id": record["route_id"],
            "terminal_state": "awaiting_backend_run",
            "display_state": "visible_in_run_history",
            "review_state": "operator_review_required",
            "history_visibility": "operator_visible",
            "runtime_truth_write_allowed": False,
            "auto_update_history_enabled": False,
            **_authority(),
        })
    return {
        "version": S54_VERSION,
        "phase": "S54R4-R6",
        "status": "run_history_integration_contract_ready",
        "history_item_count": len(run_history_items),
        "history_items": run_history_items,
        "source_record_count": persistence["record_count"],
        **_authority(),
        "next_phase": "S54R7-R8 useful output persistence plateau",
    }

def verify_useful_output_run_history() -> dict[str, Any]:
    persistence = build_useful_output_persistence_contract()
    history = build_run_history_integration_contract()
    failures: list[str] = []
    if persistence["record_count"] != 7:
        failures.append("persistence record count mismatch")
    if history["history_item_count"] != 7:
        failures.append("history item count mismatch")
    for record in persistence["records"]:
        if record["runtime_truth_write_allowed"]:
            failures.append(f"{record['record_id']} runtime truth write allowed")
        if record["auto_persist_enabled"]:
            failures.append(f"{record['record_id']} auto persist enabled")
        if record["auto_promotion_enabled"]:
            failures.append(f"{record['record_id']} auto promotion enabled")
        if not record["requires_manual_review"]:
            failures.append(f"{record['record_id']} manual review not required")
    for item in history["history_items"]:
        if item["runtime_truth_write_allowed"]:
            failures.append(f"{item['history_id']} runtime truth write allowed")
        if item["auto_update_history_enabled"]:
            failures.append(f"{item['history_id']} auto update history enabled")
        if item["history_visibility"] != "operator_visible":
            failures.append(f"{item['history_id']} visibility drift")
    return {
        "version": S54_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "record_count": persistence["record_count"],
        "history_item_count": history["history_item_count"],
        **_authority(),
    }

def build_s54r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_useful_output_run_history()
    return {
        "version": S54_VERSION,
        "phase": "S54R7-R8",
        "status": "s54r1_r8_ready" if verification["verification_ok"] else "s54r1_r8_blocked",
        "ready": verification["verification_ok"],
        "persistence": build_useful_output_persistence_contract(),
        "run_history": build_run_history_integration_contract(),
        "verification": verification,
        **_authority(),
        "next_phase": "S55 useful output replay and snapshot registry",
    }
