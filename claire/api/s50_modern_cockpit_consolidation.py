from __future__ import annotations

from typing import Any

from claire.api.s48_dashboard_route_payload_browser import build_s48r1_r8_plateau_report
from claire.api.s49_governed_web_evidence_panels import build_s49r1_r8_plateau_report

S50_VERSION = "v19.89.8-S50R1-R8"
CONSOLIDATED_ASSET_ROOT = "frontend/cockpit/modern_shell"
CONSOLIDATED_HTML = f"{CONSOLIDATED_ASSET_ROOT}/claire_consolidated_cockpit.html"
CONSOLIDATED_JS = f"{CONSOLIDATED_ASSET_ROOT}/claire_consolidated_cockpit.js"
CONSOLIDATED_CSS = f"{CONSOLIDATED_ASSET_ROOT}/claire_consolidated_cockpit.css"


def build_modern_cockpit_consolidation_manifest() -> dict[str, Any]:
    s48 = build_s48r1_r8_plateau_report()
    s49 = build_s49r1_r8_plateau_report()

    consolidated_sections = [
        {"section_id": "command_status", "title": "Command Status", "source": "s47.status_zones", "ready": True},
        {"section_id": "operator_panels", "title": "Operator Panels", "source": "s47.operator_panels", "ready": True},
        {"section_id": "route_payload_browser", "title": "Route / Payload Browser", "source": "s48.route_index", "ready": s48["ready"]},
        {"section_id": "governed_web", "title": "Governed Web", "source": "s49.governed_web", "ready": s49["ready"]},
        {"section_id": "evidence_review", "title": "Evidence Review", "source": "s49.evidence_review", "ready": s49["ready"]},
    ]

    normalized_sections = []
    for index, section in enumerate(consolidated_sections, start=1):
        normalized_sections.append({
            **section,
            "render_order": index,
            "visible": True,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
            "live_web_execution_enabled": False,
            "response_mode": "read_only_artifact",
        })

    ready = all(section["ready"] for section in normalized_sections)

    return {
        "version": S50_VERSION,
        "phase": "S50R1-R4",
        "status": "modern_cockpit_consolidation_manifest_ready" if ready else "modern_cockpit_consolidation_blocked",
        "ready": ready,
        "section_count": len(normalized_sections),
        "sections": normalized_sections,
        "asset_root": CONSOLIDATED_ASSET_ROOT,
        "html_asset": CONSOLIDATED_HTML,
        "js_asset": CONSOLIDATED_JS,
        "css_asset": CONSOLIDATED_CSS,
        "source_statuses": {"s47": "s47r1_r8_ready", "s48": s48["status"], "s49": s49["status"]},
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "next_phase": "S51 route-specific useful output surfaces",
    }


def verify_modern_cockpit_consolidation_manifest() -> dict[str, Any]:
    manifest = build_modern_cockpit_consolidation_manifest()
    failures: list[str] = []

    if not manifest["ready"]:
        failures.append("consolidation dependencies not ready")
    if manifest["section_count"] != 5:
        failures.append("section count mismatch")
    for section in manifest["sections"]:
        if not section["visible"]:
            failures.append(f"{section['section_id']} not visible")
        if not section["presentation_only"]:
            failures.append(f"{section['section_id']} presentation drift")
        if section["runtime_truth_mutation_allowed"]:
            failures.append(f"{section['section_id']} runtime truth mutation drift")
        if section["operator_mutation_enabled"]:
            failures.append(f"{section['section_id']} operator mutation enabled")
        if section["automatic_updates_enabled"]:
            failures.append(f"{section['section_id']} automatic updates enabled")
        if section["live_web_execution_enabled"]:
            failures.append(f"{section['section_id']} live web execution enabled")

    return {
        "version": S50_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "section_count": manifest["section_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }


def build_demo_readiness_snapshot() -> dict[str, Any]:
    manifest = build_modern_cockpit_consolidation_manifest()
    verification = verify_modern_cockpit_consolidation_manifest()
    return {
        "version": S50_VERSION,
        "phase": "S50R5-R6",
        "status": "demo_readiness_snapshot_ready" if verification["verification_ok"] else "demo_readiness_blocked",
        "ready": verification["verification_ok"],
        "dashboard_ready": verification["verification_ok"],
        "operator_panels_ready": True,
        "route_browser_ready": True,
        "governed_web_visible": True,
        "evidence_review_visible": True,
        "useful_outputs_ready": False,
        "live_web_updates_enabled": False,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "next_gap": "route-specific useful output surfaces",
        "next_phase": "S51 route-specific useful output surfaces",
        "manifest": manifest,
    }


def build_s50r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_modern_cockpit_consolidation_manifest()
    snapshot = build_demo_readiness_snapshot()
    return {
        "version": S50_VERSION,
        "phase": "S50R7-R8",
        "status": "s50r1_r8_ready" if verification["verification_ok"] else "s50r1_r8_blocked",
        "ready": verification["verification_ok"],
        "verification": verification,
        "demo_readiness": snapshot,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "next_phase": "S51 route-specific useful output surfaces",
    }
