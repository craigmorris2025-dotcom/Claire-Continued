from __future__ import annotations
from typing import Any

S66_VERSION = "v19.89.8-S66R1-R8"

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
    }

def build_cockpit_evidence_rendering_manifest() -> dict[str, Any]:
    panels = []
    for name in ("lineage","claims","sources","quarantine","promotion_review"):
        panels.append({
            "panel_id": f"s66-{name}",
            "visible": True,
            "render_mode": "read_only_evidence",
            "promotion_action_available": False,
            **_authority(),
        })
    return {
        "version": S66_VERSION,
        "status": "cockpit_evidence_rendering_manifest_ready",
        "panel_count": len(panels),
        "panels": panels,
        **_authority(),
        "next_phase": "S67 governed operator review dashboard",
    }

def verify_cockpit_evidence_rendering_manifest() -> dict[str, Any]:
    manifest = build_cockpit_evidence_rendering_manifest()
    failures = []
    for panel in manifest["panels"]:
        if panel["promotion_action_available"]:
            failures.append(panel["panel_id"] + " promotion enabled")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s66r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_cockpit_evidence_rendering_manifest()
    return {
        "version": S66_VERSION,
        "status": "s66r1_r8_ready" if verification["verification_ok"] else "s66r1_r8_blocked",
        "ready": verification["verification_ok"],
        "manifest": build_cockpit_evidence_rendering_manifest(),
        "verification": verification,
        **_authority(),
        "next_phase": "S67 governed operator review dashboard",
    }
