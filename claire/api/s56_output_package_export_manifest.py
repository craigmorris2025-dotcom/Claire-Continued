from __future__ import annotations

from typing import Any
from claire.api.s53_cockpit_useful_output_browser import build_output_export_registry
from claire.api.s55_useful_output_replay_snapshots import build_s55r1_r8_plateau_report

S56_VERSION = "v19.89.8-S56R1-R8"

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

def build_output_package_export_manifest() -> dict[str, Any]:
    exports = build_output_export_registry()["exports"]
    s55 = build_s55r1_r8_plateau_report()
    packages = []
    for item in exports:
        packages.append({
            "package_id": f"package-{item['route_id']}",
            "route_id": item["route_id"],
            "export_id": item["export_id"],
            "package_state": "available_for_operator_review",
            "bundle_type": "useful_output_review_bundle",
            "allowed_formats": list(item["allowed_formats"]),
            "includes_replay_snapshot": True,
            "includes_proof_requirements": True,
            "requires_manual_review": True,
            "runtime_truth_write_allowed": False,
            "auto_package_enabled": False,
            "auto_promotion_enabled": False,
            **_authority(),
        })
    return {
        "version": S56_VERSION,
        "phase": "S56R1-R4",
        "status": "output_package_export_manifest_ready",
        "source_s55_status": s55["status"],
        "package_count": len(packages),
        "packages": packages,
        **_authority(),
        "next_phase": "S56R5-R8 review bundle readiness plateau",
    }

def build_review_bundle_readiness_manifest() -> dict[str, Any]:
    package_manifest = build_output_package_export_manifest()
    bundles = []
    for package in package_manifest["packages"]:
        bundles.append({
            "bundle_id": f"review-bundle-{package['route_id']}",
            "package_id": package["package_id"],
            "route_id": package["route_id"],
            "bundle_state": "ready_for_review",
            "review_required": True,
            "operator_visible": True,
            "export_formats": list(package["allowed_formats"]),
            "runtime_truth_write_allowed": False,
            "auto_submit_enabled": False,
            "auto_promotion_enabled": False,
            **_authority(),
        })
    return {
        "version": S56_VERSION,
        "phase": "S56R5-R6",
        "status": "review_bundle_readiness_manifest_ready",
        "bundle_count": len(bundles),
        "bundles": bundles,
        **_authority(),
    }

def verify_output_package_export_manifest() -> dict[str, Any]:
    packages = build_output_package_export_manifest()
    bundles = build_review_bundle_readiness_manifest()
    failures: list[str] = []
    if packages["package_count"] != 7:
        failures.append("package count mismatch")
    if bundles["bundle_count"] != 7:
        failures.append("bundle count mismatch")
    for package in packages["packages"]:
        if package["runtime_truth_write_allowed"]:
            failures.append(f"{package['package_id']} runtime truth write allowed")
        if package["auto_package_enabled"]:
            failures.append(f"{package['package_id']} auto package enabled")
        if package["auto_promotion_enabled"]:
            failures.append(f"{package['package_id']} auto promotion enabled")
        if not package["requires_manual_review"]:
            failures.append(f"{package['package_id']} manual review not required")
        if "json" not in package["allowed_formats"]:
            failures.append(f"{package['package_id']} json format missing")
    for bundle in bundles["bundles"]:
        if bundle["runtime_truth_write_allowed"]:
            failures.append(f"{bundle['bundle_id']} runtime truth write allowed")
        if bundle["auto_submit_enabled"]:
            failures.append(f"{bundle['bundle_id']} auto submit enabled")
        if bundle["auto_promotion_enabled"]:
            failures.append(f"{bundle['bundle_id']} auto promotion enabled")
        if not bundle["review_required"]:
            failures.append(f"{bundle['bundle_id']} review not required")
    return {
        "version": S56_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "package_count": packages["package_count"],
        "bundle_count": bundles["bundle_count"],
        **_authority(),
    }

def build_s56r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_output_package_export_manifest()
    return {
        "version": S56_VERSION,
        "phase": "S56R7-R8",
        "status": "s56r1_r8_ready" if verification["verification_ok"] else "s56r1_r8_blocked",
        "ready": verification["verification_ok"],
        "package_manifest": build_output_package_export_manifest(),
        "review_bundles": build_review_bundle_readiness_manifest(),
        "verification": verification,
        **_authority(),
        "next_phase": "S57 output-to-dashboard mounting and useful output cards",
    }
