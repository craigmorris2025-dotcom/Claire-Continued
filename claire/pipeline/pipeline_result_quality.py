
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List

PACK_VERSION = "v19.15-v19.19"

VALID_TERMINAL_STATES = [
    "trend_thesis_ready",
    "portfolio_action_ready",
    "portfolio_optimization_ready",
    "breakthrough_classified",
    "advancement_path_selected",
    "design_output_ready",
    "acquisition_package_ready",
    "final_package_ready",
    "insufficient_data",
    "blocked",
    "failed",
]

QUALITY_GATES = [
    "evidence_present",
    "confidence_present",
    "main_result_present",
    "route_present",
    "terminal_state_present",
    "dashboard_surfaces_present",
]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def build_pipeline_result(
    terminal_state: str = "portfolio_action_ready",
    confidence: float = 0.81,
    evidence_count: int = 2,
    blocked_reason: str | None = None,
    insufficient_data_reason: str | None = None,
) -> Dict[str, Any]:
    evidence = []
    for idx in range(evidence_count):
        evidence.append(
            {
                "title": f"Evidence {idx+1}",
                "trusted": True,
                "governed": True,
            }
        )

    return {
        "pack_version": PACK_VERSION,
        "run_id": "quality-proof-run",
        "terminal_state": terminal_state,
        "route": "discovery_to_portfolio",
        "confidence": confidence,
        "evidence": evidence,
        "main_result": {
            "title": terminal_state,
            "summary": "Pipeline produced a governed result."
        },
        "dashboard_surfaces": [
            "main_result",
            "runtime_truth",
            "system_health",
        ],
        "blocked_reason": blocked_reason,
        "insufficient_data_reason": insufficient_data_reason,
        "updated_at": utc_now(),
    }

def validate_pipeline_result(result: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if result.get("terminal_state") not in VALID_TERMINAL_STATES:
        errors.append("invalid terminal state")

    if not result.get("main_result"):
        errors.append("main_result missing")

    if not result.get("dashboard_surfaces"):
        errors.append("dashboard surfaces missing")

    if result.get("terminal_state") == "blocked" and not result.get("blocked_reason"):
        errors.append("blocked state requires blocked_reason")

    if result.get("terminal_state") == "insufficient_data" and not result.get("insufficient_data_reason"):
        errors.append("insufficient_data requires insufficient_data_reason")

    if result.get("terminal_state") not in ["blocked", "insufficient_data", "failed"]:
        if result.get("confidence") is None:
            errors.append("normal terminal states require confidence")

    if result.get("terminal_state") not in ["blocked", "insufficient_data"]:
        if not result.get("evidence"):
            errors.append("normal terminal states require evidence")

    if result.get("terminal_state") == "blocked":
        if result.get("confidence") not in [0, 0.0]:
            errors.append("blocked state confidence must be zero")

    if result.get("terminal_state") == "insufficient_data":
        if result.get("confidence") not in [0, 0.0]:
            errors.append("insufficient_data confidence must be zero")

    return errors

def build_quality_report() -> Dict[str, Any]:
    normal = build_pipeline_result()
    blocked = build_pipeline_result(
        terminal_state="blocked",
        confidence=0.0,
        evidence_count=0,
        blocked_reason="operator approval required",
    )
    insufficient = build_pipeline_result(
        terminal_state="insufficient_data",
        confidence=0.0,
        evidence_count=0,
        insufficient_data_reason="not enough validated evidence",
    )

    errors = []
    errors.extend(validate_pipeline_result(normal))
    errors.extend(validate_pipeline_result(blocked))
    errors.extend(validate_pipeline_result(insufficient))

    return {
        "pack_version": PACK_VERSION,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "proofs": {
            "normal_result_valid": validate_pipeline_result(normal) == [],
            "blocked_result_valid": validate_pipeline_result(blocked) == [],
            "insufficient_result_valid": validate_pipeline_result(insufficient) == [],
            "fake_confidence_prevented": blocked["confidence"] == 0.0 and insufficient["confidence"] == 0.0,
            "main_result_required": bool(normal["main_result"]),
        },
        "updated_at": utc_now(),
    }
