from __future__ import annotations
from typing import Any

S67_VERSION = "v19.89.8-S67R1-R8"

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "operator_mutation_enabled": False,
        "manual_promotion_required": True,
    }

def build_operator_review_dashboard_contract() -> dict[str, Any]:
    widgets = []
    for widget in ("run_history","useful_outputs","evidence_review","provider_status","readiness_snapshot"):
        widgets.append({
            "widget_id": f"s67-{widget}",
            "visible": True,
            "interactive_mode": "read_only_review",
            "operator_execute_enabled": False,
            **_authority(),
        })
    return {
        "version": S67_VERSION,
        "status": "operator_review_dashboard_contract_ready",
        "widget_count": len(widgets),
        "widgets": widgets,
        **_authority(),
        "next_phase": "S68 governed dashboard navigation stabilization",
    }

def verify_operator_review_dashboard_contract() -> dict[str, Any]:
    payload = build_operator_review_dashboard_contract()
    failures = []
    for widget in payload["widgets"]:
        if widget["operator_execute_enabled"]:
            failures.append(widget["widget_id"] + " execution enabled")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s67r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_operator_review_dashboard_contract()
    return {
        "version": S67_VERSION,
        "status": "s67r1_r8_ready" if verification["verification_ok"] else "s67r1_r8_blocked",
        "ready": verification["verification_ok"],
        "dashboard": build_operator_review_dashboard_contract(),
        "verification": verification,
        **_authority(),
        "next_phase": "S68 governed dashboard navigation stabilization",
    }
