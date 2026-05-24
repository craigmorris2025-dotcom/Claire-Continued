from __future__ import annotations
from typing import Any

S60_VERSION = "v19.89.8-S60R1-R8"

def _authority() -> dict[str, Any]:
    return {"backend_owns_truth": True, "cockpit_presentation_only": True, "presentation_only": True, "read_only": True, "runtime_truth_mutation_allowed": False, "runtime_truth_write_allowed": False, "operator_mutation_enabled": False, "automatic_updates_enabled": False, "autonomous_execution_enabled": False, "live_web_execution_enabled": False, "manual_promotion_required": True, "quarantine_required": True, "response_mode": "quarantined_read_only_artifact"}

def build_quarantined_evidence_intake_contract() -> dict[str, Any]:
    queues = []
    for name in ("metadata_candidates","source_lineage","claim_extracts","operator_notes","promotion_candidates"):
        queues.append({"queue_id": f"s60-{name}", "state": "quarantined", "operator_visible": True, "auto_promotion_enabled": False, "runtime_truth_write_allowed": False, "manual_review_required": True, **_authority()})
    return {"version": S60_VERSION, "status": "quarantined_evidence_intake_contract_ready", "queue_count": len(queues), "queues": queues, **_authority(), "next_phase": "S61 manual promotion workflow contracts"}

def verify_quarantined_evidence_intake_contract() -> dict[str, Any]:
    payload = build_quarantined_evidence_intake_contract()
    failures = []
    if payload["queue_count"] != 5: failures.append("queue count mismatch")
    for queue in payload["queues"]:
        if queue["state"] != "quarantined": failures.append(queue["queue_id"] + " not quarantined")
        if queue["auto_promotion_enabled"]: failures.append(queue["queue_id"] + " auto promotion")
        if queue["runtime_truth_write_allowed"]: failures.append(queue["queue_id"] + " writes truth")
    return {"version": S60_VERSION, "verification_ok": failures == [], "failures": failures, "queue_count": payload["queue_count"], **_authority()}

def build_s60r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_quarantined_evidence_intake_contract()
    return {"version": S60_VERSION, "status": "s60r1_r8_ready" if verification["verification_ok"] else "s60r1_r8_blocked", "ready": verification["verification_ok"], "intake": build_quarantined_evidence_intake_contract(), "verification": verification, **_authority(), "next_phase": "S61 manual promotion workflow contracts"}
