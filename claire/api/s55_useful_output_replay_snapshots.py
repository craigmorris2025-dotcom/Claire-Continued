from __future__ import annotations

from typing import Any
from claire.api.s54_useful_output_run_history import build_s54r1_r8_plateau_report

S55_VERSION = "v19.89.8-S55R1-R8"

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

def build_output_replay_snapshot_registry() -> dict[str, Any]:
    s54 = build_s54r1_r8_plateau_report()
    snapshots = []
    for item in s54["run_history"]["history_items"]:
        snapshots.append({
            "snapshot_id": f"snapshot-{item['route_id']}",
            "history_id": item["history_id"],
            "route_id": item["route_id"],
            "snapshot_state": "replay_ready",
            "replay_mode": "read_only_snapshot",
            "source_state": item["terminal_state"],
            "operator_visible": True,
            "runtime_truth_write_allowed": False,
            "replay_mutation_allowed": False,
            "auto_replay_enabled": False,
            **_authority(),
        })
    return {
        "version": S55_VERSION,
        "phase": "S55R1-R3",
        "status": "output_replay_snapshot_registry_ready",
        "source_s54_status": s54["status"],
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
        **_authority(),
        "next_phase": "S55R4-R6 replay contract verification",
    }

def build_output_replay_contracts() -> dict[str, Any]:
    registry = build_output_replay_snapshot_registry()
    contracts = []
    for snapshot in registry["snapshots"]:
        contracts.append({
            "contract_id": f"replay-contract-{snapshot['route_id']}",
            "snapshot_id": snapshot["snapshot_id"],
            "route_id": snapshot["route_id"],
            "replay_action": "render_snapshot_for_review",
            "replay_state": "available",
            "requires_manual_review": True,
            "runtime_truth_write_allowed": False,
            "replay_mutation_allowed": False,
            "auto_replay_enabled": False,
            "auto_promotion_enabled": False,
            **_authority(),
        })
    return {
        "version": S55_VERSION,
        "phase": "S55R4-R6",
        "status": "output_replay_contracts_ready",
        "contract_count": len(contracts),
        "contracts": contracts,
        **_authority(),
        "next_phase": "S55R7-R8 replay snapshot plateau",
    }

def verify_useful_output_replay_snapshots() -> dict[str, Any]:
    registry = build_output_replay_snapshot_registry()
    contracts = build_output_replay_contracts()
    failures: list[str] = []
    if registry["snapshot_count"] != 7:
        failures.append("snapshot count mismatch")
    if contracts["contract_count"] != 7:
        failures.append("replay contract count mismatch")
    for snapshot in registry["snapshots"]:
        if snapshot["runtime_truth_write_allowed"]:
            failures.append(f"{snapshot['snapshot_id']} runtime truth write allowed")
        if snapshot["replay_mutation_allowed"]:
            failures.append(f"{snapshot['snapshot_id']} replay mutation allowed")
        if snapshot["auto_replay_enabled"]:
            failures.append(f"{snapshot['snapshot_id']} auto replay enabled")
    for contract in contracts["contracts"]:
        if contract["runtime_truth_write_allowed"]:
            failures.append(f"{contract['contract_id']} runtime truth write allowed")
        if contract["replay_mutation_allowed"]:
            failures.append(f"{contract['contract_id']} replay mutation allowed")
        if contract["auto_promotion_enabled"]:
            failures.append(f"{contract['contract_id']} auto promotion enabled")
        if not contract["requires_manual_review"]:
            failures.append(f"{contract['contract_id']} manual review not required")
    return {
        "version": S55_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "snapshot_count": registry["snapshot_count"],
        "contract_count": contracts["contract_count"],
        **_authority(),
    }

def build_s55r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_useful_output_replay_snapshots()
    return {
        "version": S55_VERSION,
        "phase": "S55R7-R8",
        "status": "s55r1_r8_ready" if verification["verification_ok"] else "s55r1_r8_blocked",
        "ready": verification["verification_ok"],
        "snapshot_registry": build_output_replay_snapshot_registry(),
        "replay_contracts": build_output_replay_contracts(),
        "verification": verification,
        **_authority(),
        "next_phase": "S56 output package export manifest and review bundle",
    }
