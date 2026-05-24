from __future__ import annotations
from typing import Any

S74_VERSION = "v19.89.8-S74R1-R8"

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
    }

def build_governed_output_quality_scoring() -> dict[str, Any]:
    scores = []
    for metric in ("completeness","evidence_lineage","route_fit","reviewability","export_readiness"):
        scores.append({
            "metric_id": f"s74-{metric}",
            "score_state": "scorable",
            "operator_visible": True,
            "auto_pass_enabled": False,
            "runtime_truth_write_allowed": False,
            **_authority(),
        })
    return {
        "version": S74_VERSION,
        "status": "governed_output_quality_scoring_ready",
        "metric_count": len(scores),
        "scores": scores,
        **_authority(),
        "next_phase": "S75 cockpit demo run packet",
    }

def verify_governed_output_quality_scoring() -> dict[str, Any]:
    payload = build_governed_output_quality_scoring()
    failures = []
    for score in payload["scores"]:
        if score["auto_pass_enabled"]:
            failures.append(score["metric_id"] + " auto pass")
        if score["runtime_truth_write_allowed"]:
            failures.append(score["metric_id"] + " writes truth")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s74r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_governed_output_quality_scoring()
    return {
        "version": S74_VERSION,
        "status": "s74r1_r8_ready" if verification["verification_ok"] else "s74r1_r8_blocked",
        "ready": verification["verification_ok"],
        "scoring": build_governed_output_quality_scoring(),
        "verification": verification,
        **_authority(),
        "next_phase": "S75 cockpit demo run packet",
    }
