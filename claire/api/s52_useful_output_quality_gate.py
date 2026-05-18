from __future__ import annotations

from typing import Any

from claire.api.s51_route_specific_useful_outputs import (
    build_all_route_output_previews,
    build_s51r1_r8_plateau_report,
)


S52_VERSION = "v19.89.8-S52R1-R8"


REQUIRED_PREVIEW_KEYS = (
    "route_id",
    "headline",
    "summary",
    "terminal_state",
    "sections",
    "confidence",
    "evidence_state",
    "review_state",
    "useful_output_ready",
)


def _base_authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "fabricated_evidence_allowed": False,
        "response_mode": "read_only_artifact",
    }


def build_useful_output_quality_gate() -> dict[str, Any]:
    s51 = build_s51r1_r8_plateau_report()
    previews = build_all_route_output_previews()["previews"]

    checks = []
    failures = []

    for preview in previews:
        missing = [key for key in REQUIRED_PREVIEW_KEYS if key not in preview]
        section_count = len(preview.get("sections", {}))
        check = {
            "route_id": preview.get("route_id"),
            "surface_id": preview.get("surface_id"),
            "missing_required_keys": missing,
            "section_count": section_count,
            "has_required_sections": section_count > 0,
            "has_headline": bool(preview.get("headline")),
            "has_summary": bool(preview.get("summary")),
            "has_terminal_state": bool(preview.get("terminal_state")),
            "has_review_state": bool(preview.get("review_state")),
            "has_evidence_state": bool(preview.get("evidence_state")),
            "runtime_truth_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "quality_gate_passed": missing == [] and section_count > 0,
        }
        if not check["quality_gate_passed"]:
            failures.append(check)
        checks.append(check)

    return {
        "version": S52_VERSION,
        "phase": "S52R1-R4",
        "status": "useful_output_quality_gate_ready",
        "source_s51_status": s51["status"],
        "output_count": len(previews),
        "check_count": len(checks),
        "passed_count": sum(1 for check in checks if check["quality_gate_passed"]),
        "failure_count": len(failures),
        "checks": checks,
        "failures": failures,
        "quality_gate_passed": failures == [],
        **_base_authority(),
        "next_phase": "S52R5-R8 output proof requirements and plateau",
    }


def build_output_proof_requirements() -> dict[str, Any]:
    gate = build_useful_output_quality_gate()
    requirements = [
        {
            "requirement_id": "evidence_lineage",
            "title": "Evidence lineage must be visible before promotion.",
            "required": True,
            "auto_promotion_allowed": False,
        },
        {
            "requirement_id": "confidence_state",
            "title": "Confidence state must be explicit.",
            "required": True,
            "auto_promotion_allowed": False,
        },
        {
            "requirement_id": "route_terminal_state",
            "title": "Route terminal state must be declared.",
            "required": True,
            "auto_promotion_allowed": False,
        },
        {
            "requirement_id": "operator_review",
            "title": "Operator review must remain required before runtime truth.",
            "required": True,
            "auto_promotion_allowed": False,
        },
    ]

    return {
        "version": S52_VERSION,
        "phase": "S52R5-R6",
        "status": "output_proof_requirements_ready",
        "source_quality_gate_passed": gate["quality_gate_passed"],
        "requirement_count": len(requirements),
        "requirements": [
            {
                **requirement,
                **_base_authority(),
                "runtime_truth_write_allowed": False,
            }
            for requirement in requirements
        ],
        **_base_authority(),
    }


def verify_useful_output_quality_gate() -> dict[str, Any]:
    gate = build_useful_output_quality_gate()
    proof = build_output_proof_requirements()
    failures: list[Any] = []

    if not gate["quality_gate_passed"]:
        failures.extend(gate["failures"])
    if gate["output_count"] != 7:
        failures.append("output count mismatch")
    if proof["requirement_count"] != 4:
        failures.append("proof requirement count mismatch")

    for requirement in proof["requirements"]:
        if not requirement["required"]:
            failures.append(f"{requirement['requirement_id']} not required")
        if requirement["auto_promotion_allowed"]:
            failures.append(f"{requirement['requirement_id']} auto promotion allowed")
        if requirement["runtime_truth_write_allowed"]:
            failures.append(f"{requirement['requirement_id']} runtime truth write allowed")

    return {
        "version": S52_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "output_count": gate["output_count"],
        "requirement_count": proof["requirement_count"],
        **_base_authority(),
    }


def build_s52r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_useful_output_quality_gate()
    return {
        "version": S52_VERSION,
        "phase": "S52R7-R8",
        "status": "s52r1_r8_ready" if verification["verification_ok"] else "s52r1_r8_blocked",
        "ready": verification["verification_ok"],
        "quality_gate": build_useful_output_quality_gate(),
        "proof_requirements": build_output_proof_requirements(),
        "verification": verification,
        **_base_authority(),
        "next_phase": "S53 cockpit useful output browser and export registry",
    }
