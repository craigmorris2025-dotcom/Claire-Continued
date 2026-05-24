from __future__ import annotations
from typing import Any

S65_VERSION = "v19.89.8-S65R1-R8"

SURFACES = (
    "main_result",
    "trend_surface",
    "portfolio_surface",
    "breakthrough_surface",
    "design_surface",
    "package_surface",
)

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
    }

def build_runtime_output_rendering_contracts() -> dict[str, Any]:
    surfaces = []
    for surface in SURFACES:
        surfaces.append({
            "surface_id": surface,
            "render_mode": "read_only_payload_render",
            "operator_visible": True,
            "runtime_execution_allowed": False,
            "writes_runtime_truth": False,
            **_authority(),
        })
    return {
        "version": S65_VERSION,
        "status": "runtime_output_rendering_contracts_ready",
        "surface_count": len(surfaces),
        "surfaces": surfaces,
        **_authority(),
        "next_phase": "S66 cockpit evidence rendering",
    }

def verify_runtime_output_rendering_contracts() -> dict[str, Any]:
    payload = build_runtime_output_rendering_contracts()
    failures = []
    for surface in payload["surfaces"]:
        if surface["runtime_execution_allowed"]:
            failures.append(surface["surface_id"] + " runtime execution enabled")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s65r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_runtime_output_rendering_contracts()
    return {
        "version": S65_VERSION,
        "status": "s65r1_r8_ready" if verification["verification_ok"] else "s65r1_r8_blocked",
        "ready": verification["verification_ok"],
        "contracts": build_runtime_output_rendering_contracts(),
        "verification": verification,
        **_authority(),
        "next_phase": "S66 cockpit evidence rendering",
    }
