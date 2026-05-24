from __future__ import annotations
from typing import Any

S57_VERSION = "v19.89.8-S57R1-R8"
ROUTES = ("trend_thesis","portfolio_action","breakthrough_classification","design_output","acquisition_package","evidence_review","governed_web_research")

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True, "cockpit_presentation_only": True, "presentation_only": True,
        "read_only": True, "runtime_truth_mutation_allowed": False, "runtime_truth_write_allowed": False,
        "operator_mutation_enabled": False, "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False, "live_web_execution_enabled": False,
        "manual_promotion_required": True, "quarantine_required": True, "response_mode": "read_only_artifact",
    }

def build_output_dashboard_mounting_manifest() -> dict[str, Any]:
    cards = []
    for route in ROUTES:
        cards.append({
            "card_id": f"s57-output-card-{route}", "route_id": route, "mount_id": f"modern-output-{route}",
            "display_mode": "useful_output_card", "mounted": True, "visible_to_operator": True,
            "review_state": "operator_review_required", "dashboard_zone": "useful_outputs", **_authority(),
        })
    return {"version": S57_VERSION, "status": "output_dashboard_mounting_manifest_ready", "card_count": len(cards), "cards": cards, **_authority(), "next_phase": "S58 governed web provider readiness cockpit controls"}

def verify_output_dashboard_mounting_manifest() -> dict[str, Any]:
    manifest = build_output_dashboard_mounting_manifest()
    failures = []
    if manifest["card_count"] != 7: failures.append("card count mismatch")
    for card in manifest["cards"]:
        if not card["mounted"]: failures.append(card["card_id"] + " not mounted")
        if card["runtime_truth_mutation_allowed"]: failures.append(card["card_id"] + " mutation allowed")
        if card["operator_mutation_enabled"]: failures.append(card["card_id"] + " operator mutation")
    return {"version": S57_VERSION, "verification_ok": failures == [], "failures": failures, "card_count": manifest["card_count"], **_authority()}

def build_s57r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_output_dashboard_mounting_manifest()
    return {"version": S57_VERSION, "status": "s57r1_r8_ready" if verification["verification_ok"] else "s57r1_r8_blocked", "ready": verification["verification_ok"], "manifest": build_output_dashboard_mounting_manifest(), "verification": verification, **_authority(), "next_phase": "S58 governed web provider readiness cockpit controls"}
